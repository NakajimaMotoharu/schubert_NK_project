package dev.codex.schubert.nk.protocol.layout.common;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts SRCRSP01, LGSRSP01, USRRSP01, NTSRSP01, QSSRSP01. */
public record PagedResponseData(int effectivePage,
    int pageSize,
    long totalCount,
    int totalPages,
    long firstResult,
    long lastResult) implements PayloadData {
  public PagedResponseData {
    TypedFieldValues.requireUnsignedRange("effectivePage", effectivePage, 6);
    TypedFieldValues.requireUnsignedRange("pageSize", pageSize, 3);
    TypedFieldValues.requireUnsignedRange("totalCount", totalCount, 9);
    TypedFieldValues.requireUnsignedRange("totalPages", totalPages, 6);
    TypedFieldValues.requireUnsignedRange("firstResult", firstResult, 9);
    TypedFieldValues.requireUnsignedRange("lastResult", lastResult, 9);
  }

  public static PagedResponseData from(FieldValueSet fields) {
    return new PagedResponseData(
        TypedFieldValues.requiredInt(fields, "Effective page"),
        TypedFieldValues.requiredInt(fields, "Page size"),
        TypedFieldValues.requiredLong(fields, "Total count"),
        TypedFieldValues.requiredInt(fields, "Total pages"),
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
