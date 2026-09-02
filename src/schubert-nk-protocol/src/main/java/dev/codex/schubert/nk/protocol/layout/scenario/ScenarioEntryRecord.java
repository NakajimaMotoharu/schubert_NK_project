package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SCNRSP01. */
public record ScenarioEntryRecord(EntryId entryId,
    int entrySequence,
    int lineNumber,
    EntryType entryType,
    Optional<String> speakerName,
    String bodyText,
    int audioSequence,
    Optional<AudioId> audioId,
    Optional<DisplayPath> audioDisplayPath) implements PayloadRecord {
  public ScenarioEntryRecord {
    Objects.requireNonNull(entryId, "entryId");
    TypedFieldValues.requireUnsignedRange("entrySequence", entrySequence, 6);
    TypedFieldValues.requireUnsignedRange("lineNumber", lineNumber, 8);
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(bodyText, "bodyText");
    TypedFieldValues.requireUnsignedRange("audioSequence", audioSequence, 3);
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(audioDisplayPath, "audioDisplayPath");
  }

  public static ScenarioEntryRecord from(FieldValueSet fields) {
    return new ScenarioEntryRecord(
        TypedFieldValues.requiredId(fields, "Entry ID", EntryId::new),
        TypedFieldValues.requiredInt(fields, "Entry sequence"),
        TypedFieldValues.requiredInt(fields, "Line番号"),
        TypedFieldValues.requiredEnum(fields, "Entry type", EntryType.class),
        TypedFieldValues.optionalString(fields, "Speaker名"),
        TypedFieldValues.requiredString(fields, "本文"),
        TypedFieldValues.requiredInt(fields, "Audio sequence"),
        TypedFieldValues.optionalId(fields, "Audio ID", AudioId::new),
        TypedFieldValues.optionalDisplayPath(fields, "Audio display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Entry ID", TypedFieldValues.id(entryId)),
            Map.entry("Entry sequence", TypedFieldValues.numeric(entrySequence)),
            Map.entry("Line番号", TypedFieldValues.numeric(lineNumber)),
            Map.entry("Entry type", TypedFieldValues.enumValue(entryType)),
            Map.entry("Speaker名", TypedFieldValues.optionalStringValue(speakerName)),
            Map.entry("本文", TypedFieldValues.text(bodyText)),
            Map.entry("Audio sequence", TypedFieldValues.numeric(audioSequence)),
            Map.entry("Audio ID", TypedFieldValues.optionalIdValue(audioId)),
            Map.entry("Audio display path", TypedFieldValues.optionalDisplayPathValue(audioDisplayPath))));
  }

  @Override
  public String toString() {
    return "ScenarioEntryRecord[REDACTED]";
  }
}
