package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.ACT;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.ANCHOR;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.BEGIN;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.CUTOFF;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.DONE;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.END;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.HASH;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.ID;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.MARKER;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.NOW;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.RUN;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.ascii;
import static dev.codex.schubert.nk.batch.file.MaintenanceRetirementRecordsTest.trace;
import static dev.codex.schubert.nk.batch.file.MaintenanceRunFiles.RetirementResult.ABSENT;
import static dev.codex.schubert.nk.batch.file.MaintenanceRunFiles.RetirementResult.PROTECTED;
import static dev.codex.schubert.nk.batch.file.MaintenanceRunFiles.RetirementResult.RETIRED;
import static dev.codex.schubert.nk.batch.file.MaintenanceRunFiles.RetirementResult.TOO_YOUNG;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** SS343 6.16; SSC055/PG161; BAT098..113. Real isolated native files and V018 PostgreSQL. */
final class MaintenanceRunRetirementTest {
  static final String OTHER = "00000000-0000-0000-0000-000000000001";
  static final String SECOND = "00000000-0000-0000-0000-000000000002";
  static final Instant TIME = Instant.parse(NOW);
  static final Map<String, Integer> IO_INVENTORY =
      Map.ofEntries(
          Map.entry("acl", 1075),
          Map.entry("attributes", 1075),
          Map.entry("close", 854),
          Map.entry("create", 2),
          Map.entry("filesystem", 1075),
          Map.entry("force", 2),
          Map.entry("namesClose", 54),
          Map.entry("namesHasNext", 138),
          Map.entry("namesIterator", 54),
          Map.entry("namesNext", 84),
          Map.entry("namesOpen", 54),
          Map.entry("openDirectory", 477),
          Map.entry("openEntry", 324),
          Map.entry("openRead", 57),
          Map.entry("openRoot", 53),
          Map.entry("openWriter", 2),
          Map.entry("publish", 2),
          Map.entry("read", 114),
          Map.entry("readClose", 57),
          Map.entry("readSize", 114),
          Map.entry("readonly", 1075),
          Map.entry("sync", 13),
          Map.entry("unlink", 5),
          Map.entry("write", 2),
          Map.entry("writeSize", 4),
          Map.entry("writerClose", 2));
  @TempDir static Path databaseRoot;
  @TempDir Path temporary;
  static BatchDatabaseFixture db;

  @BeforeAll
  static void startDatabase() throws Exception {
    db = new BatchDatabaseFixture(databaseRoot);
  }

  @AfterAll
  static void stopDatabase() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void clearReferences() throws Exception {
    try (var admin = db.admin()) {
      for (String table :
          List.of("batch_runs", "inbox_inspection_progress", "log_cleanup_progress"))
        sql(admin, "delete from schubert." + table);
    }
  }

  @Test
  void candidatesAndProtectedRuns() throws Exception {
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      other(f, true);
      Files.writeString(f.maintenance.resolve("active"), BEGIN);
      var before = disk(f);
      assertEquals(
          List.of(new BatchRun(UUID.fromString(OTHER), Instant.parse(CUTOFF))),
          f.files.execute(s -> s.retirementCandidates()));
      assertEquals(
          PROTECTED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      assertEquals(before, disk(f));
    }
    try (var f = fixture();
        var c = locked()) {
      var repository = new RunReferenceRepository(c);
      assertEquals(List.of(), f.files.execute(s -> s.retirementCandidates()));
      seed(f);
      other(f, true);
      var otherRun = new BatchRun(UUID.fromString(OTHER), Instant.parse(CUTOFF));
      List<BatchRun> candidates = f.files.execute(s -> s.retirementCandidates());
      assertEquals(List.of(otherRun, RUN), candidates);
      assertThrows(UnsupportedOperationException.class, () -> candidates.add(RUN));
      Files.delete(f.attempts.resolve(SECOND + ".done"));
      Files.writeString(
          f.maintenance.resolve("active"), BEGIN.replace(ID, OTHER).replace(ACT, SECOND));
      assertEquals(List.of(RUN), f.files.execute(s -> s.retirementCandidates()));
      Map<String, String> before = disk(f);
      assertEquals(PROTECTED, f.files.execute(s -> s.retire(otherRun, TIME, repository)));
      assertEquals(before, disk(f));
      assertEquals(RETIRED, f.files.execute(s -> s.retire(RUN, TIME, repository)));
      assertEquals(before.get("active"), Files.readString(f.maintenance.resolve("active")));
      assertEquals(List.of(), f.files.execute(s -> s.retirementCandidates()));
    }
    for (boolean begin : List.of(false, true))
      try (var f = fixture();
          var c = locked()) {
        Files.writeString(f.runs.resolve(ID + ".run"), ANCHOR);
        if (begin) Files.writeString(f.attempts.resolve(ACT + ".begin"), BEGIN);
        var before = disk(f);
        assertEquals(
            PROTECTED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
        assertEquals(before, disk(f));
      }
  }

  @Test
  void strictAgeAndLatestCompletion() throws Exception {
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      var repository = new RunReferenceRepository(c);
      var before = disk(f);
      for (Instant time : List.of(Instant.parse(CUTOFF), TIME.minusNanos(1000)))
        assertEquals(TOO_YOUNG, f.files.execute(s -> s.retire(RUN, time, repository)));
      assertEquals(before, disk(f));
      for (Instant wrong : List.of(Instant.MIN, Instant.MAX, TIME.plusNanos(1)))
        assertThrows(
            IllegalArgumentException.class,
            () -> f.files.execute(s -> s.retire(RUN, wrong, repository)));
      Files.writeString(f.attempts.resolve(SECOND + ".begin"), BEGIN.replace(ACT, SECOND));
      Files.writeString(
          f.attempts.resolve(SECOND + ".done"),
          DONE.replace(ACT, SECOND)
              .replace(END, "2025-01-03T00:00:00.000000Z")
              .replace("\n0\n", "\n10\n"));
      assertEquals(TOO_YOUNG, f.files.execute(s -> s.retire(RUN, TIME, repository)));
      var probe = new QueryProbe(c);
      String twoMarker =
          MARKER
              .replace(END, "2025-01-03T00:00:00.000000Z")
              .replace(NOW, "2026-02-07T00:00:00.000001Z")
              .replace("\n1\n", "\n2\n")
              .replace(HASH, "e6ff18dc21a10852fe4de7e8606fe0ad005c8e242bdc535ea8d391dd052528de");
      probe.beforeQuery =
          () -> {
            String marker = disk(f).get(ID + ".retire");
            if (marker != null) {
              assertEquals(twoMarker, marker);
              trace("PT-BAT-099-two-activation-marker.txt", ascii(marker));
            }
          };
      assertEquals(
          RETIRED,
          f.files.execute(
              s ->
                  s.retire(
                      RUN,
                      TIME.plusSeconds(86400),
                      new RunReferenceRepository(probe.connection()))));
      assertEquals(Map.of(), disk(f));
    }
  }

  @Test
  void referenceCombinations() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      var repository = new RunReferenceRepository(c);
      for (int mask = 0; mask < 8; mask++) {
        clearReferences();
        references(admin, mask);
        try (var f = fixture()) {
          seed(f);
          var before = disk(f);
          assertEquals(
              mask == 0 ? RETIRED : PROTECTED,
              f.files.execute(s -> s.retire(RUN, TIME, repository)),
              "mask=" + mask);
          assertEquals(mask == 0 ? Map.of() : before, disk(f));
        }
      }
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertEquals(Connection.TRANSACTION_READ_COMMITTED, c.getTransactionIsolation());
    }
  }

  @Test
  void missingAndContradictoryIdentity() throws Exception {
    try (var f = fixture();
        var c = locked();
        var admin = db.admin()) {
      var repository = new RunReferenceRepository(c);
      assertEquals(ABSENT, f.files.execute(s -> s.retire(RUN, TIME, repository)));
      seed(f);
      var before = disk(f);
      failure(
          () ->
              f.files.execute(
                  s ->
                      s.retire(
                          new BatchRun(RUN.id(), RUN.cutoff().plusNanos(1000)), TIME, repository)));
      assertEquals(before, disk(f));
      references(admin, 2);
      sql(
          admin,
          "update schubert.inbox_inspection_progress set cutoff=cutoff+interval '1 microsecond'");
      failure(() -> f.files.execute(s -> s.retire(RUN, TIME, repository)));
      assertEquals(before, disk(f));
      Files.delete(f.runs.resolve(ID + ".run"));
      failure(() -> f.files.execute(s -> s.retirementCandidates()));
    }
  }

  @Test
  void newRetirementPreservesOtherRuns() throws Exception {
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      other(f, true);
      Map<String, String> expected = new HashMap<>(disk(f));
      expected.keySet().removeIf(key -> key.contains(ID) || key.contains(ACT));
      var probe = new QueryProbe(c);
      List<Set<String>> snapshots = new ArrayList<>();
      probe.beforeQuery =
          () -> {
            var values = disk(f);
            snapshots.add(Set.copyOf(values.keySet()));
            String marker = values.get(ID + ".retire");
            if (marker != null) {
              assertEquals(MARKER, marker);
              trace("PT-BAT-102-marker.txt", ascii(marker));
            }
          };
      assertEquals(
          RETIRED,
          f.files.execute(
              s -> s.retire(RUN, TIME, new RunReferenceRepository(probe.connection()))));
      assertEquals(expected, disk(f));
      // Independent required sequence, allowing repeated validations at a stable phase.
      List<Set<String>> phases = new ArrayList<>();
      for (Set<String> snapshot : snapshots) {
        Set<String> selected = new TreeSet<>(snapshot);
        selected.removeAll(expected.keySet());
        if (phases.isEmpty() || !phases.getLast().equals(selected)) phases.add(selected);
      }
      String run = "runs/" + ID + ".run";
      String begin = "attempts/" + ACT + ".begin";
      String done = "attempts/" + ACT + ".done";
      String plan = "attempts/" + ACT + ".plan";
      String marker = ID + ".retire";
      assertEquals(
          List.of(
              Set.of(run, begin, done),
              Set.of(run, begin, done, plan),
              Set.of(run, begin, done, plan, marker),
              Set.of(run, begin, plan, marker),
              Set.of(run, plan, marker),
              Set.of(plan, marker),
              Set.of(marker),
              Set.of()),
          phases);
      assertEquals(10, probe.queries); // Initial + 7 mutations + original barrier + final.
      StringBuilder trace = new StringBuilder();
      for (int index = 0; index < phases.size(); index++) {
        trace.append("phase").append(index).append(":\n");
        for (String name : new TreeSet<>(phases.get(index))) trace.append(name).append('\n');
      }
      trace("PT-BAT-102-phases.txt", ascii(trace.toString()));
    }
  }

  @Test
  void preMarkerPlanRecovery() throws Exception {
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      Files.writeString(f.attempts.resolve(ACT + ".plan"), DONE);
      assertEquals(List.of(RUN), f.files.execute(s -> s.retirementCandidates()));
      failure(() -> f.files.execute(s -> s.resume(RUN.id(), UUID.fromString(SECOND))));
      assertEquals(
          RETIRED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      assertEquals(Map.of(), disk(f));
    }
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      Files.writeString(f.attempts.resolve(SECOND + ".begin"), BEGIN.replace(ACT, SECOND));
      Files.writeString(f.attempts.resolve(SECOND + ".done"), DONE.replace(ACT, SECOND));
      Files.writeString(f.attempts.resolve(ACT + ".plan"), DONE);
      assertEquals(
          RETIRED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      assertEquals(Map.of(), disk(f));
    }
  }

  @Test
  void markerOriginalRecovery() throws Exception {
    for (int stage = 0; stage < 3; stage++)
      try (var f = fixture();
          var c = locked()) {
        seededMarker(f, stage);
        assertEquals(List.of(RUN), f.files.execute(s -> s.retirementCandidates()));
        assertEquals(
            RETIRED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
        assertEquals(Map.of(), disk(f));
        assertEquals(
            ABSENT, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      }
  }

  @Test
  void metadataOnlyRecovery() throws Exception {
    for (int stage : List.of(3, 4))
      try (var f = fixture();
          var c = locked()) {
        seededMarker(f, stage);
        assertEquals(List.of(RUN), f.files.execute(s -> s.retirementCandidates()));
        f.reset();
        f.on(
            "unlink",
            1,
            () ->
                assertEquals(
                    List.of(
                        "var/lib/schubert-nk/maintenance", // same-marker re-publication barrier
                        "var/lib/schubert-nk/maintenance",
                        "var/lib/schubert-nk/maintenance/runs",
                        "var/lib/schubert-nk/maintenance/attempts"),
                    f.syncTargets));
        assertEquals(
            RETIRED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
        assertEquals(Map.of(), disk(f));
      }
    // BUG172: each original-directory barrier must fail BEFORE any recovery metadata disappears.
    for (int stage : List.of(3, 4))
      for (int at = 2; at <= 4; at++)
        try (var f = fixture();
            var c = locked()) {
          seededMarker(f, stage);
          var before = disk(f);
          f.reset();
          f.fail = "sync";
          f.failAt = at;
          failure(() -> f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
          assertTrue(f.triggered);
          assertEquals(before, disk(f));
          assertEquals(0, f.count("unlink"));
          f.reset();
          assertEquals(
              RETIRED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
          assertEquals(Map.of(), disk(f));
        }
    for (String extra : List.of("begin", "done"))
      try (var f = fixture();
          var c = locked()) {
        seededMarker(f, 3);
        Files.writeString(
            f.attempts.resolve(ACT + "." + extra), extra.equals("begin") ? BEGIN : DONE);
        var before = disk(f);
        failure(() -> f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
        assertEquals(before, disk(f));
      }
  }

  @Test
  void planCompletenessAndDigest() throws Exception {
    for (String fault : List.of("beginCutoff", "beginCollision", "doneCollision"))
      try (var f = fixture();
          var c = locked()) {
        seededMarker(f, 0);
        switch (fault) {
          case "beginCutoff" ->
              Files.writeString(
                  f.attempts.resolve(ACT + ".begin"),
                  BEGIN.replace(CUTOFF, "2025-01-01T00:00:00.000001Z"));
          case "beginCollision" -> {
            Files.writeString(f.runs.resolve(OTHER + ".run"), ANCHOR.replace(ID, OTHER));
            Files.writeString(f.attempts.resolve(ACT + ".begin"), BEGIN.replace(ID, OTHER));
          }
          case "doneCollision" -> {
            Files.delete(f.attempts.resolve(ACT + ".begin"));
            Files.writeString(f.runs.resolve(OTHER + ".run"), ANCHOR.replace(ID, OTHER));
            Files.writeString(f.attempts.resolve(ACT + ".done"), DONE.replace(ID, OTHER));
          }
          default -> throw new AssertionError(fault);
        }
        var before = disk(f);
        failure(() -> f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
        assertEquals(before, disk(f), fault);
      }
    for (String fault :
        List.of(
            "missing",
            "extra",
            "digest",
            "count",
            "latest",
            "value",
            "foreignBegin",
            "foreignDone"))
      try (var f = fixture();
          var c = locked()) {
        seededMarker(f, 0);
        switch (fault) {
          case "missing" -> Files.delete(f.attempts.resolve(ACT + ".plan"));
          case "extra" ->
              Files.writeString(f.attempts.resolve(SECOND + ".plan"), DONE.replace(ACT, SECOND));
          case "digest" ->
              Files.writeString(
                  f.maintenance.resolve(ID + ".retire"), MARKER.replace(HASH, "0".repeat(64)));
          case "count" ->
              Files.writeString(
                  f.maintenance.resolve(ID + ".retire"), MARKER.replace("\n1\n", "\n2\n"));
          case "latest" ->
              Files.writeString(f.maintenance.resolve(ID + ".retire"), MARKER.replace(END, CUTOFF));
          case "value" ->
              Files.writeString(f.attempts.resolve(ACT + ".plan"), DONE.replace("\n0\n", "\n10\n"));
          case "foreignBegin" ->
              Files.writeString(f.attempts.resolve(SECOND + ".begin"), BEGIN.replace(ACT, SECOND));
          case "foreignDone" ->
              Files.writeString(f.attempts.resolve(SECOND + ".done"), DONE.replace(ACT, SECOND));
          default -> throw new AssertionError(fault);
        }
        var before = disk(f);
        failure(() -> f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
        assertEquals(before, disk(f), fault);
      }
  }

  @Test
  void namespaceAndForeignArtifacts() throws Exception {
    for (String fault :
        List.of(
            "unknown", "part", "secondMarker", "foreignPlan", "active", "pending", "orphanPlan"))
      try (var f = fixture();
          var c = locked()) {
        seededMarker(f, 0);
        switch (fault) {
          case "unknown" -> Files.writeString(f.maintenance.resolve("unknown"), "synthetic");
          case "part" -> Files.writeString(f.attempts.resolve(SECOND + ".part"), DONE);
          case "secondMarker" ->
              Files.writeString(
                  f.maintenance.resolve(OTHER + ".retire"), MARKER.replace(ID, OTHER));
          case "foreignPlan" ->
              Files.writeString(
                  f.attempts.resolve(SECOND + ".plan"),
                  DONE.replace(ID, OTHER).replace(ACT, SECOND));
          case "active" -> Files.writeString(f.maintenance.resolve("active"), BEGIN);
          case "pending" -> {
            Files.delete(f.maintenance.resolve(ID + ".retire"));
            Files.writeString(f.attempts.resolve(SECOND + ".begin"), BEGIN.replace(ACT, SECOND));
          }
          case "orphanPlan" -> {
            Files.delete(f.maintenance.resolve(ID + ".retire"));
            Files.writeString(f.attempts.resolve(ACT + ".plan"), DONE.replace("\n0\n", "\n10\n"));
          }
          default -> throw new AssertionError(fault);
        }
        var before = disk(f);
        failure(() -> f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
        assertEquals(before, disk(f), fault);
      }
  }

  @Test
  void referenceReappearanceAndDbFaults() throws Exception {
    for (String mode : List.of("reference", "sql", "inconsistent"))
      for (int at = 2; at <= 10; at++)
        try (var f = fixture();
            var c = locked();
            var admin = db.admin()) {
          clearReferences();
          seed(f);
          var probe = new QueryProbe(c);
          int position = at;
          probe.beforeQuery =
              () -> {
                if (probe.queries == position) {
                  if (mode.equals("sql")) throw new SQLException("synthetic provider detail");
                  references(admin, 2);
                  if (mode.equals("inconsistent"))
                    sql(
                        admin,
                        "update schubert.inbox_inspection_progress set cutoff=cutoff+interval '1 microsecond'");
                }
              };
          if (mode.equals("sql")) {
            var error =
                assertThrows(
                    BatchRepositoryException.class,
                    () ->
                        f.files.execute(
                            s ->
                                s.retire(
                                    RUN, TIME, new RunReferenceRepository(probe.connection()))));
            assertNull(error.getCause());
            assertEquals(0, error.getSuppressed().length);
          } else
            failure(
                () ->
                    f.files.execute(
                        s -> s.retire(RUN, TIME, new RunReferenceRepository(probe.connection()))));
          assertEquals(at, probe.queries);
          assertFalse(c.isClosed());
          f.released();
        }
  }

  @Test
  void publicationAndDeletionCrashes() throws Exception {
    Map<String, Integer> count;
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      f.reset();
      assertEquals(
          RETIRED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      count = Map.copyOf(f.counts);
    }
    for (String operation : List.of("publish", "unlink", "sync"))
      for (int at = 1; at <= Objects.requireNonNull(count.get(operation)); at++)
        try (var f = fixture();
            var c = locked()) {
          seed(f);
          f.reset();
          f.fail = operation;
          f.failAt = at;
          failure(() -> f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
          assertTrue(f.triggered);
          var interrupted = disk(f);
          f.reset();
          if (interrupted.keySet().stream().anyMatch(key -> key.endsWith(".part"))) {
            failure(() -> f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
            assertEquals(interrupted, disk(f));
          } else {
            var result = f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c)));
            assertTrue(result == RETIRED || result == ABSENT);
            assertEquals(Map.of(), disk(f));
          }
        }
  }

  @Test
  void everyIoFailurePreservesState() throws Exception {
    Map<String, Integer> count;
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      f.reset();
      assertEquals(
          RETIRED, f.files.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      count = Map.copyOf(f.counts);
    }
    // SS/PT independent inventory: 18 scans, 48 scanned records, 9 mutation verification reads.
    // Added original barrier = two2-record scans plus three directory syncs; see015/BUG172.
    assertEquals(IO_INVENTORY, count);
    Path report = Path.of("target", "run-retirement-io-inventory.txt");
    Files.createDirectories(report.getParent());
    Files.writeString(report, new TreeMap<>(count).toString());
    var faults = new ArrayList<IoFault>();
    for (var operation : new TreeMap<>(IO_INVENTORY).entrySet())
      for (int at = 1; at <= operation.getValue(); at++)
        faults.add(new IoFault(operation.getKey(), at));
    assertEquals(6768, faults.size());
    var expected = Set.copyOf(faults);
    assertEquals(6768, expected.size());
    Set<IoFault> executed = ConcurrentHashMap.newKeySet();
    // Independent clusters avoid both JDBC sharing and advisory-lock serialization.
    // Each native fixture is created/closed in its worker; preserve the four-segment path oracle.
    try (var second =
            new DatabaseShard(
                new BatchDatabaseFixture(Files.createTempDirectory(temporary, "db2-")));
        var third =
            new DatabaseShard(
                new BatchDatabaseFixture(Files.createTempDirectory(temporary, "db3-")));
        var fourth =
            new DatabaseShard(
                new BatchDatabaseFixture(Files.createTempDirectory(temporary, "db4-")));
        var executor = Executors.newFixedThreadPool(4)) {
      var databases = List.of(db, second.database(), third.database(), fourth.database());
      var futures = new ArrayList<Future<Integer>>();
      for (int shard = 0; shard < 4; shard++) {
        final int worker = shard;
        futures.add(
            executor.submit(
                () -> {
                  int completed = 0;
                  try (var c = locked(databases.get(worker))) {
                    for (int position = worker; position < faults.size(); position += 4) {
                      if (Thread.currentThread().isInterrupted())
                        throw new InterruptedException("PT shard interrupted");
                      var fault = faults.get(position);
                      try (var f = fixture()) {
                        seed(f);
                        f.reset();
                        f.fail = fault.operation();
                        f.failAt = fault.occurrence();
                        failure(
                            () ->
                                f.files.execute(
                                    s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
                        assertTrue(f.triggered, fault.toString());
                        f.released();
                        assertTrue(executed.add(fault), "duplicate fault execution");
                      }
                      completed++;
                    }
                  }
                  return completed;
                }));
      }
      int completed = 0;
      try {
        for (var future : futures) completed += future.get(10, TimeUnit.MINUTES);
      } finally {
        for (var future : futures) if (!future.isDone()) future.cancel(true);
      }
      assertEquals(6768, completed);
    }
    assertEquals(expected, executed);
  }

  @Test
  void scopeNullAndInterruption() throws Exception {
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      var repository = new RunReferenceRepository(c);
      assertThrows(
          NullPointerException.class, () -> f.files.execute(s -> s.retire(null, TIME, repository)));
      assertThrows(
          NullPointerException.class, () -> f.files.execute(s -> s.retire(RUN, null, repository)));
      assertThrows(
          NullPointerException.class, () -> f.files.execute(s -> s.retire(RUN, TIME, null)));
      var before = disk(f);
      Thread.currentThread().interrupt();
      try {
        failure(() -> f.files.execute(s -> s.retirementCandidates()));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      assertEquals(before, disk(f));
      f.reset();
      f.on("namesOpen", 1, () -> Thread.currentThread().interrupt());
      try {
        failure(() -> f.files.execute(s -> s.retire(RUN, TIME, repository)));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
  }

  @Test
  void concurrentAndClosedScope() throws Exception {
    try (var f = fixture();
        var c = locked();
        var executor = Executors.newFixedThreadPool(2)) {
      seed(f);
      AtomicReference<MaintenanceRunFiles.Session> saved = new AtomicReference<>();
      CountDownLatch entered = new CountDownLatch(1);
      CountDownLatch release = new CountDownLatch(1);
      CountDownLatch competing = new CountDownLatch(1);
      f.on(
          "namesOpen",
          1,
          () -> {
            entered.countDown();
            try {
              assertTrue(release.await(10, TimeUnit.SECONDS));
            } catch (InterruptedException e) {
              Thread.currentThread().interrupt();
              throw new IOException("test interrupted");
            }
          });
      assertEquals(
          RETIRED,
          f.files.execute(
              s -> {
                saved.set(s);
                try {
                  var deletion =
                      executor.submit(() -> s.retire(RUN, TIME, new RunReferenceRepository(c)));
                  assertTrue(entered.await(10, TimeUnit.SECONDS));
                  var reader =
                      executor.submit(
                          () -> {
                            competing.countDown();
                            return s.retirementCandidates();
                          });
                  assertTrue(competing.await(10, TimeUnit.SECONDS));
                  assertFalse(reader.isDone());
                  release.countDown();
                  assertEquals(List.of(), reader.get(10, TimeUnit.SECONDS));
                  return deletion.get(10, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                  Thread.currentThread().interrupt();
                  throw new IOException("test interrupted");
                } catch (ExecutionException | TimeoutException e) {
                  throw new AssertionError(e);
                } finally {
                  release.countDown();
                }
              }));
      failure(() -> saved.get().retirementCandidates());
      failure(() -> saved.get().retire(RUN, TIME, new RunReferenceRepository(c)));
      assertEquals(Map.of(), disk(f));
    }
  }

  @Test
  void resourceCloseAndDigestFailure() throws Exception {
    try (var f = fixture();
        var c = locked()) {
      seed(f);
      assertThrows(
          NullPointerException.class,
          () -> new MaintenanceRunFiles(f.varPath, f.calls, f, f, f::part, null));
      var broken =
          new MaintenanceRunFiles(
              f.varPath,
              f.calls,
              f,
              f,
              f::part,
              () -> {
                throw new NoSuchAlgorithmException("synthetic provider detail");
              });
      failure(() -> broken.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      assertTrue(Files.exists(f.attempts.resolve(ACT + ".plan")));
      assertFalse(Files.exists(f.maintenance.resolve(ID + ".retire")));
      f.released();
      var nullDigest = new MaintenanceRunFiles(f.varPath, f.calls, f, f, f::part, () -> null);
      assertThrows(
          NullPointerException.class,
          () -> nullDigest.execute(s -> s.retire(RUN, TIME, new RunReferenceRepository(c))));
      f.released();
      f.rawCloses = true;
      failure(() -> f.files.execute(s -> s.retirementCandidates()));
      f.released();
    }
  }

  private MaintenanceRunFilesTest.Fixture fixture() throws Exception {
    var fixture =
        new MaintenanceRunFilesTest.Fixture(Files.createTempDirectory(temporary, "retire-"));
    assertEquals(4, fixture.varPath.getNameCount(), "fixed PT native path-walk inventory");
    return fixture;
  }

  private static void seed(MaintenanceRunFilesTest.Fixture f) throws IOException {
    Files.writeString(f.runs.resolve(ID + ".run"), ANCHOR);
    Files.writeString(f.attempts.resolve(ACT + ".begin"), BEGIN);
    Files.writeString(f.attempts.resolve(ACT + ".done"), DONE);
  }

  private static void other(MaintenanceRunFilesTest.Fixture f, boolean completed)
      throws IOException {
    Files.writeString(f.runs.resolve(OTHER + ".run"), ANCHOR.replace(ID, OTHER));
    Files.writeString(
        f.attempts.resolve(SECOND + ".begin"), BEGIN.replace(ID, OTHER).replace(ACT, SECOND));
    if (completed)
      Files.writeString(
          f.attempts.resolve(SECOND + ".done"), DONE.replace(ID, OTHER).replace(ACT, SECOND));
  }

  private static void seededMarker(MaintenanceRunFilesTest.Fixture f, int stage)
      throws IOException {
    seed(f);
    Files.writeString(f.attempts.resolve(ACT + ".plan"), DONE);
    Files.writeString(f.maintenance.resolve(ID + ".retire"), MARKER);
    if (stage >= 1) Files.delete(f.attempts.resolve(ACT + ".done"));
    if (stage >= 2) Files.delete(f.attempts.resolve(ACT + ".begin"));
    if (stage >= 3) Files.delete(f.runs.resolve(ID + ".run"));
    if (stage >= 4) Files.delete(f.attempts.resolve(ACT + ".plan"));
  }

  private static Map<String, String> disk(MaintenanceRunFilesTest.Fixture f) throws IOException {
    Map<String, String> result = new TreeMap<>();
    try (var paths = Files.walk(f.maintenance)) {
      for (var path : paths.filter(Files::isRegularFile).toList())
        result.put(f.maintenance.relativize(path).toString(), Files.readString(path));
    }
    return result;
  }

  private record IoFault(String operation, int occurrence) {}

  private record DatabaseShard(BatchDatabaseFixture database) implements AutoCloseable {
    @Override
    public void close() throws IOException {
      boolean interrupted = Thread.interrupted();
      try {
        database.stop();
      } catch (InterruptedException failure) {
        interrupted = true;
        throw new IOException("PT database stop interrupted", failure);
      } finally {
        if (interrupted) Thread.currentThread().interrupt();
      }
    }
  }

  private static Connection locked() throws SQLException {
    return locked(db);
  }

  private static Connection locked(BatchDatabaseFixture source) throws SQLException {
    var connection = source.open("schubert_batch");
    sql(connection, "select pg_advisory_lock(71419602)");
    connection.setAutoCommit(false);
    return connection;
  }

  private static void sql(Connection connection, String query) throws SQLException {
    try (var statement = connection.createStatement()) {
      statement.execute(query);
    }
  }

  private static void references(Connection admin, int mask) throws SQLException {
    if ((mask & 1) != 0)
      sql(
          admin,
          "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,status) values('"
              + ID
              + "','2025-01-01','RETIRE_TEST',1,'2025-01-01T00:00:00Z','RUNNING')");
    if ((mask & 2) != 0)
      sql(
          admin,
          "insert into schubert.inbox_inspection_progress(run_id,cutoff) values('"
              + ID
              + "','"
              + CUTOFF
              + "')");
    if ((mask & 4) != 0)
      sql(
          admin,
          "insert into schubert.log_cleanup_progress(run_id,cutoff) values('"
              + ID
              + "','"
              + CUTOFF
              + "')");
  }

  private static void failure(Executable action) {
    var error = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  @FunctionalInterface
  interface QueryHook {
    void execute() throws Exception;
  }

  private static final class QueryProbe {
    final Connection real;
    int queries;
    QueryHook beforeQuery = () -> {};

    QueryProbe(Connection real) {
      this.real = real;
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (method.getName().equals("prepareStatement")) {
                  queries++;
                  beforeQuery.execute();
                }
                try {
                  return method.invoke(real, args);
                } catch (InvocationTargetException e) {
                  throw e.getCause();
                }
              });
    }
  }
}
