package dev.codex.schubert.nk.migration;

import java.sql.SQLException;

/** Rethrows the fixture's supported JDBC failures without changing their identity. */
final class MigrationFixtureFailures {
  private MigrationFixtureFailures() {}

  static void raise(Throwable failure) throws SQLException {
    switch (failure) {
      case SQLException sql -> throw sql;
      case IllegalStateException state -> throw state;
      case IllegalArgumentException argument -> throw argument;
      case Error error -> throw error;
      default -> throw new AssertionError("Unexpected migration fixture failure type", failure);
    }
  }
}
