package dev.codex.schubert.nk.api.application.scenario;

import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshot;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.ProviderException;
import java.time.Instant;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Objects;
import java.util.Optional;

/**
 * Regenerates only an independently confirmed missing file from the original frozen content.
 * NK-SCN-001; MQ-006..010/FIL-001..009; UI237/241; SS324 §7.1/333 §4..6;
 * SSC-027/PG-D-069/PT-SCN-009-F01..F03. Caller closes the read-only snapshot TX first.
 */
final class ScenarioFileRegenerator {
  private final ScenarioFilePublisher publisher;
  private final DigestFactory digests;

  @FunctionalInterface
  interface DigestFactory {
    MessageDigest create() throws NoSuchAlgorithmException;
  }

  ScenarioFileRegenerator(ScenarioFilePublisher publisher) {
    this(publisher, () -> MessageDigest.getInstance("SHA-256"));
  }

  ScenarioFileRegenerator(ScenarioFilePublisher publisher, DigestFactory digests) {
    this.publisher = Objects.requireNonNull(publisher, "publisher");
    this.digests = Objects.requireNonNull(digests, "digests");
  }

  /** No delete/update/retry, and never called to repair a present but invalid file. */
  LargeResultDescriptor regenerate(
      ScenarioReplayService.Snapshot saved, ScenarioDetailSnapshot current, Instant generatedAt) {
    Objects.requireNonNull(saved, "saved");
    Objects.requireNonNull(current, "current");
    Objects.requireNonNull(generatedAt, "generatedAt");
    try {
      require(saved.resultCode() == ResultCode.SUCCESS);
      LargeResultDescriptor old = saved.descriptor().orElseThrow(IllegalArgumentException::new);
      ScenarioDetailResponseData metadata =
          saved.detail().orElseThrow(IllegalArgumentException::new);
      require(current.metadata().equals(withoutFile(metadata)));
      require(current.records().size() == old.recordCount());
      MessageDigest digest = Objects.requireNonNull(digests.create(), "digest");
      for (var record : current.records()) {
        byte[] encoded =
            PayloadCodec.standard().encodeRecord(new LayoutId("SCNRSP01"), record.fields());
        try {
          digest.update(encoded);
        } finally {
          Arrays.fill(encoded, (byte) 0);
        }
      }
      require(MessageDigest.isEqual(digest.digest(), HexFormat.of().parseHex(old.sha256())));
      LargeResultDescriptor regenerated =
          Objects.requireNonNull(
              publisher.publish(current.records(), generatedAt), "regenerated descriptor");
      require(sameContent(old, regenerated));
      return regenerated;
    } catch (IOException
        | CapacityExceededException
        | NoSuchAlgorithmException
        | ProviderException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  static boolean sameContent(LargeResultDescriptor original, LargeResultDescriptor regenerated) {
    Objects.requireNonNull(original, "original");
    Objects.requireNonNull(regenerated, "regenerated");
    return original.recordCount() == regenerated.recordCount()
        && MessageDigest.isEqual(
            HexFormat.of().parseHex(original.sha256()),
            HexFormat.of().parseHex(regenerated.sha256()));
  }

  private static ScenarioDetailResponseData withoutFile(ScenarioDetailResponseData base) {
    return new ScenarioDetailResponseData(
        base.scriptFileId(),
        base.gameCode(),
        base.displayTitle(),
        base.displayPath(),
        base.previousFileId(),
        base.previousTitle(),
        base.nextFileId(),
        base.nextTitle(),
        DeliveryMode.INLINE,
        Optional.empty(),
        Optional.empty(),
        0,
        Optional.empty(),
        0,
        0);
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("original scenario result is unavailable");
  }
}
