package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCFRSP01. */
public record ScenarioFileRecord(ScriptFileId scriptFileId,
    String displayTitle,
    DisplayPath displayPath,
    int entryCount) implements PayloadRecord {
  public ScenarioFileRecord {
    Objects.requireNonNull(scriptFileId, "scriptFileId");
    Objects.requireNonNull(displayTitle, "displayTitle");
    Objects.requireNonNull(displayPath, "displayPath");
  }

  public static ScenarioFileRecord from(FieldValueSet fields) {
    return new ScenarioFileRecord(
        TypedFieldValues.requiredId(fields, "Script file ID", ScriptFileId::new),
        TypedFieldValues.requiredString(fields, "Display title"),
        TypedFieldValues.requiredDisplayPath(fields, "Display path"),
        TypedFieldValues.requiredInt(fields, "Entry件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Script file ID", TypedFieldValues.id(scriptFileId)),
            Map.entry("Display title", TypedFieldValues.text(displayTitle)),
            Map.entry("Display path", TypedFieldValues.displayPath(displayPath)),
            Map.entry("Entry件数", TypedFieldValues.numeric(entryCount))));
  }

  @Override
  public String toString() {
    return "ScenarioFileRecord[REDACTED]";
  }
}
