package dev.codex.schubert.nk.web.logging;

import jakarta.jms.JMSException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;

/**
 * Short Web-only DB transactions surrounding independently committed JMS sends. Trace: NK-MSG-002;
 * RD MQ-006/MQ-008; UI 213/242; SS 324 section 9/332; PT-IDEM-012; YKT-009/010. Invoke on a
 * background worker, never an HTTP request thread.
 */
public final class WebLogDispatcher {
  private final DataSource database;
  private final WebLogOutboxRepository repository;
  private final WebLogMessageSender sender;
  private final Clock clock;

  public WebLogDispatcher(
      DataSource database,
      WebLogOutboxRepository repository,
      WebLogMessageSender sender,
      Clock clock) {
    this.database = Objects.requireNonNull(database, "database");
    this.repository = Objects.requireNonNull(repository, "repository");
    this.sender = Objects.requireNonNull(sender, "sender");
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  /** Failure to mark a confirmed send propagates; the persisted lease permits safe later replay. */
  public Report dispatch(String worker, int limit) throws SQLException {
    ClaimedWebLog.requireWorker(worker);
    List<ClaimedWebLog> rows =
        transaction(connection -> repository.claim(connection, worker, clock.instant(), limit));
    int sent = 0;
    int failed = 0;
    int lost = 0;
    for (ClaimedWebLog row : rows) {
      Optional<String> failureCode = send(row);
      if (failureCode.isPresent()) {
        if (transaction(
            connection ->
                repository.markFailure(
                    connection, row, clock.instant(), failureCode.orElseThrow()))) {
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
      preserveFatal(failure);
      return Optional.of("WEB_LOG_PAYLOAD_INVALID");
    } catch (WebLogSendException failure) {
      preserveFatal(failure);
      return Optional.of("JMS_SEND_FAILURE");
    }
  }

  private <T> T transaction(SqlAction<T> action) throws SQLException {
    Connection connection = Objects.requireNonNull(database.getConnection(), "JDBC connection");
    @Nullable Throwable primary = null;
    try {
      connection.setAutoCommit(false);
      try {
        T value = action.execute(connection);
        connection.commit();
        return value;
      } catch (SQLException | RuntimeException failure) {
        primary = failure;
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException rollbackFailure) {
          if (rollbackFailure != failure) failure.addSuppressed(rollbackFailure);
        } catch (Error fatal) {
          fatal.addSuppressed(failure);
          throw fatal;
        }
        throw failure;
      }
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeAfterFailure(connection, primary);
    }
  }

  private static void closeAfterFailure(Connection connection, @Nullable Throwable primary)
      throws SQLException {
    try {
      connection.close();
    } catch (SQLException | RuntimeException | Error closing) {
      if (primary == null) throw closing;
      if (closing instanceof Error fatal && fatal != primary) {
        fatal.addSuppressed(primary);
        throw fatal;
      }
      if (closing != primary) primary.addSuppressed(closing);
    }
  }

  /** SSC323/PT-IDEM-GRAPH323001/002: transient provider graph before ordinary mark/retry. */
  static void preserveFatal(Throwable failure) {
    var pending = new ArrayDeque<Throwable>();
    Set<Throwable> seen = Collections.newSetFromMap(new IdentityHashMap<>());
    pending.add(failure);
    while (!pending.isEmpty()) {
      Throwable candidate = pending.remove();
      if (!seen.add(candidate)) continue;
      if (candidate instanceof Error fatal) throw fatal;
      Throwable cause = candidate.getCause();
      if (cause != null) pending.add(cause);
      pending.addAll(Arrays.asList(candidate.getSuppressed()));
      if (candidate instanceof JMSException jms) {
        Exception linked = jms.getLinkedException();
        if (linked != null) pending.add(linked);
      }
      if (candidate instanceof SQLException sql) {
        SQLException next = sql.getNextException();
        if (next != null) pending.add(next);
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
      if (claimed < 0
          || claimed > 100
          || sent < 0
          || failed < 0
          || leaseLost < 0
          || (long) sent + failed + leaseLost != claimed) {
        throw new IllegalArgumentException("web log dispatch counts are inconsistent");
      }
    }
  }
}
