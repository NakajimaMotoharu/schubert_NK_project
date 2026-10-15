package dev.codex.schubert.nk.batch.cleanup;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Borrowed native owner check, never a replacement for the caller's OS/advisory/backup ownership.
 * NK-BAT-001/OPS009/DAT009/UI251/SS341§7.3/343§6.17/SSC119; PT-BAT-MGUARD001..003.
 * Transaction-local PG timeout is independently read back, bounded by the shared parent deadline.
 */
@NullMarked
public final class MaintenanceMutationGuard {
  private final Optional<MaintenanceOwnerFrame.Guard> owner;

  /** Legacy repository tests do not establish native parent authority. */
  MaintenanceMutationGuard() {
    owner = Optional.empty();
  }

  public MaintenanceMutationGuard(MaintenanceOwnerFrame.Guard owner) {
    this.owner = Optional.of(Objects.requireNonNull(owner, "actual same-owner guard"));
  }

  public void check() {
    if (owner.isEmpty()) return;
    try {
      owner.orElseThrow().check();
    } catch (IOException known) {
      throw new CleanupStoppedException(CleanupStopReason.TIME_LIMIT);
    }
  }

  public void bind(Connection borrowed) throws SQLException {
    Objects.requireNonNull(borrowed, "borrowed transaction");
    if (owner.isEmpty()) return;
    check();
    if (borrowed.getAutoCommit()) throw new SQLDataException("maintenance transaction required");
    int seconds;
    try {
      seconds = owner.orElseThrow().queryTimeoutSeconds();
    } catch (IOException known) {
      throw new CleanupStoppedException(CleanupStopReason.TIME_LIMIT);
    }
    try (var statement =
        borrowed.prepareStatement(
            "select pg_catalog.set_config('statement_timeout', ?, true) as bound_timeout")) {
      var checked = Objects.requireNonNull(statement, "timeout statement");
      checked.setQueryTimeout(seconds);
      checked.setString(1, Integer.toString(seconds * 1000));
      try (var rows = checked.executeQuery()) {
        var row = Objects.requireNonNull(rows, "timeout result");
        if (!row.next() || !(seconds + "s").equals(row.getString("bound_timeout")) || row.next())
          throw new SQLDataException("maintenance timeout unavailable");
      }
    }
    check();
  }
}
