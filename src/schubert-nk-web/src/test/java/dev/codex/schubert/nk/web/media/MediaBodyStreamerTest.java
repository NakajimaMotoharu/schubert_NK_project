package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class MediaBodyStreamerTest {
  /** PT-MED-006; independent synthetic content and exact slice postcondition. */
  @Test
  void exactIntervalsUseBoundedWritesAndLeaveResourcesOpen(@TempDir Path root) throws Exception {
    byte[] data = new byte[1_048_580];
    for (int index = 0; index < data.length; index++) data[index] = (byte) (index * 17 + 3);
    Path file = root.resolve("synthetic.bin");
    Files.write(file, data);
    for (int length : new int[] {0, 1, 65_536, 65_537, 1_048_576}) {
      try (var source = FileChannel.open(file, StandardOpenOption.READ)) {
        var target = new Output();
        MediaBodyStreamer.copy(source, target, 3, length);
        assertArrayEquals(Arrays.copyOfRange(data, 3, 3 + length), target.bytes.toByteArray());
        assertTrue(target.maxWrite <= 65_536);
        assertEquals(length, target.bytes.size());
        assertTrue(source.isOpen());
        assertFalse(target.closed);
        assertFalse(target.flushed);
        assertEquals(3 + length, source.position());
      }
    }
    var shortSource = new Channel();
    shortSource.maxRead = 3;
    var target = new Output();
    MediaBodyStreamer.copy(shortSource, target, 5, 12);
    assertArrayEquals(Arrays.copyOfRange(shortSource.data, 5, 17), target.bytes.toByteArray());
    assertTrue(shortSource.isOpen());
    assertFalse(target.closed);
    MediaBodyStreamer.copy(shortSource, new Output(), 100, 0);
    assertEquals(100, shortSource.position());
  }

  /** PT-MED-007; injected I/O is redacted; ownership and partial output remain explicit. */
  @Test
  void nullBoundsAndIoFailuresDoNotClaimCompleteTransfer() throws Exception {
    assertThrows(
        NullPointerException.class, () -> MediaBodyStreamer.copy(null, new Output(), 0, 1));
    assertThrows(
        NullPointerException.class, () -> MediaBodyStreamer.copy(new Channel(), null, 0, 1));
    for (long[] bounds : new long[][] {{-1, 1}, {0, -1}, {Long.MAX_VALUE, 1}})
      assertThrows(
          IllegalArgumentException.class,
          () -> MediaBodyStreamer.copy(new Channel(), new Output(), bounds[0], bounds[1]));
    for (String fault : List.of("size", "position", "read", "zero", "eof", "write", "outside")) {
      var source = new Channel();
      source.fault = fault;
      var target = new Output();
      target.fail = fault.equals("write");
      var failure =
          assertThrows(
              IOException.class,
              () -> MediaBodyStreamer.copy(source, target, 0, fault.equals("outside") ? 101 : 20));
      assertEquals("media transfer did not complete", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertTrue(source.isOpen());
      assertFalse(target.closed);
    }
    var source = new Channel();
    source.maxRead = 3;
    source.failAfter = 1;
    var target = new Output();
    assertThrows(IOException.class, () -> MediaBodyStreamer.copy(source, target, 0, 20));
    assertArrayEquals(new byte[] {0, 1, 2}, target.bytes.toByteArray());
    assertTrue(source.isOpen());
    assertFalse(target.closed);
  }

  private static final class Output extends java.io.OutputStream {
    final ByteArrayOutputStream bytes = new ByteArrayOutputStream();
    int maxWrite;
    boolean closed;
    boolean flushed;
    boolean fail;

    @Override
    public void write(int value) {
      throw new AssertionError("not a bounded array write");
    }

    @Override
    public void write(byte[] data, int start, int length) throws IOException {
      if (fail) throw new IOException("synthetic private destination");
      maxWrite = Math.max(maxWrite, length);
      bytes.write(data, start, length);
    }

    @Override
    public void close() {
      closed = true;
    }

    @Override
    public void flush() {
      flushed = true;
    }
  }

  private static final class Channel implements SeekableByteChannel {
    final byte[] data = new byte[100];
    String fault = "none";
    int cursor;
    int maxRead = 100;
    int reads;
    int failAfter = Integer.MAX_VALUE;
    boolean closed;

    Channel() {
      for (int i = 0; i < data.length; i++) data[i] = (byte) i;
    }

    @Override
    public int read(ByteBuffer buffer) throws IOException {
      if (fault.equals("read") || reads++ >= failAfter)
        throw new IOException("synthetic private source");
      if (fault.equals("zero")) return 0;
      if (fault.equals("eof")) return -1;
      int length = Math.min(Math.min(maxRead, buffer.remaining()), data.length - cursor);
      buffer.put(data, cursor, length);
      cursor += length;
      return length;
    }

    @Override
    public long size() throws IOException {
      if (fault.equals("size")) throw new IOException("synthetic private source");
      return data.length;
    }

    @Override
    public long position() {
      return cursor;
    }

    @Override
    public SeekableByteChannel position(long position) throws IOException {
      if (fault.equals("position")) throw new IOException("synthetic private source");
      cursor = Math.toIntExact(position);
      return this;
    }

    @Override
    public int write(ByteBuffer ignored) {
      throw new AssertionError("source write");
    }

    @Override
    public SeekableByteChannel truncate(long ignored) {
      throw new AssertionError("source truncate");
    }

    @Override
    public boolean isOpen() {
      return !closed;
    }

    @Override
    public void close() {
      closed = true;
    }
  }
}
