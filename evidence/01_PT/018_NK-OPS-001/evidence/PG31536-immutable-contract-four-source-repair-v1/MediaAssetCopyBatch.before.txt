package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared media set consistency, not real assets, Music pairing or full migration acceptance.
 * NK-MIG-001; MIG-DAT-003/MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004;
 * UI223/242/243/254; SS311/331/343 SSC359; PT-MIG-MEDIABATCH001..020.
 */
@NullMarked
public final class MediaAssetCopyBatch {
  private static final int ONE_TRANSACTION_TIMESTAMP = 1;
  private static final List<String> COLUMN_ORDER =
      List.of(
          "id",
          "logical_id",
          "media_type",
          "title",
          "category",
          "section",
          "storage_relative_path",
          "display_path",
          "file_name",
          "byte_size",
          "sha256",
          "mime_type",
          "parent_logical_id",
          "pair_key",
          "pair_role",
          "display_order",
          "created_at");
  private final List<MediaAssetCopyRow> retainedRows;
  private final List<List<@Nullable String>> retainedFields;

  public MediaAssetCopyBatch(
      @Nullable AssetMigrationManifest declaredAssets,
      @Nullable List<@Nullable MediaAssetCopyRow> input) {
    if (declaredAssets == null || input == null) throw invalid();
    var snapshot = new ArrayList<@Nullable MediaAssetCopyRow>(input);
    if (snapshot.size() != declaredAssets.entries().size()) throw invalid();
    var claims = new HashMap<String, AssetMigrationManifest.Entry>();
    for (var entry : declaredAssets.entries()) {
      if (entry.kind() != AssetMigrationManifest.Kind.VIDEO
          && entry.kind() != AssetMigrationManifest.Kind.MUSIC) throw invalid();
      claims.put(entry.currentPath(), entry);
    }
    var rows = new ArrayList<MediaAssetCopyRow>();
    var ids = new HashSet<String>();
    var logicalIds = new HashSet<String>();
    var storageKeys = new HashSet<String>();
    var timestamps = new HashSet<String>();
    for (var row : snapshot) {
      if (row == null) throw invalid();
      if (!ids.add(row.id())) throw invalid();
      if (!logicalIds.add(row.logicalId())) throw invalid();
      // Both type and path are control-free under the immutable row invariant.
      if (!storageKeys.add(row.mediaType() + '\t' + row.storageRelativePath())) throw invalid();
      AssetMigrationManifest.@Nullable Entry claim = claims.remove(row.displayPath());
      if (claim == null) throw invalid();
      if (!claim.kind().name().equals(row.mediaType())
          || !claim.targetPath().equals(row.storageRelativePath())
          || !Long.toString(claim.byteLength()).equals(row.byteSize())
          || !claim.sha256().equals(row.sha256())) throw invalid();
      timestamps.add(row.createdAt());
      rows.add(row);
    }
    if (timestamps.size() > ONE_TRANSACTION_TIMESTAMP) throw invalid();
    for (var row : rows) {
      var parent = row.parentLogicalId();
      if (parent.isPresent() && !logicalIds.contains(parent.get())) throw invalid();
    }
    retainedRows = List.copyOf(rows);
    retainedFields = rows.stream().map(MediaAssetCopyRow::fields).toList();
  }

  public List<String> columnNames() {
    return COLUMN_ORDER;
  }

  public List<MediaAssetCopyRow> rows() {
    return retainedRows;
  }

  public byte[] copyBytes(@Nullable PostgresCopyTextEncoder encoder) {
    if (encoder == null) throw invalid();
    return encoder.encodeRows(retainedFields);
  }

  public void writeTo(@Nullable PostgresCopyTextWriter writer, @Nullable OutputStream sink)
      throws IOException {
    if (writer == null || sink == null) throw invalid();
    writer.writeRows(retainedFields, sink);
  }

  @Override
  public String toString() {
    return "MediaAssetCopyBatch[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration media asset COPY batch is invalid");
  }
}
