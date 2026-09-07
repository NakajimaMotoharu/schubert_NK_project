package dev.codex.schubert.nk.api.idempotency;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.Objects;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.jspecify.annotations.Nullable;

/** NKOP1 length-prefixed canonical HMAC. Trace: NK-MSG-002, SS 324 §3. */
public enum OperationFingerprint {
  INSTANCE;

  private static final byte[] MAGIC = "SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII);
  private static final int NULL_LENGTH = -1;
  private static final int MINIMUM_KEY_BYTES = 32;

  /** Calculates HMAC-SHA-256 and clears the transient canonical buffer. */
  public byte[] calculate(CanonicalRequest request, byte[] key) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(key, "key");
    if (key.length < MINIMUM_KEY_BYTES) {
      throw new IllegalArgumentException("fingerprint key must contain at least 256 bits");
    }
    byte[] canonical = canonicalBytes(request);
    try {
      Mac mac = Mac.getInstance("HmacSHA256");
      mac.init(new SecretKeySpec(key, "HmacSHA256"));
      return mac.doFinal(canonical);
    } catch (java.security.GeneralSecurityException exception) {
      throw new IllegalStateException("HMAC-SHA-256 is unavailable", exception);
    } finally {
      Arrays.fill(canonical, (byte) 0);
    }
  }

  byte[] canonicalBytes(CanonicalRequest request) {
    Objects.requireNonNull(request, "request");
    try (var output = new WipingByteArrayOutputStream()) {
      output.writeBytes(MAGIC);
      writeText(output, request.ownerScope());
      writeText(output, request.layoutId());
      writeText(output, request.layoutVersion());
      writeText(output, request.target());
      writeLength(output, request.fields().size());
      for (CanonicalField field : request.fields()) {
        writeText(output, field.name());
        writeText(output, field.typeVersion());
        writeValue(output, field.value());
      }
      return output.toByteArray();
    }
  }

  private static void writeText(ByteArrayOutputStream output, String value) {
    byte[] encoded =
        Normalizer.normalize(value, Normalizer.Form.NFC).getBytes(StandardCharsets.UTF_8);
    try {
      writeLength(output, encoded.length);
      output.writeBytes(encoded);
    } finally {
      Arrays.fill(encoded, (byte) 0);
    }
  }

  private static void writeValue(ByteArrayOutputStream output, byte @Nullable [] value) {
    if (value == null) {
      writeLength(output, NULL_LENGTH);
    } else {
      try {
        writeLength(output, value.length);
        output.writeBytes(value);
      } finally {
        Arrays.fill(value, (byte) 0);
      }
    }
  }

  private static void writeLength(ByteArrayOutputStream output, int length) {
    output.writeBytes(ByteBuffer.allocate(Integer.BYTES).putInt(length).array());
  }
}
