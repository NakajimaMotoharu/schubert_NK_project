package dev.codex.schubert.nk.protocol.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class LargeResultRecordCodecTest {
  private static final String IO_FAILURE_MESSAGE = "test";
  private static final UUID FILE_ID = UUID.fromString("123e4567-e89b-12d3-a456-426614174000");
  private static final String PATH = "20260902/123e4567-e89b-12d3-a456-426614174000.ready";

  /**
   * PT-PRO-003-H01 / BUG-034: independent JCA digest, every byte-position tamper, no timing test.
   */
  @Test
  void verificationRejectsAllThirtyTwoDigestBytePositions() throws Exception {
    byte[] record = record((byte) 0x22);
    byte[] expected = MessageDigest.getInstance("SHA-256").digest(record);
    assertArrayEquals(
        record,
        LargeResultRecordCodec.decode(
                new ByteArrayInputStream(record), descriptor(1, HexFormat.of().formatHex(expected)))
            .getFirst());
    for (int i = 0; i < 32; i++) {
      byte[] changed = expected.clone();
      changed[i] ^= 1;
      LargeResultDescriptor wrong = descriptor(1, HexFormat.of().formatHex(changed));
      assertThrows(
          PermanentProtocolException.class,
          () -> LargeResultRecordCodec.decode(new ByteArrayInputStream(record), wrong));
    }
  }

  @Test
  void descriptorAcceptsOnlyCanonicalPathHashAndLengthEquation() {
    LargeResultDescriptor descriptor = descriptor(1, hash(record((byte) 1)));
    assertEquals(FILE_ID, descriptor.fileId());
    assertEquals(PATH, descriptor.relativePath());
    assertEquals(4_800, descriptor.byteLength());
    assertEquals(4_800, descriptor.recordLength());
    assertEquals(1, descriptor.recordCount());
    assertEquals(hash(record((byte) 1)), descriptor.sha256());
    assertTrue(descriptor.toString().contains("relativePath=REDACTED"));
    assertFalse(descriptor.toString().contains(PATH));
    assertThrows(
        NullPointerException.class,
        () -> new LargeResultDescriptor(null, PATH, 4_800, "0".repeat(64), 1));
    assertThrows(
        NullPointerException.class,
        () -> new LargeResultDescriptor(FILE_ID, null, 4_800, "0".repeat(64), 1));
    assertThrows(
        NullPointerException.class, () -> new LargeResultDescriptor(FILE_ID, PATH, 4_800, null, 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LargeResultDescriptor(FILE_ID, PATH, 0, "0".repeat(64), 0));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LargeResultDescriptor(FILE_ID, PATH, 48_004_800, "0".repeat(64), 10_001));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LargeResultDescriptor(FILE_ID, PATH, 4_799, "0".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LargeResultDescriptor(FILE_ID, PATH, 4_800, "A".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LargeResultDescriptor(FILE_ID, "", 4_800, "0".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LargeResultDescriptor(FILE_ID, "x".repeat(257), 4_800, "0".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LargeResultDescriptor(
                FILE_ID, "20260902/" + FILE_ID + ".ready\u0000", 4_800, "0".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LargeResultDescriptor(
                FILE_ID, "20260902/" + FILE_ID + ".réady", 4_800, "0".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LargeResultDescriptor(
                FILE_ID, "/20260902/" + FILE_ID + ".ready", 4_800, "0".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LargeResultDescriptor(
                FILE_ID, "20260230/" + FILE_ID + ".ready", 4_800, "0".repeat(64), 1));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LargeResultDescriptor(
                FILE_ID,
                "20260902/223e4567-e89b-12d3-a456-426614174000.ready",
                4_800,
                "0".repeat(64),
                1));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LargeResultDescriptor(
                FILE_ID, "20260902/" + FILE_ID + ".part", 4_800, "0".repeat(64), 1));
  }

  @Test
  void writesAndReadsHeaderlessExactRecordsWithIndependentHash() {
    byte[] first = record((byte) 1);
    byte[] second = record((byte) 2);
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    LargeResultContent content = LargeResultRecordCodec.write(output, List.of(first, second));
    byte[] expected = new byte[9_600];
    System.arraycopy(first, 0, expected, 0, 4_800);
    System.arraycopy(second, 0, expected, 4_800, 4_800);
    assertArrayEquals(expected, output.toByteArray());
    assertEquals(2, content.recordCount());
    assertEquals(9_600, content.byteLength());
    assertEquals(hash(expected), content.sha256());
    LargeResultDescriptor descriptor =
        new LargeResultDescriptor(FILE_ID, PATH, 9_600, content.sha256(), 2);
    List<byte[]> decoded =
        LargeResultRecordCodec.decode(new ChunkedInputStream(expected, 37, false), descriptor);
    assertArrayEquals(first, decoded.get(0));
    assertArrayEquals(second, decoded.get(1));
    assertThrows(UnsupportedOperationException.class, () -> decoded.clear());
    List<byte[]> decodedAfterZeroRead =
        LargeResultRecordCodec.decode(new ChunkedInputStream(expected, 53, true), descriptor);
    assertArrayEquals(expected, join(decodedAfterZeroRead));
  }

  @Test
  void acceptsTheDocumentedTenThousandRecordFortyEightMillionByteMaximum() {
    // UI237/SS333: independent fixed 4,800 * 10,000 = 48,000,000 byte contract (BUG1292).
    assertEquals(4_800, LargeResultDescriptor.RECORD_LENGTH);
    assertEquals(10_000, LargeResultDescriptor.MAXIMUM_RECORD_COUNT);
    assertEquals(48_000_000L, LargeResultDescriptor.MAXIMUM_BYTE_LENGTH);
    byte[] zeroRecord = new byte[4_800];
    String expectedHash = repeatedHash(zeroRecord, 10_000);
    CountingOutputStream output = new CountingOutputStream();
    LargeResultContent content =
        assertDoesNotThrow(
            () ->
                LargeResultRecordCodec.write(
                    output, java.util.Collections.nCopies(10_000, zeroRecord)));
    assertEquals(48_000_000L, output.count);
    assertEquals(48_000_000L, content.byteLength());
    assertEquals(expectedHash, content.sha256());

    LargeResultDescriptor descriptor =
        assertDoesNotThrow(
            () -> new LargeResultDescriptor(FILE_ID, PATH, 48_000_000L, expectedHash, 10_000));
    List<byte[]> decoded =
        assertDoesNotThrow(
            () -> LargeResultRecordCodec.decode(new ZeroInputStream(48_000_000L), descriptor));
    assertEquals(10_000, decoded.size());
    assertArrayEquals(zeroRecord, decoded.getFirst());
    assertArrayEquals(zeroRecord, decoded.getLast());
  }

  @Test
  void writeRejectsNullCountLengthAndIoFailure() {
    byte[] valid = record((byte) 1);
    assertThrows(
        NullPointerException.class, () -> LargeResultRecordCodec.write(null, List.of(valid)));
    assertThrows(
        NullPointerException.class,
        () -> LargeResultRecordCodec.write(new ByteArrayOutputStream(), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> LargeResultRecordCodec.write(new ByteArrayOutputStream(), List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            LargeResultRecordCodec.write(
                new ByteArrayOutputStream(), java.util.Collections.nCopies(10_001, valid)));
    ArrayList<byte[]> withNull = new ArrayList<>();
    withNull.add(null);
    assertThrows(
        NullPointerException.class,
        () -> LargeResultRecordCodec.write(new ByteArrayOutputStream(), withNull));
    assertThrows(
        IllegalArgumentException.class,
        () -> LargeResultRecordCodec.write(new ByteArrayOutputStream(), List.of(new byte[4_799])));
    OutputStream broken =
        new OutputStream() {
          @Override
          public void write(int value) throws IOException {
            throw new IOException(IO_FAILURE_MESSAGE);
          }

          @Override
          public void write(byte[] value) throws IOException {
            throw new IOException(IO_FAILURE_MESSAGE);
          }
        };
    assertThrows(
        LargeResultIoException.class, () -> LargeResultRecordCodec.write(broken, List.of(valid)));
  }

  @Test
  void decodeRejectsTruncationExtraHashAndIoFailure() {
    byte[] record = record((byte) 3);
    LargeResultDescriptor valid = descriptor(1, hash(record));
    assertThrows(NullPointerException.class, () -> LargeResultRecordCodec.decode(null, valid));
    assertThrows(
        NullPointerException.class,
        () -> LargeResultRecordCodec.decode(new ByteArrayInputStream(record), null));
    assertThrows(
        PermanentProtocolException.class,
        () ->
            LargeResultRecordCodec.decode(
                new ByteArrayInputStream(Arrays.copyOf(record, 4_799)), valid));
    byte[] extra = Arrays.copyOf(record, 4_801);
    assertThrows(
        PermanentProtocolException.class,
        () -> LargeResultRecordCodec.decode(new ByteArrayInputStream(extra), valid));
    LargeResultDescriptor wrongHash = descriptor(1, "0".repeat(64));
    assertThrows(
        PermanentProtocolException.class,
        () -> LargeResultRecordCodec.decode(new ByteArrayInputStream(record), wrongHash));
    InputStream broken =
        new InputStream() {
          @Override
          public int read() throws IOException {
            throw new IOException(IO_FAILURE_MESSAGE);
          }

          @Override
          public int read(byte[] value, int offset, int length) throws IOException {
            throw new IOException(IO_FAILURE_MESSAGE);
          }
        };
    assertThrows(LargeResultIoException.class, () -> LargeResultRecordCodec.decode(broken, valid));
    InputStream zeroThenEof =
        new InputStream() {
          @Override
          public int read() {
            return -1;
          }

          @Override
          public int read(byte[] value, int offset, int length) {
            return 0;
          }
        };
    assertThrows(
        PermanentProtocolException.class, () -> LargeResultRecordCodec.decode(zeroThenEof, valid));
    assertThrows(
        IllegalStateException.class, () -> LargeResultRecordCodec.digestFor("not-an-algorithm"));
  }

  @Test
  void contentMetadataRejectsInvalidValues() {
    String hash = "0".repeat(64);
    assertEquals(hash, new LargeResultContent(1, 4_800, hash).sha256());
    assertThrows(NullPointerException.class, () -> new LargeResultContent(1, 4_800, null));
    assertThrows(IllegalArgumentException.class, () -> new LargeResultContent(0, 0, hash));
    assertThrows(
        IllegalArgumentException.class, () -> new LargeResultContent(10_001, 48_004_800, hash));
    assertThrows(IllegalArgumentException.class, () -> new LargeResultContent(1, 4_799, hash));
    assertThrows(
        IllegalArgumentException.class, () -> new LargeResultContent(1, 4_800, "x".repeat(64)));
  }

  private static LargeResultDescriptor descriptor(int count, String hash) {
    return new LargeResultDescriptor(FILE_ID, PATH, 4_800L * count, hash, count);
  }

  private static byte[] record(byte value) {
    byte[] result = new byte[4_800];
    Arrays.fill(result, value);
    return result;
  }

  private static byte[] join(List<byte[]> records) {
    byte[] result = new byte[records.size() * 4_800];
    for (int index = 0; index < records.size(); index++) {
      System.arraycopy(records.get(index), 0, result, index * 4_800, 4_800);
    }
    return result;
  }

  private static String hash(byte[] value) {
    try {
      return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value));
    } catch (Exception exception) {
      throw new AssertionError(exception);
    }
  }

  private static String repeatedHash(byte[] value, int count) {
    try {
      MessageDigest digest = MessageDigest.getInstance("SHA-256");
      for (int index = 0; index < count; index++) {
        digest.update(value);
      }
      return HexFormat.of().formatHex(digest.digest());
    } catch (Exception exception) {
      throw new AssertionError(exception);
    }
  }

  private static final class CountingOutputStream extends OutputStream {
    private long count;

    @Override
    public void write(int value) {
      count++;
    }

    @Override
    public void write(byte[] value, int offset, int length) {
      count += length;
    }
  }

  private static final class ZeroInputStream extends InputStream {
    private long remaining;

    private ZeroInputStream(long remaining) {
      this.remaining = remaining;
    }

    @Override
    public int read() {
      if (remaining == 0) {
        return -1;
      }
      remaining--;
      return 0;
    }

    @Override
    public int read(byte[] target, int offset, int length) {
      if (remaining == 0) {
        return -1;
      }
      int read = (int) Math.min(remaining, length);
      Arrays.fill(target, offset, offset + read, (byte) 0);
      remaining -= read;
      return read;
    }
  }

  private static final class ChunkedInputStream extends InputStream {
    private final byte[] value;
    private final int chunkSize;
    private final boolean returnZeroOnce;
    private int offset;
    private boolean zeroReturned;

    private ChunkedInputStream(byte[] value, int chunkSize, boolean returnZeroOnce) {
      this.value = value;
      this.chunkSize = chunkSize;
      this.returnZeroOnce = returnZeroOnce;
    }

    @Override
    public int read() {
      return offset >= value.length ? -1 : Byte.toUnsignedInt(value[offset++]);
    }

    @Override
    public int read(byte[] target, int targetOffset, int length) {
      if (returnZeroOnce && !zeroReturned) {
        zeroReturned = true;
        return 0;
      }
      if (offset >= value.length) {
        return -1;
      }
      int copied = Math.min(Math.min(length, chunkSize), value.length - offset);
      System.arraycopy(value, offset, target, targetOffset, copied);
      offset += copied;
      return copied;
    }
  }
}
