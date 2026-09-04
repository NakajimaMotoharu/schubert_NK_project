package dev.codex.schubert.nk.api.idempotency;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.OptionalLong;
import java.util.UUID;

/**
 * AES-GCM AAD identity for an Inbox response snapshot.
 *
 * <p>Trace: DAT-009, UI 241/242, SS 324 §6/§15, SS 352 §11.2 and PT-IDEM-007/008.
 */
public record ResponseSnapshotIdentity(
    UUID requestMessageId,
    String responseLayoutId,
    String responseVersion,
    OptionalLong ownerUserId) {
  private static final byte[] AAD_PURPOSE =
      "api-inbox-response".getBytes(StandardCharsets.US_ASCII);
  private static final byte[] AAD_TABLE =
      "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII);
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

  byte[] aad(byte formatVersion, String keyVersion) {
    Objects.requireNonNull(keyVersion, "keyVersion");
    byte[] layout = responseLayoutId.getBytes(StandardCharsets.US_ASCII);
    byte[] version = responseVersion.getBytes(StandardCharsets.US_ASCII);
    byte[] keyId = keyVersion.getBytes(StandardCharsets.US_ASCII);
    int ownerLength = ownerUserId.isPresent() ? Long.BYTES : 0;
    ByteBuffer buffer =
        ByteBuffer.allocate(
            8 * Integer.BYTES
                + AAD_PURPOSE.length
                + AAD_TABLE.length
                + 16
                + 1
                + keyId.length
                + layout.length
                + version.length
                + ownerLength);
    putLengthPrefixed(buffer, AAD_PURPOSE);
    putLengthPrefixed(buffer, AAD_TABLE);
    buffer.putInt(16);
    buffer.putLong(requestMessageId.getMostSignificantBits());
    buffer.putLong(requestMessageId.getLeastSignificantBits());
    buffer.putInt(1);
    buffer.put(formatVersion);
    putLengthPrefixed(buffer, keyId);
    putLengthPrefixed(buffer, layout);
    putLengthPrefixed(buffer, version);
    buffer.putInt(ownerLength);
    if (ownerUserId.isPresent()) {
      buffer.putLong(ownerUserId.getAsLong());
    }
    return buffer.array();
  }

  private static void putLengthPrefixed(ByteBuffer buffer, byte[] value) {
    buffer.putInt(value.length);
    buffer.put(value);
  }

  @Override
  public String toString() {
    return "ResponseSnapshotIdentity[request/layout/version/owner=<redacted>]";
  }
}
