package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * One declared prepare/COPY/finalize path on a caller-authenticated borrowed write transaction.
 * NK-MIG-001; MIG003005006/MIG-DAT005/TST; UI223242254; SS311331343 SSC414; PT-MIG-COORD001..020.
 * Returned manifest is not a migration/commit/authorization receipt. Failure can leave staged data
 * or nontransactional sequence changes; caller decides recovery.
 */
@NullMarked
public final class MigrationMasterCopyCoordinator {
  private static final List<String> TABLES =
      List.of(
          "pg_temp.nk_mig_speakers",
          "pg_temp.nk_mig_script_files",
          "pg_temp.nk_mig_script_entries",
          "pg_temp.nk_mig_audio_files",
          "pg_temp.nk_mig_media_assets",
          "pg_temp.nk_mig_entry_audio_links");

  public MigrationMasterCopyManifest transfer(
      @Nullable Connection target,
      @Nullable CurrentMigrationMappingManifest mappings,
      @Nullable MigrationMasterCopyDataset declared,
      @Nullable MigrationCopyPort copy)
      throws SQLException, IOException, NoSuchAlgorithmException {
    if (target == null || mappings == null || declared == null || copy == null)
      throw invalidInput();
    if (target.getAutoCommit() || target.isReadOnly()) throw invalidState();
    var manifest = new MigrationMasterCopyManifest(mappings, declared);
    var rows = rows(declared);
    var publisher = new MigrationMasterTargetPublisher();
    publisher.prepare(target);
    for (int index = 0; index < TABLES.size(); index++)
      if (copy.copy(target, TABLES.get(index), rows.get(index)) != rows.get(index).size())
        throw invalidState();
    publisher.transferAndFinalize(target, declared);
    return manifest;
  }

  private static List<List<List<@Nullable String>>> rows(MigrationMasterCopyDataset declared) {
    var content = declared.content();
    return List.of(
        declared.speakers().rows().stream().map(SpeakerCopyRow::fields).toList(),
        content.scenario().files().rows(),
        content.scenario().entries().rows().stream().map(ScenarioEntryCopyRow::fields).toList(),
        content.audio().audioRows().stream().map(AudioFileCopyRow::fields).toList(),
        content.media().rows().stream().map(MediaAssetCopyRow::fields).toList(),
        content.audio().linkRows());
  }

  @Override
  public String toString() {
    return "MigrationMasterCopyCoordinator[REDACTED]";
  }

  private static IllegalArgumentException invalidInput() {
    return new IllegalArgumentException("migration copy coordinator input is invalid");
  }

  private static SQLException invalidState() {
    return new SQLException("migration copy coordinator transaction or row count is invalid");
  }
}
