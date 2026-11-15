package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Caller-admitted COPY transport on the exact borrowed target transaction, never authority.
 * NK-MIG-001; MIG003005006/MIG-DAT005/TST; UI223242254; SS311343 SSC414; PT-MIG-COORD001..020.
 * Success means this one COPY finished/closed normally and returned the actual row count. The
 * implementation owns its COPY handle/stream only, not commit/rollback/Connection.close. No driver
 * implementation or database permission is supplied by this abstract contract.
 */
@NullMarked
@FunctionalInterface
public interface MigrationCopyPort {
  long copy(Connection target, String stagingTable, List<? extends List<@Nullable String>> rows)
      throws SQLException, IOException;
}
