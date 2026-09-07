package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;

/**
 * Prepared immutable view-model records, never an entire file byte array; no DB or path access.
 * NK-SCN-001; RD FIL/PER; UI234/237; SS333 §5; PG-D-059; PT-SCN-008-W04/W05.
 */
final class ScenarioRecordStream {
  private static final LayoutId LAYOUT = new LayoutId("SCNRSP01");
  private final List<ScenarioEntryRecord> records;

  ScenarioRecordStream(List<ScenarioEntryRecord> input) {
    records = List.copyOf(input);
    if (records.isEmpty() || records.size() > 10000) {
      throw new IllegalArgumentException("invalid scenario file record count");
    }
    PayloadSemanticValidator.validateScenarioSequence(
        records.stream().map(ScenarioEntryRecord::fields).toList());
    // Check every field before any I/O. Discard each 4800-byte result, never retain all of them.
    for (ScenarioEntryRecord record : records) encode(record);
  }

  long byteLength() {
    return 4800L * records.size();
  }

  /** Writes and forces a caller-owned fresh channel; does not close, publish or delete anything. */
  LargeResultContent write(FileChannel channel)
      throws StorageIoException, NoSuchAlgorithmException {
    Objects.requireNonNull(channel, "channel");
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try {
      if (channel.position() != 0 || channel.size() != 0) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      for (ScenarioEntryRecord record : records) {
        byte[] encoded = encode(record);
        ByteBuffer buffer = ByteBuffer.wrap(encoded);
        while (buffer.hasRemaining()) {
          if (channel.write(buffer) <= 0) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }
        digest.update(encoded);
      }
      channel.force(true);
    } catch (IOException failure) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
    return new LargeResultContent(
        records.size(), byteLength(), HexFormat.of().formatHex(digest.digest()));
  }

  private static byte[] encode(ScenarioEntryRecord record) {
    return PayloadCodec.standard().encodeRecord(LAYOUT, record.fields());
  }

  @Override
  public String toString() {
    return "ScenarioRecordStream[recordCount=" + records.size() + "]";
  }
}
