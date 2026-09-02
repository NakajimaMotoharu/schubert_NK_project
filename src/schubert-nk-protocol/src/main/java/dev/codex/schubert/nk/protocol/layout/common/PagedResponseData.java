package dev.codex.schubert.nk.protocol.layout.common;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts SRCRSP01, LGSRSP01, USRRSP01, NTSRSP01, QSSRSP01. */
public record PagedResponseData(long effectivePage,
    long pageSize,
    long totalCount,
    long totalPages,
    long firstResult,
    long lastResult) implements PayloadData {
  public PagedResponseData {
  }

  public static PagedResponseData from(FieldValueSet fields) {
    return new PagedResponseData(
        TypedFieldValues.requiredLong(fields, "Effective page"),
        TypedFieldValues.requiredLong(fields, "Page size"),
        TypedFieldValues.requiredLong(fields, "Total count"),
        TypedFieldValues.requiredLong(fields, "Total pages"),
        TypedFieldValues.requiredLong(fields, "First result"),
        TypedFieldValues.requiredLong(fields, "Last result"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Effective page", TypedFieldValues.numeric(effectivePage)),
            Map.entry("Page size", TypedFieldValues.numeric(pageSize)),
            Map.entry("Total count", TypedFieldValues.numeric(totalCount)),
            Map.entry("Total pages", TypedFieldValues.numeric(totalPages)),
            Map.entry("First result", TypedFieldValues.numeric(firstResult)),
            Map.entry("Last result", TypedFieldValues.numeric(lastResult))));
  }

  @Override
  public String toString() {
    return "PagedResponseData[REDACTED]";
  }
}
