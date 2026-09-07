package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFREQ01. */
public record ScenarioFileListRequestData(GameCode gameCode, int prefix) implements PayloadData {
  public ScenarioFileListRequestData {
    Objects.requireNonNull(gameCode, "gameCode");
    TypedFieldValues.requireUnsignedRange("prefix", prefix, 2);
  }

  public static ScenarioFileListRequestData from(FieldValueSet fields) {
    return new ScenarioFileListRequestData(
        TypedFieldValues.requiredEnum(fields, "Game code", GameCode.class),
        TypedFieldValues.requiredInt(fields, "Prefix"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", TypedFieldValues.enumValue(gameCode)),
            Map.entry("Prefix", TypedFieldValues.numeric(prefix))));
  }

  @Override
  public String toString() {
    return "ScenarioFileListRequestData[REDACTED]";
  }
}
