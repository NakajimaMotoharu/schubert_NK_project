package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts RTEREQ01. */
public record RouteListRequestData(GameCode gameCode) implements PayloadData {
  public RouteListRequestData {
    Objects.requireNonNull(gameCode, "gameCode");
  }

  public static RouteListRequestData from(FieldValueSet fields) {
    return new RouteListRequestData(
        TypedFieldValues.requiredEnum(fields, "Game code", GameCode.class));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", TypedFieldValues.enumValue(gameCode))));
  }

  @Override
  public String toString() {
    return "RouteListRequestData[REDACTED]";
  }
}
