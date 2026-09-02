package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SRCRSP01. */
public record ScenarioSearchRecord(long entryId,
    long scriptFileId,
    String gameCode,
    Optional<String> chapterTitle,
    long lineNumber,
    String entryType,
    Optional<String> speakerName,
    String bodyText,
    boolean audioPresent,
    Optional<String> audioId,
    DisplayPath scriptDisplayPath,
    Optional<DisplayPath> audioDisplayPath) implements PayloadRecord {
  public ScenarioSearchRecord {
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(chapterTitle, "chapterTitle");
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(bodyText, "bodyText");
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(scriptDisplayPath, "scriptDisplayPath");
    Objects.requireNonNull(audioDisplayPath, "audioDisplayPath");
  }

  public static ScenarioSearchRecord from(FieldValueSet fields) {
    return new ScenarioSearchRecord(
        TypedFieldValues.requiredLong(fields, "Entry ID"),
        TypedFieldValues.requiredLong(fields, "Script file ID"),
        TypedFieldValues.requiredString(fields, "Game code"),
        TypedFieldValues.optionalString(fields, "章title"),
        TypedFieldValues.requiredLong(fields, "Line番号"),
        TypedFieldValues.requiredString(fields, "Entry type"),
        TypedFieldValues.optionalString(fields, "Speaker名"),
        TypedFieldValues.requiredString(fields, "本文"),
        TypedFieldValues.requiredBoolean(fields, "Audio有無"),
        TypedFieldValues.optionalString(fields, "Audio ID"),
        TypedFieldValues.requiredDisplayPath(fields, "Script display path"),
        TypedFieldValues.optionalDisplayPath(fields, "Audio display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Entry ID", TypedFieldValues.numeric(entryId)),
            Map.entry("Script file ID", TypedFieldValues.numeric(scriptFileId)),
            Map.entry("Game code", TypedFieldValues.text(gameCode)),
            Map.entry("章title", TypedFieldValues.optionalStringValue(chapterTitle)),
            Map.entry("Line番号", TypedFieldValues.numeric(lineNumber)),
            Map.entry("Entry type", TypedFieldValues.text(entryType)),
            Map.entry("Speaker名", TypedFieldValues.optionalStringValue(speakerName)),
            Map.entry("本文", TypedFieldValues.text(bodyText)),
            Map.entry("Audio有無", TypedFieldValues.flag(audioPresent)),
            Map.entry("Audio ID", TypedFieldValues.optionalStringValue(audioId)),
            Map.entry("Script display path", TypedFieldValues.displayPath(scriptDisplayPath)),
            Map.entry("Audio display path", TypedFieldValues.optionalDisplayPathValue(audioDisplayPath))));
  }

  @Override
  public String toString() {
    return "ScenarioSearchRecord[REDACTED]";
  }
}
