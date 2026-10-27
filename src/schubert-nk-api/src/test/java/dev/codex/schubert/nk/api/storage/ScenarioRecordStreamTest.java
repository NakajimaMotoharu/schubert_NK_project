package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.channels.ReadableByteChannel;
import java.nio.channels.WritableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** UI234 handwritten record bytes and independently accumulated digest. PT-SCN-008-W04/W05. */
class ScenarioRecordStreamTest {
  @TempDir Path root;

  @Test
  void w04One201And10000RecordsMatchEveryGoldenByteAndIndependentDigest() throws Exception {
    for (int count : new int[] {1, 201, 10000}) {
      List<ScenarioEntryRecord> source = records(count);
      var prepared = new ScenarioRecordStream(source);
      source.clear();
      assertEquals(4800L * count, prepared.byteLength());
      assertEquals("ScenarioRecordStream[recordCount=" + count + "]", prepared.toString());
      Path path = root.resolve("count-" + count);
      try (var channel =
          FileChannel.open(path, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
        var result = prepared.write(channel);
        assertTrue(channel.isOpen());
        assertEquals(count, result.recordCount());
        assertEquals(4800L * count, result.byteLength());
        assertEquals(result.byteLength(), channel.size());
        assertEquals(independentFileCheck(path, count), result.sha256());
      }
    }
  }

  @Test
  void w04ImmutablePreparedRecordsSupportConcurrentIndependentChannels() throws Exception {
    var prepared = new ScenarioRecordStream(records(3));
    try (var pool = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<java.util.concurrent.Callable<String>>();
      for (int i = 0; i < 16; i++) {
        Path path = root.resolve("parallel-" + i);
        tasks.add(
            () -> {
              try (var channel =
                  FileChannel.open(path, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
                String actual = prepared.write(channel).sha256();
                assertEquals(independentFileCheck(path, 3), actual);
                return actual;
              }
            });
      }
      String first = null;
      for (var result : pool.invokeAll(tasks)) {
        String actual = result.get();
        if (first == null) first = actual;
        assertEquals(first, actual);
      }
    }
  }

  @Test
  void w05PreflightRejectsNullCountSequenceAndInvalidLastRecordBeforeAnyIo() throws Exception {
    assertThrows(NullPointerException.class, () -> new ScenarioRecordStream(null));
    assertThrows(
        NullPointerException.class,
        () -> new ScenarioRecordStream(Arrays.asList((ScenarioEntryRecord) null)));
    assertThrows(IllegalArgumentException.class, () -> new ScenarioRecordStream(List.of()));
    assertThrows(IllegalArgumentException.class, () -> new ScenarioRecordStream(records(10001)));
    assertThrows(
        dev.codex.schubert.nk.protocol.layout.LayoutValidationException.class,
        () -> new ScenarioRecordStream(List.of(record(1, "本文"))));
    for (String invalid : List.of("x".repeat(4097), "bad\ntext", "bad\0text")) {
      List<ScenarioEntryRecord> input = records(201);
      input.set(200, record(200, invalid));
      assertThrows(
          dev.codex.schubert.nk.protocol.codec.FieldEncodingException.class,
          () -> new ScenarioRecordStream(input));
    }
    assertThrows(
        NullPointerException.class, () -> new ScenarioRecordStream(records(1)).write(null));
    try (var entries = Files.list(root)) {
      assertEquals(0, entries.count());
    }
  }

  @Test
  void w05PartialWritesRemainBoundedAndForceOnlyAfterAll4800Bytes() throws Exception {
    var prepared = new ScenarioRecordStream(records(1));
    Path path = root.resolve("partial");
    try (var channel = new FaultChannel(path, 0)) {
      var result = prepared.write(channel);
      assertTrue(channel.isOpen());
      assertTrue(channel.forced);
      assertTrue(channel.writes > 600);
      assertEquals(4800, channel.maximumBuffer);
      assertEquals(independentFileCheck(path, 1), result.sha256());
    }
  }

  @Test
  void w05ZeroNegativeWriteIoForceClosedAndNonfreshChannelsFailWithoutImplicitClose()
      throws Exception {
    var prepared = new ScenarioRecordStream(records(1));
    for (int mode = 1; mode <= 4; mode++) {
      Path path = root.resolve("fault-" + mode);
      try (var channel = new FaultChannel(path, mode)) {
        reject(() -> prepared.write(channel));
        assertTrue(channel.isOpen());
        assertEquals(mode == 4 ? 4800 : 0, channel.size());
        assertEquals(mode == 4, channel.forced);
      }
    }
    var closed =
        FileChannel.open(
            root.resolve("closed"), StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
    try {
      closed.close();
      reject(() -> prepared.write(closed));
    } finally {
      closed.close();
    }
    try (var channel =
        FileChannel.open(
            root.resolve("nonfresh"), StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
      channel.position(1);
      reject(() -> prepared.write(channel));
      assertEquals(0, channel.size());
      channel.position(0);
      channel.write(ByteBuffer.wrap(new byte[] {9}));
      channel.position(0);
      reject(() -> prepared.write(channel));
      assertEquals(1, channel.size());
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(root.resolve("nonfresh")));
    }
  }

  private static List<ScenarioEntryRecord> records(int count) {
    List<ScenarioEntryRecord> result = new ArrayList<>();
    for (int i = 0; i < count; i++) result.add(record(i, "本文 " + i));
    return result;
  }

  private static ScenarioEntryRecord record(int index, String body) {
    return new ScenarioEntryRecord(
        new EntryId(71 + index),
        index + 1,
        42 + index,
        EntryType.NARRATION,
        Optional.empty(),
        body,
        0,
        Optional.empty(),
        Optional.empty());
  }

  private static String independentFileCheck(Path path, int count) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var input = Files.newInputStream(path)) {
      for (int i = 0; i < count; i++) {
        byte[] expected = new byte[4800];
        Arrays.fill(expected, (byte) ' ');
        put(expected, 0, String.format(Locale.ROOT, "%012d", 71 + i));
        put(expected, 12, String.format(Locale.ROOT, "%06d", i + 1));
        put(expected, 18, String.format(Locale.ROOT, "%08d", 42 + i));
        put(expected, 26, "narration");
        put(expected, 164, "本文 " + i);
        put(expected, 4260, "000");
        assertArrayEquals(expected, input.readNBytes(4800), "record " + i);
        digest.update(expected);
      }
      assertEquals(-1, input.read());
    }
    return HexFormat.of().formatHex(digest.digest());
  }

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }

  private static void reject(org.junit.jupiter.api.function.Executable operation) {
    StorageIoException failure = assertThrows(StorageIoException.class, operation);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class FaultChannel extends FileChannel {
    private static final int ZERO_WRITE_MODE = 1;
    private static final int NEGATIVE_WRITE_MODE = 2;
    private static final int IO_FAILURE_MODE = 3;
    private static final int FORCE_FAILURE_MODE = 4;

    final FileChannel actual;
    final int mode;
    boolean forced;
    int writes;
    int maximumBuffer;

    FaultChannel(Path path, int mode) throws IOException {
      this.mode = mode;
      actual = FileChannel.open(path, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
    }

    @Override
    public int write(ByteBuffer buffer) throws IOException {
      writes++;
      maximumBuffer = Math.max(maximumBuffer, buffer.remaining());
      if (mode == ZERO_WRITE_MODE) return 0;
      if (mode == NEGATIVE_WRITE_MODE) return -1;
      if (mode == IO_FAILURE_MODE) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      int limit = buffer.limit();
      buffer.limit(buffer.position() + Math.min(7, buffer.remaining()));
      try {
        return actual.write(buffer);
      } finally {
        buffer.limit(limit);
      }
    }

    @Override
    public void force(boolean metadata) throws IOException {
      assertTrue(metadata);
      assertEquals(4800, actual.size());
      forced = true;
      if (mode == FORCE_FAILURE_MODE) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      actual.force(metadata);
    }

    @Override
    public long position() throws IOException {
      return actual.position();
    }

    @Override
    public long size() throws IOException {
      return actual.size();
    }

    @Override
    protected void implCloseChannel() throws IOException {
      actual.close();
    }

    @Override
    public int read(ByteBuffer dst) {
      throw new AssertionError("unexpected read");
    }

    @Override
    public long read(ByteBuffer[] dsts, int offset, int length) {
      throw new AssertionError("unexpected read");
    }

    @Override
    public int read(ByteBuffer dst, long position) {
      throw new AssertionError("unexpected read");
    }

    @Override
    public long write(ByteBuffer[] srcs, int offset, int length) {
      throw new AssertionError("unexpected gather");
    }

    @Override
    public int write(ByteBuffer src, long position) {
      throw new AssertionError("unexpected positioned write");
    }

    @Override
    public FileChannel position(long value) {
      throw new AssertionError("unexpected seek");
    }

    @Override
    public FileChannel truncate(long size) {
      throw new AssertionError("unexpected truncate");
    }

    @Override
    public long transferTo(long position, long count, WritableByteChannel target) {
      throw new AssertionError("unexpected transfer");
    }

    @Override
    public long transferFrom(ReadableByteChannel src, long position, long count) {
      throw new AssertionError("unexpected transfer");
    }

    @Override
    public MappedByteBuffer map(MapMode mode, long position, long size) {
      throw new AssertionError("unexpected mapping");
    }

    @Override
    public FileLock lock(long position, long size, boolean shared) {
      throw new AssertionError("unexpected lock");
    }

    @Override
    public FileLock tryLock(long position, long size, boolean shared) {
      throw new AssertionError("unexpected lock");
    }
  }
}
