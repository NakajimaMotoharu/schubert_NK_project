package dev.codex.schubert.nk.web.session;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;

/**
 * Immutable DB row binding, not a raw cookie or authentication grant. NK-WEB-001/NK-AUT-001;
 * FUN-001/AUT-001..004; UI226/242; SS314 §7.2.2/331 §9.1/352 §11.2;
 * SSC-039/PG-D-095/PT-WEB-016..023. Nonnull; creation time must already fit DB microseconds.
 */
public record SessionPayloadIdentity(UUID id, String sessionIdHash, Instant createdAt) {
  public SessionPayloadIdentity {
    Objects.requireNonNull(id, "id");
    Objects.requireNonNull(sessionIdHash, "sessionIdHash");
    Objects.requireNonNull(createdAt, "createdAt");
    if (!sessionIdHash.matches("[0-9a-f]{64}") || createdAt.getNano() % 1000 != 0)
      throw new IllegalArgumentException("session payload identity is invalid");
  }

  /** Seven explicit length-prefixed fields; caller owns and erases the returned AAD. */
  byte[] aad(String keyVersion) {
    Objects.requireNonNull(keyVersion, "keyVersion");
    byte[][] fields = {
      "web-session".getBytes(StandardCharsets.US_ASCII),
      "schubert_web_session.web_http_sessions".getBytes(StandardCharsets.US_ASCII),
      ByteBuffer.allocate(16)
          .putLong(id.getMostSignificantBits())
          .putLong(id.getLeastSignificantBits())
          .array(),
      sessionIdHash.getBytes(StandardCharsets.US_ASCII),
      ByteBuffer.allocate(12)
          .putLong(createdAt.getEpochSecond())
          .putInt(createdAt.getNano())
          .array(),
      new byte[] {1},
      keyVersion.getBytes(StandardCharsets.US_ASCII)
    };
    try {
      int size = fields.length * Integer.BYTES;
      for (byte[] field : fields) size += field.length;
      var buffer = ByteBuffer.allocate(size);
      for (byte[] field : fields) buffer.putInt(field.length).put(field);
      return buffer.array();
    } finally {
      for (byte[] field : fields) Arrays.fill(field, (byte) 0);
    }
  }

  @Override
  public String toString() {
    return "SessionPayloadIdentity[REDACTED]";
  }
}
