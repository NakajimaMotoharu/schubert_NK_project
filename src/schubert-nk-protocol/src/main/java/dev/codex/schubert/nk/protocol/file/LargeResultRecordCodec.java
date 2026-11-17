package dev.codex.schubert.nk.protocol.file;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;

/** Headerless 4,800-byte large-result stream codec. Trace: NK-PRO-003, UI 237 §4～§6. */
public interface LargeResultRecordCodec {

  public static LargeResultContent write(OutputStream output, List<byte[]> records) {
    Objects.requireNonNull(output, "output");
    Objects.requireNonNull(records, "records");
    if (records.isEmpty() || records.size() > LargeResultDescriptor.MAXIMUM_RECORD_COUNT) {
      throw new IllegalArgumentException("large-result record count is outside 1..10000");
    }
    MessageDigest digest = sha256Digest();
    long byteLength = 0;
    try {
      for (byte[] record : records) {
        Objects.requireNonNull(record, "record");
        if (record.length != LargeResultDescriptor.RECORD_LENGTH) {
          throw new IllegalArgumentException("large-result record is not exactly 4800 bytes");
        }
        output.write(record);
        digest.update(record);
        byteLength = Math.addExact(byteLength, record.length);
      }
    } catch (IOException exception) {
      throw new LargeResultIoException("large-result write failed", exception);
    }
    return new LargeResultContent(
        records.size(), byteLength, HexFormat.of().formatHex(digest.digest()));
  }

  public static List<byte[]> decode(InputStream input, LargeResultDescriptor descriptor) {
    Objects.requireNonNull(input, "input");
    Objects.requireNonNull(descriptor, "descriptor");
    MessageDigest digest = sha256Digest();
    ArrayList<byte[]> records = new ArrayList<>(descriptor.recordCount());
    try {
      for (int index = 0; index < descriptor.recordCount(); index++) {
        byte[] record = readExact(input, LargeResultDescriptor.RECORD_LENGTH);
        digest.update(record);
        records.add(record);
      }
      if (input.read() != -1) {
        throw new PermanentProtocolException("large-result stream contains extra bytes");
      }
    } catch (IOException exception) {
      throw new LargeResultIoException("large-result read failed", exception);
    }
    // BUG-034/YKT-030: verification compares fixed 32-byte digests, not early-exit String equality.
    byte[] expectedHash = HexFormat.of().parseHex(descriptor.sha256());
    if (!MessageDigest.isEqual(digest.digest(), expectedHash)) {
      throw new PermanentProtocolException("large-result SHA-256 differs from its descriptor");
    }
    return Collections.unmodifiableList(records);
  }

  private static byte[] readExact(InputStream input, int length) throws IOException {
    byte[] result = new byte[length];
    int offset = 0;
    while (offset < length) {
      int read = input.read(result, offset, length - offset);
      if (read < 0) {
        throw new PermanentProtocolException("large-result stream ends within a record");
      }
      if (read == 0) {
        int single = input.read();
        if (single < 0) {
          throw new PermanentProtocolException("large-result stream ends within a record");
        }
        result[offset] = (byte) single;
        offset++;
      } else {
        offset += read;
      }
    }
    return result;
  }

  private static MessageDigest sha256Digest() {
    return digestFor("SHA-256");
  }

  static MessageDigest digestFor(String algorithm) {
    try {
      return MessageDigest.getInstance(algorithm);
    } catch (NoSuchAlgorithmException exception) {
      throw new IllegalStateException("requested message digest is unavailable", exception);
    }
  }
}
