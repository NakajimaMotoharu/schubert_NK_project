package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts MEDREQ01. */
public record MusicDescriptorRequestData(String trackId, ContentDisposition disposition)
    implements PayloadData {
  public MusicDescriptorRequestData {
    Objects.requireNonNull(trackId, "trackId");
    Objects.requireNonNull(disposition, "disposition");
  }

  public static MusicDescriptorRequestData from(FieldValueSet fields) {
    return new MusicDescriptorRequestData(
        TypedFieldValues.requiredString(fields, "Track ID"),
        TypedFieldValues.requiredEnum(fields, "Disposition", ContentDisposition.class));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Track ID", TypedFieldValues.text(trackId)),
            Map.entry("Disposition", TypedFieldValues.enumValue(disposition))));
  }

  @Override
  public String toString() {
    return "MusicDescriptorRequestData[REDACTED]";
  }
}
