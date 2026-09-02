package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SPKREQ01. */
public record SpeakerListRequestData(Optional<FieldValue.Text> gameCode) implements PayloadData {
  public SpeakerListRequestData {
    Objects.requireNonNull(gameCode, "gameCode");
  }

  public static SpeakerListRequestData from(FieldValueSet fields) {
    return new SpeakerListRequestData(
        TypedFieldValues.optionalText(fields, "Game code"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", TypedFieldValues.orUnset(gameCode))));
  }
}
