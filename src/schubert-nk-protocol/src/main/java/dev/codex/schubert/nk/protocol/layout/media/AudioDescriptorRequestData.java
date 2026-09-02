package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts AUDREQ01. */
public record AudioDescriptorRequestData(long audioId,
    String disposition) implements PayloadData {
  public AudioDescriptorRequestData {
    Objects.requireNonNull(disposition, "disposition");
  }

  public static AudioDescriptorRequestData from(FieldValueSet fields) {
    return new AudioDescriptorRequestData(
        TypedFieldValues.requiredLong(fields, "Audio ID"),
        TypedFieldValues.requiredString(fields, "Disposition"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Audio ID", TypedFieldValues.numeric(audioId)),
            Map.entry("Disposition", TypedFieldValues.text(disposition))));
  }

  @Override
  public String toString() {
    return "AudioDescriptorRequestData[REDACTED]";
  }
}
