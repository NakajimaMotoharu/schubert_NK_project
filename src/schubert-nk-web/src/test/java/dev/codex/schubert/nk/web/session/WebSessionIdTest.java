package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Independent Python base64/hashlib fixed vectors and public CSPRNG boundary, PT-WEB-001..004. */
class WebSessionIdTest {
  static final String ZERO = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
  static final String SEQUENCE = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8";
  static final String FULL = "__________________________________________8";
  static final String[] HASHES = {
    "0f007385b6f9d4b7eeb2748605afe1a984a0a3bfa3f014d09e2a784ce9e5cd1a",
    "ea866a757e4c38babfa8127cbe9a409d3e1f93a00ff1488ff735fcf917afffd0",
    "225f7e75329dd45aa354975d73987319309393af3a4c6733bc13601a4f1b8796"
  };

  @Test
  void web001CanonicalIdsAndIndependentHashes() throws Exception {
    var values = List.of(ZERO, SEQUENCE, FULL);
    for (int i = 0; i < 3; i++) {
      var id = WebSessionId.parse(values.get(i));
      assertEquals(values.get(i), id.cookieValue());
      assertEquals(HASHES[i], id.lookupHash());
      assertEquals("WebSessionId[REDACTED]", id.toString());
      assertEquals(32, Base64.getUrlDecoder().decode(id.cookieValue()).length);
      assertFalse(id.toString().contains(id.cookieValue()));
      assertFalse(id.toString().contains(id.lookupHash()));
    }
  }

  @Test
  void web002NullLengthAlphabetAndUnusedBitsReject() {
    assertThrows(NullPointerException.class, () -> WebSessionId.parse(null));
    assertThrows(NullPointerException.class, () -> WebSessionId.generate(null));
    for (String value :
        List.of(
            "",
            "A".repeat(42),
            "A".repeat(44),
            ZERO + "=",
            "+" + ZERO.substring(1),
            "/" + ZERO.substring(1),
            " " + ZERO.substring(1),
            "\n" + ZERO.substring(1),
            "é" + ZERO.substring(1),
            "A".repeat(42) + "B",
            "A".repeat(42) + "C",
            "A".repeat(42) + "D")) {
      var error = assertThrows(IllegalArgumentException.class, () -> WebSessionId.parse(value));
      assertEquals("web session identity is invalid", error.getMessage());
      assertNull(error.getCause());
      assertEquals(0, error.getSuppressed().length);
    }
  }

  @Test
  void web003GenerationOwnsAndErasesRandomBuffers() {
    for (int mode = 0; mode < 3; mode++) {
      var random = new FixedRandom(mode, false);
      var id = WebSessionId.generate(random);
      assertEquals(List.of(ZERO, SEQUENCE, FULL).get(mode), id.cookieValue());
      assertEquals(1, random.calls);
      assertArrayEquals(new byte[32], random.observed);
    }
    var failing = new FixedRandom(1, true);
    assertThrows(IllegalStateException.class, () -> WebSessionId.generate(failing));
    assertEquals(1, failing.calls);
    assertArrayEquals(new byte[32], failing.observed);
  }

  @Test
  void web004ConcurrentIdsAndHashesShareNoMutableDigest() throws Exception {
    var random = new SecureRandom();
    var ids = ConcurrentHashMap.<String>newKeySet();
    var pool = Executors.newFixedThreadPool(10);
    try {
      var futures = new ArrayList<Future<Void>>();
      for (int i = 0; i < 100; i++)
        futures.add(
            pool.submit(
                () -> {
                  var id = WebSessionId.generate(random);
                  assertTrue(ids.add(id.cookieValue()));
                  byte[] raw = Base64.getUrlDecoder().decode(id.cookieValue());
                  assertEquals(32, raw.length);
                  assertEquals(
                      id.cookieValue(),
                      Base64.getUrlEncoder().withoutPadding().encodeToString(raw));
                  String expected =
                      HexFormat.of()
                          .formatHex(
                              MessageDigest.getInstance("SHA-256")
                                  .digest(id.cookieValue().getBytes(StandardCharsets.US_ASCII)));
                  assertEquals(expected, id.lookupHash());
                  assertEquals(HASHES[1], WebSessionId.parse(SEQUENCE).lookupHash());
                  return null;
                }));
      for (var future : futures) future.get(20, TimeUnit.SECONDS);
    } finally {
      pool.shutdownNow();
      if (!pool.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("session identity workers did not terminate");
      }
    }
    assertEquals(100, ids.size());
  }

  static final class FixedRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    final int mode;
    final boolean failure;
    int calls;
    byte[] observed;

    FixedRandom(int mode, boolean failure) {
      this.mode = mode;
      this.failure = failure;
    }

    @Override
    public void nextBytes(byte[] bytes) {
      calls++;
      assertEquals(32, bytes.length);
      observed = bytes;
      for (int i = 0; i < 32; i++) bytes[i] = (byte) (mode == 0 ? 0 : mode == 1 ? i : 255);
      if (failure) throw new IllegalStateException("synthetic random unavailable");
    }
  }
}
