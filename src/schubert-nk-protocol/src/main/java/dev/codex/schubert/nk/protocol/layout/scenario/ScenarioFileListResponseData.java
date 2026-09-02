package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFRSP01. */
public record ScenarioFileListResponseData(FieldValue.Text gameCode,
    FieldValue.Numeric prefix,
    FieldValue.Text routeName,
    FieldValue.Numeric totalCount) implements PayloadData {
  public ScenarioFileListResponseData {
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(prefix, "prefix");
    Objects.requireNonNull(routeName, "routeName");
    Objects.requireNonNull(totalCount, "totalCount");
  }

  public static ScenarioFileListResponseData from(FieldValueSet fields) {
    return new ScenarioFileListResponseData(
        TypedFieldValues.requiredText(fields, "Game code"),
        TypedFieldValues.requiredNumeric(fields, "Prefix"),
        TypedFieldValues.requiredText(fields, "Route名"),
        TypedFieldValues.requiredNumeric(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", gameCode),
            Map.entry("Prefix", prefix),
            Map.entry("Route名", routeName),
            Map.entry("Total count", totalCount)));
  }
}
