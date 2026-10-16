package dev.codex.schubert.nk.api.maintenance;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Owns one fresh restricted connection from locked inspection through deletion and commit. No
 * callback, SAVEPOINT, connection exposure, authentication, wire emission, or key ownership.
 * Composition keeps inspector keys alive/immutable until every call returns. NK-DAT-001;
 * OPS-009/DAT-009/MQ-008; UI212/241/251; SS324 12.3/331 3.5/341/343/352;
 * QA-046/UIC-006/SSC-049/BUG-014; PG-D-122/125; SS324 12.5/331 3.6; PT-DB-INBOX-033..040/057..064.
 * Question query routes: SS324 12.8/331 3.10/PG-D-139/PT-DB-INBOX-161..168. Unsupported completed
 * rows are protected, not silently skipped.
 */
@NullMarked
public final class InboxCleanup {
  private static final java.lang.String LITERAL_001 = "001";

  private static final Set<String> REQUESTS =
      Set.of(
          "LGNREQ01",
          "LOGREQ01",
          "GAMREQ01",
          "SPKREQ01",
          "RTEREQ01",
          "SCFREQ01",
          "SRCREQ01",
          "SCNREQ01",
          "AUDREQ01",
          "ANMREQ01",
          "ANLREQ01",
          "VIDREQ01",
          "MCTREQ01",
          "MCSREQ01",
          "MTRREQ01",
          "MEDREQ01",
          "USRREQ01",
          "UDTREQ01",
          "LGSREQ01",
          "NTSREQ01",
          "NTDREQ01",
          "QSSREQ01",
          "QSDREQ01",
          "QSBREQ01",
          "NTCREQ01",
          "QDLREQ01",
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01");
  private static final Set<String> TOKEN_REQUESTS =
      Set.of(
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "NTCREQ01",
          "QDLREQ01");
  private static final Set<String> QUESTION_RESPONSES = Set.of("QSBRSP01", "NTCRSP01", "QDLRSP01");
  private static final Set<String> AUTHENTICATION_RESPONSES = Set.of("LGNRSP01", "LOGRSP01");
  private static final String NEXT =
      "select message_id,correlation_id,request_layout_id,request_version,owner_user_id,"
          + "operation_token,request_fingerprint_hmac,fingerprint_key_version,processing_state,"
          + "result_ref_type,result_ref_id,result_ref_uuid,response_layout_id,response_version,"
          + "response_body_encrypted,response_key_version,created_at,completed_at,expires_at,"
          + "pg_current_xact_id()::text as inspection_xact,"
          + "sha256(response_body_encrypted) as inspection_hash"
          + " from schubert.maintenance_next_inbox(?,?,?)";
  private static final String PROGRESS_COLUMNS =
      "select run_id,cutoff,after_message_id,inspected_count,deleted_count,protected_count,"
          + "completed_at,pg_current_xact_id()::text as inspection_xact from ";
  private final SqlConnectionProvider connections;
  private final AuthenticationInboxInspector inspector;
  private final NonAuthenticationInboxInspector nonAuthentication;
  private final Set<String> fingerprintVersions;
  private final Optional<MaintenanceOwnerFrame.Guard> parentGuard;

  public InboxCleanup(
      SqlConnectionProvider connections,
      AuthenticationInboxInspector inspector,
      NonAuthenticationInboxInspector nonAuthentication,
      Set<String> fingerprintVersions) {
    this(connections, inspector, nonAuthentication, fingerprintVersions, Optional.empty());
  }

  /** Actual Inspector assembly supplies the same verified parent owner at every mutation. */
  public InboxCleanup(
      SqlConnectionProvider connections,
      AuthenticationInboxInspector inspector,
      NonAuthenticationInboxInspector nonAuthentication,
      Set<String> fingerprintVersions,
      MaintenanceOwnerFrame.Guard parentGuard) {
    this(
        connections,
        inspector,
        nonAuthentication,
        fingerprintVersions,
        Optional.of(Objects.requireNonNull(parentGuard, "same parent guard")));
  }

  private InboxCleanup(
      SqlConnectionProvider connections,
      AuthenticationInboxInspector inspector,
      NonAuthenticationInboxInspector nonAuthentication,
      Set<String> fingerprintVersions,
      Optional<MaintenanceOwnerFrame.Guard> parentGuard) {
    this.parentGuard = parentGuard;
    this.connections = Objects.requireNonNull(connections, "connections");
    this.inspector = Objects.requireNonNull(inspector, "inspector");
    this.nonAuthentication = Objects.requireNonNull(nonAuthentication, "nonAuthentication");
    this.fingerprintVersions = Set.copyOf(fingerprintVersions);
    if (this.fingerprintVersions.isEmpty()) {
      throw new IllegalArgumentException("readable fingerprint versions are required");
    }
    for (String version : this.fingerprintVersions) {
      if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
        throw new IllegalArgumentException("fingerprint version is invalid");
      }
    }
  }

  /** PROTECTED is an unverified-row warning, never successful validation. */
  public InspectionStep inspectNext(InspectionRun run, Optional<UUID> after) {
    Objects.requireNonNull(run, "run");
    Objects.requireNonNull(after, "after");
    return owned(connection -> inspect(connection, run, after));
  }

  /** One durable step, including END; SS324 12.6/PG-D-128/PT081..088. */
  public InspectionProgress inspectStoredNext(InspectionRun run) {
    Objects.requireNonNull(run, "run");
    return owned(
        connection -> {
          LoadedProgress loaded = loadProgress(connection, run);
          if (loaded.progress.complete()) return loaded.progress;
          InspectionStep step = inspect(connection, run, loaded.progress.cursor());
          return saveProgress(connection, run, loaded, step);
        });
  }

  /** Bounded continuation; complete=false never certifies whole-run success. PT081..083/087. */
  public InspectionProgress runChunk(InspectionRun run, int maximumSteps) {
    Objects.requireNonNull(run, "run");
    if (maximumSteps < 1 || maximumSteps > 1000) {
      throw new IllegalArgumentException("inspection chunk bound is invalid");
    }
    InspectionProgress progress = inspectStoredNext(run);
    for (int step = 1; step < maximumSteps && !progress.complete(); step++) {
      progress = inspectStoredNext(run);
    }
    return progress;
  }

  @FunctionalInterface
  private interface Work<T> {
    T run(Connection connection) throws SQLException;
  }

  // Closures are created only above inside this class; no external transaction callback is exposed.
  private <T> T owned(Work<T> work) {
    try {
      checkParent(); // Before obtaining any new connection.
      try (Connection connection = requireValue(connections.open())) {
        checkParent();
        if (!connection.getAutoCommit()) {
          throw new SQLDataException("inspection requires a fresh connection");
        }
        connection.setAutoCommit(false);
        boolean committed = false;
        try {
          boundTransaction(connection);
          T result = work.run(connection);
          // An inner replay may aggregate a failed SQL read into false. Never commit an aborted TX.
          verifyTransaction(connection);
          checkParent();
          connection.commit();
          committed = true;
          checkParent(); // A late failure is NOT proof that committed mutation was rolled back.
          return result;
        } catch (SQLException | RuntimeException failure) {
          if (!committed)
            try {
              connection.rollback();
            } catch (SQLException rollbackFailure) {
              failure.addSuppressed(rollbackFailure);
            }
          throw failure;
        }
      }
    } catch (SQLException | RuntimeException failure) {
      // Do not retain bound columns/provider text/cause/suppressed close or uncertain commit data.
      throw new InboxMaintenanceException();
    }
  }

  private void checkParent() throws SQLException {
    if (parentGuard.isPresent()) {
      try {
        parentGuard.orElseThrow().check();
      } catch (IOException unavailable) {
        throw new SQLDataException("maintenance owner unavailable");
      }
    }
  }

  /** Server-side timeout bounds all nested replay/inspection SQL, not just the final DELETE. */
  private void boundTransaction(Connection connection) throws SQLException {
    if (parentGuard.isEmpty()) return;
    int seconds;
    try {
      seconds = parentGuard.orElseThrow().queryTimeoutSeconds();
    } catch (IOException unavailable) {
      throw new SQLDataException("maintenance owner unavailable");
    }
    try (var statement =
        connection.prepareStatement(
            "select pg_catalog.set_config('statement_timeout', ?, true) as bound_timeout")) {
      requireValue(statement);
      statement.setQueryTimeout(seconds);
      statement.setString(1, Integer.toString(seconds * 1000));
      try (var rows = statement.executeQuery()) {
        requireValue(rows);
        if (!rows.next() || !(seconds + "s").equals(rows.getString("bound_timeout")) || rows.next())
          throw new SQLDataException("maintenance SQL bound unavailable");
      }
    }
    checkParent();
  }

  private static LoadedProgress loadProgress(Connection connection, InspectionRun run)
      throws SQLException {
    try (var statement =
        connection.prepareStatement(
            PROGRESS_COLUMNS + "schubert.maintenance_open_inbox_inspection(?,?)")) {
      statement.setObject(1, run.id());
      statement.setObject(2, run.cutoff().atOffset(java.time.ZoneOffset.UTC));
      return readProgress(statement, run);
    }
  }

  private static InspectionProgress saveProgress(
      Connection connection, InspectionRun run, LoadedProgress loaded, InspectionStep step)
      throws SQLException {
    try (var statement =
        connection.prepareStatement(
            PROGRESS_COLUMNS + "schubert.maintenance_record_inbox_inspection(?,?,?,?,?,?,?)")) {
      statement.setObject(1, run.id());
      statement.setObject(2, run.cutoff().atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(3, loaded.progress.cursor().orElse(null));
      statement.setLong(4, loaded.progress.inspected());
      statement.setObject(5, step.cursor().orElse(null));
      statement.setString(6, step.outcome().name());
      statement.setString(7, loaded.transaction);
      return readProgress(statement, run).progress;
    }
  }

  private static LoadedProgress readProgress(PreparedStatement statement, InspectionRun run)
      throws SQLException {
    try (var row = statement.executeQuery()) {
      if (!row.next()) throw new SQLDataException("inspection progress is missing");
      if (!run.id().equals(requireValue(row.getObject("run_id", UUID.class)))
          || !run.cutoff()
              .equals(
                  requireValue(row.getObject("cutoff", java.time.OffsetDateTime.class))
                      .toInstant())) {
        throw new SQLDataException("inspection progress identity mismatch");
      }
      var progress =
          new InspectionProgress(
              run,
              Optional.ofNullable(row.getObject("after_message_id", UUID.class)),
              requireValue(row.getObject("inspected_count", Long.class)),
              requireValue(row.getObject("deleted_count", Long.class)),
              requireValue(row.getObject("protected_count", Long.class)),
              row.getObject("completed_at", java.time.OffsetDateTime.class) != null);
      String transaction = requireValue(row.getString("inspection_xact"));
      if (!transaction.matches("[0-9]{1,20}")) {
        throw new SQLDataException("inspection progress transaction is invalid");
      }
      if (row.next()) throw new SQLDataException("inspection progress count is invalid");
      return new LoadedProgress(progress, transaction);
    }
  }

  private record LoadedProgress(InspectionProgress progress, String transaction) {}

  private InspectionStep inspect(Connection connection, InspectionRun run, Optional<UUID> after)
      throws SQLException {
    InspectionStep result;
    try (var statement = connection.prepareStatement(NEXT)) {
      statement.setObject(1, run.id());
      statement.setObject(2, run.cutoff().atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(3, after.orElse(null));
      try (var row = statement.executeQuery()) {
        if (!row.next()) {
          result = new InspectionStep(InspectionStep.Outcome.END, Optional.empty());
        } else {
          UUID message = requireValue(row.getObject("message_id", UUID.class));
          Optional<Candidate> candidate = read(row, message);
          if (row.next()) throw new SQLDataException("inspection candidate count is invalid");
          var outcome = InspectionStep.Outcome.PROTECTED;
          if (candidate.isPresent()) {
            Candidate value = candidate.orElseThrow();
            boolean consistent =
                AUTHENTICATION_RESPONSES.contains(value.identity.responseLayoutId())
                    ? inspector.isConsistent(connection, value.identity, value.completion)
                    : QUESTION_RESPONSES.contains(value.identity.responseLayoutId())
                        ? nonAuthentication.isMutationConsistent(
                            connection,
                            value.identity,
                            value.completion,
                            value.operationToken.orElseThrow())
                        : nonAuthentication.isConsistent(
                            connection, value.identity, value.completion);
            if (consistent && delete(connection, run, value)) {
              outcome = InspectionStep.Outcome.DELETED;
            }
          }
          result = new InspectionStep(outcome, Optional.of(message));
        }
      }
    }
    return result;
  }

  private Optional<Candidate> read(ResultSet row, UUID message) throws SQLException {
    String request = requireValue(row.getString("request_layout_id"));
    String response = requireValue(row.getString("response_layout_id"));
    requireValue(row.getObject("correlation_id", UUID.class));
    requireValue(row.getObject("created_at", java.time.OffsetDateTime.class));
    requireValue(row.getObject("expires_at", java.time.OffsetDateTime.class));
    boolean login = request.equals("LGNREQ01");
    UUID token = row.getObject("operation_token", UUID.class);
    if (!REQUESTS.contains(request)
        || !response.equals(request.substring(0, 3) + "RSP01")
        || !requireValue(row.getString("request_version")).equals(LITERAL_001)
        || !requireValue(row.getString("response_version")).equals(LITERAL_001)
        || (token != null) != TOKEN_REQUESTS.contains(request)
        || !requireValue(row.getString("request_fingerprint_hmac")).matches("[0-9a-f]{64}")
        || !fingerprintVersions.contains(requireValue(row.getString("fingerprint_key_version")))) {
      return Optional.empty();
    }
    Long owner = row.getObject("owner_user_id", Long.class);
    if (login != (owner == null)) return Optional.empty();
    byte[] body = row.getBytes("response_body_encrypted");
    if (body == null) return Optional.empty();
    try {
      // Provider getters are outside the malformed-value catch. A JDBC failure must roll back
      // the owned inspection step, never advance the durable cursor as PROTECTED. BUG-319/YKT-162.
      Long numeric = row.getObject("result_ref_id", Long.class);
      String referenceType = requireValue(row.getString("result_ref_type"));
      UUID referenceId = row.getObject("result_ref_uuid", UUID.class);
      String completionState = requireValue(row.getString("processing_state"));
      String responseKeyVersion = requireValue(row.getString("response_key_version"));
      Instant completed =
          requireValue(row.getObject("completed_at", java.time.OffsetDateTime.class)).toInstant();
      String inspectionTransaction = requireValue(row.getString("inspection_xact"));
      byte[] inspectionHash = requireValue(row.getBytes("inspection_hash"));
      try {
        var identity =
            new ResponseSnapshotIdentity(
                message,
                response,
                LITERAL_001,
                owner == null ? OptionalLong.empty() : OptionalLong.of(owner));
        var reference =
            new InboxResultReference(
                InboxResultReferenceType.valueOf(referenceType),
                numeric == null ? OptionalLong.empty() : OptionalLong.of(numeric),
                Optional.ofNullable(referenceId));
        var saved =
            new InboxCompletion(
                InboxCompletionState.valueOf(completionState),
                reference,
                response,
                LITERAL_001,
                Optional.of(new EncryptedResponseSnapshot(responseKeyVersion, body)),
                completed);
        return Optional.of(
            new Candidate(
                identity,
                saved,
                Optional.ofNullable(token),
                inspectionTransaction,
                inspectionHash));
      } catch (IllegalArgumentException inconsistent) {
        return Optional.empty();
      }
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  private boolean delete(Connection connection, InspectionRun run, Candidate candidate)
      throws SQLException {
    checkParent();
    try (var statement =
        connection.prepareStatement(
            "select schubert.maintenance_delete_inbox(?,?,?,?,?) as deleted")) {
      statement.setObject(1, run.id());
      statement.setObject(2, run.cutoff().atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(3, candidate.identity.requestMessageId());
      statement.setString(4, candidate.transaction);
      statement.setBytes(5, candidate.hash);
      try (var row = statement.executeQuery()) {
        if (!row.next()) throw new SQLDataException("inspection deletion result is missing");
        boolean deleted = requireValue(row.getObject("deleted", Boolean.class));
        if (row.next()) throw new SQLDataException("inspection deletion result count is invalid");
        checkParent();
        return deleted;
      }
    }
  }

  private static void verifyTransaction(Connection connection) throws SQLException {
    try (var statement = connection.prepareStatement("select 1 as inspection_health");
        var row = statement.executeQuery()) {
      if (!row.next()
          || requireValue(row.getObject("inspection_health", Integer.class)) != 1
          || row.next()) {
        throw new SQLDataException("inspection transaction is not healthy");
      }
    }
  }

  private static final class Candidate {
    private final ResponseSnapshotIdentity identity;
    private final InboxCompletion completion;
    private final Optional<UUID> operationToken;
    private final String transaction;
    private final byte[] hash;

    private Candidate(
        ResponseSnapshotIdentity identity,
        InboxCompletion completion,
        Optional<UUID> operationToken,
        String transaction,
        byte[] hash) {
      this.identity = identity;
      this.completion = completion;
      this.operationToken = operationToken;
      this.transaction = transaction;
      this.hash = hash;
    }
  }
}
