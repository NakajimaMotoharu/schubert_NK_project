package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.SQLException;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * One borrowed-connection target path; caller supplies authorized COPY between prepare and
 * transfer. NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343
 * SSC373/379/381; PT-MIG-TARGET001..032. No transaction/authorization/actual migration success
 * receipt is issued.
 */
@NullMarked
public final class MigrationMasterTargetPublisher {
  public void prepare(@Nullable Connection connection) throws SQLException {
    if (connection == null) throw invalid();
    new MigrationMasterColumnVerifier().verify(connection);
    new SpeakerStagingTable().prepare(connection);
    new ScenarioStagingTables().prepare(connection);
    new AssetStagingTables().prepare(connection);
  }

  /**
   * First failure propagates unchanged; caller authenticates partial state and decides recovery.
   */
  public void transferAndFinalize(
      @Nullable Connection connection, @Nullable MigrationMasterCopyDataset declared)
      throws SQLException {
    if (connection == null || declared == null) throw invalid();
    var content = declared.content();
    new SpeakerStagingTable().transfer(connection, declared.speakers().rows().size());
    new ScenarioStagingTables()
        .transfer(
            connection,
            content.scenario().files().rows().size(),
            content.scenario().entries().rows().size());
    new AssetStagingTables()
        .transfer(
            connection,
            content.audio().audioRows().size(),
            content.media().rows().size(),
            content.audio().linkRows().size());
    new MigrationMasterReferenceVerifier().verify(connection, declared);
    new MigrationMasterContentVerifier().verify(connection, declared);
    new MigrationMasterFinalizer().finish(connection, declared);
  }

  @Override
  public String toString() {
    return "MigrationMasterTargetPublisher[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration master target input is invalid");
  }
}
