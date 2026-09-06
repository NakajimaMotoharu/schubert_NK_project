package dev.codex.schubert.nk.web.logging;

import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import javax.sql.DataSource;

/**
 * Short Web-only DB transactions surrounding independently committed JMS sends.
 * Trace: NK-MSG-002; RD MQ-006/MQ-008; UI 213/242; SS 324 section 9/332;
 * PT-IDEM-012; YKT-009/010. Invoke on a background worker, never an HTTP request thread.
 */
public final class WebLogDispatcher {
  private final DataSource database;
  private final WebLogOutboxRepository repository;
  private final WebLogMessageSender sender;
  private final Clock clock;

  public WebLogDispatcher(DataSource database, WebLogOutboxRepository repository,
      WebLogMessageSender sender, Clock clock) {
    this.database = Objects.requireNonNull(database, "database");
    this.repository = Objects.requireNonNull(repository, "repository");
    this.sender = Objects.requireNonNull(sender, "sender");
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  /** Failure to mark a confirmed send propagates; the persisted lease permits safe later replay. */
  public Report dispatch(String worker, int limit) throws SQLException {
    ClaimedWebLog.requireWorker(worker);
    List<ClaimedWebLog> rows = transaction(
        connection -> repository.claim(connection, worker, clock.instant(), limit));
    int sent = 0;
    int failed = 0;
    int lost = 0;
    for (ClaimedWebLog row : rows) {
      Optional<String> failureCode = send(row);
      if (failureCode.isPresent()) {
        if (transaction(connection -> repository.markFailure(connection, row, clock.instant(), failureCode.orElseThrow()))) {
          failed++;
        } else {
          lost++;
        }
        continue;
      }
      if (transaction(connection -> repository.markSent(connection, row, clock.instant()))) {
        sent++;
      } else {
        lost++;
      }
    }
    return new Report(rows.size(), sent, failed, lost);
  }

  /** Typed catches keep payload rejection distinct from unconfirmed transport; BUG-013. */
  private Optional<String> send(ClaimedWebLog row) {
    try {
      sender.send(row);
      return Optional.empty();
    } catch (WebLogPayloadException failure) {
      return Optional.of("WEB_LOG_PAYLOAD_INVALID");
    } catch (WebLogSendException failure) {
      return Optional.of("JMS_SEND_FAILURE");
    }
  }

  private <T> T transaction(SqlAction<T> action) throws SQLException {
    try (Connection connection = Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      try {
        T value = action.execute(connection);
        connection.commit();
        return value;
      } catch (SQLException | RuntimeException failure) {
        try {
          connection.rollback();
        } catch (SQLException rollbackFailure) {
          failure.addSuppressed(rollbackFailure);
        }
        throw failure;
      }
    }
  }

  @FunctionalInterface
  private interface SqlAction<T> {
    T execute(Connection connection) throws SQLException;
  }

  /** Aggregate-only metric values: no row identity, body, credential, or exception detail. */
  public record Report(int claimed, int sent, int failed, int leaseLost) {
    public Report {
      if (claimed < 0 || claimed > 100 || sent < 0 || failed < 0 || leaseLost < 0
          || (long) sent + failed + leaseLost != claimed) {
        throw new IllegalArgumentException("web log dispatch counts are inconsistent");
      }
    }
  }
}
