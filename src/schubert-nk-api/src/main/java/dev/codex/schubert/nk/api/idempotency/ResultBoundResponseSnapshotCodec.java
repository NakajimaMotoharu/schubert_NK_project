package dev.codex.schubert.nk.api.idempotency;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Authenticates result metadata inside the unchanged NKENC1 encryption envelope. Does not validate
 * fixed-wire semantics or DB references and never authorizes deletion. Borrowed codec/keys and
 * input wire stay caller-owned; returned wire must be cleared by caller. NK-DAT-001/NK-MSG-002;
 * DAT-009/MQ-008/OPS-009; UI232/236/241; SS324 6/331 7.1/352 11.2.1; QA-046/SSC-052/049/PG-D-140;
 * PT-DB-INBOX-169..176.
 */
@NullMarked
public final class ResultBoundResponseSnapshotCodec {
  private static final byte[] MAGIC = "NKREF1".getBytes(StandardCharsets.US_ASCII);
  private static final int PREFIX_BYTES = 35;
  private final ResponseSnapshotCodec snapshots;

  public ResultBoundResponseSnapshotCodec(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
  }

  public EncryptedResponseSnapshot encrypt(
      ResponseSnapshotIdentity identity,
      InboxResultReference reference,
      UUID operationToken,
      byte[] wire) {
    Objects.requireNonNull(wire, "wire");
    int length = wireLength(identity, reference, operationToken);
    if (wire.length != length)
      throw new IllegalArgumentException("bound response length is invalid");
    byte[] prefix = prefix(reference, operationToken, length);
    byte[] plaintext = new byte[PREFIX_BYTES + length];
    try {
      System.arraycopy(prefix, 0, plaintext, 0, PREFIX_BYTES);
      System.arraycopy(wire, 0, plaintext, PREFIX_BYTES, length);
      return snapshots.encrypt(identity, plaintext);
    } finally {
      Arrays.fill(prefix, (byte) 0);
      Arrays.fill(plaintext, (byte) 0);
    }
  }

  public byte[] decrypt(
      ResponseSnapshotIdentity identity,
      InboxResultReference reference,
      UUID operationToken,
      EncryptedResponseSnapshot snapshot) {
    Objects.requireNonNull(snapshot, "snapshot");
    int length = wireLength(identity, reference, operationToken);
    byte[] plaintext = snapshots.decrypt(identity, snapshot);
    byte[] expected = prefix(reference, operationToken, length);
    byte[] actual = new byte[PREFIX_BYTES];
    try {
      if (plaintext.length != PREFIX_BYTES + length) throw invalid();
      System.arraycopy(plaintext, 0, actual, 0, PREFIX_BYTES);
      if (!MessageDigest.isEqual(actual, expected)) throw invalid();
      return Arrays.copyOfRange(plaintext, PREFIX_BYTES, plaintext.length);
    } finally {
      Arrays.fill(plaintext, (byte) 0);
      Arrays.fill(expected, (byte) 0);
      Arrays.fill(actual, (byte) 0);
    }
  }

  private static int wireLength(
      ResponseSnapshotIdentity identity, InboxResultReference reference, UUID operationToken) {
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(reference, "reference");
    Objects.requireNonNull(operationToken, "operationToken");
    if (identity.ownerUserId().isEmpty() || !identity.responseVersion().equals("001"))
      throw new IllegalArgumentException("bound response identity is invalid");
    int length =
        switch (identity.responseLayoutId()) {
          case "QSBRSP01" -> 320;
          case "NTCRSP01" -> 288;
          case "QDLRSP01" -> 280;
          default -> throw new IllegalArgumentException("bound response layout is unsupported");
        };
    var expected =
        identity.responseLayoutId().equals("NTCRSP01")
            ? InboxResultReferenceType.JOB
            : InboxResultReferenceType.QUESTION;
    if (reference.type() != expected)
      throw new IllegalArgumentException("bound response reference type is invalid");
    return length;
  }

  private static byte[] prefix(InboxResultReference reference, UUID token, int length) {
    return ByteBuffer.allocate(PREFIX_BYTES)
        .put(MAGIC)
        .put((byte) (reference.type() == InboxResultReferenceType.QUESTION ? 1 : 2))
        .putLong(reference.numericId().orElseThrow())
        .putLong(token.getMostSignificantBits())
        .putLong(token.getLeastSignificantBits())
        .putInt(length)
        .array();
  }

  private static ResponseSnapshotException invalid() {
    return new ResponseSnapshotException(
        ResponseSnapshotException.Reason.SNAPSHOT_INVALID, "bound response metadata is invalid");
  }

  @Override
  public String toString() {
    return "ResultBoundResponseSnapshotCodec[REDACTED]";
  }
}
