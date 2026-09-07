package dev.codex.schubert.nk.web.logging;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.UUID;

/**
 * Logical row and correlation binding for an encrypted WLGEVT01 event.
 *
 * <p>Trace: NK-MSG-002; RD MON-003; UI 235 §12/242; SS 324 §9, 352 §11.2; PT-IDEM-012/015. The
 * unique Message ID identifies the row before its identity PK is allocated.
 */
public record WebLogPayloadIdentity(UUID messageId, UUID correlationId) {
  public WebLogPayloadIdentity {
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(correlationId, "correlationId");
  }

  /** Internal canonical form: eight 32-bit big-endian length-prefixed fields. */
  byte[] aad(String keyVersion) {
    Objects.requireNonNull(keyVersion, "keyVersion");
    byte[][] fields = {
      "web-log-outbox".getBytes(StandardCharsets.US_ASCII),
      "schubert_web_session.web_log_outbox".getBytes(StandardCharsets.US_ASCII),
      uuidBytes(messageId),
      uuidBytes(correlationId),
      new byte[] {1},
      keyVersion.getBytes(StandardCharsets.US_ASCII),
      "WLGEVT01".getBytes(StandardCharsets.US_ASCII),
      "001".getBytes(StandardCharsets.US_ASCII)
    };
    int length = fields.length * Integer.BYTES;
    for (byte[] field : fields) {
      length += field.length;
    }
    ByteBuffer buffer = ByteBuffer.allocate(length);
    for (byte[] field : fields) {
      buffer.putInt(field.length).put(field);
    }
    return buffer.array();
  }

  private static byte[] uuidBytes(UUID value) {
    return ByteBuffer.allocate(16)
        .putLong(value.getMostSignificantBits())
        .putLong(value.getLeastSignificantBits())
        .array();
  }

  @Override
  public String toString() {
    return "WebLogPayloadIdentity[message/correlation=<redacted>]";
  }
}
