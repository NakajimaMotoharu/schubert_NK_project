package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts SCNREQ01. */
public record ScenarioDetailRequestData(FieldValue.Numeric scriptFileId) implements PayloadData {
  public ScenarioDetailRequestData {
    Objects.requireNonNull(scriptFileId, "scriptFileId");
  }

  public static ScenarioDetailRequestData from(FieldValueSet fields) {
    return new ScenarioDetailRequestData(
        TypedFieldValues.requiredNumeric(fields, "Script file ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Script file ID", scriptFileId)));
  }
}
