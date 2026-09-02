package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts RTERSP01. */
public record RouteListResponseData(FieldValue.Numeric totalCount) implements PayloadData {
  public RouteListResponseData {
    Objects.requireNonNull(totalCount, "totalCount");
  }

  public static RouteListResponseData from(FieldValueSet fields) {
    return new RouteListResponseData(
        TypedFieldValues.requiredNumeric(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Total count", totalCount)));
  }
}
