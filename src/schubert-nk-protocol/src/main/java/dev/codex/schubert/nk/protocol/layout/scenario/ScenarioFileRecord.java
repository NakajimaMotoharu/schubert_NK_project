package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFRSP01. */
public record ScenarioFileRecord(FieldValue.Numeric scriptFileId,
    FieldValue.Text displayTitle,
    FieldValue.Text displayPath,
    FieldValue.Numeric entryCount) implements PayloadRecord {
  public ScenarioFileRecord {
    Objects.requireNonNull(scriptFileId, "scriptFileId");
    Objects.requireNonNull(displayTitle, "displayTitle");
    Objects.requireNonNull(displayPath, "displayPath");
    Objects.requireNonNull(entryCount, "entryCount");
  }

  public static ScenarioFileRecord from(FieldValueSet fields) {
    return new ScenarioFileRecord(
        TypedFieldValues.requiredNumeric(fields, "Script file ID"),
        TypedFieldValues.requiredText(fields, "Display title"),
        TypedFieldValues.requiredText(fields, "Display path"),
        TypedFieldValues.requiredNumeric(fields, "Entry件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Script file ID", scriptFileId),
            Map.entry("Display title", displayTitle),
            Map.entry("Display path", displayPath),
            Map.entry("Entry件数", entryCount)));
  }
}
