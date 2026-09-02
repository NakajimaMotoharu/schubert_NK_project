package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts RTEREQ01. */
public record RouteListRequestData(FieldValue.Text gameCode) implements PayloadData {
  public RouteListRequestData {
    Objects.requireNonNull(gameCode, "gameCode");
  }

  public static RouteListRequestData from(FieldValueSet fields) {
    return new RouteListRequestData(
        TypedFieldValues.requiredText(fields, "Game code"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", gameCode)));
  }
}
