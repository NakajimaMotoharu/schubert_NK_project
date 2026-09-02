package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts VIDREQ01. */
public record VideoDescriptorRequestData(FieldValue.Text videoId) implements PayloadData {
  public VideoDescriptorRequestData {
    Objects.requireNonNull(videoId, "videoId");
  }

  public static VideoDescriptorRequestData from(FieldValueSet fields) {
    return new VideoDescriptorRequestData(
        TypedFieldValues.requiredText(fields, "Video ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Video ID", videoId)));
  }
}
