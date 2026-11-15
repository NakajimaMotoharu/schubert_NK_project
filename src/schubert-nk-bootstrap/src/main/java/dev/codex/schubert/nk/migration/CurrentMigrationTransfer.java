package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Caller-authenticated Current read to declared six-COPY target path, no transaction ownership.
 * NK-MIG-001; MIG003005006/MIG-DAT005/TST; UI223242254; SS311331343 SSC415;
 * PT-MIG-CURRENTTRANSFER001..020. Returned declaration is never an actual migration receipt.
 */
@NullMarked
public final class CurrentMigrationTransfer {
  public record SourceCounts(int speakers, int files, int entries, int audio, int links) {
    public SourceCounts {
      if (speakers < 0 || files < 0 || entries < 0 || audio < 0 || links < 0) throw invalid();
    }
  }

  public MigrationMasterCopyManifest transfer(
      @Nullable Connection source,
      @Nullable Connection target,
      @Nullable CurrentMigrationAssembler assembler,
      @Nullable SourceCounts expected,
      @Nullable List<? extends @Nullable MediaAssetCopyRow> media,
      @Nullable Instant at,
      @Nullable MigrationCopyPort copy)
      throws SQLException, IOException, NoSuchAlgorithmException {
    if (source == null
        || target == null
        || assembler == null
        || expected == null
        || media == null
        || at == null
        || copy == null
        || source == target) throw invalid();
    if (target.getAutoCommit() || target.isReadOnly())
      throw new SQLException("migration Current transfer target is invalid");
    var snapshot =
        new CurrentMigrationProjection()
            .read(
                source,
                expected.speakers(),
                expected.files(),
                expected.entries(),
                expected.audio(),
                expected.links());
    var declared = assembler.assemble(snapshot, media, at);
    var mappings = assembler.mappingManifest();
    return new MigrationMasterCopyCoordinator().transfer(target, mappings, declared, copy);
  }

  @Override
  public String toString() {
    return "CurrentMigrationTransfer[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration Current transfer input is invalid");
  }
}
