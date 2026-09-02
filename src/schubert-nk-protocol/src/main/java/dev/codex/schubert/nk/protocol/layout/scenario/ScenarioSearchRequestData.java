package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SRCREQ01. */
public record ScenarioSearchRequestData(Optional<FieldValue.Text> bodyKeyword,
    Optional<FieldValue.Text> gameCode,
    Optional<FieldValue.Text> speakerName,
    Optional<FieldValue.Text> chapterTitle,
    Optional<FieldValue.Text> entryType,
    Optional<FieldValue.Text> voiceCondition,
    FieldValue.Numeric page,
    FieldValue.Numeric pageSize) implements PayloadData {
  public ScenarioSearchRequestData {
    Objects.requireNonNull(bodyKeyword, "bodyKeyword");
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(chapterTitle, "chapterTitle");
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(voiceCondition, "voiceCondition");
    Objects.requireNonNull(page, "page");
    Objects.requireNonNull(pageSize, "pageSize");
  }

  public static ScenarioSearchRequestData from(FieldValueSet fields) {
    return new ScenarioSearchRequestData(
        TypedFieldValues.optionalText(fields, "本文keyword"),
        TypedFieldValues.optionalText(fields, "Game code"),
        TypedFieldValues.optionalText(fields, "Speaker名"),
        TypedFieldValues.optionalText(fields, "章title"),
        TypedFieldValues.optionalText(fields, "Entry type"),
        TypedFieldValues.optionalText(fields, "Voice条件"),
        TypedFieldValues.requiredNumeric(fields, "Page"),
        TypedFieldValues.requiredNumeric(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("本文keyword", TypedFieldValues.orUnset(bodyKeyword)),
            Map.entry("Game code", TypedFieldValues.orUnset(gameCode)),
            Map.entry("Speaker名", TypedFieldValues.orUnset(speakerName)),
            Map.entry("章title", TypedFieldValues.orUnset(chapterTitle)),
            Map.entry("Entry type", TypedFieldValues.orUnset(entryType)),
            Map.entry("Voice条件", TypedFieldValues.orUnset(voiceCondition)),
            Map.entry("Page", page),
            Map.entry("Page size", pageSize)));
  }
}
