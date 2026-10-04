package dev.codex.schubert.nk.web.revocation;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;

/**
 * One retained Logout retry through existing genuine fixed-wire facade after DB resources close.
 * NK-WEB-002/AUT004/UI226232234/SS314331332352/QA050/SSC171/PG-D361/RERUN005. Borrows dependencies;
 * outer owner controls HTTP drain/worker join/replies/DB/JMS/key shutdown.
 */
public final class RevocationRetryCoordinator {
  public enum Outcome {
    EMPTY,
    CONFIRMED,
    RETAINED,
    STALE
  }

  private final DataSource source;
  private final RevocationPayloadCodec codec;
  private final LogoutWireClient wire;
  private final Clock clock;
  private final PendingRevocationRepository repository = new PendingRevocationRepository();

  public RevocationRetryCoordinator(
      DataSource source, RevocationPayloadCodec codec, LogoutWireClient wire, Clock clock) {
    this.source = Objects.requireNonNull(source, "revocation data source");
    this.codec = Objects.requireNonNull(codec, "revocation codec");
    this.wire = Objects.requireNonNull(wire, "Logout wire facade");
    this.clock = Objects.requireNonNull(clock, "revocation clock");
  }

  public Outcome dispatchOne() {
    List<ClaimedRevocation> rows =
        transaction(
            connection -> {
              Instant at = now();
              return repository.claim(connection, UUID.randomUUID(), at, at.plusSeconds(10), 1);
            });
    if (rows.isEmpty()) return Outcome.EMPTY;
    ClaimedRevocation row = rows.getFirst();
    @Nullable EncryptedRevocationPayload payload = row.payload();
    if (payload == null) return failed(row, RevocationFailureCode.PAYLOAD_INVALID);
    try {
      var context = codec.decrypt(row.identity(), payload);
      if (!now().plus(JmsRequestReplyClient.MAXIMUM_WAIT).isBefore(row.leaseUntil()))
        return Outcome.STALE;
      var response =
          wire.exchange(
              new TypedPayloadValues(new LayoutId("LOGREQ01"), new LogoutRequestData(), List.of()),
              context);
      String code = response.resultCode().wireValue();
      if (code.equals("0000") || code.equals("0200")) {
        return transaction(connection -> repository.removeConfirmed(connection, row, now()))
            ? Outcome.CONFIRMED
            : Outcome.STALE;
      }
      return failed(
          row,
          code.equals("0102")
              ? RevocationFailureCode.SESSION_INVALID
              : RevocationFailureCode.API_REJECTED);
    } catch (RevocationPayloadException failure) {
      return failed(
          row,
          failure.reason() == RevocationPayloadException.Reason.KEY_UNAVAILABLE
              ? RevocationFailureCode.KEY_UNAVAILABLE
              : RevocationFailureCode.PAYLOAD_INVALID);
    } catch (ProtectedReadWireException failure) {
      return failed(
          row,
          failure.reason() == ProtectedReadWireException.Reason.INVALID_RESPONSE
              ? RevocationFailureCode.INVALID_RESPONSE
              : RevocationFailureCode.UNAVAILABLE);
    }
  }

  private Outcome failed(ClaimedRevocation row, RevocationFailureCode reason) {
    return transaction(connection -> repository.markFailure(connection, row, now(), reason))
        ? Outcome.RETAINED
        : Outcome.STALE;
  }

  private Instant now() {
    return Objects.requireNonNull(clock.instant(), "revocation clock instant")
        .truncatedTo(ChronoUnit.MICROS);
  }

  /** Result cannot escape until both commit and owned close succeeded, even on unknown outcomes. */
  private <T> T transaction(SqlWork<T> work) {
    @Nullable Connection connection = null;
    @Nullable T result = null;
    @Nullable Throwable failure = null;
    try {
      connection = source.getConnection();
      if (connection == null) throw new RevocationRetryException();
      connection.setAutoCommit(false);
      connection.setReadOnly(false);
      connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      result = Objects.requireNonNull(work.run(connection), "revocation transaction result");
      connection.commit();
    } catch (SQLException | RuntimeException | Error primary) {
      failure = primary;
    }
    if (failure != null && connection != null) {
      try {
        connection.rollback();
      } catch (SQLException | RuntimeException | Error secondary) {
        failure = combine(failure, secondary);
      }
    }
    if (connection != null) {
      try {
        connection.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        failure = combine(failure, secondary);
      }
    }
    if (failure != null) {
      preserveFatal(failure);
      throw new RevocationRetryException();
    }
    return Objects.requireNonNull(result, "revocation transaction completed result");
  }

  private static Throwable combine(@Nullable Throwable primary, Throwable secondary) {
    if (primary == null) return secondary;
    if (primary != secondary) primary.addSuppressed(secondary);
    return primary;
  }

  private static void preserveFatal(Throwable failure) {
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
    }
  }

  @FunctionalInterface
  private interface SqlWork<T> {
    T run(Connection connection) throws SQLException;
  }
}
