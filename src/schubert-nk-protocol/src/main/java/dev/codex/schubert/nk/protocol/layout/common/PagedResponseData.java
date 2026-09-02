package dev.codex.schubert.nk.protocol.layout.common;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SRCRSP01, LGSRSP01, USRRSP01, NTSRSP01, QSSRSP01. */
public record PagedResponseData(FieldValue.Numeric effectivePage,
    FieldValue.Numeric pageSize,
    FieldValue.Numeric totalCount,
    FieldValue.Numeric totalPages,
    FieldValue.Numeric firstResult,
    FieldValue.Numeric lastResult) implements PayloadData {
  public PagedResponseData {
    Objects.requireNonNull(effectivePage, "effectivePage");
    Objects.requireNonNull(pageSize, "pageSize");
    Objects.requireNonNull(totalCount, "totalCount");
    Objects.requireNonNull(totalPages, "totalPages");
    Objects.requireNonNull(firstResult, "firstResult");
    Objects.requireNonNull(lastResult, "lastResult");
  }

  public static PagedResponseData from(FieldValueSet fields) {
    return new PagedResponseData(
        TypedFieldValues.requiredNumeric(fields, "Effective page"),
        TypedFieldValues.requiredNumeric(fields, "Page size"),
        TypedFieldValues.requiredNumeric(fields, "Total count"),
        TypedFieldValues.requiredNumeric(fields, "Total pages"),
        TypedFieldValues.requiredNumeric(fields, "First result"),
        TypedFieldValues.requiredNumeric(fields, "Last result"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Effective page", effectivePage),
            Map.entry("Page size", pageSize),
            Map.entry("Total count", totalCount),
            Map.entry("Total pages", totalPages),
            Map.entry("First result", firstResult),
            Map.entry("Last result", lastResult)));
  }
}
