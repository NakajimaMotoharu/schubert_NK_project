package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.idempotency.ResultBoundResponseSnapshotCodec;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.zip.InflaterInputStream;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** PT-DB-INBOX-169..176; SS352 11.2.1/SSC-052/PG-D-140; no real credential or business DB. */
final class ResultBoundResponseSnapshotCodecTest {
  private static final String FIXTURE_NTCRSP01_CFC2AD25 = "NTCRSP01";
  private static final String FIXTURE_QDLRSP01_1746478A = "QDLRSP01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final List<String> ROUTES =
      List.of("QSBRSP01", FIXTURE_NTCRSP01_CFC2AD25, FIXTURE_QDLRSP01_1746478A);
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID TOKEN = new UUID(0, 5);
  private static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123Z");

  @Test
  void independentWriteAndReadAllRoutes() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture()) {
      var codec = new ResultBoundResponseSnapshotCodec(f.codec);
      for (String route : ROUTES)
        for (long target : new long[] {1, 999_999_999_999L})
          for (UUID token : List.of(new UUID(0, 0), new UUID(-1, -1))) {
            byte[] wire = wire(route, 42);
            byte[] expected = plain(route, target, token, wire);
            var encrypted = codec.encrypt(id(route), ref(route, target), token, wire);
            assertArrayEquals(expected, independentDecrypt(f.key, id(route), encrypted));
            var independentlySaved = saved(f, id(route), expected);
            assertArrayEquals(
                wire, codec.decrypt(id(route), ref(route, target), token, independentlySaved));
          }
      byte[] literal =
          plain(FIXTURE_QDLRSP01_1746478A, 9, TOKEN, wire(FIXTURE_QDLRSP01_1746478A, 0));
      assertEquals(
          "4e4b524546310100000000000000090000000000000000000000000000000500000118",
          HexFormat.of().formatHex(Arrays.copyOf(literal, 35)));
    }
  }

  @Test
  void nullIdentityAndReferenceContracts() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture()) {
      var codec = new ResultBoundResponseSnapshotCodec(f.codec);
      assertThrows(NullPointerException.class, () -> new ResultBoundResponseSnapshotCodec(null));
      for (String route : ROUTES) {
        var identity = id(route);
        var reference = ref(route, 9);
        byte[] wire = wire(route, 1);
        var snapshot = codec.encrypt(identity, reference, TOKEN, wire);
        assertThrows(NullPointerException.class, () -> codec.encrypt(null, reference, TOKEN, wire));
        assertThrows(NullPointerException.class, () -> codec.encrypt(identity, null, TOKEN, wire));
        assertThrows(
            NullPointerException.class, () -> codec.encrypt(identity, reference, null, wire));
        assertThrows(
            NullPointerException.class, () -> codec.encrypt(identity, reference, TOKEN, null));
        assertThrows(
            NullPointerException.class, () -> codec.decrypt(null, reference, TOKEN, snapshot));
        assertThrows(
            NullPointerException.class, () -> codec.decrypt(identity, null, TOKEN, snapshot));
        assertThrows(
            NullPointerException.class, () -> codec.decrypt(identity, reference, null, snapshot));
        assertThrows(
            NullPointerException.class, () -> codec.decrypt(identity, reference, TOKEN, null));
        for (var invalid :
            List.of(
                ResponseSnapshotIdentity.anonymous(MESSAGE, route, FIXTURE_001_A3FEAA64),
                ResponseSnapshotIdentity.authenticated(MESSAGE, route, "002", 7),
                ResponseSnapshotIdentity.authenticated(
                    MESSAGE, "GAMRSP01", FIXTURE_001_A3FEAA64, 7))) {
          assertThrows(
              IllegalArgumentException.class, () -> codec.encrypt(invalid, reference, TOKEN, wire));
          assertThrows(
              IllegalArgumentException.class,
              () -> codec.decrypt(invalid, reference, TOKEN, snapshot));
        }
        for (var invalid :
            List.of(
                InboxResultReference.none(),
                InboxResultReference.authSession(MESSAGE),
                InboxResultReference.numeric(InboxResultReferenceType.USER, 9),
                InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 9),
                InboxResultReference.numeric(
                    route.equals(FIXTURE_NTCRSP01_CFC2AD25)
                        ? InboxResultReferenceType.QUESTION
                        : InboxResultReferenceType.JOB,
                    9))) {
          assertThrows(
              IllegalArgumentException.class, () -> codec.encrypt(identity, invalid, TOKEN, wire));
          assertThrows(
              IllegalArgumentException.class,
              () -> codec.decrypt(identity, invalid, TOKEN, snapshot));
        }
      }
    }
  }

  @Test
  void everyMetadataByteIsAuthenticated() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture()) {
      var codec = new ResultBoundResponseSnapshotCodec(f.codec);
      for (String route : ROUTES) {
        byte[] wire = wire(route, 3);
        byte[] original = plain(route, 9, TOKEN, wire);
        for (int position = 0; position < 35; position++) {
          byte[] changed = original.clone();
          changed[position] ^= 1;
          var encrypted = saved(f, id(route), changed);
          var failure =
              assertThrows(
                  ResponseSnapshotException.class,
                  () -> codec.decrypt(id(route), ref(route, 9), TOKEN, encrypted));
          assertEquals(ResponseSnapshotException.Reason.SNAPSHOT_INVALID, failure.reason());
          assertEquals("bound response metadata is invalid", failure.getMessage());
          assertNull(failure.getCause());
          assertEquals(0, failure.getSuppressed().length);
        }
        assertArrayEquals(
            wire, codec.decrypt(id(route), ref(route, 9), TOKEN, saved(f, id(route), original)));
      }
    }
  }

  @Test
  void exactLengthAndLegacyRejection() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture()) {
      var codec = new ResultBoundResponseSnapshotCodec(f.codec);
      for (String route : ROUTES) {
        int length = length(route);
        for (int size : new int[] {0, 1, length - 1, length + 1, 1_000_001})
          assertThrows(
              IllegalArgumentException.class,
              () -> codec.encrypt(id(route), ref(route, 9), TOKEN, new byte[size]));
        byte[] valid = plain(route, 9, TOKEN, wire(route, 2));
        for (int size : new int[] {0, 1, 34, 35, length, valid.length - 1, valid.length + 1}) {
          var snapshot = saved(f, id(route), Arrays.copyOf(valid, size));
          assertThrows(
              ResponseSnapshotException.class,
              () -> codec.decrypt(id(route), ref(route, 9), TOKEN, snapshot));
        }
        for (int declared : new int[] {0, -1, Integer.MAX_VALUE}) {
          byte[] changed = valid.clone();
          ByteBuffer.wrap(changed, 31, 4).putInt(declared);
          var snapshot = saved(f, id(route), changed);
          assertThrows(
              ResponseSnapshotException.class,
              () -> codec.decrypt(id(route), ref(route, 9), TOKEN, snapshot));
        }
      }
    }
  }

  @Test
  void keysAadAndCipherDamage() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture()) {
      byte[] newKey = new byte[32];
      new SecureRandom().nextBytes(newKey);
      try (var rotated = new ResponseSnapshotCodec("v2", newKey, "v1", f.key);
          var unrelated = new ResponseSnapshotCodec("v1", newKey, null, null);
          var unknown = new ResponseSnapshotCodec("v2", newKey, null, null)) {
        var codec = new ResultBoundResponseSnapshotCodec(f.codec);
        var snapshot =
            codec.encrypt(
                id(FIXTURE_QDLRSP01_1746478A),
                ref(FIXTURE_QDLRSP01_1746478A, 9),
                TOKEN,
                wire(FIXTURE_QDLRSP01_1746478A, 7));
        assertArrayEquals(
            wire(FIXTURE_QDLRSP01_1746478A, 7),
            new ResultBoundResponseSnapshotCodec(rotated)
                .decrypt(
                    id(FIXTURE_QDLRSP01_1746478A),
                    ref(FIXTURE_QDLRSP01_1746478A, 9),
                    TOKEN,
                    snapshot));
        assertThrows(
            ResponseSnapshotException.class,
            () ->
                new ResultBoundResponseSnapshotCodec(unrelated)
                    .decrypt(
                        id(FIXTURE_QDLRSP01_1746478A),
                        ref(FIXTURE_QDLRSP01_1746478A, 9),
                        TOKEN,
                        snapshot));
        assertEquals(
            ResponseSnapshotException.Reason.KEY_UNAVAILABLE,
            assertThrows(
                    ResponseSnapshotException.class,
                    () ->
                        new ResultBoundResponseSnapshotCodec(unknown)
                            .decrypt(
                                id(FIXTURE_QDLRSP01_1746478A),
                                ref(FIXTURE_QDLRSP01_1746478A, 9),
                                TOKEN,
                                snapshot))
                .reason());
        for (var altered :
            List.of(
                ResponseSnapshotIdentity.authenticated(
                    new UUID(0, 2), FIXTURE_QDLRSP01_1746478A, FIXTURE_001_A3FEAA64, 7),
                ResponseSnapshotIdentity.authenticated(
                    MESSAGE, FIXTURE_QDLRSP01_1746478A, FIXTURE_001_A3FEAA64, 8),
                id("QSBRSP01"))) {
          assertThrows(
              ResponseSnapshotException.class,
              () -> codec.decrypt(altered, ref(altered.responseLayoutId(), 9), TOKEN, snapshot));
        }
        for (int position : new int[] {0, 6, 8, 10, snapshot.ciphertext().length - 1}) {
          byte[] bytes = snapshot.ciphertext();
          bytes[position] ^= 1;
          var changed = new EncryptedResponseSnapshot("v1", bytes);
          assertThrows(
              ResponseSnapshotException.class,
              () ->
                  codec.decrypt(
                      id(FIXTURE_QDLRSP01_1746478A),
                      ref(FIXTURE_QDLRSP01_1746478A, 9),
                      TOKEN,
                      changed));
        }
      } finally {
        Arrays.fill(newKey, (byte) 0);
      }
    }
  }

  @Test
  void borrowedOwnershipAndRedaction() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture()) {
      var codec = new ResultBoundResponseSnapshotCodec(f.codec);
      String route = FIXTURE_NTCRSP01_CFC2AD25;
      byte[] input = wire(route, 6);
      byte[] before = input.clone();
      var snapshot = codec.encrypt(id(route), ref(route, 9), TOKEN, input);
      assertArrayEquals(before, input);
      byte[] first = codec.decrypt(id(route), ref(route, 9), TOKEN, snapshot);
      Arrays.fill(first, (byte) 0);
      assertArrayEquals(before, codec.decrypt(id(route), ref(route, 9), TOKEN, snapshot));
      assertThrows(
          ResponseSnapshotException.class,
          () -> codec.decrypt(id(route), ref(route, 10), TOKEN, snapshot));
      assertArrayEquals(before, input);
      assertArrayEquals(plain(route, 9, TOKEN, input), f.codec.decrypt(id(route), snapshot));
      assertEquals("ResultBoundResponseSnapshotCodec[REDACTED]", codec.toString());
      f.codec.close();
      assertThrows(
          IllegalStateException.class, () -> codec.encrypt(id(route), ref(route, 9), TOKEN, input));
      assertThrows(
          IllegalStateException.class,
          () -> codec.decrypt(id(route), ref(route, 9), TOKEN, snapshot));
      assertArrayEquals(before, input);
    }
  }

  @Test
  void concurrentBindingsNeverCross() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var codec = new ResultBoundResponseSnapshotCodec(f.codec);
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 1; i <= 100; i++) {
        int n = i;
        String route = ROUTES.get(i % 3);
        tasks.add(
            () -> {
              var identity =
                  ResponseSnapshotIdentity.authenticated(
                      new UUID(0, n), route, FIXTURE_001_A3FEAA64, n);
              var token = new UUID(1, n);
              byte[] wire = wire(route, n);
              var snapshot = codec.encrypt(identity, ref(route, n), token, wire);
              assertArrayEquals(wire, codec.decrypt(identity, ref(route, n), token, snapshot));
              assertThrows(
                  ResponseSnapshotException.class,
                  () -> codec.decrypt(identity, ref(route, n + 1), token, snapshot));
              return true;
            });
      }
      var results = pool.invokeAll(tasks);
      assertEquals(100, results.size());
      for (var r : results) assertTrue(r.get());
    }
  }

  @Test
  void equalBusinessTimesDoNotAuthorizeAnotherTarget() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture()) {
      var codec = new ResultBoundResponseSnapshotCodec(f.codec);
      for (String route : ROUTES) {
        byte[] sameResponse = wire(route, 32);
        byte[] fixedTime = "20260909090000123".getBytes(StandardCharsets.US_ASCII);
        System.arraycopy(fixedTime, 0, sameResponse, sameResponse.length - 24, 17);
        var old = f.codec.encrypt(id(route), sameResponse);
        assertArrayEquals(sameResponse, f.codec.decrypt(id(route), old));
        assertThrows(
            ResponseSnapshotException.class,
            () -> codec.decrypt(id(route), ref(route, 9), TOKEN, old));
        var bound = codec.encrypt(id(route), ref(route, 9), TOKEN, sameResponse);
        assertArrayEquals(sameResponse, codec.decrypt(id(route), ref(route, 9), TOKEN, bound));
        assertThrows(
            ResponseSnapshotException.class,
            () -> codec.decrypt(id(route), ref(route, 10), TOKEN, bound));
        assertThrows(
            ResponseSnapshotException.class,
            () -> codec.decrypt(id(route), ref(route, 9), new UUID(1, 5), bound));
        assertThrows(
            ResponseSnapshotException.class,
            () -> codec.decrypt(id(route), ref(route, 9), new UUID(0, 6), bound));
        // Old generic cipher has not been changed: opaque bytes decrypt unchanged, not a wire
        // certificate.
        assertArrayEquals(plain(route, 9, TOKEN, sameResponse), f.codec.decrypt(id(route), bound));
      }
    }
  }

  private static ResponseSnapshotIdentity id(String route) {
    return ResponseSnapshotIdentity.authenticated(MESSAGE, route, FIXTURE_001_A3FEAA64, 7);
  }

  private static InboxResultReference ref(String route, long value) {
    return InboxResultReference.numeric(
        route.equals(FIXTURE_NTCRSP01_CFC2AD25)
            ? InboxResultReferenceType.JOB
            : InboxResultReferenceType.QUESTION,
        value);
  }

  private static int length(String route) {
    return Map.of("QSBRSP01", 320, FIXTURE_NTCRSP01_CFC2AD25, 288, FIXTURE_QDLRSP01_1746478A, 280)
        .get(route);
  }

  private static byte[] wire(String route, int value) {
    byte[] bytes = new byte[length(route)];
    Arrays.fill(bytes, (byte) value);
    return bytes;
  }

  private static byte[] plain(String route, long target, UUID token, byte[] wire)
      throws IOException {
    var bytes = new ByteArrayOutputStream();
    try (var out = new DataOutputStream(bytes)) {
      out.writeBytes("NKREF1");
      out.writeByte(route.equals(FIXTURE_NTCRSP01_CFC2AD25) ? 2 : 1);
      out.writeLong(target);
      out.writeLong(token.getMostSignificantBits());
      out.writeLong(token.getLeastSignificantBits());
      out.writeInt(length(route));
      out.write(wire);
    }
    return bytes.toByteArray();
  }

  private static EncryptedResponseSnapshot saved(
      InboxResponseInspectorTest.Fixture f, ResponseSnapshotIdentity id, byte[] plaintext)
      throws Exception {
    try {
      return f.saved(id, plaintext, InboxCompletionState.COMPLETED, TIME)
          .responseSnapshot()
          .orElseThrow();
    } finally {
      Arrays.fill(plaintext, (byte) 0);
    }
  }

  private static byte[] independentDecrypt(
      byte[] key, ResponseSnapshotIdentity id, EncryptedResponseSnapshot snapshot)
      throws Exception {
    byte[] bytes = snapshot.ciphertext();
    assertEquals("NKENC1", new String(bytes, 0, 6, StandardCharsets.US_ASCII));
    assertEquals(1, bytes[6]);
    assertEquals(2, bytes[7]);
    assertEquals("v1", new String(bytes, 8, 2, StandardCharsets.US_ASCII));
    var aadBytes = new ByteArrayOutputStream();
    try (var out = new DataOutputStream(aadBytes)) {
      for (byte[] part :
          List.of(
              "api-inbox-response".getBytes(StandardCharsets.US_ASCII),
              "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(16)
                  .putLong(id.requestMessageId().getMostSignificantBits())
                  .putLong(id.requestMessageId().getLeastSignificantBits())
                  .array(),
              new byte[] {1},
              new byte[] {'v', '1'},
              id.responseLayoutId().getBytes(StandardCharsets.US_ASCII),
              new byte[] {'0', '0', '1'},
              ByteBuffer.allocate(8).putLong(id.ownerUserId().orElseThrow()).array())) {
        out.writeInt(part.length);
        out.write(part);
      }
    }
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE,
        new SecretKeySpec(key, "AES"),
        new GCMParameterSpec(128, bytes, 10, 12));
    cipher.updateAAD(aadBytes.toByteArray());
    byte[] compressed = cipher.doFinal(bytes, 22, bytes.length - 22);
    try (var in = new InflaterInputStream(new ByteArrayInputStream(compressed))) {
      return in.readAllBytes();
    } finally {
      Arrays.fill(bytes, (byte) 0);
      Arrays.fill(compressed, (byte) 0);
    }
  }
}
