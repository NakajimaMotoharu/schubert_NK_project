package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts ANLREQ01. */
public record AnimationListRequestData(FieldValue.Text category) implements PayloadData {
  public AnimationListRequestData {
    Objects.requireNonNull(category, "category");
  }

  public static AnimationListRequestData from(FieldValueSet fields) {
    return new AnimationListRequestData(
        TypedFieldValues.requiredText(fields, "Category"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Category", category)));
  }
}
