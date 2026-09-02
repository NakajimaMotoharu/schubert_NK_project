package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SRCREQ01. */
public record ScenarioSearchRequestData(Optional<String> bodyKeyword,
    Optional<String> gameCode,
    Optional<String> speakerName,
    Optional<String> chapterTitle,
    Optional<String> entryType,
    Optional<String> voiceCondition,
    long page,
    long pageSize) implements PayloadData {
  public ScenarioSearchRequestData {
    Objects.requireNonNull(bodyKeyword, "bodyKeyword");
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(chapterTitle, "chapterTitle");
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(voiceCondition, "voiceCondition");
  }

  public static ScenarioSearchRequestData from(FieldValueSet fields) {
    return new ScenarioSearchRequestData(
        TypedFieldValues.optionalString(fields, "本文keyword"),
        TypedFieldValues.optionalString(fields, "Game code"),
        TypedFieldValues.optionalString(fields, "Speaker名"),
        TypedFieldValues.optionalString(fields, "章title"),
        TypedFieldValues.optionalString(fields, "Entry type"),
        TypedFieldValues.optionalString(fields, "Voice条件"),
        TypedFieldValues.requiredLong(fields, "Page"),
        TypedFieldValues.requiredLong(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("本文keyword", TypedFieldValues.optionalStringValue(bodyKeyword)),
            Map.entry("Game code", TypedFieldValues.optionalStringValue(gameCode)),
            Map.entry("Speaker名", TypedFieldValues.optionalStringValue(speakerName)),
            Map.entry("章title", TypedFieldValues.optionalStringValue(chapterTitle)),
            Map.entry("Entry type", TypedFieldValues.optionalStringValue(entryType)),
            Map.entry("Voice条件", TypedFieldValues.optionalStringValue(voiceCondition)),
            Map.entry("Page", TypedFieldValues.numeric(page)),
            Map.entry("Page size", TypedFieldValues.numeric(pageSize))));
  }

  @Override
  public String toString() {
    return "ScenarioSearchRequestData[REDACTED]";
  }
}
