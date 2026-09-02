package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts SCNREQ01. */
public record ScenarioDetailRequestData(long scriptFileId) implements PayloadData {
  public ScenarioDetailRequestData {
  }

  public static ScenarioDetailRequestData from(FieldValueSet fields) {
    return new ScenarioDetailRequestData(
        TypedFieldValues.requiredLong(fields, "Script file ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Script file ID", TypedFieldValues.numeric(scriptFileId))));
  }

  @Override
  public String toString() {
    return "ScenarioDetailRequestData[REDACTED]";
  }
}
