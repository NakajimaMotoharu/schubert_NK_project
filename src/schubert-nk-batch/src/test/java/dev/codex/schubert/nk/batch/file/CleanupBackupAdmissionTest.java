package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.MANIFEST_HASH;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BackupStepFixture;
import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** OPS-009/BAK-001/UI251/SS341/343/SSC104/PG332; CBA001..005 independent SQL/file oracle. */
final class CleanupBackupAdmissionTest {
  private static final String FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E =
      "root cleanup backup unavailable";
  private static final String FIXTURE_ROLLBACK_3770B198 = "rollback";
  private static final String FIXTURE_PUBLIC_CANARY_73B3ABA9 = "PUBLIC_CANARY";
  @TempDir static Path databaseRoot;
  @TempDir Path temporary;
  private static final Instant OBSERVED = Instant.parse("2026-09-12T15:00:06Z");
  private static final UUID ACTIVATION = UUID.fromString("11111111-2222-4333-8444-555555555555");
  private static BatchDatabaseFixture database;

  @BeforeAll
  static void start() throws Exception {
    database = new BatchDatabaseFixture(databaseRoot);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    try (var admin = database.admin()) {
      BackupStepFixture.sql(admin, "delete from schubert.batch_runs");
      BackupStepFixture.sql(admin, "delete from schubert.inbox_inspection_progress");
      BackupStepFixture.sql(admin, "delete from schubert.log_cleanup_progress");
      BackupStepFixture.sql(
          admin,
          "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,"
              + "ended_at,status,target_count,success_count,failure_count,byte_count) values "
              + "(90000,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','BACKUP_DB',1,"
              + "'2026-09-12T15:00:00Z','2026-09-12T15:00:05Z','SUCCESS',1,1,0,26),"
              + "(90001,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','BACKUP_CONFIG',1,"
              + "'2026-09-12T15:00:01Z','2026-09-12T15:00:05Z','SUCCESS',2,2,0,67)");
    }
  }

  private static CleanupWorkerRequest request() {
    return new CleanupWorkerRequest(
        UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
        ACTIVATION,
        Instant.parse("2026-09-12T15:00:00Z"),
        MANIFEST_HASH);
  }

  private static CleanupBackupAdmission admission(BackupArtifactFixture f) {
    return new CleanupBackupAdmission(
        new BackupManifestReader(
            f.root, f, BackupArtifactFixture.UID, BackupArtifactFixture.GID, f, f::clock),
        f.verifier());
  }

  private static CleanupBackupAdmission atInterrupt(
      BackupArtifactFixture f, int stopAt, AtomicInteger checks) {
    return new CleanupBackupAdmission(
        new BackupManifestReader(
            f.root, f, BackupArtifactFixture.UID, BackupArtifactFixture.GID, f, f::clock),
        f.verifier(),
        () -> checks.incrementAndGet() == stopAt);
  }

  private Connection childConnection() throws SQLException {
    Connection child = database.open("schubert_batch");
    BackupStepFixture.sql(child, "select pg_advisory_lock(71419602)");
    return child;
  }

  private static String rows(Connection connection) throws SQLException {
    return BackupStepFixture.query(
        connection,
        "select string_agg(step||':'||status||':'||success_count||':'||byte_count,',' order by step)"
            + " from schubert.batch_runs");
  }

  @Test
  void successAndReplayAreReadOnlyAndBorrowed() throws Exception { // CBA001/005
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var admission = admission(f);
      assertEquals(f.expected, admission.verify(request(), OBSERVED, child));
      assertTrue(child.getAutoCommit());
      assertFalse(child.isClosed());
      assertEquals(f.expected, admission.verify(request(), OBSERVED, child));
      assertEquals("BACKUP_CONFIG:SUCCESS:2:67,BACKUP_DB:SUCCESS:1:26", rows(child));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void actualByteTamperAndWrongRequestNeverReadDatabase() throws Exception { // CBA002
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var forbidden = spy(child, "getAutoCommit", new AssertionError("DB reached before files"));
      byte[] bytes = Files.readAllBytes(f.child.resolve("config.tar"));
      bytes[0] ^= 1;
      Files.write(f.child.resolve("config.tar"), bytes);
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(IOException.class, () -> admission(f).verify(request(), OBSERVED, forbidden))
              .getMessage());
      assertEquals(0, f.counts.getOrDefault("create", 0));
    }
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var wrong =
          new CleanupWorkerRequest(request().run(), ACTIVATION, request().cutoff(), "a".repeat(64));
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(
                  IOException.class,
                  () ->
                      admission(f)
                          .verify(
                              wrong,
                              OBSERVED,
                              spy(
                                  child,
                                  "getAutoCommit",
                                  new AssertionError("DB reached before MANIFEST"))))
              .getMessage());
    }
  }

  @Test
  void runningOrIncorrectPairIsNeverCompleted() throws Exception { // CBA003
    try (var admin = database.admin()) {
      BackupStepFixture.sql(
          admin,
          "update schubert.batch_runs set status='RUNNING',ended_at=null,target_count=0,"
              + "success_count=0,byte_count=0");
    }
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(IOException.class, () -> admission(f).verify(request(), OBSERVED, child))
              .getMessage());
      assertTrue(child.getAutoCommit());
      assertEquals("BACKUP_CONFIG:RUNNING:0:0,BACKUP_DB:RUNNING:0:0", rows(child));
    }
    try (var admin = database.admin()) {
      BackupStepFixture.sql(
          admin,
          "update schubert.batch_runs set status='SUCCESS',ended_at='2026-09-12T15:00:05Z',"
              + "target_count=case step when 'BACKUP_DB' then 1 else 2 end,"
              + "success_count=case step when 'BACKUP_DB' then 1 else 2 end,"
              + "byte_count=case step when 'BACKUP_DB' then 26 else 67 end");
      BackupStepFixture.sql(
          admin, "update schubert.batch_runs set byte_count=68 where step='BACKUP_CONFIG'");
    }
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(IOException.class, () -> admission(f).verify(request(), OBSERVED, child))
              .getMessage());
      assertTrue(child.getAutoCommit());
      assertEquals("BACKUP_CONFIG:SUCCESS:2:68,BACKUP_DB:SUCCESS:1:26", rows(child));
    }
  }

  @Test
  void rollbackFailureDoesNotRestoreAutoCommit() throws Exception { // CBA004
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var rollbacks = new AtomicInteger();
      var restoration = new AtomicInteger();
      Connection broken =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals(FIXTURE_ROLLBACK_3770B198)) {
                      rollbacks.incrementAndGet();
                      throw new SQLException("PUBLIC_SYNTHETIC_CANARY");
                    }
                    if (method.getName().equals("setAutoCommit") && Boolean.TRUE.equals(args[0]))
                      restoration.incrementAndGet();
                    try {
                      return method.invoke(child, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                  });
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(IOException.class, () -> admission(f).verify(request(), OBSERVED, broken))
              .getMessage());
      assertEquals(2, rollbacks.get());
      assertEquals(0, restoration.get());
      assertFalse(child.getAutoCommit());
      child.rollback();
    }
  }

  @Test
  void nullAndInvalidSessionAreNotSuccess() throws Exception { // CBA004
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var admission = admission(f);
      assertThrows(
          NullPointerException.class, () -> new CleanupBackupAdmission(null, f.verifier()));
      assertThrows(
          NullPointerException.class,
          () ->
              new CleanupBackupAdmission(
                  new BackupManifestReader(
                      f.root, f, BackupArtifactFixture.UID, BackupArtifactFixture.GID, f, f::clock),
                  null));
      assertThrows(NullPointerException.class, () -> admission.verify(null, OBSERVED, child));
      assertThrows(NullPointerException.class, () -> admission.verify(request(), null, child));
      assertThrows(NullPointerException.class, () -> admission.verify(request(), OBSERVED, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new CleanupBackupAdmission(
                  new BackupManifestReader(
                      f.root, f, BackupArtifactFixture.UID, BackupArtifactFixture.GID, f, f::clock),
                  f.verifier(),
                  null));
      child.setReadOnly(true);
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(IOException.class, () -> admission.verify(request(), OBSERVED, child))
              .getMessage());
      child.setReadOnly(false);
      child.setAutoCommit(false);
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(IOException.class, () -> admission.verify(request(), OBSERVED, child))
              .getMessage());
      child.rollback();
      child.setAutoCommit(true);
      child.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(IOException.class, () -> admission.verify(request(), OBSERVED, child))
              .getMessage());
    }
  }

  @Test
  void interruptAtEveryAdmissionBarrierIsNotSuccess() throws Exception { // CBA004
    for (int barrier = 1; barrier <= 4; barrier++) {
      int stopAt = barrier;
      try (var f = new BackupArtifactFixture(temporary);
          var child = childConnection()) {
        var checks = new AtomicInteger();
        assertEquals(
            FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
            assertThrows(
                    IOException.class,
                    () -> atInterrupt(f, stopAt, checks).verify(request(), OBSERVED, child))
                .getMessage());
        assertEquals(barrier, checks.get());
        assertTrue(child.getAutoCommit());
        f.released();
      }
    }
  }

  @Test
  void sqlAndUnknownCleanupFailuresStayNonSuccess() throws Exception { // CBA004
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(
                  IOException.class,
                  () ->
                      admission(f)
                          .verify(
                              request(),
                              OBSERVED,
                              spy(
                                  child,
                                  "getAutoCommit",
                                  new SQLException(FIXTURE_PUBLIC_CANARY_73B3ABA9))))
              .getMessage());
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(
                  IOException.class,
                  () ->
                      admission(f)
                          .verify(
                              request(),
                              OBSERVED,
                              spy(
                                  child,
                                  "setAutoCommit",
                                  new SQLException(FIXTURE_PUBLIC_CANARY_73B3ABA9))))
              .getMessage());
      assertTrue(child.getAutoCommit());
    }
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var unknown = new IllegalStateException(FIXTURE_PUBLIC_CANARY_73B3ABA9);
      var rollbacks = new AtomicInteger();
      Connection fault =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("prepareStatement")) throw unknown;
                    if (method.getName().equals(FIXTURE_ROLLBACK_3770B198)) {
                      rollbacks.incrementAndGet();
                      throw new SQLException(FIXTURE_PUBLIC_CANARY_73B3ABA9);
                    }
                    try {
                      return method.invoke(child, args);
                    } catch (InvocationTargetException reflected) {
                      throw reflected.getCause();
                    }
                  });
      assertSame(
          unknown,
          assertThrows(
              IllegalStateException.class, () -> admission(f).verify(request(), OBSERVED, fault)));
      assertEquals(1, unknown.getSuppressed().length);
      assertEquals(1, rollbacks.get());
      assertFalse(child.getAutoCommit());
      child.rollback();
    }
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var unknown = new IllegalStateException(FIXTURE_PUBLIC_CANARY_73B3ABA9);
      var fault = spy(child, FIXTURE_ROLLBACK_3770B198, unknown);
      assertSame(
          unknown,
          assertThrows(
              IllegalStateException.class, () -> admission(f).verify(request(), OBSERVED, fault)));
      assertFalse(child.getAutoCommit());
      child.rollback();
    }
  }

  @Test
  void unknownPrimaryErrorSurvivesKnownRollbackFault() throws Exception { // CBA004
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var fatal = new AssertionError(FIXTURE_PUBLIC_CANARY_73B3ABA9);
      Connection fault =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("prepareStatement")) throw fatal;
                    if (method.getName().equals(FIXTURE_ROLLBACK_3770B198))
                      throw new SQLException(FIXTURE_PUBLIC_CANARY_73B3ABA9);
                    try {
                      return method.invoke(child, args);
                    } catch (InvocationTargetException reflected) {
                      throw reflected.getCause();
                    }
                  });
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class, () -> admission(f).verify(request(), OBSERVED, fault)));
      assertEquals(1, fatal.getSuppressed().length);
      assertFalse(child.getAutoCommit());
      child.rollback();
    }
  }

  @Test
  void knownPrimaryAndUnknownOrKnownCleanupNeverSucceed() throws Exception { // CBA004
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var unknown = new IllegalStateException(FIXTURE_PUBLIC_CANARY_73B3ABA9);
      var checks = new AtomicInteger();
      assertSame(
          unknown,
          assertThrows(
              IllegalStateException.class,
              () ->
                  atInterrupt(f, 3, checks)
                      .verify(
                          request(), OBSERVED, spy(child, FIXTURE_ROLLBACK_3770B198, unknown))));
      assertEquals(3, checks.get());
      assertFalse(child.getAutoCommit());
      child.rollback();
    }
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      var checks = new AtomicInteger();
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(
                  IOException.class,
                  () ->
                      atInterrupt(f, 3, checks)
                          .verify(
                              request(),
                              OBSERVED,
                              spy(
                                  child,
                                  FIXTURE_ROLLBACK_3770B198,
                                  new BatchRepositoryException())))
              .getMessage());
      assertFalse(child.getAutoCommit());
      child.rollback();
    }
  }

  @Test
  void repositoryFailureAndRollbackFailureRemainClosed() throws Exception { // CBA003/004
    try (var admin = database.admin()) {
      BackupStepFixture.sql(
          admin, "update schubert.batch_runs set byte_count=68 where step='BACKUP_CONFIG'");
    }
    try (var f = new BackupArtifactFixture(temporary);
        var child = childConnection()) {
      assertEquals(
          FIXTURE_ROOT_CLEANUP_BACKUP_UNAVAILABLE_E87CD24E,
          assertThrows(
                  IOException.class,
                  () ->
                      admission(f)
                          .verify(
                              request(),
                              OBSERVED,
                              spy(
                                  child,
                                  FIXTURE_ROLLBACK_3770B198,
                                  new SQLException(FIXTURE_PUBLIC_CANARY_73B3ABA9))))
              .getMessage());
      assertFalse(child.getAutoCommit());
      assertEquals("BACKUP_CONFIG:SUCCESS:2:68,BACKUP_DB:SUCCESS:1:26", rows(child));
      child.rollback();
    }
  }

  private static Connection spy(Connection real, String rejected, Throwable failure) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              if (method.getName().equals(rejected)) throw failure;
              try {
                return method.invoke(real, args);
              } catch (InvocationTargetException reflected) {
                throw reflected.getCause();
              }
            });
  }
}
