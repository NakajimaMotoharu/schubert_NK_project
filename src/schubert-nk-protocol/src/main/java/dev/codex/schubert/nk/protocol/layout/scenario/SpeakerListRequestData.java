package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SPKREQ01. */
public record SpeakerListRequestData(Optional<GameCode> gameCode) implements PayloadData {
  public SpeakerListRequestData {
    Objects.requireNonNull(gameCode, "gameCode");
  }

  public static SpeakerListRequestData from(FieldValueSet fields) {
    return new SpeakerListRequestData(
        TypedFieldValues.optionalEnum(fields, "Game code", GameCode.class));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(Map.entry("Game code", TypedFieldValues.optionalEnumValue(gameCode))));
  }

  @Override
  public String toString() {
    return "SpeakerListRequestData[REDACTED]";
  }
}
