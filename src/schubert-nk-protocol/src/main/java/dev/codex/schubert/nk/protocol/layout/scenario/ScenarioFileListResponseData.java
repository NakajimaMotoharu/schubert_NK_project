package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFRSP01. */
public record ScenarioFileListResponseData(GameCode gameCode,
    int prefix,
    String routeName,
    long totalCount) implements PayloadData {
  public ScenarioFileListResponseData {
    Objects.requireNonNull(gameCode, "gameCode");
    TypedFieldValues.requireUnsignedRange("prefix", prefix, 2);
    Objects.requireNonNull(routeName, "routeName");
    TypedFieldValues.requireUnsignedRange("totalCount", totalCount, 9);
  }

  public static ScenarioFileListResponseData from(FieldValueSet fields) {
    return new ScenarioFileListResponseData(
        TypedFieldValues.requiredEnum(fields, "Game code", GameCode.class),
        TypedFieldValues.requiredInt(fields, "Prefix"),
        TypedFieldValues.requiredString(fields, "Route名"),
        TypedFieldValues.requiredLong(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", TypedFieldValues.enumValue(gameCode)),
            Map.entry("Prefix", TypedFieldValues.numeric(prefix)),
            Map.entry("Route名", TypedFieldValues.text(routeName)),
            Map.entry("Total count", TypedFieldValues.numeric(totalCount))));
  }

  @Override
  public String toString() {
    return "ScenarioFileListResponseData[REDACTED]";
  }
}
