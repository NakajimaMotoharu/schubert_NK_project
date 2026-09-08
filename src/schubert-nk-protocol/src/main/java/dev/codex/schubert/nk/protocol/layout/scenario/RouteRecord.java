package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts RTERSP01. */
public record RouteRecord(int prefix, String routeName, int fileCount) implements PayloadRecord {
  public RouteRecord {
    TypedFieldValues.requireUnsignedRange("prefix", prefix, 2);
    Objects.requireNonNull(routeName, "routeName");
    TypedFieldValues.requireUnsignedRange("fileCount", fileCount, 6);
  }

  public static RouteRecord from(FieldValueSet fields) {
    return new RouteRecord(
        TypedFieldValues.requiredInt(fields, "Prefix"),
        TypedFieldValues.requiredString(fields, "Route名"),
        TypedFieldValues.requiredInt(fields, "File件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Prefix", TypedFieldValues.numeric(prefix)),
            Map.entry("Route名", TypedFieldValues.text(routeName)),
            Map.entry("File件数", TypedFieldValues.numeric(fileCount))));
  }

  @Override
  public String toString() {
    return "RouteRecord[REDACTED]";
  }
}
