package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.Fixture;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.TestIo;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.TestSecurity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.maintenance.InspectionExecution;
import dev.codex.schubert.nk.api.maintenance.InspectionProgress;
import dev.codex.schubert.nk.api.maintenance.InspectionRun;
import dev.codex.schubert.nk.api.maintenance.InspectorSettings;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-212..220: real file/native/JDBC composition, explicitly synthetic OS admission. */
final class InspectorApplicationTest {
  private static final String FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88 =
      "inbox_inspection_progress";
  private static final String FIXTURE_DB_INBOX_INSPECTOR_03997756 = "db-inbox-inspector";
  private static final String FIXTURE_READ_ONLY_210AFF1C = "read only";
  @TempDir static Path databaseRoot;
  @TempDir Path temporary;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 42), Instant.parse("2026-09-17T00:00:00.123Z"));

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(databaseRoot);
    try (var c = db.admin()) {
      url = c.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("delete from schubert.inbox_inspection_progress");
      s.execute("delete from schubert.request_inbox");
      s.execute("delete from schubert.batch_runs");
    }
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) values(?,'2026-09-17',?,1,'2026-09-17T00:00:00Z','2026-09-17T00:00:00.001Z','SUCCESS')")) {
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG")) {
        s.setObject(1, RUN.id());
        s.setString(2, step);
        assertEquals(1, s.executeUpdate());
      }
    }
  }

  @Test
  void successAndResume() throws Exception {
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      var app = application(f, calls, io);
      var first = app.execute(RUN);
      assertEquals(InspectionExecution.Status.SUCCESS, first.status());
      assertEquals(
          new InspectionProgress(RUN, Optional.empty(), 0, 0, 0, true),
          first.lastConfirmed().orElseThrow());
      assertTrue(calls.live.isEmpty());
      assertEquals(1, calls.finalCloses);
      assertEquals(first, app.execute(RUN));
      assertTrue(calls.live.isEmpty());
      assertEquals(2, calls.finalCloses);
      assertEquals(10, io.opens);
      assertEquals(io.opens, io.closes);
      cleared(io);
      assertEquals(1, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
    }
  }

  @Test
  void protectedResult() throws Exception {
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at) values(?,?,'LGNREQ01','001',repeat('a',64),'fp1','ERROR','NONE','LGNRSP01','001',?,'s1','2026-09-09T00:00:00Z','2026-09-09T00:00:00.123Z','2026-09-16T00:00:00.123Z')")) {
      s.setObject(1, new UUID(0, 100));
      s.setObject(2, new UUID(0, 100));
      s.setBytes(3, new byte[30]);
      assertEquals(1, s.executeUpdate());
    }
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      var result = application(f, calls, io).execute(RUN);
      assertEquals(InspectionExecution.Status.WARNING, result.status());
      assertEquals(
          new InspectionProgress(RUN, Optional.of(new UUID(0, 100)), 1, 0, 1, true),
          result.lastConfirmed().orElseThrow());
      assertEquals(1, count("request_inbox"));
      assertTrue(calls.live.isEmpty());
      assertEquals(1, calls.finalCloses);
      cleared(io);
    }
  }

  @Test
  void databaseFailure() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      assertEquals(2, s.executeUpdate("delete from schubert.batch_runs"));
    }
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      assertEquals(
          InspectionExecution.Status.STORAGE_FAILURE,
          application(f, calls, io).execute(RUN).status());
      assertTrue(calls.live.isEmpty());
      assertEquals(0, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
      cleared(io);
      var unavailable =
          new InspectorSettings(
              f.root, url.replace("/postgres", "/absent_inspector_pt"), Set.of("fp1"));
      var otherIo = new TestIo();
      var disconnected =
          new InspectorApplication(unavailable, calls, new TestSecurity(otherIo), otherIo);
      assertEquals(InspectionExecution.Status.STORAGE_FAILURE, disconnected.execute(RUN).status());
      assertTrue(calls.live.isEmpty());
      assertEquals(0, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
      cleared(otherIo);
    }
  }

  @Test
  void app925001GuardIoFailurePrecedesAllCredentialAndDatabaseIo() throws Exception {
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      var failure =
          assertThrows(
              InspectorCredentialException.class,
              () ->
                  application(f, calls, io)
                      .execute(
                          RUN,
                          Optional.of(
                              () -> {
                                throw new IOException(
                                    "independent-private-diagnostic-never-export");
                              })));
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertEquals(0, io.fileAttributes);
      assertTrue(io.buffers.isEmpty());
      assertTrue(calls.live.isEmpty());
      assertEquals(1, calls.finalCloses);
      assertEquals(0, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
    }
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      var app = application(f, calls, io);
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard available = () -> 5_000_000_000L;
      var first = app.execute(RUN, Optional.of(available));
      assertEquals(InspectionExecution.Status.SUCCESS, first.status());
      assertEquals(
          new InspectionProgress(RUN, Optional.empty(), 0, 0, 0, true),
          first.lastConfirmed().orElseThrow());
      assertEquals(1, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
      var replay = app.execute(RUN, Optional.of(available));
      assertEquals(InspectionExecution.Status.SUCCESS, replay.status());
      assertEquals(
          new InspectionProgress(RUN, Optional.empty(), 0, 0, 0, true),
          replay.lastConfirmed().orElseThrow());
      assertEquals(
          1,
          count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88),
          "borrowed-guard replay never duplicates progress");
      assertTrue(calls.live.isEmpty());
      cleared(io);
    }
  }

  @Test
  void app925002OwnerParserConsumesLiteralDataAndSanitizesMalformedClaim() throws Exception {
    String golden =
        "NKMAINTOWNER1\nboot=11111111-1111-4111-8111-111111111111\n"
            + "run=22222222-2222-4222-8222-222222222222\n"
            + "activation=33333333-3333-4333-8333-333333333333\n"
            + "cutoff=2026-09-27T15:00:00Z\nepoch=44444444-4444-4444-8444-444444444444\n"
            + "morning_invocation=55555555555555555555555555555555\nmorning_pid=42\n"
            + "morning_start_ticks=12345\ncleanup_invocation=-\ncleanup_pid=-\n"
            + "cleanup_start_ticks=-\ndeadline_nanos=1800000000007\n";
    for (String input : List.of(golden, "independent-private-diagnostic-invalid")) {
      try (var f = fixture()) {
        Files.writeString(f.root.resolve("maintenance-owner"), input);
        var calls = new Calls(f.root);
        var io = new TestIo();
        try (var root = OwnedTransferDirectory.open(calls, f.root)) {
          var reader = new InspectorCredentialLoader(root, new TestSecurity(io), io);
          if (input.equals(golden)) {
            var observed = InspectorApplication.readMaintenanceOwner(reader);
            assertEquals(UUID.fromString("11111111-1111-4111-8111-111111111111"), observed.boot());
            assertEquals(UUID.fromString("22222222-2222-4222-8222-222222222222"), observed.run());
            assertEquals(1_800_000_000_007L, observed.deadlineNanos());
            assertEquals(42, observed.morning().pid());
            assertTrue(observed.cleanup().isEmpty(), "data parse is not Inspector admission");
          } else {
            var failure =
                assertThrows(
                    IOException.class, () -> InspectorApplication.readMaintenanceOwner(reader));
            assertEquals("maintenance owner unavailable", failure.getMessage());
            assertNull(failure.getCause());
            assertEquals(0, failure.getSuppressed().length);
          }
        }
        assertTrue(calls.live.isEmpty());
        assertEquals(1, calls.finalCloses);
        cleared(io);
      }
    }
  }

  @Test
  void app925003OwnerReaderFailureRetainsCredentialFailureClassification() throws Exception {
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      try (var root = OwnedTransferDirectory.open(calls, f.root)) {
        var reader = new InspectorCredentialLoader(root, new TestSecurity(io), io);
        assertThrows(
            InspectorCredentialException.class,
            () -> InspectorApplication.readMaintenanceOwner(reader));
      }
      assertTrue(calls.live.isEmpty());
      cleared(io);
    }
    assertThrows(NullPointerException.class, () -> InspectorApplication.readMaintenanceOwner(null));
  }

  @Test
  void credentialFailures() throws Exception {
    for (String fault :
        List.of("password-missing", "password-invalid", "aes-missing", "same-version")) {
      try (var f = fixture()) {
        switch (fault) {
          case "password-missing" ->
              Files.delete(f.root.resolve(FIXTURE_DB_INBOX_INSPECTOR_03997756));
          case "password-invalid" ->
              Files.write(f.root.resolve(FIXTURE_DB_INBOX_INSPECTOR_03997756), new byte[] {0});
          case "aes-missing" ->
              Files.delete(f.root.resolve(AesCredentialFile.RESPONSE_CURRENT.fileName()));
          case "same-version" -> f.write(AesCredentialFile.CONTEXT_PREVIOUS, "v1");
          default -> throw new AssertionError();
        }
        var calls = new Calls(f.root);
        var io = new TestIo();
        var failure =
            assertThrows(
                InspectorCredentialException.class, () -> application(f, calls, io).execute(RUN));
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertTrue(calls.live.isEmpty());
        assertEquals(1, calls.finalCloses);
        cleared(io);
        assertEquals(0, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
      }
    }
  }

  @Test
  void rootFailures() throws Exception {
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      var app = application(f, calls, io);
      calls.failOpen = true;
      assertThrows(StorageIoException.class, () -> app.execute(RUN));
      assertEquals(0, io.opens);
      assertTrue(calls.live.isEmpty());
      calls.failOpen = false;
      calls.failFinalClose = true;
      assertThrows(StorageIoException.class, () -> app.execute(RUN));
      assertTrue(calls.live.isEmpty());
      assertEquals(1, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
      calls.failFinalClose = false;
      assertEquals(InspectionExecution.Status.SUCCESS, app.execute(RUN).status());
      assertTrue(calls.live.isEmpty());
      assertEquals(2, calls.finalCloses);
      cleared(io);
    }
  }

  @Test
  void nativeAdmission() throws Exception {
    try (var f = fixture()) {
      var app = new InspectorApplication(settings(f));
      assertThrows(InspectorCredentialException.class, () -> app.execute(RUN));
      assertEquals(0, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
      assertTrue(Files.isRegularFile(f.root.resolve(FIXTURE_DB_INBOX_INSPECTOR_03997756)));
    }
  }

  @Test
  void nullContracts() throws Exception {
    assertThrows(NullPointerException.class, () -> new InspectorApplication(null));
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      var security = new TestSecurity(io);
      assertThrows(
          NullPointerException.class, () -> new InspectorApplication(null, calls, security, io));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorApplication(settings(f), null, security, io));
      assertThrows(
          NullPointerException.class, () -> new InspectorApplication(settings(f), calls, null, io));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorApplication(settings(f), calls, security, null));
      assertThrows(NullPointerException.class, () -> application(f, calls, io).execute(null));
      assertTrue(calls.live.isEmpty());
      assertEquals(0, io.opens);
      assertEquals(0, calls.finalCloses);
    }
  }

  @Test
  void interruptedExecution() throws Exception {
    try (var f = fixture()) {
      var calls = new Calls(f.root);
      var io = new TestIo();
      try {
        Thread.currentThread().interrupt();
        assertEquals(
            InspectionExecution.Status.INTERRUPTED,
            application(f, calls, io).execute(RUN).status());
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      assertEquals(0, io.opens);
      assertEquals(0, calls.finalCloses);
      io.beforeRead = () -> Thread.currentThread().interrupt();
      try {
        assertThrows(
            InspectorCredentialException.class, () -> application(f, calls, io).execute(RUN));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      assertEquals(1, io.opens);
      assertEquals(1, io.closes);
      assertTrue(calls.live.isEmpty());
      assertEquals(1, calls.finalCloses);
      cleared(io);
      assertEquals(0, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
    }
  }

  @Test
  void concurrentLifetimes() throws Exception {
    try (var f = fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      Files.delete(f.root.resolve(FIXTURE_DB_INBOX_INSPECTOR_03997756));
      var calls = new Calls(f.root);
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 64; i++)
        work.add(
            () -> {
              var io = new TestIo();
              assertThrows(
                  InspectorCredentialException.class, () -> application(f, calls, io).execute(RUN));
              assertEquals(0, io.opens);
              cleared(io);
              return true;
            });
      for (var done : pool.invokeAll(work)) assertTrue(done.get(5, TimeUnit.SECONDS));
      assertTrue(calls.live.isEmpty());
      assertEquals(64, calls.finalCloses);
      assertEquals(0, count(FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88));
    }
  }

  private Fixture fixture() throws Exception {
    var f = new Fixture(temporary);
    for (var id : AesCredentialFile.values()) f.write(id, id.optional() ? "old" : "v1");
    Files.write(f.root.resolve(FIXTURE_DB_INBOX_INSPECTOR_03997756), new byte[] {65});
    return f;
  }

  private InspectorSettings settings(Fixture f) {
    return new InspectorSettings(f.root, url, Set.of("fp1"));
  }

  private InspectorApplication application(Fixture f, Calls calls, TestIo io) {
    return new InspectorApplication(settings(f), calls, new TestSecurity(io), io);
  }

  private static int count(String table) throws SQLException {
    String sql =
        switch (table) {
          case "request_inbox" -> "select count(*) from schubert.request_inbox";
          case FIXTURE_INBOX_INSPECTION_PROGRESS_4282AA88 ->
              "select count(*) from schubert.inbox_inspection_progress";
          default -> throw new AssertionError();
        };
    try (var c = db.admin();
        var s = c.createStatement();
        var r = s.executeQuery(sql)) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void cleared(TestIo io) {
    for (byte[] buffer : io.buffers) assertArrayEquals(new byte[buffer.length], buffer);
    Arrays.fill(io.observedContent, (byte) 0);
  }

  private static final class Calls implements DirectoryCalls {
    final DirectoryCalls actual = LinuxDirectoryCalls.create();
    final Set<Integer> live = new HashSet<>();
    final Set<Integer> finals = new HashSet<>();
    final String leaf;
    boolean failOpen;
    boolean failFinalClose;
    int finalCloses;

    Calls(Path root) {
      leaf = root.getFileName().toString();
    }

    @Override
    public synchronized int openRoot() throws StorageIoException {
      if (failOpen) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      int fd = actual.openRoot();
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public synchronized int openDirectory(int parent, String name) throws StorageIoException {
      int fd = actual.openDirectory(parent, name);
      assertTrue(live.add(fd));
      if (name.equals(leaf)) finals.add(fd);
      return fd;
    }

    @Override
    public synchronized int openEntry(int parent, String name) throws StorageIoException {
      int fd = actual.openEntry(parent, name);
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public synchronized void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd));
      boolean last = finals.remove(fd);
      actual.close(fd);
      if (last) {
        finalCloses++;
        if (failFinalClose) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public int createFile(int p, String n) {
      throw new AssertionError(FIXTURE_READ_ONLY_210AFF1C);
    }

    @Override
    public void createDirectory(int p, String n) {
      throw new AssertionError(FIXTURE_READ_ONLY_210AFF1C);
    }

    @Override
    public void publish(int p, String a, String b) {
      throw new AssertionError(FIXTURE_READ_ONLY_210AFF1C);
    }

    @Override
    public void unlink(int p, String n) {
      throw new AssertionError(FIXTURE_READ_ONLY_210AFF1C);
    }

    @Override
    public void sync(int p) {
      throw new AssertionError(FIXTURE_READ_ONLY_210AFF1C);
    }
  }
}
