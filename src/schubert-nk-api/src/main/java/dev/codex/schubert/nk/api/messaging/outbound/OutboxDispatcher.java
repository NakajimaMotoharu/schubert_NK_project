package dev.codex.schubert.nk.api.messaging.outbound;

import jakarta.jms.JMSException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/**
 * Coordinates short DB claim/mark transactions around a separate transacted JMS send.
 *
 * <p>Trace: NK-MSG-002; RD ASY-001/MQ-006/MQ-008; UI 213/241; SS 324 section 8.
 */
public final class OutboxDispatcher {
  private final SqlConnectionProvider connectionProvider;
  private final TransactedJmsContextProvider contextProvider;
  private final JdbcOutboxRepository repository;
  private final OutboxJmsSender sender;
  private final Clock clock;

  public OutboxDispatcher(
      SqlConnectionProvider connectionProvider,
      TransactedJmsContextProvider contextProvider,
      JdbcOutboxRepository repository,
      OutboxJmsSender sender,
      Clock clock) {
    this.connectionProvider = Objects.requireNonNull(connectionProvider, "connectionProvider");
    this.contextProvider = Objects.requireNonNull(contextProvider, "contextProvider");
    this.repository = Objects.requireNonNull(repository, "repository");
    this.sender = Objects.requireNonNull(sender, "sender");
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  /** Samples claim and each send-result time separately; trace: PT-IDEM-010, BUG-011. */
  public OutboxDispatchReport dispatch(String worker, int limit) throws SQLException {
    OutboxEntry.requireLeaseOwner(worker);
    List<OutboxEntry> entries = claim(worker, clock.instant(), limit);
    int sent = 0;
    int failed = 0;
    int leaseLost = 0;
    for (OutboxEntry entry : entries) {
      try {
        sender.send(contextProvider, entry);
      } catch (OutboxSendException | RuntimeException exception) {
        preserveFatal(exception);
        if (markFailure(entry, clock.instant(), failureCode(exception))) {
          failed++;
        } else {
          leaseLost++;
        }
        continue;
      }
      if (markSent(entry, clock.instant())) {
        sent++;
      } else {
        leaseLost++;
      }
    }
    return new OutboxDispatchReport(entries.size(), sent, failed, leaseLost);
  }

  private List<OutboxEntry> claim(String worker, Instant now, int limit) throws SQLException {
    try (Connection connection = transaction()) {
      try {
        List<OutboxEntry> claimed = repository.claim(connection, worker, now, limit);
        connection.commit();
        return claimed;
      } catch (SQLException | RuntimeException exception) {
        rollback(connection, exception);
        throw exception;
      }
    }
  }

  private boolean markSent(OutboxEntry entry, Instant now) throws SQLException {
    try (Connection connection = transaction()) {
      try {
        boolean marked = repository.markSent(connection, entry, now);
        connection.commit();
        return marked;
      } catch (SQLException | RuntimeException exception) {
        rollback(connection, exception);
        throw exception;
      }
    }
  }

  private boolean markFailure(OutboxEntry entry, Instant now, String code) throws SQLException {
    try (Connection connection = transaction()) {
      try {
        boolean marked =
            repository.markFailure(connection, entry, now, code, "outbox send was not confirmed");
        connection.commit();
        return marked;
      } catch (SQLException | RuntimeException exception) {
        rollback(connection, exception);
        throw exception;
      }
    }
  }

  private Connection transaction() throws SQLException {
    Connection connection = Objects.requireNonNull(connectionProvider.open(), "JDBC connection");
    try {
      connection.setAutoCommit(false);
      return connection;
    } catch (SQLException | RuntimeException | Error exception) {
      closeAfterSetupFailure(connection, exception);
      throw exception;
    }
  }

  static void closeAfterSetupFailure(Connection connection, Throwable failure) {
    try {
      connection.close();
    } catch (SQLException | RuntimeException | Error closeFailure) {
      retainFailure(failure, closeFailure);
    }
  }

  private static String failureCode(Throwable exception) {
    return exception instanceof OutboxIntegrityException ? "OUTBOX_INTEGRITY" : "JMS_SEND_FAILURE";
  }

  /** SSC322/PT-IDEM-GRAPH322001/002: inspect transient edges before ordinary retry/mark. */
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

  private static void rollback(Connection connection, Throwable failure) {
    try {
      connection.rollback();
    } catch (SQLException | RuntimeException | Error rollbackFailure) {
      retainFailure(failure, rollbackFailure);
    }
  }

  // SSC320/PT-IDEM-FAIL320002..004: a failed cleanup never authorizes a new transaction.
  private static void retainFailure(Throwable primary, Throwable secondary) {
    if (secondary instanceof Error fatal && !(primary instanceof Error)) {
      fatal.addSuppressed(primary); // Fatal/nonfatal objects cannot be identical.
      throw fatal;
    }
    if (primary != secondary) primary.addSuppressed(secondary);
  }
}
