package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts RTERSP01. */
public record RouteRecord(FieldValue.Numeric prefix,
    FieldValue.Text routeName,
    FieldValue.Numeric fileCount) implements PayloadRecord {
  public RouteRecord {
    Objects.requireNonNull(prefix, "prefix");
    Objects.requireNonNull(routeName, "routeName");
    Objects.requireNonNull(fileCount, "fileCount");
  }

  public static RouteRecord from(FieldValueSet fields) {
    return new RouteRecord(
        TypedFieldValues.requiredNumeric(fields, "Prefix"),
        TypedFieldValues.requiredText(fields, "Route名"),
        TypedFieldValues.requiredNumeric(fields, "File件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Prefix", prefix),
            Map.entry("Route名", routeName),
            Map.entry("File件数", fileCount)));
  }
}
