package dev.codex.schubert.nk.web.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Arrays;
import java.util.HexFormat;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent record bytes, partial I/O and changed-between-pass rejection. RD03/RD04. */
class ScenarioRecordReaderTest {
  @TempDir Path root;

  @Test
  void rd03GoldenRecordsThrough48000000BytesHaveBoundedBuffersAndImmutableOrderedValues()
      throws Exception {
    for (int count : new int[] {1, 201, 10000}) {
      Path file = root.resolve("records-" + count);
      var descriptor = ScenarioFileFixture.write(file, count);
      try (var channel = new FaultChannel(file)) {
        if (count == 1) channel.maximumRead = 7;
        var records = ScenarioRecordReader.read(channel, descriptor);
        assertEquals(count, records.size());
        for (int index = 0; index < count; index++) {
          var record = records.get(index);
          assertEquals(50000 - index, record.entryId().value());
          assertEquals(index + 1, record.entrySequence());
          assertEquals(42, record.lineNumber());
          assertEquals(EntryType.NARRATION, record.entryType());
          assertEquals("本文", record.bodyText());
          assertEquals(0, record.audioSequence());
          assertTrue(record.speakerName().isEmpty());
          assertTrue(record.audioId().isEmpty());
          assertTrue(record.audioDisplayPath().isEmpty());
        }
        assertThrows(UnsupportedOperationException.class, records::clear);
        assertEquals(4800, channel.maximumRequested);
        assertEquals(2 * 4800L * count, channel.bytesRead);
        assertEquals(1, channel.rewinds);
        assertTrue(channel.isOpen());
      }
    }
  }

  @Test
  void rd04NullNonfreshClosedAndExactLengthHashFailuresNeverCloseCallerChannel() throws Exception {
    Path file = root.resolve("fixture");
    var descriptor = ScenarioFileFixture.write(file, 1);
    assertThrows(NullPointerException.class, () -> ScenarioRecordReader.read(null, descriptor));
    try (var channel = new FaultChannel(file)) {
      assertThrows(NullPointerException.class, () -> ScenarioRecordReader.read(channel, null));
      channel.delegate.position(1);
      assertThrows(
          FileIntegrityException.class, () -> ScenarioRecordReader.read(channel, descriptor));
    }
    try (var channel = new FaultChannel(file)) {
      channel.delegate.close();
      assertThrows(IOException.class, () -> ScenarioRecordReader.read(channel, descriptor));
    }
    for (int length : new int[] {0, 4799, 4801}) {
      Files.write(file, Arrays.copyOf(ScenarioFileFixture.golden(1), length));
      try (var channel = new FaultChannel(file)) {
        assertThrows(
            FileIntegrityException.class, () -> ScenarioRecordReader.read(channel, descriptor));
        assertTrue(channel.isOpen());
        assertEquals(0, channel.rewinds);
      }
    }
    Files.write(file, ScenarioFileFixture.golden(1));
    for (int index = 0; index < 32; index++) {
      byte[] wrong = HexFormat.of().parseHex(descriptor.sha256());
      wrong[index] ^= 1;
      var bad = ScenarioFileFixture.descriptor(1, HexFormat.of().formatHex(wrong));
      try (var channel = new FaultChannel(file)) {
        assertThrows(FileIntegrityException.class, () -> ScenarioRecordReader.read(channel, bad));
        assertEquals(0, channel.rewinds);
      }
    }
  }

  @Test
  void rd04ZeroProgressReadSeekFailuresAndContentChangedAfterFirstHashAreRejected()
      throws Exception {
    Path file = root.resolve("faults");
    var descriptor = ScenarioFileFixture.write(file, 1);
    for (String mode : new String[] {"ZERO", "IO", "EOF_ZERO", "SEEK", "SECOND_IO", "MUTATE"}) {
      Files.write(file, ScenarioFileFixture.golden(1));
      try (var channel = new FaultChannel(file)) {
        channel.mode = mode;
        assertThrows(IOException.class, () -> ScenarioRecordReader.read(channel, descriptor));
        assertTrue(channel.isOpen());
        if (mode.equals("MUTATE")) {
          assertEquals(1, channel.rewinds);
          assertEquals(9600, channel.bytesRead);
        }
      }
    }
  }

  @Test
  void rd04ValidHashesDoNotPermitInvalidBytesOrSequenceAndBadHashPrecedesDecode() throws Exception {
    Path file = root.resolve("invalid");
    byte[] reserved = ScenarioFileFixture.golden(1);
    reserved[4799] = '#';
    byte[] missing = ScenarioFileFixture.golden(1);
    Arrays.fill(missing, 0, 12, (byte) ' ');
    byte[] utf8 = ScenarioFileFixture.golden(1);
    utf8[164] = (byte) 0xff;
    byte[] nfc = ScenarioFileFixture.golden(1);
    ScenarioFileFixture.put(nfc, 164, "か\u3099");
    for (byte[] bytes : new byte[][] {reserved, missing, utf8, nfc}) {
      Files.write(file, bytes);
      var descriptor = ScenarioFileFixture.descriptor(1, ScenarioFileFixture.hash(bytes));
      try (var channel = new FaultChannel(file)) {
        assertThrows(
            PermanentProtocolException.class, () -> ScenarioRecordReader.read(channel, descriptor));
        assertEquals(1, channel.rewinds);
      }
    }
    byte[] sequence = ScenarioFileFixture.golden(2);
    Files.write(file, sequence);
    var badSequence = ScenarioFileFixture.descriptor(1, ScenarioFileFixture.hash(sequence));
    try (var channel = new FaultChannel(file)) {
      assertThrows(
          LayoutValidationException.class, () -> ScenarioRecordReader.read(channel, badSequence));
      assertEquals(1, channel.rewinds);
    }
    Files.write(file, reserved);
    var mismatch = ScenarioFileFixture.descriptor(1, "0".repeat(64));
    try (var channel = new FaultChannel(file)) {
      assertThrows(
          FileIntegrityException.class, () -> ScenarioRecordReader.read(channel, mismatch));
      assertEquals(0, channel.rewinds);
    }
  }

  private static final class FaultChannel implements SeekableByteChannel {
    final FileChannel delegate;
    final Path file;
    String mode = "NORMAL";
    int maximumRead = 4800;
    int maximumRequested;
    int rewinds;
    long bytesRead;

    FaultChannel(Path file) throws IOException {
      this.file = file;
      delegate = FileChannel.open(file, StandardOpenOption.READ);
    }

    @Override
    public int read(ByteBuffer target) throws IOException {
      maximumRequested = Math.max(maximumRequested, target.remaining());
      if (mode.equals("ZERO")) return 0;
      if (mode.equals("IO") || mode.equals("SECOND_IO") && rewinds == 1)
        throw new IOException("SYNTHETIC_PRIVATE_PATH");
      if (mode.equals("EOF_ZERO") && delegate.position() == delegate.size()) return 0;
      int limit = target.limit();
      target.limit(target.position() + Math.min(target.remaining(), maximumRead));
      int result = delegate.read(target);
      target.limit(limit);
      if (result > 0) bytesRead += result;
      return result;
    }

    @Override
    public long position() throws IOException {
      return delegate.position();
    }

    @Override
    public SeekableByteChannel position(long next) throws IOException {
      if (mode.equals("SEEK")) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      rewinds++;
      if (mode.equals("MUTATE")) {
        byte[] different = ScenarioFileFixture.golden(1);
        different[0] = '9';
        Files.write(file, different);
      }
      delegate.position(next);
      return this;
    }

    @Override
    public long size() throws IOException {
      return delegate.size();
    }

    @Override
    public int write(ByteBuffer source) {
      throw new AssertionError("read-only contract");
    }

    @Override
    public SeekableByteChannel truncate(long size) {
      throw new AssertionError("read-only contract");
    }

    @Override
    public boolean isOpen() {
      return delegate.isOpen();
    }

    @Override
    public void close() throws IOException {
      delegate.close();
    }
  }
}
