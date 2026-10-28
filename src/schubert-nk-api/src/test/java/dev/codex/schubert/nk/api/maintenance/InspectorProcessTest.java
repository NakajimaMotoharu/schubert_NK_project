package dev.codex.schubert.nk.api.maintenance;

import static dev.codex.schubert.nk.api.file.AesCredentialFile.CONTEXT_CURRENT;
import static dev.codex.schubert.nk.api.file.AesCredentialFile.CONTEXT_PREVIOUS;
import static dev.codex.schubert.nk.api.file.AesCredentialFile.RESPONSE_CURRENT;
import static dev.codex.schubert.nk.api.file.AesCredentialFile.RESPONSE_PREVIOUS;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.INTERRUPTED;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.STORAGE_FAILURE;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.SUCCESS;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.TIME_LIMIT;
import static dev.codex.schubert.nk.api.maintenance.InspectionExecution.Status.WARNING;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.AesCredentialFile;
import dev.codex.schubert.nk.api.file.InspectorCredentialException;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoader;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.outbound.SqlConnectionProvider;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-141..152; PG-D-135; real PG and independent JCE/ASCII fixtures. */
final class InspectorProcessTest {
  private static final String FIXTURE_INSERT_INTO_1D1568AF = "insert into";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 92), Instant.parse("2026-09-17T00:00:00Z"));

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.api()) {
      url = c.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    sql("delete from schubert.inbox_inspection_progress");
    sql("delete from schubert.request_inbox");
    sql("delete from schubert.batch_runs");
    sql(
        FIXTURE_INSERT_INTO_1D1568AF
            + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " values(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-01','2026-09-01','2026-09-01')"
            + " on conflict(id) do nothing");
    for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
      sql(
          FIXTURE_INSERT_INTO_1D1568AF
              + " schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status)"
              + " values('"
              + RUN.id()
              + "','2026-09-17','"
              + step
              + "',1,'2026-09-17','2026-09-17','SUCCESS')");
  }

  @Test
  void currentOnlyAndEmptyScan() throws Exception {
    try (var source = new Source()) {
      source.omitPrevious();
      var result = process(source).execute(RUN);
      assertEquals(SUCCESS, result.status());
      assertEquals(0, result.exitCode());
      assertEquals("0|0|0|true", stored());
      assertEquals(4, source.calls);
      assertEquals(2, source.materials.size());
      source.assertClosed();
    }
  }

  @Test
  void previousKeysAndAtomicDeletion() throws Exception {
    try (var fixture = new AuthenticationInboxInspectorTest.Fixture();
        var source = new Source()) {
      source.replace(RESPONSE_PREVIOUS, fixture.key, "s1");
      source.replace(CONTEXT_PREVIOUS, fixture.contextKey, "a1");
      validLoginError(fixture);
      var result = process(source).execute(RUN);
      assertEquals(SUCCESS, result.status());
      assertEquals("1|1|0|true", stored());
      assertEquals("0", inboxCount());
      source.assertClosed();
    }
  }

  @Test
  void unverifiableRowsWarnWithoutMutation() throws Exception {
    try (var source = new Source()) {
      invalidRows();
      String before =
          scalar(
              "select string_agg(message_id::text||':'||encode(response_body_encrypted,'hex'),','"
                  + " order by message_id) from schubert.request_inbox");
      var result = process(source).execute(RUN);
      assertEquals(WARNING, result.status());
      assertEquals(10, result.exitCode());
      assertEquals("2|0|2|true", stored());
      assertEquals("2", inboxCount());
      assertEquals(
          before,
          scalar(
              "select string_agg(message_id::text||':'||encode(response_body_encrypted,'hex'),','"
                  + " order by message_id) from schubert.request_inbox"));
      assertEquals(
          "Learner|USER|ACTIVE",
          scalar("select username||'|'||role||'|'||status from schubert.app_users where id=7"));
      source.assertClosed();
    }
  }

  @Test
  void missingAndFaultedKeyLoads() throws Exception {
    for (var id : AesCredentialFile.values()) {
      try (var source = new Source()) {
        source.fail = Optional.of(id);
        assertCredentialFailure(
            () -> new InspectorProcess(source, noDatabase(), Set.of("v1"), () -> 0).execute(RUN));
        assertEquals(id.ordinal() + 1, source.calls);
        source.assertClosed();
      }
    }
    for (var id : List.of(CONTEXT_CURRENT, RESPONSE_CURRENT)) {
      try (var source = new Source()) {
        source.absent.add(id);
        assertCredentialFailure(
            () -> new InspectorProcess(source, noDatabase(), Set.of("v1"), () -> 0).execute(RUN));
        source.assertClosed();
      }
    }
    for (var id : List.of(CONTEXT_PREVIOUS, RESPONSE_PREVIOUS)) {
      try (var source = new Source()) {
        source.absent.add(id);
        assertEquals(SUCCESS, process(source).execute(RUN).status());
        source.assertClosed();
      }
    }
  }

  @Test
  void versionsAndPurposeSeparation() throws Exception {
    for (var pair :
        List.of(
            List.of(CONTEXT_CURRENT, CONTEXT_PREVIOUS),
            List.of(RESPONSE_CURRENT, RESPONSE_PREVIOUS))) {
      try (var source = new Source()) {
        source.versions.put(pair.get(1), source.versions.get(pair.get(0)));
        assertCredentialFailure(
            () -> new InspectorProcess(source, noDatabase(), Set.of("v1"), () -> 0).execute(RUN));
        source.assertClosed();
      }
    }
    for (var ctx : List.of(CONTEXT_CURRENT, CONTEXT_PREVIOUS))
      for (var rsp : List.of(RESPONSE_CURRENT, RESPONSE_PREVIOUS))
        try (var source = new Source()) {
          source.replace(rsp, source.keys.get(ctx), source.versions.get(rsp));
          assertCredentialFailure(
              () -> new InspectorProcess(source, noDatabase(), Set.of("v1"), () -> 0).execute(RUN));
          source.assertClosed();
        }
    try (var source = new Source()) {
      source.versions.put(RESPONSE_CURRENT, source.versions.get(CONTEXT_CURRENT));
      source.versions.put(RESPONSE_PREVIOUS, source.versions.get(CONTEXT_PREVIOUS));
      assertEquals(SUCCESS, process(source).execute(RUN).status());
      source.assertClosed();
    }
  }

  @Test
  void closedMaterialFailsBeforeDatabase() throws Exception {
    for (var id : AesCredentialFile.values()) {
      try (var source = new Source()) {
        source.closed = Optional.of(id);
        assertCredentialFailure(
            () -> new InspectorProcess(source, noDatabase(), Set.of("v1"), () -> 0).execute(RUN));
        assertEquals(id.ordinal() + 1, source.calls);
        source.assertClosed();
      }
    }
  }

  @Test
  void timeoutsAndInterruptionCloseKeys() throws Exception {
    try (var source = new Source()) {
      AtomicInteger tick = new AtomicInteger();
      var result =
          new InspectorProcess(
                  source,
                  noDatabase(),
                  Set.of("v1"),
                  () -> tick.getAndIncrement() == 0 ? 0 : 1_800_000_000_000L)
              .execute(RUN);
      assertEquals(TIME_LIMIT, result.status());
      assertEquals(50, result.exitCode());
      assertTrue(result.lastConfirmed().isEmpty());
      source.assertClosed();
    }
    try (var source = new Source()) {
      try {
        Thread.currentThread().interrupt();
        var result = new InspectorProcess(source, noDatabase(), Set.of("v1"), () -> 0).execute(RUN);
        assertEquals(INTERRUPTED, result.status());
        assertEquals(0, source.calls);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        assertTrue(Thread.interrupted());
      }
    }
    try (var source = new Source()) {
      var probe = new MaintenanceJdbcProbe();
      probe.afterClose = () -> Thread.currentThread().interrupt();
      try {
        var result =
            new InspectorProcess(source, () -> probe.wrap(connection()), Set.of("v1"), () -> 0)
                .execute(RUN);
        assertEquals(INTERRUPTED, result.status());
        assertTrue(Thread.currentThread().isInterrupted());
        assertEquals("0|0|0|true", stored());
        source.assertClosed();
      } finally {
        assertTrue(Thread.interrupted());
      }
    }
  }

  @Test
  void databaseFailureAndResume() throws Exception {
    for (String fault : List.of("connection", "commit", "close")) {
      reset();
      try (var fixture = new AuthenticationInboxInspectorTest.Fixture();
          var source = new Source()) {
        source.replace(RESPONSE_CURRENT, fixture.key, "s1");
        validLoginError(fixture);
        var probe = new MaintenanceJdbcProbe();
        probe.fault = fault;
        probe.commitAfter = true;
        SqlConnectionProvider provider =
            () -> {
              if (fault.equals("connection"))
                throw new SQLException("public fixture marker", "08006");
              return probe.wrap(connection());
            };
        var failed = new InspectorProcess(source, provider, Set.of("v1"), () -> 0).execute(RUN);
        assertEquals(STORAGE_FAILURE, failed.status());
        assertEquals(50, failed.exitCode());
        assertTrue(failed.lastConfirmed().isEmpty());
        source.assertClosed();
        assertEquals(fault.equals("connection") ? "1" : "0", inboxCount());
        // A new instance rereads the immutable key set and resumes the DB-owned checkpoint.
        assertEquals(SUCCESS, process(source).execute(RUN).status());
        assertEquals("1|1|0|true", stored());
        assertEquals("0", inboxCount());
        source.assertClosed();
      }
    }
  }

  @Test
  void singleUseAndConcurrentContenders() throws Exception {
    try (var source = new Source();
        var pool = Executors.newFixedThreadPool(8)) {
      var process = process(source);
      var jobs = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              try {
                assertEquals(SUCCESS, process.execute(RUN).status());
                return true;
              } catch (IllegalStateException already) {
                assertEquals("inspector instance has already executed", already.getMessage());
                return false;
              }
            });
      int winners = 0;
      for (var result : pool.invokeAll(jobs)) if (result.get()) winners++;
      assertEquals(1, winners);
      assertEquals(4, source.calls);
      source.assertClosed();
      assertThrows(
          IllegalStateException.class,
          () -> process.execute(new InspectionRun(new UUID(0, 93), RUN.cutoff())));
    }
  }

  @Test
  void constructorAndSnapshotContracts() throws Exception {
    try (var source = new Source()) {
      assertThrows(
          NullPointerException.class,
          () -> new InspectorProcess(null, noDatabase(), Set.of("v1"), () -> 0));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorProcess(source, null, Set.of("v1"), () -> 0));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorProcess(source, noDatabase(), null, () -> 0));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorProcess(source, noDatabase(), Set.of("v1"), null));
      assertThrows(
          NullPointerException.class, () -> new InspectorProcess(null, noDatabase(), Set.of("v1")));
      var missing = new HashSet<String>();
      missing.add(null);
      assertThrows(
          NullPointerException.class,
          () -> new InspectorProcess(source, noDatabase(), missing, () -> 0));
      for (var invalid :
          List.of(
              Set.<String>of(),
              Set.of(""),
              Set.of(".v1"),
              Set.of("v 1"),
              Set.of("abcdefghijklmnopq"))) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new InspectorProcess(source, noDatabase(), invalid, () -> 0));
      }
      String boundaryVersion = "A._-0123456789ab";
      assertEquals(16, boundaryVersion.getBytes(StandardCharsets.US_ASCII).length);
      var versions = new HashSet<>(Set.of("v1", boundaryVersion));
      var runner =
          new InspectorProcess(source, InspectorProcessTest::connection, versions, () -> 0);
      versions.clear();
      assertThrows(NullPointerException.class, () -> runner.execute(null));
      assertEquals(0, source.calls);
      assertEquals(SUCCESS, runner.execute(RUN).status());
      source.assertClosed();
    }
  }

  @Test
  void ownedCopiesAndMaterialLifetimes() throws Exception {
    try (var source = new Source()) {
      byte[] before = source.keys.get(CONTEXT_CURRENT).clone();
      AtomicInteger opens = new AtomicInteger();
      var result =
          new InspectorProcess(
                  source,
                  () -> {
                    opens.incrementAndGet();
                    for (var material : source.materials) {
                      byte[] copy = material.copyKey();
                      try {
                        assertEquals(32, copy.length);
                      } finally {
                        Arrays.fill(copy, (byte) 0);
                      }
                    }
                    return connection();
                  },
                  Set.of("v1"),
                  () -> 0)
              .execute(RUN);
      assertEquals(SUCCESS, result.status());
      assertEquals(1, opens.get());
      assertArrayEquals(before, source.keys.get(CONTEXT_CURRENT));
      Arrays.fill(before, (byte) 0);
      source.assertClosed();
    }
    try (var source = new Source()) {
      var failure = new UnsupportedOperationException("public clock fault");
      assertSame(
          failure,
          assertThrows(
              UnsupportedOperationException.class,
              () ->
                  new InspectorProcess(
                          source,
                          noDatabase(),
                          Set.of("v1"),
                          () -> {
                            throw failure;
                          })
                      .execute(RUN)));
      source.assertClosed();
    }
  }

  @Test
  void own002ParentAcceptedThroughActualSqlAndPublicLoaderRetainsRoot() throws Exception {
    try (var source = new Source()) {
      AtomicInteger checks = new AtomicInteger();
      var process =
          new InspectorProcess(
              source,
              InspectorProcessTest::connection,
              Set.of("v1"),
              () -> 0,
              Optional.of(
                  () -> {
                    checks.incrementAndGet();
                    return 1_800_000_000_000L;
                  }));
      assertEquals(SUCCESS, process.execute(RUN).status());
      assertEquals("0|0|0|true", stored());
      assertEquals(4, source.calls);
      assertTrue(checks.get() > 6, "parent must remain checked through keys and SQL");
      source.assertClosed();
      assertThrows(IllegalStateException.class, () -> process.execute(RUN));
    }
    Path directory = Files.createDirectory(root.resolve("own002-public-loader"));
    try (var owned = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), directory)) {
      var loader = new InspectorCredentialLoader(owned, LinuxInodeSecurity.create());
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard unavailable =
          () -> {
            throw new java.io.IOException("synthetic parent unavailable");
          };
      var process = InspectorProcess.withParent(loader, noDatabase(), Set.of("v1"), unavailable);
      assertCredentialFailure(() -> process.execute(RUN));
      assertThrows(IllegalStateException.class, () -> process.execute(RUN));
      assertThrows(
          NullPointerException.class,
          () -> InspectorProcess.withParent(null, noDatabase(), Set.of("v1"), unavailable));
      assertThrows(
          NullPointerException.class,
          () -> InspectorProcess.withParent(loader, noDatabase(), Set.of("v1"), null));
      assertEquals(Boolean.TRUE, owned.atDirectory(Files::isDirectory));
      try (var files = Files.list(directory)) {
        assertEquals(0, files.count());
      }
    }
  }

  @Test
  void sameParentGuardRejectsBeforeKeysAndClosesKeysAfterLaterFailure() throws Exception {
    for (int failAt : List.of(1, 3, 6)) {
      try (var source = new Source()) {
        int[] reads = {0};
        var process =
            new InspectorProcess(
                source,
                noDatabase(),
                Set.of("v1"),
                () -> 0,
                Optional.of(
                    () -> {
                      if (++reads[0] == failAt) throw new java.io.IOException("private owner");
                      return 5_000_000_000L;
                    }));
        assertCredentialFailure(() -> process.execute(RUN));
        assertEquals(failAt, reads[0]);
        assertEquals(failAt == 1 ? 0 : failAt - 2, source.calls);
        source.assertClosed();
        assertThrows(IllegalStateException.class, () -> process.execute(RUN));
      }
    }
  }

  @Test
  void publicLoaderFailureAndRedaction() throws Exception {
    Path directory = Files.createDirectory(root.resolve("public-credential-root"));
    try (var owned = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), directory)) {
      var loader = new InspectorCredentialLoader(owned, LinuxInodeSecurity.create());
      var process = new InspectorProcess(loader, noDatabase(), Set.of("v1"));
      assertCredentialFailure(() -> process.execute(RUN));
      boolean readable = owned.atDirectory(Files::isDirectory);
      assertTrue(readable);
      assertThrows(IllegalStateException.class, () -> process.execute(RUN));
    }
  }

  private static InspectorProcess process(Source source) {
    return new InspectorProcess(source, InspectorProcessTest::connection, Set.of("v1"), () -> 0);
  }

  private static SqlConnectionProvider noDatabase() {
    return () -> {
      throw new AssertionError("credential rejection must precede database");
    };
  }

  private static void assertCredentialFailure(org.junit.jupiter.api.function.Executable action) {
    var failed = assertThrows(InspectorCredentialException.class, action);
    assertEquals("inspector credential cannot be loaded", failed.getMessage());
    assertNull(failed.getCause());
    assertEquals(0, failed.getSuppressed().length);
  }

  private static Connection connection() throws SQLException {
    return DriverManager.getConnection(url, "schubert_inbox_inspector", "");
  }

  private static void sql(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(query);
    }
  }

  private static String scalar(String query) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement();
        var row = s.executeQuery(query)) {
      assertTrue(row.next());
      String value = row.getString(1);
      assertNotNull(value);
      assertFalse(row.next());
      return value;
    }
  }

  private static String stored() throws SQLException {
    return scalar(
        "select inspected_count||'|'||deleted_count||'|'||protected_count||'|'||(completed_at is"
            + " not null)::text from schubert.inbox_inspection_progress");
  }

  private static String inboxCount() throws SQLException {
    return scalar("select count(*) from schubert.request_inbox");
  }

  private static void invalidRows() throws SQLException {
    for (int i = 1; i <= 2; i++) {
      String prefix = i == 1 ? "GAM" : "QSB";
      sql(
          FIXTURE_INSERT_INTO_1D1568AF
              + " schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,owner_user_id,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at,operation_token)"
              + " values('"
              + new UUID(0, i)
              + "','"
              + new UUID(0, i)
              + "','"
              + prefix
              + "REQ01','001',7,repeat('a',64),'v1','ERROR','NONE','"
              + prefix
              + "RSP01','001',decode(repeat('00',30),'hex'),'unknown','2026-09-09','2026-09-09','2026-09-10',"
              + (i == 1 ? "NULL" : "gen_random_uuid()")
              + ")");
    }
  }

  private static void validLoginError(AuthenticationInboxInspectorTest.Fixture f) throws Exception {
    UUID id = new UUID(0, 101);
    var identity = ResponseSnapshotIdentity.anonymous(id, "LGNRSP01", "001");
    var saved = f.saved(identity, "0101", InboxResultReference.none());
    byte[] bytes = saved.responseSnapshot().orElseThrow().ciphertext();
    try (var c = db.admin();
        var s =
            c.prepareStatement(
                FIXTURE_INSERT_INTO_1D1568AF
                    + " schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,response_layout_id,response_version,response_body_encrypted,response_key_version,created_at,completed_at,expires_at)"
                    + " values(?,?,'LGNREQ01','001',repeat('a',64),'v1','ERROR','NONE','LGNRSP01','001',?,'s1','2026-09-09"
                    + " 00:00:00.122+00','2026-09-09 00:00:00.123+00','2026-09-16"
                    + " 00:00:00.123+00')")) {
      s.setObject(1, id);
      s.setObject(2, id);
      s.setBytes(3, bytes);
      assertEquals(1, s.executeUpdate());
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static final class Source implements InspectorProcess.CredentialSource, AutoCloseable {
    final EnumMap<AesCredentialFile, byte[]> keys = new EnumMap<>(AesCredentialFile.class);
    final EnumMap<AesCredentialFile, String> versions = new EnumMap<>(AesCredentialFile.class);
    final Set<AesCredentialFile> absent = EnumSet.noneOf(AesCredentialFile.class);
    final List<InspectorAesCredential> materials = new ArrayList<>();
    Optional<AesCredentialFile> fail = Optional.empty();
    Optional<AesCredentialFile> closed = Optional.empty();
    int calls;

    Source() {
      for (var id : AesCredentialFile.values()) {
        byte[] key = new byte[32];
        new SecureRandom().nextBytes(key);
        keys.put(id, key);
        versions.put(id, "k" + id.ordinal());
      }
    }

    void omitPrevious() {
      absent.addAll(List.of(CONTEXT_PREVIOUS, RESPONSE_PREVIOUS));
    }

    void replace(AesCredentialFile id, byte[] bytes, String version) {
      byte[] copy = bytes.clone();
      Arrays.fill(keys.put(id, copy), (byte) 0);
      versions.put(id, version);
    }

    @Override
    public Optional<InspectorAesCredential> load(AesCredentialFile id)
        throws InspectorCredentialException {
      calls++;
      if (fail.equals(Optional.of(id))) throw new InspectorCredentialException();
      if (absent.contains(id)) return Optional.empty();
      byte[] prefix = ("NKKEY1\n" + versions.get(id) + "\n").getBytes(StandardCharsets.US_ASCII);
      byte[] encoded = Base64.getEncoder().encode(keys.get(id));
      byte[] input = new byte[prefix.length + encoded.length + 1];
      System.arraycopy(prefix, 0, input, 0, prefix.length);
      System.arraycopy(encoded, 0, input, prefix.length, encoded.length);
      input[input.length - 1] = '\n';
      try {
        var material = InspectorAesCredential.consume(input);
        materials.add(material);
        if (closed.equals(Optional.of(id))) material.close();
        return Optional.of(material);
      } finally {
        Arrays.fill(encoded, (byte) 0);
        Arrays.fill(input, (byte) 0);
      }
    }

    void assertClosed() {
      for (var material : materials) assertThrows(IllegalStateException.class, material::copyKey);
    }

    @Override
    public void close() {
      for (var material : materials) material.close();
      for (var key : keys.values()) Arrays.fill(key, (byte) 0);
    }
  }
}
