package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.security.ProviderException;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * NK-WEB-001/PT-WEB-032..035; FUN-001/AUT-004; UI226; SS314/352; PG-D-097. Fixed hex is independent
 * of the production formatter; no deployed token/secret is used.
 */
class WebCsrfTokenTest {
  private static final int MIN_TOKEN_LENGTH = 64;
  private static final int MAX_TOKEN_LENGTH = 128;

  private static final String HEX =
      "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f";
  private static final String ALPHABET =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-";

  @Test
  void web032GenerationMatchesIndependentHexAndErasesBuffers() {
    var random = new FixedRandom();
    var token = WebCsrfToken.generate(random);
    assertEquals(HEX, token.formValue());
    assertTrue(token.matches(HEX));
    assertArrayEquals(new byte[32], random.last);
    random.fail = true;
    var error = assertThrows(IllegalStateException.class, () -> WebCsrfToken.generate(random));
    assertEquals("CSRF generation is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertArrayEquals(new byte[32], random.last);
    assertThrows(NullPointerException.class, () -> WebCsrfToken.generate(null));
  }

  @Test
  void web033EveryAllowedLengthMatchesOnlyIdenticalToken() {
    for (int length = 64; length <= 128; length++) {
      String expected = ALPHABET.repeat(2).substring(0, length);
      var token = WebCsrfToken.parse(expected);
      assertEquals(expected, token.formValue());
      assertTrue(token.matches(expected));
      for (int position : new int[] {0, length / 2, length - 1}) {
        var different = new StringBuilder(expected);
        different.setCharAt(position, expected.charAt(position) == 'Z' ? 'X' : 'Z');
        assertFalse(token.matches(different.toString()));
      }
      if (length > MIN_TOKEN_LENGTH) assertFalse(token.matches(expected.substring(0, length - 1)));
      if (length < MAX_TOKEN_LENGTH) assertFalse(token.matches(expected + "A"));
    }
  }

  @Test
  void web034MissingMalformedAndNullBoundariesStayRedacted() {
    assertThrows(NullPointerException.class, () -> WebCsrfToken.parse(null));
    var token = WebCsrfToken.parse(HEX);
    assertFalse(token.matches(null));
    for (String bad :
        List.of(
            "",
            "a".repeat(63),
            "a".repeat(129),
            "a".repeat(100000),
            "あ".repeat(64),
            "a".repeat(63) + "+",
            "a".repeat(63) + "/",
            "a".repeat(63) + "=",
            " " + "a".repeat(63),
            "a".repeat(63) + "\n",
            "a".repeat(63) + "\0",
            "a".repeat(63) + "\ud800")) {
      var error = assertThrows(IllegalArgumentException.class, () -> WebCsrfToken.parse(bad));
      assertEquals("CSRF token is invalid", error.getMessage());
      assertNull(error.getCause());
      assertEquals(0, error.getSuppressed().length);
      assertFalse(token.matches(bad));
    }
    assertEquals("WebCsrfToken[REDACTED]", token.toString());
  }

  @Test
  void web035ConcurrentGenerationAndMatchingStayIndependent() throws Exception {
    var shared = WebCsrfToken.parse(HEX);
    var random = new SecureRandom();
    try (var pool = Executors.newFixedThreadPool(10)) {
      var jobs = new ArrayList<Callable<String>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              var token = WebCsrfToken.generate(random);
              assertEquals(64, token.formValue().length());
              assertTrue(token.formValue().matches("[0-9a-f]{64}"));
              assertTrue(token.matches(token.formValue()));
              assertTrue(shared.matches(HEX));
              assertFalse(shared.matches("f".repeat(64)));
              return token.formValue();
            });
      var values = new HashSet<String>();
      for (var future : pool.invokeAll(jobs))
        assertTrue(values.add(future.get(20, TimeUnit.SECONDS)));
      assertEquals(100, values.size());
    }
  }

  private static final class FixedRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    byte[] last = new byte[0];
    boolean fail;

    @Override
    public void nextBytes(byte[] bytes) {
      assertEquals(32, bytes.length);
      last = bytes;
      for (int i = 0; i < 32; i++) bytes[i] = (byte) i;
      if (fail) throw new ProviderException("private-provider-marker");
    }
  }
}
