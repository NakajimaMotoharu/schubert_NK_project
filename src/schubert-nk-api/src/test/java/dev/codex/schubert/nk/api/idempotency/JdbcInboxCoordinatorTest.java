package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/** PostgreSQL 18 component PT for PT-IDEM-004..006. */
final class JdbcInboxCoordinatorTest {
  private static final String DATABASE = "inbox_pt";
  private static final String ADMIN = "pgpt_admin";
  private static final String MIGRATION = "schubert_migration";
  private static final String APP = "schubert_app";
  private static final Instant RECEIVED = Instant.parse("2026-09-05T00:00:00Z");
  private static final Instant COMPLETED = Instant.parse("2026-09-05T00:00:01Z");
  private static final Instant EXPIRES = Instant.parse("2026-09-12T00:00:00Z");
  private static final UUID MESSAGE = UUID.fromString("51000000-0000-0000-0000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("52000000-0000-0000-0000-000000000001");
  private static final UUID TOKEN = UUID.fromString("53000000-0000-0000-0000-000000000001");
  private static final Path MODULE = Path.of("").toAbsolutePath().normalize();

  private static Path pgRoot;
  private static Path clusterRoot;
  private static Path dataDirectory;
  private static int port;
  private static String jdbcUrl;

  @BeforeAll
  static void startPostgreSqlAndMigrate() throws Exception {
    pgRoot = locatePostgreSqlRoot();
    Path target = MODULE.resolve("target");
    Files.createDirectories(target);
    clusterRoot = Files.createTempDirectory(target, "inbox-postgresql-18-");
    dataDirectory = clusterRoot.resolve("data");
    port = availablePort();
    run(
        pgBinary("initdb"),
        "-D",
        dataDirectory.toString(),
        "-L",
        pgRoot.resolve("share/postgresql/18").toString(),
        "--no-locale",
        "--encoding=UTF8",
        "--auth=trust",
        "--username=" + ADMIN);
    run(
        pgBinary("pg_ctl"),
        "-D",
        dataDirectory.toString(),
        "-l",
        clusterRoot.resolve("postgresql.log").toString(),
        "-o",
        serverOptions(),
        "start");
    run(
        pgBinary("createdb"),
        "-h",
        "127.0.0.1",
        "-p",
        Integer.toString(port),
        "-U",
        ADMIN,
        DATABASE);
    jdbcUrl = "jdbc:postgresql://127.0.0.1:" + port + "/" + DATABASE;
    executeResourceAsAdmin("db/provisioning/001_roles.sql");
    Flyway.configure()
        .dataSource(jdbcUrl, MIGRATION, "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .table("flyway_schema_history")
        .locations("classpath:db/migration")
        .validateOnMigrate(true)
        .outOfOrder(false)
        .baselineOnMigrate(false)
        .cleanDisabled(true)
        .load()
        .migrate();
  }

  @AfterAll
  static void stopPostgreSql() throws Exception {
    if (dataDirectory != null && Files.exists(dataDirectory.resolve("postmaster.pid"))) {
      run(pgBinary("pg_ctl"), "-D", dataDirectory.toString(), "stop", "-m", "fast");
    }
  }

  @BeforeEach
  void resetDatabase() throws SQLException {
    try (Connection connection = appConnection();
        Statement statement = connection.createStatement()) {
      statement.executeUpdate("delete from schubert.request_inbox");
      statement.executeUpdate("delete from schubert.app_logs");
      statement.executeUpdate("delete from schubert.app_users");
      statement.executeUpdate(userInsert(101, "owner101"));
      statement.executeUpdate(userInsert(102, "owner102"));
    }
  }

  @Test
  void completionRetentionStartsAtCompletionAndReplayNeverExtendsIt() throws Exception {
    try (var keys = new FingerprintKeyRing("fp1", key((byte) 11), null, null)) {
      var coordinator = new JdbcInboxCoordinator(keys);
      for (long seconds : new long[] {86400, 604800}) {
        for (var state : InboxCompletionState.values()) {
          for (Duration processing :
              List.of(
                  Duration.ZERO,
                  Duration.ofSeconds(1),
                  Duration.ofDays(2),
                  Duration.ofNanos(1000))) {
            UUID message = UUID.randomUUID();
            boolean update = seconds == 604800;
            var request =
                new InboxRequest(
                    message,
                    message,
                    OptionalLong.of(101),
                    update ? Optional.of(UUID.randomUUID()) : Optional.empty(),
                    canonical(101, update ? "QSBREQ01" : "GAMREQ01", "001", "retention"),
                    RECEIVED,
                    RECEIVED.plusSeconds(seconds));
            Instant finished = RECEIVED.plus(processing);
            var completion =
                new InboxCompletion(
                    state,
                    InboxResultReference.none(),
                    update ? "QSBRSP01" : "GAMRSP01",
                    "001",
                    Optional.empty(),
                    finished);
            try (Connection connection = transaction()) {
              assertEquals(
                  InboxExecutionStatus.EXECUTED,
                  coordinator.execute(connection, request, ignored -> completion).status());
              assertEquals(finished.plusSeconds(seconds), storedExpiry(connection, message));
              connection.rollback();
              assertEquals(
                  InboxExecutionStatus.EXECUTED,
                  coordinator.execute(connection, request, ignored -> completion).status());
              connection.commit();
              var later =
                  new InboxRequest(
                      message,
                      message,
                      request.ownerUserId(),
                      request.operationToken(),
                      request.canonicalRequest(),
                      RECEIVED.plusSeconds(3600),
                      RECEIVED.plusSeconds(seconds + 3600));
              assertEquals(
                  InboxExecutionStatus.REPLAY,
                  coordinator
                      .execute(
                          connection,
                          later,
                          ignored -> {
                            throw new AssertionError("replay executed handler");
                          })
                      .status());
              assertEquals(finished.plusSeconds(seconds), storedExpiry(connection, message));
              if (update) {
                UUID another = UUID.randomUUID();
                var tokenReplay =
                    new InboxRequest(
                        another,
                        another,
                        request.ownerUserId(),
                        request.operationToken(),
                        request.canonicalRequest(),
                        later.receivedAt(),
                        later.expiresAt());
                assertEquals(
                    InboxExecutionStatus.REPLAY,
                    coordinator
                        .execute(
                            connection,
                            tokenReplay,
                            ignored -> {
                              throw new AssertionError("token replay executed handler");
                            })
                        .status());
                assertEquals(finished.plusSeconds(seconds), storedExpiry(connection, message));
              }
              connection.commit();
            }
          }
        }
      }
    }
  }

  private static Instant storedExpiry(Connection connection, UUID message) throws SQLException {
    try (var statement =
        connection.prepareStatement(
            "select expires_at from schubert.request_inbox where message_id=?")) {
      statement.setObject(1, message);
      try (var row = statement.executeQuery()) {
        assertTrue(row.next());
        Instant value = row.getTimestamp(1).toInstant();
        assertFalse(row.next());
        return value;
      }
    }
  }

  @Test
  void sameMessageReplaysAndEveryIdentityOrPayloadMutationIsRejected() throws Exception {
    InboxRequest original =
        tokenRequest(MESSAGE, CORRELATION, 101, TOKEN, "question", "QSBREQ01", "001");
    byte[] previousKey = key((byte) 11);
    try (FingerprintKeyRing originalKeys = new FingerprintKeyRing("fp1", previousKey, null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(originalKeys);
      try (Connection connection = transaction()) {
        InboxExecution first =
            coordinator.execute(
                connection,
                original,
                active -> {
                  insertAudit(active, "initial");
                  return snapshotCompletion();
                });
        assertEquals(InboxExecutionStatus.EXECUTED, first.status());
        connection.commit();
      }
    }

    byte[] currentKey = key((byte) 12);
    try (FingerprintKeyRing rotated =
        new FingerprintKeyRing("fp2", currentKey, "fp1", previousKey)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(rotated);
      AtomicInteger handlers = new AtomicInteger();
      try (Connection connection = transaction()) {
        InboxExecution replay =
            coordinator.execute(
                connection,
                original,
                ignored -> {
                  handlers.incrementAndGet();
                  return snapshotCompletion();
                });
        assertEquals(InboxExecutionStatus.REPLAY, replay.status());
        InboxCompletion saved = replay.completion().orElseThrow();
        assertEquals(InboxCompletionState.COMPLETED, saved.state());
        assertEquals("QBSRSP01", saved.responseLayoutId());
        assertEquals("snapshot1", saved.responseSnapshot().orElseThrow().keyVersion());
        assertArrayEquals(new byte[29], saved.responseSnapshot().orElseThrow().ciphertext());
        connection.commit();
      }
      assertEquals(0, handlers.get());
      assertEquals(1, count("schubert.request_inbox"));
      assertEquals(1, count("schubert.app_logs"));

      assertMessageReuse(
          coordinator, tokenRequest(MESSAGE, uuid(2), 101, TOKEN, "question", "QSBREQ01", "001"));
      assertMessageReuse(
          coordinator,
          tokenRequest(MESSAGE, CORRELATION, 101, TOKEN, "question", "USTREQ01", "001"));
      assertMessageReuse(
          coordinator,
          tokenRequest(MESSAGE, CORRELATION, 101, TOKEN, "question", "QSBREQ01", "002"));
      assertMessageReuse(
          coordinator,
          tokenRequest(MESSAGE, CORRELATION, 102, TOKEN, "question", "QSBREQ01", "001"));
      assertMessageReuse(
          coordinator,
          tokenRequest(MESSAGE, CORRELATION, 101, uuid(3), "question", "QSBREQ01", "001"));
      assertMessageReuse(
          coordinator,
          tokenRequest(
              MESSAGE, CORRELATION, 101, TOKEN, "sensitive-target-7f3c", "QSBREQ01", "001"));
    }

    try (FingerprintKeyRing unavailable = new FingerprintKeyRing("fp2", currentKey, null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(unavailable);
      try (Connection connection = transaction()) {
        InboxException exception =
            assertThrows(
                InboxException.class,
                () -> coordinator.execute(connection, original, ignored -> snapshotCompletion()));
        assertEquals(InboxException.Reason.FINGERPRINT_KEY_UNAVAILABLE, exception.reason());
        connection.rollback();
      }
    }
  }

  @Test
  void tokenReplaysAcrossMessageIdsRejectsChangedPayloadAndExposesProcessing() throws Exception {
    InboxRequest original =
        tokenRequest(MESSAGE, CORRELATION, 101, TOKEN, "question", "QSBREQ01", "001");
    try (FingerprintKeyRing keys = new FingerprintKeyRing("fp1", key((byte) 21), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      try (Connection connection = transaction()) {
        InboxExecution first =
            coordinator.execute(connection, original, ignored -> numericCompletion());
        assertEquals(InboxExecutionStatus.EXECUTED, first.status());
        connection.commit();
      }

      InboxRequest retry =
          tokenRequest(uuid(10), uuid(11), 101, TOKEN, "question", "QSBREQ01", "001");
      try (Connection connection = transaction()) {
        InboxExecution replay =
            coordinator.execute(
                connection,
                retry,
                ignored -> {
                  throw new AssertionError("replay must not invoke the business handler");
                });
        assertEquals(InboxExecutionStatus.REPLAY, replay.status());
        assertEquals(
            OptionalLong.of(77), replay.completion().orElseThrow().resultReference().numericId());
        connection.commit();
      }

      InboxRequest changed =
          tokenRequest(uuid(12), uuid(13), 101, TOKEN, "changed", "QSBREQ01", "001");
      try (Connection connection = transaction()) {
        InboxException exception =
            assertThrows(
                InboxException.class,
                () -> coordinator.execute(connection, changed, ignored -> numericCompletion()));
        assertEquals(InboxException.Reason.OPERATION_TOKEN_REUSE, exception.reason());
        connection.rollback();
      }

      executeApp("delete from schubert.request_inbox");
      UUID processingToken = uuid(20);
      InboxRequest processing =
          tokenRequest(uuid(21), uuid(22), 101, processingToken, "pending", "QSBREQ01", "001");
      try (Connection connection = transaction()) {
        insertProcessing(connection, processing, keys.calculate(processing.canonicalRequest()));
        connection.commit();
      }
      try (Connection connection = transaction()) {
        assertEquals(
            InboxExecutionStatus.IN_PROGRESS,
            coordinator.execute(connection, processing, ignored -> numericCompletion()).status());
        connection.commit();
      }
      InboxRequest processingRetry =
          tokenRequest(uuid(23), uuid(24), 101, processingToken, "pending", "QSBREQ01", "001");
      try (Connection connection = transaction()) {
        assertEquals(
            InboxExecutionStatus.IN_PROGRESS,
            coordinator
                .execute(connection, processingRetry, ignored -> numericCompletion())
                .status());
        connection.commit();
      }
    }
  }

  @Test
  void anonymousAndErrorRowsPersistUuidAndEmptySnapshotUnions() throws Exception {
    try (FingerprintKeyRing keys = new FingerprintKeyRing("fp1", key((byte) 31), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      InboxRequest login = anonymousRequest(MESSAGE, CORRELATION, "login");
      UUID authSession = uuid(30);
      try (Connection connection = transaction()) {
        InboxCompletion completion =
            new InboxCompletion(
                InboxCompletionState.COMPLETED,
                InboxResultReference.authSession(authSession),
                "LGNRSP01",
                "001",
                Optional.empty(),
                COMPLETED);
        assertEquals(
            InboxExecutionStatus.EXECUTED,
            coordinator.execute(connection, login, ignored -> completion).status());
        connection.commit();
      }
      try (Connection connection = transaction()) {
        InboxCompletion saved =
            coordinator
                .execute(connection, login, ignored -> snapshotCompletion())
                .completion()
                .orElseThrow();
        assertEquals(Optional.of(authSession), saved.resultReference().uuid());
        assertTrue(saved.responseSnapshot().isEmpty());
        connection.commit();
      }

      InboxRequest errorRequest =
          authenticatedRequest(uuid(31), uuid(32), 101, "QSTREQ01", "read-error");
      try (Connection connection = transaction()) {
        InboxCompletion error =
            new InboxCompletion(
                InboxCompletionState.ERROR,
                InboxResultReference.none(),
                "QSTRSP01",
                "001",
                Optional.empty(),
                COMPLETED);
        coordinator.execute(connection, errorRequest, ignored -> error);
        connection.commit();
      }
      try (Connection connection = transaction()) {
        assertEquals(
            InboxCompletionState.ERROR,
            coordinator
                .execute(connection, errorRequest, ignored -> numericCompletion())
                .completion()
                .orElseThrow()
                .state());
        connection.commit();
      }
    }
  }

  @Test
  void handlerAndCallerRollbackKeepInboxBusinessAndAuditAtomic() throws Exception {
    InboxRequest request = authenticatedRequest(MESSAGE, CORRELATION, 101, "QSTREQ01", "read");
    try (FingerprintKeyRing keys = new FingerprintKeyRing("fp1", key((byte) 41), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      try (Connection connection = transaction()) {
        SQLException failure =
            assertThrows(
                SQLException.class,
                () ->
                    coordinator.execute(
                        connection,
                        request,
                        active -> {
                          insertAudit(active, "handler-failure");
                          throw new SQLException("public test failpoint", "40001");
                        }));
        assertEquals("40001", failure.getSQLState());
        connection.rollback();
      }
      assertEquals(0, count("schubert.request_inbox"));
      assertEquals(0, count("schubert.app_logs"));

      try (Connection connection = transaction()) {
        coordinator.execute(
            connection,
            request,
            active -> {
              insertAudit(active, "caller-rollback");
              return noSnapshotCompletion();
            });
        connection.rollback();
      }
      assertEquals(0, count("schubert.request_inbox"));
      assertEquals(0, count("schubert.app_logs"));

      try (Connection connection = transaction()) {
        coordinator.execute(
            connection,
            request,
            active -> {
              insertAudit(active, "commit");
              return noSnapshotCompletion();
            });
        connection.commit();
      }
      assertEquals(1, count("schubert.request_inbox"));
      assertEquals(1, count("schubert.app_logs"));
    }
  }

  @Test
  void transactionNullCompletionTimeAndForeignKeyFailuresDenyClosed() throws Exception {
    InboxRequest request = authenticatedRequest(MESSAGE, CORRELATION, 101, "QSTREQ01", "read");
    assertThrows(NullPointerException.class, () -> new JdbcInboxCoordinator(null));
    try (FingerprintKeyRing keys = new FingerprintKeyRing("fp1", key((byte) 51), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      assertThrows(
          NullPointerException.class,
          () -> coordinator.execute(null, request, ignored -> noSnapshotCompletion()));
      try (Connection connection = appConnection()) {
        InboxException autoCommit =
            assertThrows(
                InboxException.class,
                () -> coordinator.execute(connection, request, ignored -> noSnapshotCompletion()));
        assertEquals(InboxException.Reason.TRANSACTION_REQUIRED, autoCommit.reason());
      }
      try (Connection connection = transaction()) {
        assertThrows(
            NullPointerException.class,
            () -> coordinator.execute(connection, null, ignored -> noSnapshotCompletion()));
        assertThrows(
            NullPointerException.class, () -> coordinator.execute(connection, request, null));
        connection.rollback();
      }
      try (Connection connection = transaction()) {
        assertThrows(
            NullPointerException.class,
            () -> coordinator.execute(connection, request, ignored -> null));
        connection.rollback();
      }
      try (Connection connection = transaction()) {
        InboxCompletion tooEarly =
            new InboxCompletion(
                InboxCompletionState.COMPLETED,
                InboxResultReference.none(),
                "QSTRSP01",
                "001",
                Optional.empty(),
                RECEIVED.minusSeconds(1));
        InboxException exception =
            assertThrows(
                InboxException.class,
                () -> coordinator.execute(connection, request, ignored -> tooEarly));
        assertEquals(InboxException.Reason.STATE_CORRUPT, exception.reason());
        connection.rollback();
      }

      InboxRequest missingOwner =
          authenticatedRequest(uuid(50), uuid(51), 999, "QSTREQ01", "missing-owner");
      try (Connection connection = transaction()) {
        SQLException exception =
            assertThrows(
                SQLException.class,
                () ->
                    coordinator.execute(
                        connection, missingOwner, ignored -> noSnapshotCompletion()));
        assertEquals("23503", exception.getSQLState());
        connection.rollback();
      }
    }
  }

  @Test
  void concurrentUniqueRacesAreRereadOnceAndImpossibleOutcomesDenyClosed() throws Exception {
    try (FingerprintKeyRing keys = new FingerprintKeyRing("fp1", key((byte) 61), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      InboxRequest messageRace =
          tokenRequest(MESSAGE, CORRELATION, 101, TOKEN, "race", "QSBREQ01", "001");
      try (Connection delegate = transaction()) {
        Connection intercepted =
            afterSavepoint(
                delegate,
                () -> {
                  try (Connection winner = transaction()) {
                    insertProcessing(
                        winner, messageRace, keys.calculate(messageRace.canonicalRequest()));
                    winner.commit();
                  }
                });
        assertEquals(
            InboxExecutionStatus.IN_PROGRESS,
            coordinator.execute(intercepted, messageRace, ignored -> numericCompletion()).status());
        intercepted.commit();
      }

      executeApp("delete from schubert.request_inbox");
      UUID racedToken = uuid(60);
      InboxRequest tokenRace =
          tokenRequest(uuid(61), uuid(62), 101, racedToken, "race-token", "QSBREQ01", "001");
      InboxRequest tokenWinner =
          tokenRequest(uuid(63), uuid(64), 101, racedToken, "race-token", "QSBREQ01", "001");
      try (Connection delegate = transaction()) {
        Connection intercepted =
            afterSavepoint(
                delegate,
                () -> {
                  try (Connection winner = transaction()) {
                    insertProcessing(
                        winner, tokenWinner, keys.calculate(tokenWinner.canonicalRequest()));
                    winner.commit();
                  }
                });
        assertEquals(
            InboxExecutionStatus.IN_PROGRESS,
            coordinator.execute(intercepted, tokenRace, ignored -> numericCompletion()).status());
        intercepted.commit();
      }

      executeApp("delete from schubert.request_inbox");
      InboxRequest artificialUnique =
          authenticatedRequest(uuid(65), uuid(66), 101, "QSTREQ01", "artificial-race");
      try (Connection delegate = transaction()) {
        Connection intercepted = failRequestInboxInsertAsUnique(delegate);
        SQLException exception =
            assertThrows(
                SQLException.class,
                () ->
                    coordinator.execute(
                        intercepted, artificialUnique, ignored -> noSnapshotCompletion()));
        assertEquals("23505", exception.getSQLState());
        intercepted.rollback();
      }

      InboxRequest artificialTokenUnique =
          tokenRequest(
              uuid(69), uuid(70), 101, uuid(71), "artificial-token-race", "QSBREQ01", "001");
      try (Connection delegate = transaction()) {
        Connection intercepted = failRequestInboxInsertAsUnique(delegate);
        SQLException exception =
            assertThrows(
                SQLException.class,
                () ->
                    coordinator.execute(
                        intercepted, artificialTokenUnique, ignored -> numericCompletion()));
        assertEquals("23505", exception.getSQLState());
        intercepted.rollback();
      }

      InboxRequest vanished = authenticatedRequest(uuid(67), uuid(68), 101, "QSTREQ01", "vanished");
      try (Connection connection = transaction()) {
        InboxException exception =
            assertThrows(
                InboxException.class,
                () ->
                    coordinator.execute(
                        connection,
                        vanished,
                        active -> {
                          try (PreparedStatement delete =
                              active.prepareStatement(
                                  "delete from schubert.request_inbox where message_id=?")) {
                            delete.setObject(1, vanished.messageId());
                            assertEquals(1, delete.executeUpdate());
                          }
                          return noSnapshotCompletion();
                        }));
        assertEquals(InboxException.Reason.STATE_CORRUPT, exception.reason());
        connection.rollback();
      }
    }
  }

  private static void assertMessageReuse(JdbcInboxCoordinator coordinator, InboxRequest changed)
      throws SQLException {
    try (Connection connection = transaction()) {
      InboxException exception =
          assertThrows(
              InboxException.class,
              () -> coordinator.execute(connection, changed, ignored -> snapshotCompletion()));
      assertEquals(InboxException.Reason.MESSAGE_ID_REUSE, exception.reason());
      assertFalse(exception.getMessage().contains(changed.canonicalRequest().target()));
      connection.rollback();
    }
  }

  private static InboxRequest tokenRequest(
      UUID message,
      UUID correlation,
      long owner,
      UUID token,
      String target,
      String layout,
      String version) {
    return new InboxRequest(
        message,
        correlation,
        OptionalLong.of(owner),
        Optional.of(token),
        canonical(owner, layout, version, target),
        RECEIVED,
        EXPIRES);
  }

  private static InboxRequest authenticatedRequest(
      UUID message, UUID correlation, long owner, String layout, String target) {
    return new InboxRequest(
        message,
        correlation,
        OptionalLong.of(owner),
        Optional.empty(),
        canonical(owner, layout, "001", target),
        RECEIVED,
        EXPIRES);
  }

  private static InboxRequest anonymousRequest(UUID message, UUID correlation, String target) {
    return new InboxRequest(
        message,
        correlation,
        OptionalLong.empty(),
        Optional.empty(),
        new CanonicalRequest("ANONYMOUS", "LGNREQ01", "001", target, List.of()),
        RECEIVED,
        EXPIRES);
  }

  private static CanonicalRequest canonical(
      long owner, String layout, String version, String target) {
    return new CanonicalRequest(Long.toString(owner), layout, version, target, List.of());
  }

  private static InboxCompletion snapshotCompletion() {
    return new InboxCompletion(
        InboxCompletionState.COMPLETED,
        InboxResultReference.none(),
        "QBSRSP01",
        "001",
        Optional.of(new EncryptedResponseSnapshot("snapshot1", new byte[29])),
        COMPLETED);
  }

  private static InboxCompletion numericCompletion() {
    return new InboxCompletion(
        InboxCompletionState.COMPLETED,
        InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 77),
        "QBSRSP01",
        "001",
        Optional.empty(),
        COMPLETED);
  }

  private static InboxCompletion noSnapshotCompletion() {
    return new InboxCompletion(
        InboxCompletionState.COMPLETED,
        InboxResultReference.none(),
        "QSTRSP01",
        "001",
        Optional.empty(),
        COMPLETED);
  }

  private static void insertProcessing(
      Connection connection, InboxRequest request, Fingerprint fingerprint) throws SQLException {
    String sql =
        "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,"
            + "request_version,owner_user_id,operation_token,request_fingerprint_hmac,"
            + "fingerprint_key_version,processing_state,created_at,expires_at) "
            + "values(?,?,?,?,?,?,?,?, 'PROCESSING',?,?)";
    try (PreparedStatement statement = connection.prepareStatement(sql)) {
      statement.setObject(1, request.messageId());
      statement.setObject(2, request.correlationId());
      statement.setString(3, request.canonicalRequest().layoutId());
      statement.setString(4, request.canonicalRequest().layoutVersion());
      statement.setLong(5, request.ownerUserId().orElseThrow());
      statement.setObject(6, request.operationToken().orElseThrow());
      statement.setString(7, HexFormat.of().formatHex(fingerprint.digest()));
      statement.setString(8, fingerprint.keyVersion());
      statement.setTimestamp(9, Timestamp.from(request.receivedAt()));
      statement.setTimestamp(10, Timestamp.from(request.expiresAt()));
      assertEquals(1, statement.executeUpdate());
    }
  }

  private static Connection afterSavepoint(Connection delegate, SqlAction action) {
    AtomicInteger invocations = new AtomicInteger();
    return (Connection)
        Proxy.newProxyInstance(
            JdbcInboxCoordinatorTest.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) -> {
              Object value = invoke(delegate, method, arguments);
              if (method.getName().equals("setSavepoint")
                  && method.getParameterCount() == 0
                  && invocations.getAndIncrement() == 0) {
                action.run();
              }
              return value;
            });
  }

  private static Connection failRequestInboxInsertAsUnique(Connection delegate) {
    return (Connection)
        Proxy.newProxyInstance(
            JdbcInboxCoordinatorTest.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) -> {
              Object value = invoke(delegate, method, arguments);
              if (method.getName().equals("prepareStatement")
                  && arguments != null
                  && arguments[0] instanceof String sql
                  && sql.startsWith("insert into schubert.request_inbox")) {
                PreparedStatement statement = (PreparedStatement) value;
                return Proxy.newProxyInstance(
                    JdbcInboxCoordinatorTest.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (statementProxy, statementMethod, statementArguments) -> {
                      if (statementMethod.getName().equals("executeUpdate")
                          && statementMethod.getParameterCount() == 0) {
                        throw new SQLException("public artificial unique race", "23505");
                      }
                      return invoke(statement, statementMethod, statementArguments);
                    });
              }
              return value;
            });
  }

  private static Object invoke(Object target, java.lang.reflect.Method method, Object[] arguments)
      throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException exception) {
      throw exception.getCause();
    }
  }

  @FunctionalInterface
  private interface SqlAction {
    void run() throws SQLException;
  }

  private static void insertAudit(Connection connection, String action) throws SQLException {
    try (PreparedStatement statement =
        connection.prepareStatement(
            "insert into schubert.app_logs(logged_at,service,category,level,action,message) "
                + "values(?,'API','ACTION','INFO',?,'public PT audit')")) {
      statement.setTimestamp(1, Timestamp.from(COMPLETED));
      statement.setString(2, action);
      assertEquals(1, statement.executeUpdate());
    }
  }

  private static long count(String table) throws SQLException {
    try (Connection connection = appConnection();
        Statement statement = connection.createStatement();
        ResultSet result = statement.executeQuery("select count(*) from " + table)) {
      assertTrue(result.next());
      return result.getLong(1);
    }
  }

  private static void executeApp(String sql) throws SQLException {
    try (Connection connection = appConnection();
        Statement statement = connection.createStatement()) {
      statement.execute(sql);
    }
  }

  private static Connection transaction() throws SQLException {
    Connection connection = appConnection();
    connection.setAutoCommit(false);
    return connection;
  }

  private static Connection appConnection() throws SQLException {
    return DriverManager.getConnection(jdbcUrl, APP, "");
  }

  private static String userInsert(long id, String username) {
    return "insert into schubert.app_users(id,username,username_key,password_hash,role,status,"
        + "password_changed_at,created_at,updated_at) values("
        + id
        + ",'"
        + username
        + "','key"
        + id
        + "','{pbkdf2-v1}public-test-hash','USER','ACTIVE','2026-09-05 00:00:00+00',"
        + "'2026-09-05 00:00:00+00','2026-09-05 00:00:00+00')";
  }

  private static byte[] key(byte value) {
    byte[] key = new byte[32];
    Arrays.fill(key, value);
    return key;
  }

  private static UUID uuid(long suffix) {
    return new UUID(0x6000000000000000L, suffix);
  }

  private static Path locatePostgreSqlRoot() {
    String configured = System.getenv("SCHUBERT_PG_ROOT");
    Path candidate =
        configured == null || configured.isBlank()
            ? Path.of("/home/mini/codex/project1/work/characterization-tools/root/usr")
            : Path.of(configured);
    assertTrue(
        Files.isExecutable(candidate.resolve("lib/postgresql/18/bin/postgres")),
        "PostgreSQL 18 root not found: " + candidate);
    return candidate.toAbsolutePath().normalize();
  }

  private static String pgBinary(String name) {
    return pgRoot.resolve("lib/postgresql/18/bin").resolve(name).toString();
  }

  private static String serverOptions() {
    return "-p "
        + port
        + " -h 127.0.0.1 -k /tmp -c extension_control_path="
        + pgRoot.resolve("share/postgresql/18")
        + " -c dynamic_library_path="
        + pgRoot.resolve("lib/postgresql/18/lib")
        + " -c timezone=UTC";
  }

  private static int availablePort() throws IOException {
    try (ServerSocket socket = new ServerSocket(0, 1, InetAddress.getLoopbackAddress())) {
      return socket.getLocalPort();
    }
  }

  private static void run(String... command) throws IOException, InterruptedException {
    ProcessBuilder builder = new ProcessBuilder(command);
    builder.redirectErrorStream(true);
    builder.redirectOutput(
        ProcessBuilder.Redirect.appendTo(clusterRoot.resolve("process.log").toFile()));
    builder
        .environment()
        .put(
            "LD_LIBRARY_PATH",
            pgRoot.resolve("lib/x86_64-linux-gnu") + ":" + pgRoot.resolve("lib/postgresql/18/lib"));
    Process process = builder.start();
    boolean finished = process.waitFor(Duration.ofSeconds(30));
    assertTrue(finished, "command timed out: " + command[0]);
    assertEquals(0, process.exitValue(), "command failed: " + String.join(" ", command));
  }

  private static void executeResourceAsAdmin(String resource) throws Exception {
    var url = JdbcInboxCoordinatorTest.class.getClassLoader().getResource(resource);
    assertNotNull(url, "missing resource " + resource);
    URI uri = url.toURI();
    String sql = Files.readString(Path.of(uri), StandardCharsets.UTF_8);
    try (Connection connection = DriverManager.getConnection(jdbcUrl, ADMIN, "");
        Statement statement = connection.createStatement()) {
      statement.execute(sql);
    }
  }
}
