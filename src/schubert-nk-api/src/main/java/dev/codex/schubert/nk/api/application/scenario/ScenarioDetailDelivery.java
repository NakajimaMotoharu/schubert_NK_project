package dev.codex.schubert.nk.api.application.scenario;

import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshot;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * Post-commit delivery selection and typed response projection; no DB/JMS/ACK/cleanup ownership.
 * NK-SCN-001; RD FUN-004/005/FIL-001..009; UI234 §10/237; SS333 §4/5; PT-SCN-008-R01..R03.
 */
public final class ScenarioDetailDelivery {
  private static final LayoutId RESPONSE = new LayoutId("SCNRSP01");
  private final ScenarioFilePublisher publisher;

  public ScenarioDetailDelivery(ScenarioFilePublisher publisher) {
    this.publisher = Objects.requireNonNull(publisher, "publisher");
  }

  /** Caller must have committed and closed the snapshot transaction before invoking this method. */
  public TypedPayloadValues deliver(ScenarioDetailSnapshot snapshot, Instant generatedAt)
      throws IOException {
    Objects.requireNonNull(snapshot, "snapshot");
    Objects.requireNonNull(generatedAt, "generatedAt");
    // 256 + 1728 + 200 * 4800 = 961984 < 1000000. Snapshot validation fixes all these widths.
    if (snapshot.records().size() <= 200) {
      return new TypedPayloadValues(RESPONSE, snapshot.metadata(), List.copyOf(snapshot.records()));
    }
    LargeResultDescriptor file =
        Objects.requireNonNull(
            publisher.publish(snapshot.records(), generatedAt), "published descriptor");
    if (file.recordCount() != snapshot.records().size()) {
      throw new IllegalStateException("published scenario record count differs from snapshot");
    }
    ScenarioDetailResponseData base = snapshot.metadata();
    ScenarioDetailResponseData metadata =
        new ScenarioDetailResponseData(
            base.scriptFileId(),
            base.gameCode(),
            base.displayTitle(),
            base.displayPath(),
            base.previousFileId(),
            base.previousTitle(),
            base.nextFileId(),
            base.nextTitle(),
            DeliveryMode.FILE,
            Optional.of(file.fileId()),
            Optional.of(RelativePath.of(file.relativePath())),
            file.byteLength(),
            Optional.of(Sha256Hex.of(file.sha256())),
            file.recordLength(),
            file.recordCount());
    return new TypedPayloadValues(RESPONSE, metadata, List.of());
  }
}
