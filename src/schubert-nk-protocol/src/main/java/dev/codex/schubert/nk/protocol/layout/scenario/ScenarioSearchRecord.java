package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SRCRSP01. */
public record ScenarioSearchRecord(
    EntryId entryId,
    ScriptFileId scriptFileId,
    GameCode gameCode,
    Optional<String> chapterTitle,
    int lineNumber,
    EntryType entryType,
    Optional<String> speakerName,
    String bodyText,
    boolean audioPresent,
    Optional<AudioId> audioId,
    DisplayPath scriptDisplayPath,
    Optional<DisplayPath> audioDisplayPath)
    implements PayloadRecord {
  public ScenarioSearchRecord {
    Objects.requireNonNull(entryId, "entryId");
    Objects.requireNonNull(scriptFileId, "scriptFileId");
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(chapterTitle, "chapterTitle");
    TypedFieldValues.requireUnsignedRange("lineNumber", lineNumber, 8);
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(bodyText, "bodyText");
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(scriptDisplayPath, "scriptDisplayPath");
    Objects.requireNonNull(audioDisplayPath, "audioDisplayPath");
  }

  public static ScenarioSearchRecord from(FieldValueSet fields) {
    return new ScenarioSearchRecord(
        TypedFieldValues.requiredId(fields, "Entry ID", EntryId::new),
        TypedFieldValues.requiredId(fields, "Script file ID", ScriptFileId::new),
        TypedFieldValues.requiredEnum(fields, "Game code", GameCode.class),
        TypedFieldValues.optionalString(fields, "章title"),
        TypedFieldValues.requiredInt(fields, "Line番号"),
        TypedFieldValues.requiredEnum(fields, "Entry type", EntryType.class),
        TypedFieldValues.optionalString(fields, "Speaker名"),
        TypedFieldValues.requiredString(fields, "本文"),
        TypedFieldValues.requiredBoolean(fields, "Audio有無"),
        TypedFieldValues.optionalId(fields, "Audio ID", AudioId::new),
        TypedFieldValues.requiredDisplayPath(fields, "Script display path"),
        TypedFieldValues.optionalDisplayPath(fields, "Audio display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Entry ID", TypedFieldValues.id(entryId)),
            Map.entry("Script file ID", TypedFieldValues.id(scriptFileId)),
            Map.entry("Game code", TypedFieldValues.enumValue(gameCode)),
            Map.entry("章title", TypedFieldValues.optionalStringValue(chapterTitle)),
            Map.entry("Line番号", TypedFieldValues.numeric(lineNumber)),
            Map.entry("Entry type", TypedFieldValues.enumValue(entryType)),
            Map.entry("Speaker名", TypedFieldValues.optionalStringValue(speakerName)),
            Map.entry("本文", TypedFieldValues.text(bodyText)),
            Map.entry("Audio有無", TypedFieldValues.flag(audioPresent)),
            Map.entry("Audio ID", TypedFieldValues.optionalIdValue(audioId)),
            Map.entry("Script display path", TypedFieldValues.displayPath(scriptDisplayPath)),
            Map.entry(
                "Audio display path",
                TypedFieldValues.optionalDisplayPathValue(audioDisplayPath))));
  }

  @Override
  public String toString() {
    return "ScenarioSearchRecord[REDACTED]";
  }
}
