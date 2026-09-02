package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.SpeakerId;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SPKRSP01. */
public record SpeakerRecord(SpeakerId speakerId,
    String speakerName,
    long occurrenceCount) implements PayloadRecord {
  public SpeakerRecord {
    Objects.requireNonNull(speakerId, "speakerId");
    Objects.requireNonNull(speakerName, "speakerName");
    TypedFieldValues.requireUnsignedRange("occurrenceCount", occurrenceCount, 9);
  }

  public static SpeakerRecord from(FieldValueSet fields) {
    return new SpeakerRecord(
        TypedFieldValues.requiredId(fields, "Speaker ID", SpeakerId::new),
        TypedFieldValues.requiredString(fields, "Speaker名"),
        TypedFieldValues.requiredLong(fields, "出現件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Speaker ID", TypedFieldValues.id(speakerId)),
            Map.entry("Speaker名", TypedFieldValues.text(speakerName)),
            Map.entry("出現件数", TypedFieldValues.numeric(occurrenceCount))));
  }

  @Override
  public String toString() {
    return "SpeakerRecord[REDACTED]";
  }
}
