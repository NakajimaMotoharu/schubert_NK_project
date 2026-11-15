package dev.codex.schubert.nk.web.revocation;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;

/** Immutable pending row binding. NK-WEB-002/AUT004/UI226234/SS331352/PG-D359/RERUN003. */
public record RevocationPayloadIdentity(UUID id, Instant requestedAt) {
  public RevocationPayloadIdentity {
    Objects.requireNonNull(id, "revocation row id");
    Objects.requireNonNull(requestedAt, "revocation requested time");
    if (requestedAt.getNano() % 1000 != 0)
      throw new IllegalArgumentException("revocation time must fit database microseconds");
  }

  /** Six explicit length-prefixed fields; caller owns and erases returned bytes. */
  byte[] aad(String version) {
    byte[][] fields = {
      "web-revoke".getBytes(StandardCharsets.US_ASCII),
      "schubert_web_session.pending_context_revocations".getBytes(StandardCharsets.US_ASCII),
      ByteBuffer.allocate(16)
          .putLong(id.getMostSignificantBits())
          .putLong(id.getLeastSignificantBits())
          .array(),
      ByteBuffer.allocate(12)
          .putLong(requestedAt.getEpochSecond())
          .putInt(requestedAt.getNano())
          .array(),
      new byte[] {1},
      version.getBytes(StandardCharsets.US_ASCII)
    };
    try {
      int size = fields.length * Integer.BYTES;
      for (byte[] field : fields) size += field.length;
      var buffer = ByteBuffer.allocate(size);
      for (byte[] field : fields) buffer.putInt(field.length).put(field);
      return buffer.array();
    } finally {
      eraseFields(fields);
    }
  }

  private static void eraseFields(byte[][] fields) {
    for (byte[] field : fields) Arrays.fill(field, (byte) 0);
  }

  @Override
  public String toString() {
    return "RevocationPayloadIdentity[REDACTED]";
  }
}
