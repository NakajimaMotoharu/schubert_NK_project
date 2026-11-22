package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.ReadableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.HexFormat;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent synthetic bytes, not production writer/encoder output. PT-SCN-008-W06. */
class TransferContentVerifierTest {
  @TempDir Path root;

  @Test
  void w06ActualOne201And10000RecordFilesMatchIndependentLengthAndHash()
      throws IOException, NoSuchAlgorithmException {
    for (int count : new int[] {1, 201, 10000}) {
      byte[] golden = golden();
      MessageDigest digest = MessageDigest.getInstance("SHA-256");
      Path file = root.resolve("count-" + count);
      try (var output = Files.newOutputStream(file, StandardOpenOption.CREATE_NEW)) {
        for (int i = 0; i < count; i++) {
          output.write(golden);
          digest.update(golden);
        }
      }
      var expected =
          new LargeResultContent(count, 4800L * count, HexFormat.of().formatHex(digest.digest()));
      try (var input = FileChannel.open(file, StandardOpenOption.READ)) {
        TransferContentVerifier.verify(input, expected);
        assertTrue(input.isOpen());
        assertEquals(4800L * count, input.position());
        assertEquals(4800L * count, input.size());
      }
    }
  }

  @Test
  void w06ThreeByteReadsStayBoundedAndEveryDigestByteDifferenceIsRejected()
      throws StorageIoException, NoSuchAlgorithmException {
    byte[] golden = golden();
    var expected = expected(golden);
    try (var input = new ChunkedInput(golden, 0)) {
      TransferContentVerifier.verify(input, expected);
      assertTrue(input.isOpen());
      assertEquals(4800, input.offset);
      assertEquals(4800, input.maximumBuffer);
    }
    byte[] hash = HexFormat.of().parseHex(expected.sha256());
    for (int position = 0; position < 32; position++) {
      byte[] modified = hash.clone();
      modified[position] ^= 1;
      var wrong = new LargeResultContent(1, 4800, HexFormat.of().formatHex(modified));
      try (var input = new ChunkedInput(golden, 0)) {
        reject(() -> TransferContentVerifier.verify(input, wrong));
        assertTrue(input.isOpen());
        assertEquals(4800, input.offset);
      }
    }
  }

  @Test
  void w06NullEarlyEofZeroExtraBytesIoClosedAndAmbiguousEofFailWithoutClosing()
      throws NoSuchAlgorithmException {
    byte[] golden = golden();
    var expected = expected(golden);
    assertThrows(NullPointerException.class, () -> TransferContentVerifier.verify(null, expected));
    try (var input = new ChunkedInput(golden, 0)) {
      assertThrows(NullPointerException.class, () -> TransferContentVerifier.verify(input, null));
      assertEquals(0, input.offset);
    }
    for (byte[] bytes :
        new byte[][] {new byte[0], Arrays.copyOf(golden, 4799), Arrays.copyOf(golden, 4801)}) {
      try (var input = new ChunkedInput(bytes, 0)) {
        reject(() -> TransferContentVerifier.verify(input, expected));
        assertTrue(input.isOpen());
      }
    }
    for (int mode = 1; mode <= 3; mode++) {
      try (var input = new ChunkedInput(golden, mode)) {
        reject(() -> TransferContentVerifier.verify(input, expected));
        assertTrue(input.isOpen());
      }
    }
    var closed = new ChunkedInput(golden, 0);
    try {
      closed.close();
      reject(() -> TransferContentVerifier.verify(closed, expected));
      assertFalse(closed.isOpen());
    } finally {
      closed.close();
    }
  }

  private static byte[] golden() {
    byte[] result = new byte[4800];
    Arrays.fill(result, (byte) ' ');
    result[0] = '1';
    result[4799] = '2';
    return result;
  }

  /** PT-SCN-008-W06-FATAL; SS333 §6.2 / SSC-478. */
  @Test
  void w06ReadFailurePreservesTheFirstWrappedErrorAndKeepsTheChannelBorrowed()
      throws NoSuchAlgorithmException {
    var expected = expected(golden());
    var cause = new AssertionError("fixture cause");
    var suppressed = new LinkageError("fixture suppressed");
    var both = new IOException("fixture wrapper", cause);
    both.addSuppressed(suppressed);
    var suppressedOnly = new IOException("fixture wrapper");
    suppressedOnly.addSuppressed(suppressed);
    assertReadError(expected, both, cause);
    assertReadError(expected, suppressedOnly, suppressed);

    var ordinary = new IOException("fixture wrapper", new IllegalStateException("fixture cause"));
    ordinary.addSuppressed(new IOException("fixture suppressed"));
    try (var input = new FailingInput(ordinary)) {
      reject(() -> TransferContentVerifier.verify(input, expected));
      assertTrue(input.isOpen());
      assertEquals(1, input.reads);
    }
  }

  private static void assertReadError(
      LargeResultContent expected, IOException failure, Error expectedError) {
    try (var input = new FailingInput(failure)) {
      assertSame(
          expectedError,
          assertThrows(Error.class, () -> TransferContentVerifier.verify(input, expected)));
      assertTrue(input.isOpen());
      assertEquals(1, input.reads);
    }
  }

  private static final class FailingInput implements ReadableByteChannel {
    private final IOException failure;
    private boolean open = true;
    private int reads;

    private FailingInput(IOException failure) {
      this.failure = failure;
    }

    @Override
    public int read(ByteBuffer destination) throws IOException {
      reads++;
      throw failure;
    }

    @Override
    public boolean isOpen() {
      return open;
    }

    @Override
    public void close() {
      open = false;
    }
  }

  private static LargeResultContent expected(byte[] bytes) throws NoSuchAlgorithmException {
    return new LargeResultContent(
        1, 4800, HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)));
  }

  private static void reject(org.junit.jupiter.api.function.Executable operation) {
    StorageIoException failure = assertThrows(StorageIoException.class, operation);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class ChunkedInput implements ReadableByteChannel {
    private static final int ZERO_PROGRESS_MODE = 1;

    final byte[] bytes;
    final int mode;
    int offset;
    int maximumBuffer;
    boolean open = true;

    ChunkedInput(byte[] bytes, int mode) {
      this.bytes = bytes;
      this.mode = mode;
    }

    @Override
    public int read(ByteBuffer target) throws IOException {
      if (!open || mode == 2) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      maximumBuffer = Math.max(maximumBuffer, target.remaining());
      if (mode == ZERO_PROGRESS_MODE) return 0;
      if (offset == bytes.length) return mode == 3 ? 0 : -1;
      int length = Math.min(3, Math.min(target.remaining(), bytes.length - offset));
      target.put(bytes, offset, length);
      offset += length;
      return length;
    }

    @Override
    public boolean isOpen() {
      return open;
    }

    @Override
    public void close() {
      open = false;
    }
  }
}
