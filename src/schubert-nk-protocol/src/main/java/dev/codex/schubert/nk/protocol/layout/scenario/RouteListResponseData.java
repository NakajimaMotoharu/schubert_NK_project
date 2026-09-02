package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts RTERSP01. */
public record RouteListResponseData(long totalCount) implements PayloadData {
  public RouteListResponseData {
    TypedFieldValues.requireUnsignedRange("totalCount", totalCount, 9);
  }

  public static RouteListResponseData from(FieldValueSet fields) {
    return new RouteListResponseData(
        TypedFieldValues.requiredLong(fields, "Total count"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Total count", TypedFieldValues.numeric(totalCount))));
  }

  @Override
  public String toString() {
    return "RouteListResponseData[REDACTED]";
  }
}
