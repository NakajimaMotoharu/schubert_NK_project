package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.zip.Deflater;
import java.util.zip.DeflaterOutputStream;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** PT-DB-INBOX-001..008; independently assembled SS322/323/234 bytes and JCE envelope. */
final class InboxResponseInspectorTest {
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final ResponseSnapshotIdentity ID =
      ResponseSnapshotIdentity.authenticated(MESSAGE, "GAMRSP01", "001", 1);

  @Test
  void validSuccessAndErrorProfiles() throws Exception {
    try (var f = new Fixture()) {
      for (String code : List.of("0000", "0200")) {
        for (int count : List.of(0, 1, 10)) {
          var saved = f.saved(ID, wire(code, count), InboxCompletionState.COMPLETED, TIME);
          byte[] before = saved.responseSnapshot().orElseThrow().ciphertext();
          assertTrue(f.inspector.isStructurallyValid(ID, saved));
          assertArrayEquals(before, saved.responseSnapshot().orElseThrow().ciphertext());
        }
      }
      for (String code :
          List.of("0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "9000", "9001"))
        assertTrue(
            f.inspector.isStructurallyValid(
                ID, f.saved(ID, wire(code, 0), InboxCompletionState.ERROR, TIME)));
    }
  }

  @Test
  void headerAndMetadataMismatchesReject() throws Exception {
    try (var f = new Fixture()) {
      var saved = f.saved(ID, wire("0000", 0), InboxCompletionState.COMPLETED, TIME);
      for (var id :
          List.of(
              ResponseSnapshotIdentity.authenticated(MESSAGE, "SPKRSP01", "001", 1),
              ResponseSnapshotIdentity.authenticated(MESSAGE, "GAMRSP01", "002", 1),
              ResponseSnapshotIdentity.authenticated(MESSAGE, "GAMRSP01", "001", 2),
              ResponseSnapshotIdentity.authenticated(new UUID(0, 2), "GAMRSP01", "001", 1)))
        assertFalse(f.inspector.isStructurallyValid(id, saved));
      for (Object[] mutation :
          List.of(
              new Object[] {0, "X"},
              new Object[] {8, "002"},
              new Object[] {11, "UNKNOWN1"},
              new Object[] {19, "002"},
              new Object[] {22, "E"},
              new Object[] {23, "A"},
              new Object[] {60, new UUID(0, 9).toString()},
              new Object[] {96, "20260909090001123"},
              new Object[] {113, "z"},
              new Object[] {177, "0255"},
              new Object[] {181, "000010"},
              new Object[] {187, "000271"},
              new Object[] {193, "000001"},
              new Object[] {199, "000000266"},
              new Object[] {208, "9999"},
              new Object[] {212, "X"})) {
        byte[] bytes = wire("0000", 0);
        put(bytes, (int) mutation[0], (String) mutation[1]);
        assertFalse(
            f.inspector.isStructurallyValid(
                ID, f.saved(ID, bytes, InboxCompletionState.COMPLETED, TIME)),
            "offset " + mutation[0]);
      }
      assertFalse(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, wire("0000", 0), InboxCompletionState.ERROR, TIME)));
      assertFalse(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, wire("0100", 0), InboxCompletionState.COMPLETED, TIME)));
      var wrongWireId = ResponseSnapshotIdentity.authenticated(MESSAGE, "SPKRSP01", "001", 1);
      assertFalse(
          f.inspector.isStructurallyValid(
              wrongWireId,
              f.saved(wrongWireId, wire("0000", 0), InboxCompletionState.COMPLETED, TIME)));
      var version = ResponseSnapshotIdentity.authenticated(MESSAGE, "GAMRSP01", "002", 1);
      assertFalse(
          f.inspector.isStructurallyValid(
              version, f.saved(version, wire("0000", 0), InboxCompletionState.COMPLETED, TIME)));
    }
  }

  @Test
  void payloadEncodingAndSemanticFaultsReject() throws Exception {
    try (var f = new Fixture()) {
      for (Object[] mutation :
          List.of(
              new Object[] {256, "000000002"},
              new Object[] {265, "UNKNOWN"},
              new Object[] {277, "\u0065\u0301"},
              new Object[] {533, "00X"},
              new Object[] {536, "X"})) {
        byte[] bytes = wire("0000", 1);
        put(bytes, (int) mutation[0], (String) mutation[1]);
        assertFalse(
            f.inspector.isStructurallyValid(
                ID, f.saved(ID, bytes, InboxCompletionState.COMPLETED, TIME)),
            "offset " + mutation[0]);
      }
      byte[] bad = wire("0000", 1);
      // UI234 section5.3: unsigned N3, not the database positive-order constraint (BUG-075).
      for (String order : List.of("000", "999")) {
        byte[] boundary = wire("0000", 1);
        put(boundary, 533, order);
        assertTrue(
            f.inspector.isStructurallyValid(
                ID, f.saved(ID, boundary, InboxCompletionState.COMPLETED, TIME)));
      }
      byte[] ordered = wire("0000", 2);
      put(ordered, 533, "002");
      put(ordered, 805, "001");
      assertFalse(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, ordered, InboxCompletionState.COMPLETED, TIME)));
      put(ordered, 805, "002");
      assertTrue(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, ordered, InboxCompletionState.COMPLETED, TIME)));
      bad[277] = (byte) 0xff;
      assertFalse(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, bad, InboxCompletionState.COMPLETED, TIME)));
      byte[] good = wire("0000", 1);
      put(good, 277, "日本語é");
      assertTrue(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, good, InboxCompletionState.COMPLETED, TIME)));
      byte[] error = wire("0100", 0);
      put(error, 256, "1");
      assertFalse(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, error, InboxCompletionState.ERROR, TIME)));
    }
  }

  @Test
  void cryptographicDamageAndMissingSnapshotReject() throws Exception {
    try (var f = new Fixture();
        var different = new Fixture()) {
      var saved = f.saved(ID, wire("0000", 1), InboxCompletionState.COMPLETED, TIME);
      byte[] ciphertext = saved.responseSnapshot().orElseThrow().ciphertext();
      for (int i = 0; i < ciphertext.length; i++) {
        byte[] corrupt = ciphertext.clone();
        corrupt[i] ^= 1;
        var value = replace(saved, Optional.of(new EncryptedResponseSnapshot("v1", corrupt)));
        assertFalse(f.inspector.isStructurallyValid(ID, value), "encrypted offset " + i);
        assertArrayEquals(corrupt, value.responseSnapshot().orElseThrow().ciphertext());
      }
      assertFalse(different.inspector.isStructurallyValid(ID, saved));
      assertFalse(
          f.inspector.isStructurallyValid(
              ID,
              replace(saved, Optional.of(new EncryptedResponseSnapshot("unknown", ciphertext)))));
      assertFalse(f.inspector.isStructurallyValid(ID, replace(saved, Optional.empty())));
      f.codec.close();
      assertFalse(f.inspector.isStructurallyValid(ID, saved));
    }
  }

  @Test
  void exactLengthsAndTimestampPrecision() throws Exception {
    try (var f = new Fixture()) {
      byte[] original = wire("0000", 0);
      for (int length : List.of(0, 1, 255, 256, 264, 266, 1_000_001))
        assertFalse(
            f.inspector.isStructurallyValid(
                ID,
                f.saved(ID, Arrays.copyOf(original, length), InboxCompletionState.COMPLETED, TIME)),
            "length " + length);
      assertTrue(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, original, InboxCompletionState.COMPLETED, TIME.plusNanos(999_000))));
      assertFalse(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, original, InboxCompletionState.COMPLETED, TIME.minusNanos(1_000))));
      assertFalse(
          f.inspector.isStructurallyValid(
              ID, f.saved(ID, original, InboxCompletionState.COMPLETED, TIME.plusMillis(1))));
    }
  }

  @Test
  void nullContractsFailBeforeValidation() throws Exception {
    assertThrows(NullPointerException.class, () -> new InboxResponseInspector(null));
    try (var f = new Fixture()) {
      var saved = f.saved(ID, wire("0000", 0), InboxCompletionState.COMPLETED, TIME);
      assertThrows(NullPointerException.class, () -> f.inspector.isStructurallyValid(null, saved));
      assertThrows(NullPointerException.class, () -> f.inspector.isStructurallyValid(ID, null));
    }
  }

  @Test
  void concurrentInspectionsDoNotShareState() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++) {
        int number = i;
        jobs.add(
            () -> {
              var identity =
                  ResponseSnapshotIdentity.authenticated(
                      new UUID(0, number + 1), "GAMRSP01", "001", number + 1);
              byte[] bytes = wire("0000", number % 11);
              put(bytes, 60, identity.requestMessageId().toString());
              var saved = f.saved(identity, bytes, InboxCompletionState.COMPLETED, TIME);
              var original = saved.responseSnapshot().orElseThrow().ciphertext();
              assertTrue(f.inspector.isStructurallyValid(identity, saved));
              var foreign =
                  ResponseSnapshotIdentity.authenticated(
                      new UUID(0, number + 200), "GAMRSP01", "001", number + 1);
              assertFalse(f.inspector.isStructurallyValid(foreign, saved));
              assertArrayEquals(original, saved.responseSnapshot().orElseThrow().ciphertext());
              return true;
            });
      }
      for (var result : pool.invokeAll(jobs)) assertTrue(result.get());
    }
  }

  @Test
  void databaseReferenceIsNotCertifiedByStructure() throws Exception {
    try (var f = new Fixture()) {
      var original = f.saved(ID, wire("0000", 0), InboxCompletionState.COMPLETED, TIME);
      var unverified =
          new InboxCompletion(
              original.state(),
              InboxResultReference.numeric(InboxResultReferenceType.USER, 999),
              original.responseLayoutId(),
              original.responseVersion(),
              original.responseSnapshot(),
              TIME);
      assertTrue(
          f.inspector.isStructurallyValid(ID, unverified), "structure is not DB authorization");
      byte[] request = Arrays.copyOf(wire("0000", 0), 256);
      put(request, 11, "GAMREQ01");
      put(request, 22, "Q");
      put(request, 24, MESSAGE.toString());
      put(request, 181, "000000000000000000000000256");
      put(request, 208, "    ");
      var identity = ResponseSnapshotIdentity.authenticated(MESSAGE, "GAMREQ01", "001", 1);
      assertFalse(
          f.inspector.isStructurallyValid(
              identity, f.saved(identity, request, InboxCompletionState.COMPLETED, TIME)));
    }
  }

  private static InboxCompletion replace(InboxCompletion c, Optional<EncryptedResponseSnapshot> s) {
    return new InboxCompletion(
        c.state(),
        c.resultReference(),
        c.responseLayoutId(),
        c.responseVersion(),
        s,
        c.completedAt());
  }

  private static byte[] wire(String code, int count) {
    byte[] bytes = new byte[265 + 272 * count];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, "SCHBNK01001GAMRSP01001SS");
    put(bytes, 24, new UUID(0, 2).toString());
    put(bytes, 60, MESSAGE.toString());
    put(bytes, 96, "20260909090000123");
    put(bytes, 113, "a".repeat(64));
    put(bytes, 177, "0256000009000272");
    put(bytes, 193, String.format(Locale.ROOT, "%06d%09d", count, bytes.length));
    put(bytes, 208, code);
    put(bytes, 256, String.format(Locale.ROOT, "%09d", count));
    for (int i = 0; i < count; i++) {
      int start = 265 + 272 * i;
      put(bytes, start, "NUKITASHI1");
      put(bytes, start + 12, "Game");
      put(bytes, start + 268, String.format(Locale.ROOT, "%03d", i + 1));
    }
    return bytes;
  }

  private static void put(byte[] bytes, int offset, String text) {
    byte[] value = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(value, 0, bytes, offset, value.length);
  }

  static final class Fixture implements AutoCloseable {
    final byte[] key = new byte[32];
    final ResponseSnapshotCodec codec;
    final InboxResponseInspector inspector;

    Fixture() {
      new SecureRandom().nextBytes(key);
      codec = new ResponseSnapshotCodec("v1", key, null, null);
      inspector = new InboxResponseInspector(codec);
    }

    InboxCompletion saved(
        ResponseSnapshotIdentity id, byte[] wire, InboxCompletionState state, Instant time)
        throws Exception {
      var compressed = new ByteArrayOutputStream();
      Deflater deflater = new Deflater(3);
      try (var zip = new DeflaterOutputStream(compressed, deflater)) {
        zip.write(wire);
      } finally {
        deflater.end();
      }
      var aadBytes = new ByteArrayOutputStream();
      try (var aad = new DataOutputStream(aadBytes)) {
        for (byte[] part :
            List.of(
                "api-inbox-response".getBytes(StandardCharsets.US_ASCII),
                "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII),
                ByteBuffer.allocate(16)
                    .putLong(id.requestMessageId().getMostSignificantBits())
                    .putLong(id.requestMessageId().getLeastSignificantBits())
                    .array(),
                new byte[] {1},
                "v1".getBytes(StandardCharsets.US_ASCII),
                id.responseLayoutId().getBytes(StandardCharsets.US_ASCII),
                id.responseVersion().getBytes(StandardCharsets.US_ASCII),
                id.ownerUserId().isPresent()
                    ? ByteBuffer.allocate(8).putLong(id.ownerUserId().getAsLong()).array()
                    : new byte[0])) {
          aad.writeInt(part.length);
          aad.write(part);
        }
      }
      byte[] nonce = new byte[12];
      new SecureRandom().nextBytes(nonce);
      var cipher = Cipher.getInstance("AES/GCM/NoPadding");
      cipher.init(
          Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
      cipher.updateAAD(aadBytes.toByteArray());
      byte[] ciphertext = cipher.doFinal(compressed.toByteArray());
      byte[] envelope =
          ByteBuffer.allocate(22 + ciphertext.length)
              .put("NKENC1".getBytes(StandardCharsets.US_ASCII))
              .put((byte) 1)
              .put((byte) 2)
              .put("v1".getBytes(StandardCharsets.US_ASCII))
              .put(nonce)
              .put(ciphertext)
              .array();
      return new InboxCompletion(
          state,
          InboxResultReference.none(),
          id.responseLayoutId(),
          id.responseVersion(),
          Optional.of(new EncryptedResponseSnapshot("v1", envelope)),
          time);
    }

    @Override
    public void close() {
      codec.close();
      Arrays.fill(key, (byte) 0);
    }
  }
}
