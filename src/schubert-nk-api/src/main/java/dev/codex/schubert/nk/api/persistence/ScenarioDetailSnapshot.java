package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import java.util.List;
import java.util.Objects;

/**
 * Immutable, validated DB snapshot without any file I/O or fabricated descriptor. NK-SCN-001;
 * FUN-004/005; UI234 §10; SS332/333; PG-D-054; PT-SCN-008-D01..004.
 */
public record ScenarioDetailSnapshot(
    ScenarioDetailResponseData metadata, List<ScenarioEntryRecord> records) {
  public ScenarioDetailSnapshot {
    Objects.requireNonNull(metadata, "metadata");
    records = List.copyOf(records);
    if (metadata.deliveryMode() != DeliveryMode.INLINE || records.size() > 10000)
      throw new IllegalArgumentException("invalid scenario snapshot shape");
    PayloadCodec.standard()
        .encode(
            PayloadTypeCatalog.encode(
                new TypedPayloadValues(new LayoutId("SCNRSP01"), metadata, List.of())),
            false);
    PayloadSemanticValidator.validateScenarioSequence(
        records.stream().map(ScenarioEntryRecord::fields).toList());
    for (ScenarioEntryRecord record : records) {
      // Full-list sequence was checked above. A single file record is not an inline response.
      PayloadCodec.standard()
          .encode(
              new PayloadValues(
                  new LayoutId("SCNRSP01"), metadata.fields(), List.of(record.fields())),
              false);
    }
  }

  @Override
  public String toString() {
    return "ScenarioDetailSnapshot[recordCount=" + records.size() + "]";
  }
}
