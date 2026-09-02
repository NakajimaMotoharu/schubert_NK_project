package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts SCNRSP01. */
public record ScenarioDetailResponseData(FieldValue.Numeric scriptFileId,
    FieldValue.Text gameCode,
    FieldValue.Text displayTitle,
    FieldValue.Text displayPath,
    Optional<FieldValue.Text> previousFileId,
    Optional<FieldValue.Text> previousTitle,
    Optional<FieldValue.Text> nextFileId,
    Optional<FieldValue.Text> nextTitle,
    FieldValue.Text deliveryMode,
    Optional<FieldValue.Text> fileId,
    Optional<FieldValue.Text> fileRelativePath,
    FieldValue.Numeric fileByteLength,
    Optional<FieldValue.Text> fileSha256,
    FieldValue.Numeric fileRecordLength,
    FieldValue.Numeric fileRecordCount) implements PayloadData {
  public ScenarioDetailResponseData {
    Objects.requireNonNull(scriptFileId, "scriptFileId");
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(displayTitle, "displayTitle");
    Objects.requireNonNull(displayPath, "displayPath");
    Objects.requireNonNull(previousFileId, "previousFileId");
    Objects.requireNonNull(previousTitle, "previousTitle");
    Objects.requireNonNull(nextFileId, "nextFileId");
    Objects.requireNonNull(nextTitle, "nextTitle");
    Objects.requireNonNull(deliveryMode, "deliveryMode");
    Objects.requireNonNull(fileId, "fileId");
    Objects.requireNonNull(fileRelativePath, "fileRelativePath");
    Objects.requireNonNull(fileByteLength, "fileByteLength");
    Objects.requireNonNull(fileSha256, "fileSha256");
    Objects.requireNonNull(fileRecordLength, "fileRecordLength");
    Objects.requireNonNull(fileRecordCount, "fileRecordCount");
  }

  public static ScenarioDetailResponseData from(FieldValueSet fields) {
    return new ScenarioDetailResponseData(
        TypedFieldValues.requiredNumeric(fields, "Script file ID"),
        TypedFieldValues.requiredText(fields, "Game code"),
        TypedFieldValues.requiredText(fields, "Display title"),
        TypedFieldValues.requiredText(fields, "Display path"),
        TypedFieldValues.optionalText(fields, "Previous file ID"),
        TypedFieldValues.optionalText(fields, "Previous title"),
        TypedFieldValues.optionalText(fields, "Next file ID"),
        TypedFieldValues.optionalText(fields, "Next title"),
        TypedFieldValues.requiredText(fields, "Delivery mode"),
        TypedFieldValues.optionalText(fields, "File ID"),
        TypedFieldValues.optionalText(fields, "File relative path"),
        TypedFieldValues.requiredNumeric(fields, "File byte長"),
        TypedFieldValues.optionalText(fields, "File SHA-256"),
        TypedFieldValues.requiredNumeric(fields, "File record長"),
        TypedFieldValues.requiredNumeric(fields, "File record件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Script file ID", scriptFileId),
            Map.entry("Game code", gameCode),
            Map.entry("Display title", displayTitle),
            Map.entry("Display path", displayPath),
            Map.entry("Previous file ID", TypedFieldValues.orUnset(previousFileId)),
            Map.entry("Previous title", TypedFieldValues.orUnset(previousTitle)),
            Map.entry("Next file ID", TypedFieldValues.orUnset(nextFileId)),
            Map.entry("Next title", TypedFieldValues.orUnset(nextTitle)),
            Map.entry("Delivery mode", deliveryMode),
            Map.entry("File ID", TypedFieldValues.orUnset(fileId)),
            Map.entry("File relative path", TypedFieldValues.orUnset(fileRelativePath)),
            Map.entry("File byte長", fileByteLength),
            Map.entry("File SHA-256", TypedFieldValues.orUnset(fileSha256)),
            Map.entry("File record長", fileRecordLength),
            Map.entry("File record件数", fileRecordCount)));
  }
}
