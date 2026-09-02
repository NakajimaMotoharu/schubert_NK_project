package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SPKRSP01. */
public record SpeakerRecord(FieldValue.Numeric speakerId,
    FieldValue.Text speakerName,
    FieldValue.Numeric occurrenceCount) implements PayloadRecord {
  public SpeakerRecord {
    Objects.requireNonNull(speakerId, "speakerId");
    Objects.requireNonNull(speakerName, "speakerName");
    Objects.requireNonNull(occurrenceCount, "occurrenceCount");
  }

  public static SpeakerRecord from(FieldValueSet fields) {
    return new SpeakerRecord(
        TypedFieldValues.requiredNumeric(fields, "Speaker ID"),
        TypedFieldValues.requiredText(fields, "Speaker名"),
        TypedFieldValues.requiredNumeric(fields, "出現件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Speaker ID", speakerId),
            Map.entry("Speaker名", speakerName),
            Map.entry("出現件数", occurrenceCount)));
  }
}
