package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts SCNRSP01. */
public record ScenarioDetailResponseData(ScriptFileId scriptFileId,
    GameCode gameCode,
    String displayTitle,
    DisplayPath displayPath,
    Optional<ScriptFileId> previousFileId,
    Optional<String> previousTitle,
    Optional<ScriptFileId> nextFileId,
    Optional<String> nextTitle,
    DeliveryMode deliveryMode,
    Optional<UUID> fileId,
    Optional<RelativePath> fileRelativePath,
    long fileByteLength,
    Optional<Sha256Hex> fileSha256,
    int fileRecordLength,
    long fileRecordCount) implements PayloadData {
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
    Objects.requireNonNull(fileSha256, "fileSha256");
  }

  public static ScenarioDetailResponseData from(FieldValueSet fields) {
    return new ScenarioDetailResponseData(
        TypedFieldValues.requiredId(fields, "Script file ID", ScriptFileId::new),
        TypedFieldValues.requiredEnum(fields, "Game code", GameCode.class),
        TypedFieldValues.requiredString(fields, "Display title"),
        TypedFieldValues.requiredDisplayPath(fields, "Display path"),
        TypedFieldValues.optionalId(fields, "Previous file ID", ScriptFileId::new),
        TypedFieldValues.optionalString(fields, "Previous title"),
        TypedFieldValues.optionalId(fields, "Next file ID", ScriptFileId::new),
        TypedFieldValues.optionalString(fields, "Next title"),
        TypedFieldValues.requiredEnum(fields, "Delivery mode", DeliveryMode.class),
        TypedFieldValues.optionalUuid(fields, "File ID"),
        TypedFieldValues.optionalRelativePath(fields, "File relative path"),
        TypedFieldValues.requiredLong(fields, "File byte長"),
        TypedFieldValues.optionalSha256(fields, "File SHA-256"),
        TypedFieldValues.requiredInt(fields, "File record長"),
        TypedFieldValues.requiredLong(fields, "File record件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Script file ID", TypedFieldValues.id(scriptFileId)),
            Map.entry("Game code", TypedFieldValues.enumValue(gameCode)),
            Map.entry("Display title", TypedFieldValues.text(displayTitle)),
            Map.entry("Display path", TypedFieldValues.displayPath(displayPath)),
            Map.entry("Previous file ID", TypedFieldValues.optionalIdValue(previousFileId)),
            Map.entry("Previous title", TypedFieldValues.optionalStringValue(previousTitle)),
            Map.entry("Next file ID", TypedFieldValues.optionalIdValue(nextFileId)),
            Map.entry("Next title", TypedFieldValues.optionalStringValue(nextTitle)),
            Map.entry("Delivery mode", TypedFieldValues.enumValue(deliveryMode)),
            Map.entry("File ID", TypedFieldValues.optionalUuidValue(fileId)),
            Map.entry("File relative path", TypedFieldValues.optionalRelativePathValue(fileRelativePath)),
            Map.entry("File byte長", TypedFieldValues.numeric(fileByteLength)),
            Map.entry("File SHA-256", TypedFieldValues.optionalSha256Value(fileSha256)),
            Map.entry("File record長", TypedFieldValues.numeric(fileRecordLength)),
            Map.entry("File record件数", TypedFieldValues.numeric(fileRecordCount))));
  }

  @Override
  public String toString() {
    return "ScenarioDetailResponseData[REDACTED]";
  }
}
