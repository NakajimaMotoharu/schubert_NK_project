package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFRSP01. */
public record ScenarioFileRecord(long scriptFileId,
    String displayTitle,
    DisplayPath displayPath,
    long entryCount) implements PayloadRecord {
  public ScenarioFileRecord {
    Objects.requireNonNull(displayTitle, "displayTitle");
    Objects.requireNonNull(displayPath, "displayPath");
  }

  public static ScenarioFileRecord from(FieldValueSet fields) {
    return new ScenarioFileRecord(
        TypedFieldValues.requiredLong(fields, "Script file ID"),
        TypedFieldValues.requiredString(fields, "Display title"),
        TypedFieldValues.requiredDisplayPath(fields, "Display path"),
        TypedFieldValues.requiredLong(fields, "Entry件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Script file ID", TypedFieldValues.numeric(scriptFileId)),
            Map.entry("Display title", TypedFieldValues.text(displayTitle)),
            Map.entry("Display path", TypedFieldValues.displayPath(displayPath)),
            Map.entry("Entry件数", TypedFieldValues.numeric(entryCount))));
  }

  @Override
  public String toString() {
    return "ScenarioFileRecord[REDACTED]";
  }
}
