package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFREQ01. */
public record ScenarioFileListRequestData(String gameCode,
    long prefix) implements PayloadData {
  public ScenarioFileListRequestData {
    Objects.requireNonNull(gameCode, "gameCode");
  }

  public static ScenarioFileListRequestData from(FieldValueSet fields) {
    return new ScenarioFileListRequestData(
        TypedFieldValues.requiredString(fields, "Game code"),
        TypedFieldValues.requiredLong(fields, "Prefix"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", TypedFieldValues.text(gameCode)),
            Map.entry("Prefix", TypedFieldValues.numeric(prefix))));
  }

  @Override
  public String toString() {
    return "ScenarioFileListRequestData[REDACTED]";
  }
}
