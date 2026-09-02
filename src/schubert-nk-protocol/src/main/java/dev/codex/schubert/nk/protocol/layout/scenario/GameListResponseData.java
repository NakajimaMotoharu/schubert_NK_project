package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts GAMRSP01. */
public record GameListResponseData(FieldValue.Numeric totalCount) implements PayloadData {
  public GameListResponseData {
    Objects.requireNonNull(totalCount, "totalCount");
  }

  public static GameListResponseData from(FieldValueSet fields) {
    return new GameListResponseData(
        TypedFieldValues.requiredNumeric(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Total count", totalCount)));
  }
}
