package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFREQ01. */
public record ScenarioFileListRequestData(FieldValue.Text gameCode,
    FieldValue.Numeric prefix) implements PayloadData {
  public ScenarioFileListRequestData {
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(prefix, "prefix");
  }

  public static ScenarioFileListRequestData from(FieldValueSet fields) {
    return new ScenarioFileListRequestData(
        TypedFieldValues.requiredText(fields, "Game code"),
        TypedFieldValues.requiredNumeric(fields, "Prefix"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", gameCode),
            Map.entry("Prefix", prefix)));
  }
}
