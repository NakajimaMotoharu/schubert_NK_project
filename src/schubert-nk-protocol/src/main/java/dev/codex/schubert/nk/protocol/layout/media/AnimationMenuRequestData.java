package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;

/** Generated named wire record. Trace: SS 323; layouts ANMREQ01. */
public record AnimationMenuRequestData() implements PayloadData {

  public static AnimationMenuRequestData from(FieldValueSet fields) {
    TypedFieldValues.requireEmpty(fields);
    return new AnimationMenuRequestData();
  }

  @Override
  public FieldValueSet fields() {
    return FieldValueSet.empty();
  }

  @Override
  public String toString() {
    return "AnimationMenuRequestData[REDACTED]";
  }
}
