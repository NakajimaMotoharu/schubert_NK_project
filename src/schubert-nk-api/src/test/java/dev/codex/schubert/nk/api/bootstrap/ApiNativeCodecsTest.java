package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.security.AuthContextIdentity;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/**
 * PT-OPS-API-KEY-001..005, public synthetic material only. SS343/352 purpose mapping and
 * independent LP/HMAC oracle; not native key/rotation readiness acceptance.
 */
final class ApiNativeCodecsTest {
  private static final String FIXTURE_001_A3FEAA64 = "001";
  @org.junit.jupiter.api.io.TempDir java.nio.file.Path directory;

  @Test
  void actualServiceCredentialReaderSuppliesPublicPurposesAndBorrowedOwnerSurvives()
      throws Exception {
    // PT-OPS-API-KEY-006: synthetic metadata, actual reader bytes and retained FD.
    try (var fixture = new dev.codex.schubert.nk.api.file.PublicApiCredentialFixture(directory)) {
      var credentials = fixture.credentials();
      try (var codecs = ApiNativeCodecs.create(credentials)) {
        var auth =
            codecs
                .contexts()
                .encrypt(
                    new AuthContextIdentity(new UUID(0, 1), 7),
                    AuthenticationContext.of("a".repeat(64)));
        assertEquals("ctx1", auth.keyVersion());
      }
      byte[] borrowed = credentials.copyKey(ServiceCredentialId.OPERATION_HMAC_CURRENT);
      byte[] expected = new byte[32];
      Arrays.fill(expected, (byte) 67);
      assertArrayEquals(expected, borrowed);
      Arrays.fill(borrowed, (byte) 0);
      assertEquals("fp1", credentials.version(ServiceCredentialId.OPERATION_HMAC_CURRENT));
      credentials.close();
      assertThrows(IllegalStateException.class, () -> ApiNativeCodecs.create(credentials));
    }
  }

  static final List<ServiceCredentialId> IDS =
      List.of(
          ServiceCredentialId.API_CONTEXT_AES_CURRENT,
          ServiceCredentialId.API_INBOX_RESPONSE_AES_CURRENT,
          ServiceCredentialId.OPERATION_HMAC_CURRENT);

  static final class Keys implements ApiNativeCodecs.KeySource {
    final List<byte[]> copies = new ArrayList<>();
    int failRead = -1;
    int failVersion = -1;
    int nullRead = -1;
    int badLength = -1;
    int same = -1;
    boolean fatal;

    public byte[] copyKey(ServiceCredentialId id) {
      int index = IDS.indexOf(id);
      assertTrue(index >= 0);
      if (index == failRead) {
        if (fatal) throw new AssertionError("public fatal");
        throw new IllegalStateException("public failure");
      }
      if (index == nullRead) return null;
      byte[] copy = new byte[index == badLength ? 31 : 32];
      Arrays.fill(copy, (byte) (index == same ? 65 : same == 3 && index == 2 ? 66 : 65 + index));
      copies.add(copy);
      return copy;
    }

    public String version(ServiceCredentialId id) {
      int index = IDS.indexOf(id);
      return index == failVersion ? "!" : List.of("ctx1", "snp1", "fp1").get(index);
    }

    void erased() {
      for (byte[] copy : copies) assertArrayEquals(new byte[copy.length], copy);
    }
  }

  @Test
  void exactPurposesVersionsAndIndependentHmacSurviveTemporaryCopyErasure() throws Exception {
    var keys = new Keys();
    try (var owner = ApiNativeCodecs.create(keys);
        var request =
            new CanonicalRequest(
                "7", "LOGREQ01", FIXTURE_001_A3FEAA64, "REQUEST:LOGREQ01", List.of())) {
      keys.erased();
      assertEquals(3, keys.copies.size());
      var auth =
          owner
              .contexts()
              .encrypt(
                  new AuthContextIdentity(new UUID(0, 1), 7),
                  AuthenticationContext.of("a".repeat(64)));
      assertEquals("ctx1", auth.keyVersion());
      var fingerprint = owner.fingerprints().calculate(request);
      assertEquals("fp1", fingerprint.keyVersion());
      var bytes = new ByteArrayOutputStream();
      try (var out = new DataOutputStream(bytes)) {
        out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
        for (String value : List.of("7", "LOGREQ01", FIXTURE_001_A3FEAA64, "REQUEST:LOGREQ01")) {
          byte[] utf8 = value.getBytes(StandardCharsets.UTF_8);
          out.writeInt(utf8.length);
          out.write(utf8);
        }
        out.writeInt(0);
      }
      byte[] publicKey = new byte[32];
      Arrays.fill(publicKey, (byte) 67);
      var mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(publicKey, "HmacSHA256"));
      assertArrayEquals(mac.doFinal(bytes.toByteArray()), fingerprint.digest());
      assertEquals(
          "snp1",
          owner
              .snapshots()
              .encrypt(
                  dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity.anonymous(
                      new UUID(0, 2), "LGNRSP01", FIXTURE_001_A3FEAA64),
                  new byte[] {1})
              .keyVersion());
    }
  }

  @Test
  void everyReadVersionNullAndInvalidLengthClearsAllAcquiredCopies() {
    for (int i = 0; i < 3; i++) {
      var read = new Keys();
      read.failRead = i;
      assertThrows(IllegalStateException.class, () -> ApiNativeCodecs.create(read));
      read.erased();
      var version = new Keys();
      version.failVersion = i;
      assertThrows(IllegalArgumentException.class, () -> ApiNativeCodecs.create(version));
      version.erased();
      var nil = new Keys();
      nil.nullRead = i;
      assertThrows(NullPointerException.class, () -> ApiNativeCodecs.create(nil));
      nil.erased();
      var length = new Keys();
      length.badLength = i;
      assertThrows(IllegalArgumentException.class, () -> ApiNativeCodecs.create(length));
      length.erased();
    }
  }

  @Test
  void repeatedPurposeMaterialAndFatalAcquisitionNeverReturnAnOwner() {
    for (int i : List.of(1, 2, 3)) {
      var keys = new Keys();
      keys.same = i;
      assertThrows(IllegalArgumentException.class, () -> ApiNativeCodecs.create(keys));
      keys.erased();
    }
    var keys = new Keys();
    keys.failRead = 2;
    keys.fatal = true;
    assertThrows(AssertionError.class, () -> ApiNativeCodecs.create(keys));
    keys.erased();
  }

  @Test
  void closeIsIdempotentAndBorrowedObjectsCannotContinueAfterOwnerClose() {
    var keys = new Keys();
    var owner = ApiNativeCodecs.create(keys);
    var contexts = owner.contexts();
    var fingerprints = owner.fingerprints();
    try {
      owner.close();
      owner.close();
      assertThrows(IllegalStateException.class, owner::contexts);
      assertThrows(IllegalStateException.class, owner::snapshots);
      assertThrows(IllegalStateException.class, owner::fingerprints);
      assertThrows(
          IllegalStateException.class,
          () ->
              contexts.encrypt(
                  new AuthContextIdentity(new UUID(0, 1), 7),
                  AuthenticationContext.of("a".repeat(64))));
      try (var request =
          new CanonicalRequest(
              "7", "LOGREQ01", FIXTURE_001_A3FEAA64, "REQUEST:LOGREQ01", List.of())) {
        assertThrows(IllegalStateException.class, () -> fingerprints.calculate(request));
      }
      keys.erased();
    } finally {
      owner.close();
    }
  }

  @Test
  void missingSourcesRejectBeforeAcquisition() {
    assertThrows(
        NullPointerException.class, () -> ApiNativeCodecs.create((ApiNativeCodecs.KeySource) null));
    assertThrows(
        NullPointerException.class,
        () -> ApiNativeCodecs.create((dev.codex.schubert.nk.api.file.ServiceCredentialSet) null));
  }
}
