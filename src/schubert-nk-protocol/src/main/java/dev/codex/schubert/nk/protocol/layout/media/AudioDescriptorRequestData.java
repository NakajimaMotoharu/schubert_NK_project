package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts AUDREQ01. */
public record AudioDescriptorRequestData(FieldValue.Numeric audioId,
    FieldValue.Text disposition) implements PayloadData {
  public AudioDescriptorRequestData {
    Objects.requireNonNull(audioId, "audioId");
    Objects.requireNonNull(disposition, "disposition");
  }

  public static AudioDescriptorRequestData from(FieldValueSet fields) {
    return new AudioDescriptorRequestData(
        TypedFieldValues.requiredNumeric(fields, "Audio ID"),
        TypedFieldValues.requiredText(fields, "Disposition"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Audio ID", audioId),
            Map.entry("Disposition", disposition)));
  }
}
