package dev.codex.schubert.nk.web.storage;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;

/**
 * Hash before decode, then recheck bytes actually decoded; never returns partial/unverified data.
 * NK-SCN-001; RD FIL-006/007; UI234/237; SS333 §6; PT-SCN-008-RD03/RD04. Caller owns channel.
 */
final class ScenarioRecordReader {
  private static final LayoutId SCENARIO = new LayoutId("SCNRSP01");

  private ScenarioRecordReader() {}

  static List<ScenarioEntryRecord> read(
      SeekableByteChannel channel, LargeResultDescriptor descriptor)
      throws IOException, NoSuchAlgorithmException {
    Objects.requireNonNull(channel, "channel");
    Objects.requireNonNull(descriptor, "descriptor");
    if (channel.position() != 0) {
      throw new FileIntegrityException();
    }
    scan(channel, descriptor, false);
    channel.position(0);
    List<ScenarioEntryRecord> records = scan(channel, descriptor, true);
    PayloadSemanticValidator.validateScenarioSequence(
        records.stream().map(ScenarioEntryRecord::fields).toList());
    return List.copyOf(records);
  }

  private static List<ScenarioEntryRecord> scan(
      SeekableByteChannel channel, LargeResultDescriptor descriptor, boolean decode)
      throws IOException, NoSuchAlgorithmException {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    ByteBuffer buffer = ByteBuffer.allocate(4800);
    var records = new ArrayList<ScenarioEntryRecord>();
    for (int index = 0; index < descriptor.recordCount(); index++) {
      while (buffer.hasRemaining()) {
        if (channel.read(buffer) <= 0) {
          throw new FileIntegrityException();
        }
      }
      digest.update(buffer.array());
      if (decode) {
        records.add(
            ScenarioEntryRecord.from(
                PayloadCodec.standard().decodeRecord(SCENARIO, buffer.array())));
      }
      buffer.clear();
    }
    buffer.limit(1);
    if (channel.read(buffer) != -1
        || !MessageDigest.isEqual(digest.digest(), HexFormat.of().parseHex(descriptor.sha256()))) {
      throw new FileIntegrityException();
    }
    return records;
  }
}
