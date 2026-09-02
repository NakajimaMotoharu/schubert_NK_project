package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SRCRSP01. */
public record ScenarioSearchRecord(FieldValue.Numeric entryId,
    FieldValue.Numeric scriptFileId,
    FieldValue.Text gameCode,
    Optional<FieldValue.Text> chapterTitle,
    FieldValue.Numeric lineNumber,
    FieldValue.Text entryType,
    Optional<FieldValue.Text> speakerName,
    FieldValue.Text bodyText,
    FieldValue.Flag audioPresent,
    Optional<FieldValue.Text> audioId,
    FieldValue.Text scriptDisplayPath,
    Optional<FieldValue.Text> audioDisplayPath) implements PayloadRecord {
  public ScenarioSearchRecord {
    Objects.requireNonNull(entryId, "entryId");
    Objects.requireNonNull(scriptFileId, "scriptFileId");
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(chapterTitle, "chapterTitle");
    Objects.requireNonNull(lineNumber, "lineNumber");
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(bodyText, "bodyText");
    Objects.requireNonNull(audioPresent, "audioPresent");
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(scriptDisplayPath, "scriptDisplayPath");
    Objects.requireNonNull(audioDisplayPath, "audioDisplayPath");
  }

  public static ScenarioSearchRecord from(FieldValueSet fields) {
    return new ScenarioSearchRecord(
        TypedFieldValues.requiredNumeric(fields, "Entry ID"),
        TypedFieldValues.requiredNumeric(fields, "Script file ID"),
        TypedFieldValues.requiredText(fields, "Game code"),
        TypedFieldValues.optionalText(fields, "章title"),
        TypedFieldValues.requiredNumeric(fields, "Line番号"),
        TypedFieldValues.requiredText(fields, "Entry type"),
        TypedFieldValues.optionalText(fields, "Speaker名"),
        TypedFieldValues.requiredText(fields, "本文"),
        TypedFieldValues.requiredFlag(fields, "Audio有無"),
        TypedFieldValues.optionalText(fields, "Audio ID"),
        TypedFieldValues.requiredText(fields, "Script display path"),
        TypedFieldValues.optionalText(fields, "Audio display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Entry ID", entryId),
            Map.entry("Script file ID", scriptFileId),
            Map.entry("Game code", gameCode),
            Map.entry("章title", TypedFieldValues.orUnset(chapterTitle)),
            Map.entry("Line番号", lineNumber),
            Map.entry("Entry type", entryType),
            Map.entry("Speaker名", TypedFieldValues.orUnset(speakerName)),
            Map.entry("本文", bodyText),
            Map.entry("Audio有無", audioPresent),
            Map.entry("Audio ID", TypedFieldValues.orUnset(audioId)),
            Map.entry("Script display path", scriptDisplayPath),
            Map.entry("Audio display path", TypedFieldValues.orUnset(audioDisplayPath))));
  }
}
