package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
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
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/** PostgreSQL 18 component PT for PT-IDEM-004..006. */
final class JdbcInboxCoordinatorTest {
  private static final String FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC =
      "delete from schubert.request_inbox";
  private static final String FIXTURE_FP1_54E2C4E0 = "fp1";
  private static final String FIXTURE_QSBREQ01_F9A27626 = "QSBREQ01";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_QUESTION_6D6CA52E = "question";
  private static final String FIXTURE_FP2_0F8E0697 = "fp2";
  private static final String FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA = "schubert.request_inbox";
  private static final String FIXTURE_SCHUBERT_APP_LOGS_D6BE6409 = "schubert.app_logs";
  private static final String FIXTURE_QSTREQ01_D01029E2 = "QSTREQ01";
  private static final String FIXTURE_COMPLETED_BA0AE16A = "COMPLETED";
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
      statement.executeUpdate(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      statement.executeUpdate("delete from schubert.app_logs");
      statement.executeUpdate("delete from schubert.app_users");
      statement.executeUpdate(userInsert(101, "owner101"));
      statement.executeUpdate(userInsert(102, "owner102"));
    }
  }

  @Test
  void completionRetentionStartsAtCompletionAndReplayNeverExtendsIt() throws Exception {
    try (var keys = new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 11), null, null)) {
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
                    canonical(
                        101,
                        update ? FIXTURE_QSBREQ01_F9A27626 : "GAMREQ01",
                        FIXTURE_001_A3FEAA64,
                        "retention"),
                    RECEIVED,
                    RECEIVED.plusSeconds(seconds));
            Instant finished = RECEIVED.plus(processing);
            var completion =
                new InboxCompletion(
                    state,
                    InboxResultReference.none(),
                    update ? "QSBRSP01" : "GAMRSP01",
                    FIXTURE_001_A3FEAA64,
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
        Instant value = row.getObject(1, java.time.OffsetDateTime.class).toInstant();
        assertFalse(row.next());
        return value;
      }
    }
  }

  @Test
  void sameMessageReplaysAndEveryIdentityOrPayloadMutationIsRejected() throws Exception {
    InboxRequest original =
        tokenRequest(
            MESSAGE,
            CORRELATION,
            101,
            TOKEN,
            FIXTURE_QUESTION_6D6CA52E,
            FIXTURE_QSBREQ01_F9A27626,
            FIXTURE_001_A3FEAA64);
    byte[] previousKey = key((byte) 11);
    try (FingerprintKeyRing originalKeys =
        new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, previousKey, null, null)) {
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
        new FingerprintKeyRing(
            FIXTURE_FP2_0F8E0697, currentKey, FIXTURE_FP1_54E2C4E0, previousKey)) {
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
      assertEquals(1, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
      assertEquals(1, count(FIXTURE_SCHUBERT_APP_LOGS_D6BE6409));

      assertMessageReuse(
          coordinator,
          tokenRequest(
              MESSAGE,
              uuid(2),
              101,
              TOKEN,
              FIXTURE_QUESTION_6D6CA52E,
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64));
      assertMessageReuse(
          coordinator,
          tokenRequest(
              MESSAGE,
              CORRELATION,
              101,
              TOKEN,
              FIXTURE_QUESTION_6D6CA52E,
              "USTREQ01",
              FIXTURE_001_A3FEAA64));
      assertMessageReuse(
          coordinator,
          tokenRequest(
              MESSAGE,
              CORRELATION,
              101,
              TOKEN,
              FIXTURE_QUESTION_6D6CA52E,
              FIXTURE_QSBREQ01_F9A27626,
              "002"));
      assertMessageReuse(
          coordinator,
          tokenRequest(
              MESSAGE,
              CORRELATION,
              102,
              TOKEN,
              FIXTURE_QUESTION_6D6CA52E,
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64));
      assertMessageReuse(
          coordinator,
          tokenRequest(
              MESSAGE,
              CORRELATION,
              101,
              uuid(3),
              FIXTURE_QUESTION_6D6CA52E,
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64));
      assertMessageReuse(
          coordinator,
          tokenRequest(
              MESSAGE,
              CORRELATION,
              101,
              TOKEN,
              "sensitive-target-7f3c",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64));
    }

    try (FingerprintKeyRing unavailable =
        new FingerprintKeyRing(FIXTURE_FP2_0F8E0697, currentKey, null, null)) {
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
        tokenRequest(
            MESSAGE,
            CORRELATION,
            101,
            TOKEN,
            FIXTURE_QUESTION_6D6CA52E,
            FIXTURE_QSBREQ01_F9A27626,
            FIXTURE_001_A3FEAA64);
    try (FingerprintKeyRing keys =
        new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 21), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      try (Connection connection = transaction()) {
        InboxExecution first =
            coordinator.execute(connection, original, ignored -> numericCompletion());
        assertEquals(InboxExecutionStatus.EXECUTED, first.status());
        connection.commit();
      }

      InboxRequest retry =
          tokenRequest(
              uuid(10),
              uuid(11),
              101,
              TOKEN,
              FIXTURE_QUESTION_6D6CA52E,
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
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
          tokenRequest(
              uuid(12),
              uuid(13),
              101,
              TOKEN,
              "changed",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
      try (Connection connection = transaction()) {
        InboxException exception =
            assertThrows(
                InboxException.class,
                () -> coordinator.execute(connection, changed, ignored -> numericCompletion()));
        assertEquals(InboxException.Reason.OPERATION_TOKEN_REUSE, exception.reason());
        connection.rollback();
      }

      executeApp(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      UUID processingToken = uuid(20);
      InboxRequest processing =
          tokenRequest(
              uuid(21),
              uuid(22),
              101,
              processingToken,
              "pending",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
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
          tokenRequest(
              uuid(23),
              uuid(24),
              101,
              processingToken,
              "pending",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
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
    try (FingerprintKeyRing keys =
        new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 31), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      InboxRequest login = anonymousRequest(MESSAGE, CORRELATION, "login");
      UUID authSession = uuid(30);
      try (Connection connection = transaction()) {
        InboxCompletion completion =
            new InboxCompletion(
                InboxCompletionState.COMPLETED,
                InboxResultReference.authSession(authSession),
                "LGNRSP01",
                FIXTURE_001_A3FEAA64,
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
          authenticatedRequest(uuid(31), uuid(32), 101, FIXTURE_QSTREQ01_D01029E2, "read-error");
      try (Connection connection = transaction()) {
        InboxCompletion error =
            new InboxCompletion(
                InboxCompletionState.ERROR,
                InboxResultReference.none(),
                "QSTRSP01",
                FIXTURE_001_A3FEAA64,
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
    InboxRequest request =
        authenticatedRequest(MESSAGE, CORRELATION, 101, FIXTURE_QSTREQ01_D01029E2, "read");
    try (FingerprintKeyRing keys =
        new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 41), null, null)) {
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
      assertEquals(0, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
      assertEquals(0, count(FIXTURE_SCHUBERT_APP_LOGS_D6BE6409));

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
      assertEquals(0, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
      assertEquals(0, count(FIXTURE_SCHUBERT_APP_LOGS_D6BE6409));

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
      assertEquals(1, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
      assertEquals(1, count(FIXTURE_SCHUBERT_APP_LOGS_D6BE6409));
    }
  }

  @Test
  void transactionNullCompletionTimeAndForeignKeyFailuresDenyClosed() throws Exception {
    InboxRequest request =
        authenticatedRequest(MESSAGE, CORRELATION, 101, FIXTURE_QSTREQ01_D01029E2, "read");
    assertThrows(NullPointerException.class, () -> new JdbcInboxCoordinator(null));
    try (FingerprintKeyRing keys =
        new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 51), null, null)) {
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
                FIXTURE_001_A3FEAA64,
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
          authenticatedRequest(uuid(50), uuid(51), 999, FIXTURE_QSTREQ01_D01029E2, "missing-owner");
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
    try (FingerprintKeyRing keys =
        new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 61), null, null)) {
      JdbcInboxCoordinator coordinator = new JdbcInboxCoordinator(keys);
      InboxRequest messageRace =
          tokenRequest(
              MESSAGE,
              CORRELATION,
              101,
              TOKEN,
              "race",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
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

      executeApp(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      UUID racedToken = uuid(60);
      InboxRequest tokenRace =
          tokenRequest(
              uuid(61),
              uuid(62),
              101,
              racedToken,
              "race-token",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
      InboxRequest tokenWinner =
          tokenRequest(
              uuid(63),
              uuid(64),
              101,
              racedToken,
              "race-token",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
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

      executeApp(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      InboxRequest artificialUnique =
          authenticatedRequest(
              uuid(65), uuid(66), 101, FIXTURE_QSTREQ01_D01029E2, "artificial-race");
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
              uuid(69),
              uuid(70),
              101,
              uuid(71),
              "artificial-token-race",
              FIXTURE_QSBREQ01_F9A27626,
              FIXTURE_001_A3FEAA64);
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

      InboxRequest vanished =
          authenticatedRequest(uuid(67), uuid(68), 101, FIXTURE_QSTREQ01_D01029E2, "vanished");
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

  @Test
  void readOnlyMessageLookupPreservesAbsenceCompletionErrorAndProcessing() throws Exception {
    var request =
        tokenRequest(
            MESSAGE,
            CORRELATION,
            101,
            TOKEN,
            FIXTURE_QUESTION_6D6CA52E,
            FIXTURE_QSBREQ01_F9A27626,
            FIXTURE_001_A3FEAA64);
    try (var keys = new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 11), null, null)) {
      var coordinator = new JdbcInboxCoordinator(keys);
      try (Connection connection = transaction()) {
        connection.setReadOnly(true);
        assertTrue(coordinator.inspectMessage(connection, request).isEmpty());
        assertEquals(0, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
        assertFalse(connection.getAutoCommit());
        assertFalse(connection.isClosed());
        try (var statement = connection.createStatement();
            var row = statement.executeQuery("show transaction_read_only")) {
          assertTrue(row.next());
          assertEquals("on", row.getString(1));
        }
        connection.commit();
      }
      for (String state : List.of(FIXTURE_COMPLETED_BA0AE16A, "ERROR", "PROCESSING")) {
        executeApp(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
        insertReadOnlyFixture(request, state);
        try (Connection connection = transaction()) {
          connection.setReadOnly(true);
          InboxExecution result = coordinator.inspectMessage(connection, request).orElseThrow();
          if (state.equals("PROCESSING")) {
            assertEquals(InboxExecutionStatus.IN_PROGRESS, result.status());
            assertTrue(result.completion().isEmpty());
          } else {
            assertEquals(InboxExecutionStatus.REPLAY, result.status());
            InboxCompletion saved = result.completion().orElseThrow();
            assertEquals(state, saved.state().name());
            assertEquals(InboxResultReferenceType.NONE, saved.resultReference().type());
            assertTrue(saved.resultReference().numericId().isEmpty());
            assertTrue(saved.resultReference().uuid().isEmpty());
            assertEquals("QSBRSP01", saved.responseLayoutId());
            assertEquals(FIXTURE_001_A3FEAA64, saved.responseVersion());
            assertEquals(COMPLETED, saved.completedAt());
            assertEquals("snapshot1", saved.responseSnapshot().orElseThrow().keyVersion());
            assertArrayEquals(new byte[29], saved.responseSnapshot().orElseThrow().ciphertext());
          }
          var another =
              tokenRequest(
                  uuid(400),
                  CORRELATION,
                  101,
                  TOKEN,
                  FIXTURE_QUESTION_6D6CA52E,
                  FIXTURE_QSBREQ01_F9A27626,
                  FIXTURE_001_A3FEAA64);
          assertTrue(coordinator.inspectMessage(connection, another).isEmpty());
          assertEquals(EXPIRES, storedExpiry(connection, MESSAGE));
          connection.commit();
        }
        assertEquals(1, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
        assertEquals(0, count(FIXTURE_SCHUBERT_APP_LOGS_D6BE6409));
      }
      executeApp(FIXTURE_DELETE_FROM_SCHUBERT_REQUEST_INBOX_D18913CC);
      var reference =
          authenticatedRequest(MESSAGE, CORRELATION, 101, "GAMREQ01", FIXTURE_QUESTION_6D6CA52E);
      insertReadOnlyFixture(reference, FIXTURE_COMPLETED_BA0AE16A);
      try (Connection connection = transaction()) {
        connection.setReadOnly(true);
        assertEquals(
            InboxExecutionStatus.REPLAY,
            coordinator.inspectMessage(connection, reference).orElseThrow().status());
        connection.commit();
      }
    }
  }

  @Test
  void readOnlyMessageLookupUsesAllIdentityAndFingerprintChecks() throws Exception {
    var original =
        tokenRequest(
            MESSAGE,
            CORRELATION,
            101,
            TOKEN,
            FIXTURE_QUESTION_6D6CA52E,
            FIXTURE_QSBREQ01_F9A27626,
            FIXTURE_001_A3FEAA64);
    insertReadOnlyFixture(original, FIXTURE_COMPLETED_BA0AE16A);
    try (var keys =
        new FingerprintKeyRing(
            FIXTURE_FP2_0F8E0697, key((byte) 12), FIXTURE_FP1_54E2C4E0, key((byte) 11))) {
      var coordinator = new JdbcInboxCoordinator(keys);
      try (Connection connection = transaction()) {
        connection.setReadOnly(true);
        assertEquals(
            InboxExecutionStatus.REPLAY,
            coordinator.inspectMessage(connection, original).orElseThrow().status());
        for (var changed :
            List.of(
                tokenRequest(
                    MESSAGE,
                    uuid(401),
                    101,
                    TOKEN,
                    FIXTURE_QUESTION_6D6CA52E,
                    FIXTURE_QSBREQ01_F9A27626,
                    FIXTURE_001_A3FEAA64),
                tokenRequest(
                    MESSAGE,
                    CORRELATION,
                    101,
                    TOKEN,
                    FIXTURE_QUESTION_6D6CA52E,
                    "USTREQ01",
                    FIXTURE_001_A3FEAA64),
                tokenRequest(
                    MESSAGE,
                    CORRELATION,
                    101,
                    TOKEN,
                    FIXTURE_QUESTION_6D6CA52E,
                    FIXTURE_QSBREQ01_F9A27626,
                    "002"),
                tokenRequest(
                    MESSAGE,
                    CORRELATION,
                    102,
                    TOKEN,
                    FIXTURE_QUESTION_6D6CA52E,
                    FIXTURE_QSBREQ01_F9A27626,
                    FIXTURE_001_A3FEAA64),
                tokenRequest(
                    MESSAGE,
                    CORRELATION,
                    101,
                    uuid(402),
                    FIXTURE_QUESTION_6D6CA52E,
                    FIXTURE_QSBREQ01_F9A27626,
                    FIXTURE_001_A3FEAA64),
                tokenRequest(
                    MESSAGE,
                    CORRELATION,
                    101,
                    TOKEN,
                    "changed",
                    FIXTURE_QSBREQ01_F9A27626,
                    FIXTURE_001_A3FEAA64))) {
          var failure =
              assertThrows(
                  InboxException.class, () -> coordinator.inspectMessage(connection, changed));
          assertEquals(InboxException.Reason.MESSAGE_ID_REUSE, failure.reason());
        }
        try (var canonical =
            new CanonicalRequest(
                "101",
                FIXTURE_QSBREQ01_F9A27626,
                FIXTURE_001_A3FEAA64,
                FIXTURE_QUESTION_6D6CA52E,
                List.of(new CanonicalField("body", "UTF8-v1", new byte[] {65})))) {
          var changed =
              new InboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OptionalLong.of(101),
                  Optional.of(TOKEN),
                  canonical,
                  RECEIVED,
                  EXPIRES);
          assertEquals(
              InboxException.Reason.MESSAGE_ID_REUSE,
              assertThrows(
                      InboxException.class, () -> coordinator.inspectMessage(connection, changed))
                  .reason());
        }
        connection.commit();
      }
    }
    try (var keys = new FingerprintKeyRing(FIXTURE_FP2_0F8E0697, key((byte) 12), null, null);
        Connection connection = transaction()) {
      connection.setReadOnly(true);
      var coordinator = new JdbcInboxCoordinator(keys);
      var failure =
          assertThrows(
              InboxException.class, () -> coordinator.inspectMessage(connection, original));
      assertEquals(InboxException.Reason.FINGERPRINT_KEY_UNAVAILABLE, failure.reason());
      connection.rollback();
    }
  }

  @Test
  void readOnlyMessageLookupRejectsNullModesCorruptionAndJdbcFaults() throws Exception {
    var request =
        tokenRequest(
            MESSAGE,
            CORRELATION,
            101,
            TOKEN,
            FIXTURE_QUESTION_6D6CA52E,
            FIXTURE_QSBREQ01_F9A27626,
            FIXTURE_001_A3FEAA64);
    insertReadOnlyFixture(request, FIXTURE_COMPLETED_BA0AE16A);
    try (var keys = new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 11), null, null)) {
      var coordinator = new JdbcInboxCoordinator(keys);
      assertThrows(NullPointerException.class, () -> coordinator.inspectMessage(null, request));
      try (Connection connection = appConnection()) {
        assertThrows(
            NullPointerException.class, () -> coordinator.inspectMessage(connection, null));
        assertEquals(
            InboxException.Reason.TRANSACTION_REQUIRED,
            assertThrows(
                    InboxException.class, () -> coordinator.inspectMessage(connection, request))
                .reason());
        connection.setAutoCommit(false);
        assertEquals(
            InboxException.Reason.TRANSACTION_REQUIRED,
            assertThrows(
                    InboxException.class, () -> coordinator.inspectMessage(connection, request))
                .reason());
      }
      for (String fault :
          List.of(
              "getAutoCommit",
              "isReadOnly",
              "prepareStatement",
              "setObject",
              "executeQuery",
              "next",
              "getObject",
              "rowClose",
              "statementClose",
              "null:correlation_id",
              "null:request_layout_id",
              "null:request_version",
              "null:fingerprint_key_version",
              "null:request_fingerprint_hmac",
              "null:processing_state",
              "null:result_ref_type",
              "null:response_layout_id",
              "null:response_version",
              "null:completed_at")) {
        try (Connection connection = transaction()) {
          connection.setReadOnly(true);
          assertThrows(
              SQLException.class,
              () -> coordinator.inspectMessage(readOnlyFault(connection, fault), request));
          assertFalse(connection.isClosed());
          assertFalse(connection.getAutoCommit());
          connection.rollback();
        }
      }
      try (Connection connection = transaction()) {
        connection.setReadOnly(true);
        assertThrows(
            IllegalArgumentException.class,
            () -> coordinator.inspectMessage(readOnlyFault(connection, "unknownState"), request));
        connection.rollback();
      }
      assertEquals(1, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
    }
  }

  @Test
  void readOnlyMessageLookupRunsOneHundredTimesWhileRowIsLocked() throws Exception {
    var request =
        tokenRequest(
            MESSAGE,
            CORRELATION,
            101,
            TOKEN,
            FIXTURE_QUESTION_6D6CA52E,
            FIXTURE_QSBREQ01_F9A27626,
            FIXTURE_001_A3FEAA64);
    insertReadOnlyFixture(request, FIXTURE_COMPLETED_BA0AE16A);
    try (var keys = new FingerprintKeyRing(FIXTURE_FP1_54E2C4E0, key((byte) 11), null, null);
        Connection locked = transaction();
        var statement = locked.createStatement()) {
      try (var row =
          statement.executeQuery("select message_id from schubert.request_inbox for update")) {
        assertTrue(row.next());
      }
      var coordinator = new JdbcInboxCoordinator(keys);
      try (var executor = Executors.newFixedThreadPool(16)) {
        var results = new ArrayList<Future<InboxExecution>>();
        for (int i = 0; i < 100; i++) {
          results.add(
              executor.submit(
                  () -> {
                    try (Connection connection = transaction()) {
                      connection.setReadOnly(true);
                      try (var timeout = connection.createStatement()) {
                        timeout.execute("set local statement_timeout='500ms'");
                      }
                      var result = coordinator.inspectMessage(connection, request).orElseThrow();
                      connection.commit();
                      return result;
                    }
                  }));
        }
        for (var result : results) {
          assertEquals(InboxExecutionStatus.REPLAY, result.get().status());
          assertArrayEquals(
              new byte[29],
              result
                  .get()
                  .completion()
                  .orElseThrow()
                  .responseSnapshot()
                  .orElseThrow()
                  .ciphertext());
        }
      }
      assertEquals(EXPIRES, storedExpiry(locked, MESSAGE));
      locked.rollback();
    }
    assertEquals(1, count(FIXTURE_SCHUBERT_REQUEST_INBOX_CEAADFAA));
  }

  private static void insertReadOnlyFixture(InboxRequest request, String state) throws Exception {
    // Independent SS324 LP/HMAC oracle; no production canonical encoder or fingerprint method.
    var bytes = new ByteArrayOutputStream();
    try (var out = new DataOutputStream(bytes)) {
      out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
      String layout = request.operationToken().isPresent() ? FIXTURE_QSBREQ01_F9A27626 : "GAMREQ01";
      for (String value : List.of("101", layout, FIXTURE_001_A3FEAA64, FIXTURE_QUESTION_6D6CA52E)) {
        byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
        out.writeInt(encoded.length);
        out.write(encoded);
      }
      out.writeInt(0);
    }
    var mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(key((byte) 11), "HmacSHA256"));
    try (Connection connection = transaction()) {
      insertProcessing(
          connection,
          request,
          new Fingerprint(FIXTURE_FP1_54E2C4E0, mac.doFinal(bytes.toByteArray())));
      if (!state.equals("PROCESSING")) {
        try (var statement =
            connection.prepareStatement(
                "update schubert.request_inbox set processing_state=?,result_ref_type='NONE',"
                    + "response_layout_id='QSBRSP01',response_version='001',"
                    + "response_body_encrypted=decode(repeat('00',29),'hex'),"
                    + "response_key_version='snapshot1',completed_at='2026-09-05T00:00:01Z' where message_id=?")) {
          statement.setString(1, state);
          statement.setObject(2, request.messageId());
          assertEquals(1, statement.executeUpdate());
        }
      }
      // PROCESSING fixture intentionally represents a pre-existing anomaly, never production flow.
      connection.commit();
    }
  }

  private static Connection readOnlyFault(Connection real, String fault) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, arguments) -> {
              if (method.getName().equals(fault))
                throw new SQLException("synthetic-provider-fault");
              Object result = invoke(real, method, arguments);
              if (method.getName().equals("prepareStatement")) {
                assertTrue(((String) arguments[0]).endsWith("where message_id=?"));
                return Proxy.newProxyInstance(
                    PreparedStatement.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (sp, sm, sa) -> {
                      if (sm.getName().equals(fault))
                        throw new SQLException("synthetic-provider-fault");
                      Object sr = invoke(result, sm, sa);
                      if (sm.getName().equals("close") && fault.equals("statementClose"))
                        throw new SQLException("synthetic-close-fault");
                      if (sm.getName().equals("executeQuery")) {
                        return Proxy.newProxyInstance(
                            ResultSet.class.getClassLoader(),
                            new Class<?>[] {ResultSet.class},
                            (rp, rm, ra) -> {
                              if (rm.getName().equals(fault))
                                throw new SQLException("synthetic-provider-fault");
                              if (fault.startsWith("null:")
                                  && ra != null
                                  && fault.substring(5).equals(ra[0])) return null;
                              if (fault.equals("unknownState")
                                  && rm.getName().equals("getString")
                                  && ra[0].equals("processing_state")) return "UNKNOWN";
                              Object rr = invoke(sr, rm, ra);
                              if (rm.getName().equals("close") && fault.equals("rowClose"))
                                throw new SQLException("synthetic-close-fault");
                              return rr;
                            });
                      }
                      return sr;
                    });
              }
              return result;
            });
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
        canonical(owner, layout, FIXTURE_001_A3FEAA64, target),
        RECEIVED,
        EXPIRES);
  }

  private static InboxRequest anonymousRequest(UUID message, UUID correlation, String target) {
    return new InboxRequest(
        message,
        correlation,
        OptionalLong.empty(),
        Optional.empty(),
        new CanonicalRequest("ANONYMOUS", "LGNREQ01", FIXTURE_001_A3FEAA64, target, List.of()),
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
        FIXTURE_001_A3FEAA64,
        Optional.of(new EncryptedResponseSnapshot("snapshot1", new byte[29])),
        COMPLETED);
  }

  private static InboxCompletion numericCompletion() {
    return new InboxCompletion(
        InboxCompletionState.COMPLETED,
        InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 77),
        "QBSRSP01",
        FIXTURE_001_A3FEAA64,
        Optional.empty(),
        COMPLETED);
  }

  private static InboxCompletion noSnapshotCompletion() {
    return new InboxCompletion(
        InboxCompletionState.COMPLETED,
        InboxResultReference.none(),
        "QSTRSP01",
        FIXTURE_001_A3FEAA64,
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
      statement.setObject(6, request.operationToken().orElse(null));
      statement.setString(7, HexFormat.of().formatHex(fingerprint.digest()));
      statement.setString(8, fingerprint.keyVersion());
      statement.setObject(9, request.receivedAt().atOffset(java.time.ZoneOffset.UTC));
      statement.setObject(10, request.expiresAt().atOffset(java.time.ZoneOffset.UTC));
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
      statement.setObject(1, COMPLETED.atOffset(java.time.ZoneOffset.UTC));
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
