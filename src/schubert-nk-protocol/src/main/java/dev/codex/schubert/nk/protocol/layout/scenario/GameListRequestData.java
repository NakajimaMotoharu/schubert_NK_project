package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;

/** Generated named wire record. Trace: SS 323; layouts GAMREQ01. */
public record GameListRequestData() implements PayloadData {

  public static GameListRequestData from(FieldValueSet fields) {
    TypedFieldValues.requireEmpty(fields);
    return new GameListRequestData();
  }

  @Override
  public FieldValueSet fields() {
    return FieldValueSet.empty();
  }
}
