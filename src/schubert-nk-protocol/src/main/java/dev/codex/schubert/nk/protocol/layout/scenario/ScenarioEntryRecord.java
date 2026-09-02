package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SCNRSP01. */
public record ScenarioEntryRecord(FieldValue.Numeric entryId,
    FieldValue.Numeric entrySequence,
    FieldValue.Numeric lineNumber,
    FieldValue.Text entryType,
    Optional<FieldValue.Text> speakerName,
    FieldValue.Text bodyText,
    FieldValue.Numeric audioSequence,
    Optional<FieldValue.Text> audioId,
    Optional<FieldValue.Text> audioDisplayPath) implements PayloadRecord {
  public ScenarioEntryRecord {
    Objects.requireNonNull(entryId, "entryId");
    Objects.requireNonNull(entrySequence, "entrySequence");
    Objects.requireNonNull(lineNumber, "lineNumber");
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(bodyText, "bodyText");
    Objects.requireNonNull(audioSequence, "audioSequence");
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(audioDisplayPath, "audioDisplayPath");
  }

  public static ScenarioEntryRecord from(FieldValueSet fields) {
    return new ScenarioEntryRecord(
        TypedFieldValues.requiredNumeric(fields, "Entry ID"),
        TypedFieldValues.requiredNumeric(fields, "Entry sequence"),
        TypedFieldValues.requiredNumeric(fields, "Line番号"),
        TypedFieldValues.requiredText(fields, "Entry type"),
        TypedFieldValues.optionalText(fields, "Speaker名"),
        TypedFieldValues.requiredText(fields, "本文"),
        TypedFieldValues.requiredNumeric(fields, "Audio sequence"),
        TypedFieldValues.optionalText(fields, "Audio ID"),
        TypedFieldValues.optionalText(fields, "Audio display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Entry ID", entryId),
            Map.entry("Entry sequence", entrySequence),
            Map.entry("Line番号", lineNumber),
            Map.entry("Entry type", entryType),
            Map.entry("Speaker名", TypedFieldValues.orUnset(speakerName)),
            Map.entry("本文", bodyText),
            Map.entry("Audio sequence", audioSequence),
            Map.entry("Audio ID", TypedFieldValues.orUnset(audioId)),
            Map.entry("Audio display path", TypedFieldValues.orUnset(audioDisplayPath))));
  }
}
