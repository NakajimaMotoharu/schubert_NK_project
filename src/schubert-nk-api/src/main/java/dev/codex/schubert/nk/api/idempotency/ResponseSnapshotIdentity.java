package dev.codex.schubert.nk.api.idempotency;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.OptionalLong;
import java.util.UUID;

/**
 * AES-GCM AAD identity for an Inbox response snapshot.
 *
 * <p>Trace: DAT-009, UI 241/242, SS 324 §6/§15 and PT-IDEM-007/008.
 */
public record ResponseSnapshotIdentity(
    UUID requestMessageId,
    String responseLayoutId,
    String responseVersion,
    OptionalLong ownerUserId) {
  private static final byte[] AAD_MAGIC =
      "SCHUBERT-NK-SNAPSHOT1".getBytes(StandardCharsets.US_ASCII);
  private static final long MAXIMUM_OWNER_ID = 999_999_999_999L;

  public ResponseSnapshotIdentity {
    Objects.requireNonNull(requestMessageId, "requestMessageId");
    Objects.requireNonNull(responseLayoutId, "responseLayoutId");
    Objects.requireNonNull(responseVersion, "responseVersion");
    Objects.requireNonNull(ownerUserId, "ownerUserId");
    if (!responseLayoutId.matches("[A-Z0-9]{8}")) {
      throw new IllegalArgumentException("responseLayoutId is invalid");
    }
    if (!responseVersion.matches("[0-9]{3}")) {
      throw new IllegalArgumentException("responseVersion is invalid");
    }
    if (ownerUserId.isPresent()
        && (ownerUserId.getAsLong() < 1 || ownerUserId.getAsLong() > MAXIMUM_OWNER_ID)) {
      throw new IllegalArgumentException("ownerUserId is outside N12");
    }
  }

  public static ResponseSnapshotIdentity authenticated(
      UUID requestMessageId, String responseLayoutId, String responseVersion, long ownerUserId) {
    return new ResponseSnapshotIdentity(
        requestMessageId, responseLayoutId, responseVersion, OptionalLong.of(ownerUserId));
  }

  public static ResponseSnapshotIdentity anonymous(
      UUID requestMessageId, String responseLayoutId, String responseVersion) {
    return new ResponseSnapshotIdentity(
        requestMessageId, responseLayoutId, responseVersion, OptionalLong.empty());
  }

  byte[] aad() {
    byte[] layout = responseLayoutId.getBytes(StandardCharsets.US_ASCII);
    byte[] version = responseVersion.getBytes(StandardCharsets.US_ASCII);
    ByteBuffer buffer =
        ByteBuffer.allocate(AAD_MAGIC.length + 16 + layout.length + version.length + 1 + Long.BYTES);
    buffer.put(AAD_MAGIC);
    buffer.putLong(requestMessageId.getMostSignificantBits());
    buffer.putLong(requestMessageId.getLeastSignificantBits());
    buffer.put(layout);
    buffer.put(version);
    buffer.put((byte) (ownerUserId.isPresent() ? 1 : 0));
    buffer.putLong(ownerUserId.orElse(0));
    return buffer.array();
  }

  @Override
  public String toString() {
    return "ResponseSnapshotIdentity[request/layout/version/owner=<redacted>]";
  }
}
