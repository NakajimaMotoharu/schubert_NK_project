package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;

/** Generated named wire record. Trace: SS 323; layouts MCTREQ01. */
public record MusicCategoryRequestData() implements PayloadData {

  public static MusicCategoryRequestData from(FieldValueSet fields) {
    TypedFieldValues.requireEmpty(fields);
    return new MusicCategoryRequestData();
  }

  @Override
  public FieldValueSet fields() {
    return FieldValueSet.empty();
  }
}
