package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DIR;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.GID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.MANIFEST_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.UID;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupCommitService;
import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** Independent golden file + SQL oracle, SSC067/SS341 6.11/017070, BAT274..281. */
final class BackupBundleCompletionTest {
  private static final String FIXTURE_CLOCK_49F3C56E = "clock";
  private static final String FIXTURE_CONNECTION_COMMIT_37C1B216 = "connection.commit";
  private static final String FIXTURE_SCHUBERT_NK_DUMP_96644B79 = "schubert_nk.dump";
  @TempDir static Path databaseRoot;
  @TempDir Path temporary;
  static BatchDatabaseFixture db;
  static final Instant WALL = Instant.parse("2026-09-12T15:00:04.987654321Z");
  static final Instant END = Instant.parse("2026-09-12T15:00:04.987654Z");
  static final long LIMIT = 1_800_000_000_000L;
  static final Map<String, Integer> INVENTORY =
      Map.ofEntries(
          Map.entry("attributes", 25),
          Map.entry("acl", 25),
          Map.entry("readonly", 25),
          Map.entry("openChannel", 5),
          Map.entry("size", 10),
          Map.entry("read", 10),
          Map.entry("closeChannel", 5),
          Map.entry("openDirectory", 4),
          Map.entry("closeDirectory", 4),
          Map.entry("openEntry", 10),
          Map.entry("closeEntry", 10),
          Map.entry("digest", 4),
          Map.entry("openNames", 2),
          Map.entry("iterator", 2),
          Map.entry("hasNext", 10),
          Map.entry("next", 8),
          Map.entry("closeNames", 2),
          Map.entry("effectiveUid", 4),
          Map.entry(FIXTURE_CLOCK_49F3C56E, 274));

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(databaseRoot);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    reset();
  }

  @Test
  void verifiedCommitAndReplay() throws Exception {
    try (var f = fixture();
        var c = owned()) {
      AtomicReference<Instant> now = new AtomicReference<>(WALL);
      var completion = completion(f, now::get);
      var p = new CompletionJdbcProbe();
      assertEquals(END, complete(completion, p.wrap(c), f));
      assertEquals(INVENTORY, f.counts);
      assertEquals(161, f.position);
      assertEquals(1, p.seen.get(FIXTURE_CONNECTION_COMMIT_37C1B216));
      assertEquals(1, p.seen.get("connection.rollback"));
      assertEquals(4, p.seen.get("connection.setAutoCommit"));
      succeeded(END);
      p.released();
      f.released();
      f.unchanged();
      now.set(WALL.plusSeconds(10));
      assertEquals(END, complete(completion, c, f));
      succeeded(END);
      assertTrue(c.getAutoCommit());
      assertFalse(c.isClosed());
      f.released();
      f.unchanged();
    }
  }

  @Test
  void postCommitReadbackFailureNeverClaimsRollbackOfCommittedPair() throws Exception {
    // Literal operation positions: write transaction false/true, then readback false/true.
    // Every injected failure occurs AFTER the real write commit; independent SQL must still
    // show the two genuine SUCCESS rows, while the public completion does not return success.
    for (String fault :
        List.of(
            "connection.setAutoCommit#3",
            "readback.query",
            "connection.rollback#1",
            "connection.setAutoCommit#4")) {
      reset();
      try (var f = fixture();
          var c = owned()) {
        var p = new CompletionJdbcProbe();
        var hits = new AtomicInteger();
        var committed = new AtomicBoolean();
        p.before =
            (key, n) -> {
              if (key.equals(FIXTURE_CONNECTION_COMMIT_37C1B216)) committed.set(true);
              if ((key + "#" + n).equals(fault)
                  || (fault.equals("readback.query")
                      && committed.get()
                      && key.equals("statement.executeQuery")
                      && hits.get() == 0)) {
                hits.incrementAndGet();
                throw new SQLException("public readback fault");
              }
            };
        repositoryFailure(() -> complete(completion(f, () -> WALL), p.wrap(c), f));
        assertEquals(1, hits.get(), fault);
        assertEquals(1, p.seen.get(FIXTURE_CONNECTION_COMMIT_37C1B216), fault);
        succeeded(END);
        p.released();
        f.released();
        f.unchanged();
      }
    }
  }

  @Test
  void bat539001ChangedValidReadbackTimeNeverReturnsCommittedSuccess() throws Exception {
    // Independent SQL fault AFTER the actual owner write commit. Both complete rows remain
    // otherwise valid, but their time no longer equals the value returned by that commit.
    Instant drift = Instant.parse("2026-09-12T15:00:04.987653Z");
    try (var f = fixture();
        var c = owned()) {
      assertTrue(drift.isAfter(f.expected.contentFinishedAt()));
      var p = new CompletionJdbcProbe();
      var writes = new AtomicInteger();
      p.after =
          (key, n) -> {
            if (key.equals(FIXTURE_CONNECTION_COMMIT_37C1B216)) {
              assertEquals(1, n);
              sql(
                  "update schubert.batch_runs set ended_at='2026-09-12T15:00:04.987653Z'"
                      + " where id in (90000,90001)");
              writes.incrementAndGet();
            }
          };
      repositoryFailure(() -> complete(completion(f, () -> WALL), p.wrap(c), f));
      assertEquals(1, writes.get());
      assertEquals(1, p.seen.get(FIXTURE_CONNECTION_COMMIT_37C1B216));
      assertEquals(0, p.seen.getOrDefault("connection.rollback", 0));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      succeeded(drift);
      p.released();
      f.released();
      f.unchanged();
    }
  }

  @Test
  void invalidFilesAndHandleBinding() throws Exception {
    for (String bad :
        List.of(
            "name",
            "part",
            "manifest",
            "dump",
            "config",
            "credentials",
            "extra",
            "owner",
            "acl",
            "handle")) {
      try (var f = fixture();
          var c = owned()) {
        String name = bad.equals("name") ? ".." : bad.equals("part") ? DIR + ".part" : DIR;
        switch (bad) {
          case "manifest" -> Files.writeString(f.child.resolve("MANIFEST.json"), "{}\n");
          case "dump", "config", "credentials" -> {
            String file =
                bad.equals("dump")
                    ? FIXTURE_SCHUBERT_NK_DUMP_96644B79
                    : bad.equals("config") ? "config.tar" : "credentials.tar.age";
            byte[] bytes = Files.readAllBytes(f.child.resolve(file));
            bytes[0] ^= 1;
            Files.write(f.child.resolve(file), bytes);
          }
          case "extra" -> Files.writeString(f.child.resolve("extra"), "public");
          case "owner" -> f.metadata = (role, values) -> values.put("uid", 9);
          case "acl" -> f.acl = new byte[] {1};
          default -> {}
        }
        var before = f.disk();
        var p = new CompletionJdbcProbe();
        var database = f.expected.databaseStep();
        if (bad.equals("handle"))
          database =
              new BatchStepAttempt(
                  90010, database.run(), database.step(), 1, database.startedAt(), false);
        var fixed = database;
        denied(
            () ->
                completion(f, () -> WALL)
                    .complete(p.wrap(c), name, fixed, f.expected.configurationStep()));
        assertTrue(p.seen.isEmpty(), bad);
        assertDisk(before, f.disk());
        f.released();
        running();
      }
    }
    for (String mutation :
        List.of(
            "update schubert.batch_runs set run_id='22345678-9abc-def0-8123-456789abcdef' where id=90000",
            "update schubert.batch_runs set target_count=1 where id=90000",
            "update schubert.batch_runs set status='SUCCESS',ended_at='2026-09-12T15:00:04.987654Z',target_count=1,success_count=1,byte_count=26 where id=90000")) {
      reset();
      sql(mutation);
      var before = state();
      try (var f = fixture();
          var c = owned()) {
        repositoryFailure(() -> complete(completion(f, () -> WALL), c, f));
        assertEquals(before, state());
        f.released();
        f.unchanged();
      }
    }
  }

  @Test
  void allReadAndDatabaseFailures() throws Exception {
    try (var c = owned()) {
      for (int at = 1; at <= 161; at++) {
        try (var f = fixture()) {
          f.faultAt = at;
          var p = new CompletionJdbcProbe();
          denied(() -> complete(completion(f, () -> WALL), p.wrap(c), f));
          assertTrue(f.position >= at);
          assertTrue(p.seen.isEmpty(), "IO " + at);
          f.released();
          f.unchanged();
        }
      }
      running();
    }
    for (String fault :
        List.of(
            "connection.getAutoCommit#1",
            "statement.executeUpdate#1",
            "statement.executeUpdate#2",
            "connection.commit#1",
            "connection.setAutoCommit#2",
            "connection.rollback#1")) {
      reset();
      try (var f = fixture();
          var c = owned()) {
        var p = new CompletionJdbcProbe();
        var hits = new AtomicInteger();
        p.before =
            (key, n) -> {
              if ((key + "#" + n).equals(fault)) {
                hits.incrementAndGet();
                throw new SQLException("public fault");
              }
              if (fault.equals("connection.rollback#1")
                  && key.equals("statement.executeUpdate")
                  && n == 2) throw new SQLException("public primary");
            };
        repositoryFailure(() -> complete(completion(f, () -> WALL), p.wrap(c), f));
        assertEquals(1, hits.get());
        p.released();
        f.released();
        f.unchanged();
      }
      if (fault.equals("connection.setAutoCommit#2")) succeeded(END);
      else running();
    }
  }

  @Test
  void sharedDeadlineAndInterrupt() throws Exception {
    for (boolean interrupt : List.of(false, true)) {
      for (int at = interrupt ? 1 : 2; at <= 274; at++) {
        reset();
        try (var f = fixture();
            var c = owned()) {
          int target = at;
          f.hook =
              (name, n) -> {
                if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == target) {
                  if (interrupt) Thread.currentThread().interrupt();
                  else f.clockValue = 100 + LIMIT;
                }
              };
          try {
            denied(() -> complete(completion(f, () -> WALL), c, f));
            assertEquals(interrupt, Thread.currentThread().isInterrupted());
          } finally {
            Thread.interrupted();
          }
          f.released();
          f.unchanged();
        }
        if (at == 274) succeeded(END);
        else running();
      }
    }
    for (long elapsed : new long[] {-1, LIMIT + 1, LIMIT - 1}) {
      reset();
      try (var f = fixture();
          var c = owned()) {
        f.hook =
            (name, n) -> {
              if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) f.clockValue = 100 + elapsed;
            };
        if (elapsed == LIMIT - 1) assertEquals(END, complete(completion(f, () -> WALL), c, f));
        else denied(() -> complete(completion(f, () -> WALL), c, f));
        f.released();
        f.unchanged();
      }
    }
    reset();
    try (var f = fixture();
        var c = owned()) {
      f.clockValue = Long.MAX_VALUE - 100;
      f.hook =
          (name, n) -> {
            if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) f.clockValue = Long.MIN_VALUE + 100;
          };
      assertEquals(END, complete(completion(f, () -> WALL), c, f));
      f.released();
      f.unchanged();
    }
  }

  @Test
  void completionClockAndCommitUncertainty() throws Exception {
    for (Instant invalid :
        Arrays.asList(null, Instant.MIN, Instant.MAX, Instant.parse("2026-09-12T15:00:03Z"))) {
      reset();
      try (var f = fixture();
          var c = owned()) {
        var calls = new AtomicInteger();
        Supplier<Instant> clock =
            () -> {
              assertEquals(161, f.position);
              assertEquals(272, f.counts.get(FIXTURE_CLOCK_49F3C56E));
              calls.incrementAndGet();
              return invalid;
            };
        Class<? extends RuntimeException> expectedFailure =
            invalid == null ? NullPointerException.class : IllegalArgumentException.class;
        assertThrows(expectedFailure, () -> complete(completion(f, clock), c, f));
        assertEquals(1, calls.get());
        running();
        f.released();
        f.unchanged();
      }
    }
    reset();
    try (var f = fixture()) {
      try (var c = owned()) {
        var p = new CompletionJdbcProbe();
        p.after =
            (key, n) -> {
              if (key.equals(FIXTURE_CONNECTION_COMMIT_37C1B216))
                throw new SQLException("public uncertain response");
            };
        repositoryFailure(() -> complete(completion(f, () -> WALL), p.wrap(c), f));
        p.released();
        succeeded(END);
        f.released();
      }
      byte[] original = Files.readAllBytes(f.child.resolve(FIXTURE_SCHUBERT_NK_DUMP_96644B79));
      Files.writeString(f.child.resolve(FIXTURE_SCHUBERT_NK_DUMP_96644B79), "public damage");
      try (var c = owned()) {
        var p = new CompletionJdbcProbe();
        denied(() -> complete(completion(f, () -> WALL.plusSeconds(10)), p.wrap(c), f));
        assertTrue(p.seen.isEmpty());
        succeeded(END);
      }
      Files.write(f.child.resolve(FIXTURE_SCHUBERT_NK_DUMP_96644B79), original);
      try (var c = owned()) {
        assertEquals(END, complete(completion(f, () -> WALL.plusSeconds(10)), c, f));
        succeeded(END);
        f.released();
        f.unchanged();
      }
    }
  }

  @Test
  void nullOwnershipAndFactory() throws Exception {
    try (var f = fixture();
        var c = owned()) {
      var reader = reader(f);
      var verifier = f.verifier();
      var commits = new BackupCommitService();
      assertAll(
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> new BackupBundleCompletion(null, verifier, commits, f::clock, () -> WALL)),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> new BackupBundleCompletion(reader, null, commits, f::clock, () -> WALL)),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> new BackupBundleCompletion(reader, verifier, null, f::clock, () -> WALL)),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> new BackupBundleCompletion(reader, verifier, commits, null, () -> WALL)),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> new BackupBundleCompletion(reader, verifier, commits, f::clock, null)),
          () ->
              assertThrows(
                  NullPointerException.class, () -> new BackupBundleCompletion(null, f, UID, GID)),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> new BackupBundleCompletion(f.root, null, UID, GID)));
      for (long bad : new long[] {-1, 0, 0x1_0000_0000L}) {
        assertThrows(
            IllegalArgumentException.class, () -> new BackupBundleCompletion(f.root, f, bad, GID));
        assertThrows(
            IllegalArgumentException.class, () -> new BackupBundleCompletion(f.root, f, UID, bad));
      }
      var service = completion(f, () -> WALL);
      assertAll(
          () -> assertThrows(NullPointerException.class, () -> complete(service, null, f)),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () ->
                      service.complete(
                          c, null, f.expected.databaseStep(), f.expected.configurationStep())),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> service.complete(c, DIR, null, f.expected.configurationStep())),
          () ->
              assertThrows(
                  NullPointerException.class,
                  () -> service.complete(c, DIR, f.expected.databaseStep(), null)));
      assertTrue(f.counts.isEmpty());
      // Real native metadata is not rewritten to claim a deployed root-owned backup.
      denied(() -> complete(new BackupBundleCompletion(f.root, f, UID, GID), c, f));
      f.released();
      f.unchanged();
      assertFalse(c.isClosed());
      f.root.close();
      denied(() -> complete(service, c, f));
      assertTrue(f.directories.isEmpty());
    }
  }

  @Test
  void unknownFailuresAndResourceOwnership() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      for (String stage : List.of("io", FIXTURE_CLOCK_49F3C56E, "wall", "jdbc")) {
        reset();
        try (var f = fixture();
            var c = owned()) {
          Throwable original =
              kind == 0
                  ? new IllegalStateException("public unknown")
                  : kind == 1
                      ? new NullPointerException("public null")
                      : new AssertionError("public fatal");
          var p = new CompletionJdbcProbe();
          if (stage.equals("io")) {
            f.extraFaults.addAll(Set.of("read#1", "closeChannel#1"));
            f.faultTypes.put("read#1", original);
            f.faultTypes.put("closeChannel#1", original);
          }
          if (stage.equals(FIXTURE_CLOCK_49F3C56E))
            f.hook =
                (name, n) -> {
                  if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 2) unchecked(original);
                };
          if (stage.equals("jdbc"))
            p.before =
                (key, n) -> {
                  if (key.equals("statement.executeUpdate") && n == 1) throw original;
                };
          Supplier<Instant> wall =
              () -> {
                if (stage.equals("wall")) unchecked(original);
                return WALL;
              };
          assertSame(
              original,
              assertThrows(Throwable.class, () -> complete(completion(f, wall), p.wrap(c), f)));
          assertEquals(stage.equals("io") ? 1 : 0, original.getSuppressed().length);
          if (stage.equals("io")) {
            var safe = assertInstanceOf(StorageIoException.class, original.getSuppressed()[0]);
            assertNull(safe.getCause());
          }
          p.released();
          f.released();
          f.unchanged();
          running();
        }
      }
    }
  }

  @Test
  void concurrentAndIndependentTrace() throws Exception {
    try (var f = fixture();
        var owner = owned();
        var other = db.open("schubert_batch");
        var pool = Executors.newFixedThreadPool(2)) {
      List<Long> threads = Collections.synchronizedList(new ArrayList<>());
      CountDownLatch entered = new CountDownLatch(1);
      CountDownLatch release = new CountDownLatch(1);
      f.hook =
          (name, n) -> {
            threads.add(Thread.currentThread().threadId());
            if (name.equals(FIXTURE_CLOCK_49F3C56E) && n == 1) {
              entered.countDown();
              try {
                assertTrue(release.await(10, TimeUnit.SECONDS));
              } catch (InterruptedException failure) {
                Thread.currentThread().interrupt();
                throw new AssertionError(failure);
              }
            }
          };
      var completion = completion(f, () -> WALL);
      synchronized (completion) {
        var first = pool.submit(() -> complete(completion, owner, f));
        try {
          assertTrue(entered.await(10, TimeUnit.SECONDS));
          var second =
              pool.submit(
                  () ->
                      assertThrows(
                          BatchRepositoryException.class, () -> complete(completion, other, f)));
          release.countDown();
          assertEquals(END, first.get(10, TimeUnit.SECONDS));
          assertNotNull(second.get(10, TimeUnit.SECONDS));
        } finally {
          release.countDown();
        }
      }
      int changes = 0;
      for (int i = 1; i < threads.size(); i++)
        if (!threads.get(i).equals(threads.get(i - 1))) changes++;
      assertEquals(1, changes);
      succeeded(END);
      f.released();
      f.unchanged();
      Path trace = Path.of("target/backup-completion-traces");
      Files.createDirectories(trace);
      Files.writeString(
          trace.resolve("PT-BAT-281-completion.txt"),
          "manifestSha256="
              + MANIFEST_HASH
              + "\nfiles=4\nDB=1/1/0/26\nCONFIG=2/2/0/67\nend=2026-09-12T15:00:04.987654Z\nowner=SUCCESS\nnonowner=REJECTED\n");
    }
  }

  private BackupArtifactFixture fixture() throws Exception {
    return new BackupArtifactFixture(temporary);
  }

  private static BackupManifestReader reader(BackupArtifactFixture f) {
    return new BackupManifestReader(f.root, f, UID, GID, f, f::clock);
  }

  private static BackupBundleCompletion completion(
      BackupArtifactFixture f, Supplier<Instant> wall) {
    return new BackupBundleCompletion(
        reader(f), f.verifier(), new BackupCommitService(), f::clock, wall);
  }

  private static Instant complete(
      BackupBundleCompletion service, Connection c, BackupArtifactFixture f) throws Exception {
    return service.complete(c, DIR, f.expected.databaseStep(), f.expected.configurationStep());
  }

  private static Connection owned() throws SQLException {
    Connection c = db.open("schubert_batch");
    try (var s = c.createStatement()) {
      s.execute("set timezone='UTC'");
      s.execute("select pg_advisory_lock(71419602)");
    }
    return c;
  }

  private static void reset() throws SQLException {
    sql("delete from schubert.batch_runs");
    sql(
        "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,status) values"
            + "(90000,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','BACKUP_DB',1,'2026-09-12T15:00:00Z','RUNNING'),"
            + "(90001,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','BACKUP_CONFIG',1,'2026-09-12T15:00:01Z','RUNNING')");
  }

  private static void sql(String sql) throws SQLException {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(sql);
    }
  }

  private static List<String> state() throws SQLException {
    var result = new ArrayList<String>();
    try (var c = db.admin();
        var s = c.createStatement();
        var row =
            s.executeQuery(
                "select id,step,status,target_count,success_count,failure_count,byte_count,ended_at from schubert.batch_runs order by id")) {
      while (row.next()) {
        OffsetDateTime end = row.getObject("ended_at", OffsetDateTime.class);
        result.add(
            row.getLong("id")
                + "|"
                + row.getString("step")
                + "|"
                + row.getString("status")
                + "|"
                + row.getLong("target_count")
                + "|"
                + row.getLong("success_count")
                + "|"
                + row.getLong("failure_count")
                + "|"
                + row.getLong("byte_count")
                + "|"
                + (end == null ? "NULL" : end.toInstant()));
      }
    }
    return result;
  }

  private static void running() throws SQLException {
    assertEquals(
        List.of("90000|BACKUP_DB|RUNNING|0|0|0|0|NULL", "90001|BACKUP_CONFIG|RUNNING|0|0|0|0|NULL"),
        state());
  }

  private static void succeeded(Instant end) throws SQLException {
    assertEquals(
        List.of(
            "90000|BACKUP_DB|SUCCESS|1|1|0|26|" + end,
            "90001|BACKUP_CONFIG|SUCCESS|2|2|0|67|" + end),
        state());
  }

  private static void denied(Executable call) {
    var e = assertThrows(StorageIoException.class, call);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, e.reason());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static void repositoryFailure(Executable call) {
    var e = assertThrows(BatchRepositoryException.class, call);
    assertEquals("batch repository operation failed", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static void assertDisk(Map<String, byte[]> expected, Map<String, byte[]> actual) {
    assertEquals(expected.keySet(), actual.keySet());
    for (String name : expected.keySet()) assertArrayEquals(expected.get(name), actual.get(name));
  }

  private static void unchecked(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }
}
