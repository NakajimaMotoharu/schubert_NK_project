package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts AUDREQ01. */
public record AudioDescriptorRequestData(AudioId audioId, ContentDisposition disposition)
    implements PayloadData {
  public AudioDescriptorRequestData {
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(disposition, "disposition");
  }

  public static AudioDescriptorRequestData from(FieldValueSet fields) {
    return new AudioDescriptorRequestData(
        TypedFieldValues.requiredId(fields, "Audio ID", AudioId::new),
        TypedFieldValues.requiredEnum(fields, "Disposition", ContentDisposition.class));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Audio ID", TypedFieldValues.id(audioId)),
            Map.entry("Disposition", TypedFieldValues.enumValue(disposition))));
  }

  @Override
  public String toString() {
    return "AudioDescriptorRequestData[REDACTED]";
  }
}
