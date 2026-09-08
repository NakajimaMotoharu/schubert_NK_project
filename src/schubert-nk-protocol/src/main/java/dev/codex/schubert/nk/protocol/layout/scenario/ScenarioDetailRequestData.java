package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCNREQ01. */
public record ScenarioDetailRequestData(ScriptFileId scriptFileId) implements PayloadData {
  public ScenarioDetailRequestData {
    Objects.requireNonNull(scriptFileId, "scriptFileId");
  }

  public static ScenarioDetailRequestData from(FieldValueSet fields) {
    return new ScenarioDetailRequestData(
        TypedFieldValues.requiredId(fields, "Script file ID", ScriptFileId::new));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(Map.entry("Script file ID", TypedFieldValues.id(scriptFileId))));
  }

  @Override
  public String toString() {
    return "ScenarioDetailRequestData[REDACTED]";
  }
}
