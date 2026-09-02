package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SCNRSP01. */
public record ScenarioEntryRecord(long entryId,
    long entrySequence,
    long lineNumber,
    String entryType,
    Optional<String> speakerName,
    String bodyText,
    long audioSequence,
    Optional<String> audioId,
    Optional<DisplayPath> audioDisplayPath) implements PayloadRecord {
  public ScenarioEntryRecord {
    Objects.requireNonNull(entryType, "entryType");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(bodyText, "bodyText");
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(audioDisplayPath, "audioDisplayPath");
  }

  public static ScenarioEntryRecord from(FieldValueSet fields) {
    return new ScenarioEntryRecord(
        TypedFieldValues.requiredLong(fields, "Entry ID"),
        TypedFieldValues.requiredLong(fields, "Entry sequence"),
        TypedFieldValues.requiredLong(fields, "Line番号"),
        TypedFieldValues.requiredString(fields, "Entry type"),
        TypedFieldValues.optionalString(fields, "Speaker名"),
        TypedFieldValues.requiredString(fields, "本文"),
        TypedFieldValues.requiredLong(fields, "Audio sequence"),
        TypedFieldValues.optionalString(fields, "Audio ID"),
        TypedFieldValues.optionalDisplayPath(fields, "Audio display path"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Entry ID", TypedFieldValues.numeric(entryId)),
            Map.entry("Entry sequence", TypedFieldValues.numeric(entrySequence)),
            Map.entry("Line番号", TypedFieldValues.numeric(lineNumber)),
            Map.entry("Entry type", TypedFieldValues.text(entryType)),
            Map.entry("Speaker名", TypedFieldValues.optionalStringValue(speakerName)),
            Map.entry("本文", TypedFieldValues.text(bodyText)),
            Map.entry("Audio sequence", TypedFieldValues.numeric(audioSequence)),
            Map.entry("Audio ID", TypedFieldValues.optionalStringValue(audioId)),
            Map.entry("Audio display path", TypedFieldValues.optionalDisplayPathValue(audioDisplayPath))));
  }

  @Override
  public String toString() {
    return "ScenarioEntryRecord[REDACTED]";
  }
}
