package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Pure Morning exception policy; never owns JDBC, credentials, transactions, or runtime authority.
 * NK-BAT-001/OPS009/DAT009/UI251; SS332/354 SSC341; BUG2852/YKT2359; PT-MDB-PURE341-001..012. The
 * actual Morning caller retains cleanup and primary tracking.
 */
@NullMarked
interface MorningSqlFailures {
  static void preserveCatalogFatal(Throwable failure) {
    Objects.requireNonNull(failure, "known catalog failure");
    if (failure instanceof SQLException || failure instanceof BatchRepositoryException) {
      JdbcFailureGraph.preserveFatal(failure);
    }
  }

  static boolean closeReplace(@Nullable Throwable primary, Throwable secondary) {
    Objects.requireNonNull(secondary, "cleanup failure");
    boolean known =
        primary instanceof SQLException
            || primary instanceof IOException
            || primary instanceof BatchRepositoryException;
    if (primary == null || (known && !(secondary instanceof SQLException))) return true;
    if (!known) primary.addSuppressed(new BatchRepositoryException());
    else if (primary instanceof SQLException || primary instanceof BatchRepositoryException) {
      preserveCatalogFatal(primary);
      preserveCatalogFatal(secondary);
    }
    return false;
  }
}
