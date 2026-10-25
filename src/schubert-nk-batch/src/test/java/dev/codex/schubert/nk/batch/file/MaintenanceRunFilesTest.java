package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PG158/SSC055; OPS009/UI251/SS343 6.15; PT-BAT-058..081, independent bytes/crash states. */
final class MaintenanceRunFilesTest {
  private static final String RUN_ID = "12345678-9abc-def0-8123-456789abcdef";
  private static final String ACT_ID = "fedcba98-7654-3210-8fed-cba987654321";
  private static final UUID NEXT = UUID.fromString("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee");
  private static final UUID OTHER = UUID.fromString("11111111-2222-3333-4444-555555555555");
  private static final BatchRun RUN =
      new BatchRun(UUID.fromString(RUN_ID), Instant.parse("2026-09-12T04:05:06.123456Z"));
  private static final MaintenanceActivation ACTIVATION =
      new MaintenanceActivation(RUN, UUID.fromString(ACT_ID));
  private static final String ANCHOR = "NKRUN1\n" + RUN_ID + "\n2026-09-12T04:05:06.123456Z\n";
  private static final String BEGIN =
      "NKACT1\n" + RUN_ID + "\n2026-09-12T04:05:06.123456Z\n" + ACT_ID + "\n";
  private static final String DONE_PREFIX =
      "NKDONE1\n"
          + RUN_ID
          + "\n2026-09-12T04:05:06.123456Z\n"
          + ACT_ID
          + "\n2026-09-12T05:06:07.234567Z\n";
  private static final String DONE0 = DONE_PREFIX + "0\n";
  private static final String DONE10 = DONE_PREFIX + "10\n";
  @TempDir Path temporary;

  /**
   * BUG968/RLOOK852001: real same Session, unchanged historical reference after active retirement.
   */
  @Test
  void doneAfterRealSessionRetainsTypedDataReferenceButRejectsPendingCapability() throws Exception {
    try (var f = fixture()) {
      f.files.execute(
          s -> {
            s.start(RUN, ACTIVATION.id());
            assertEquals(RUN, s.successReferenceRun(ACTIVATION, RUN.id(), RUN.cutoff()));
            var done =
                new MaintenanceCompletion(
                    ACTIVATION,
                    Instant.parse("2026-09-12T05:06:07.234567Z"),
                    MaintenanceCompletion.Outcome.SUCCESS);
            assertEquals(done, s.complete(done));
            assertEquals(
                new MaintenanceRunFiles.StartupOriginal(ACTIVATION, Optional.of(done)),
                s.observeStartup(ACTIVATION));
            assertFalse(Files.exists(f.maintenance.resolve("active")));
            assertEquals(DONE0, Files.readString(f.attempts.resolve(ACT_ID + ".done")));
            assertThrows(
                IOException.class, () -> s.successReferenceRun(ACTIVATION, RUN.id(), RUN.cutoff()));
            var before = new HashMap<>(f.counts);
            assertEquals(RUN, s.completedSuccessReferenceRun(done, RUN.id(), RUN.cutoff()));
            assertEquals(before.getOrDefault("write", 0), f.counts.getOrDefault("write", 0));
            assertEquals(before.getOrDefault("remove", 0), f.counts.getOrDefault("remove", 0));
            assertEquals(DONE0, Files.readString(f.attempts.resolve(ACT_ID + ".done")));
            return RUN;
          });
    }
  }

  /**
   * RLOOK852002: completed current is exact data proof, never missing/failed/future/foreign
   * authority.
   */
  @Test
  void completedReferenceRefusesForeignDonePendingUnknownAndHistoricalTimeFaults()
      throws Exception {
    try (var f = fixture()) {
      f.files.execute(
          s -> {
            s.start(RUN, ACTIVATION.id());
            var done = completion(MaintenanceCompletion.Outcome.SUCCESS);
            assertThrows(
                IOException.class,
                () -> s.completedSuccessReferenceRun(done, RUN.id(), RUN.cutoff()));
            s.complete(done);
            for (var bad :
                List.of(
                    completion(MaintenanceCompletion.Outcome.WARNING),
                    new MaintenanceCompletion(
                        ACTIVATION,
                        done.endedAt().plusNanos(1000),
                        MaintenanceCompletion.Outcome.SUCCESS),
                    new MaintenanceCompletion(
                        new MaintenanceActivation(RUN, NEXT),
                        done.endedAt(),
                        MaintenanceCompletion.Outcome.SUCCESS)))
              assertThrows(
                  IOException.class,
                  () -> s.completedSuccessReferenceRun(bad, RUN.id(), RUN.cutoff()));
            for (Instant t :
                List.of(
                    RUN.cutoff().minusNanos(1000),
                    RUN.cutoff().plusNanos(1),
                    Instant.parse("9999-12-31T23:59:59.999999Z").plusNanos(1000)))
              assertThrows(
                  IOException.class, () -> s.completedSuccessReferenceRun(done, RUN.id(), t));
            assertThrows(
                IOException.class, () -> s.completedSuccessReferenceRun(done, NEXT, RUN.cutoff()));
            assertThrows(
                NullPointerException.class,
                () -> s.completedSuccessReferenceRun(null, RUN.id(), RUN.cutoff()));
            assertThrows(
                NullPointerException.class,
                () -> s.completedSuccessReferenceRun(done, null, RUN.cutoff()));
            assertThrows(
                NullPointerException.class,
                () -> s.completedSuccessReferenceRun(done, RUN.id(), null));
            return RUN;
          });
    }
  }

  /** RLOOK200001: independent retained bytes/cutoff, not a DB-derived original. */
  @Test
  void completedWarningRetainsHistoricalPriorButNeverPendingOrForeignActive() throws Exception {
    try (var f = fixture()) {
      f.seed(true, false, true);
      var current = new BatchRun(NEXT, Instant.parse("2026-09-12T06:00:00Z"));
      var activation = new MaintenanceActivation(current, OTHER);
      var done =
          new MaintenanceCompletion(
              activation,
              Instant.parse("2026-09-12T07:00:00Z"),
              MaintenanceCompletion.Outcome.WARNING);
      f.files.execute(s -> s.start(current, OTHER));
      f.files.execute(s -> s.complete(done));
      assertEquals(
          RUN,
          f.files.execute(s -> s.completedSuccessReferenceRun(done, RUN.id(), current.cutoff())));
      assertEquals(
          current,
          f.files.execute(s -> s.completedSuccessReferenceRun(done, NEXT, current.cutoff())));
      assertThrows(
          IOException.class,
          () ->
              f.files.execute(
                  s ->
                      s.completedSuccessReferenceRun(
                          done, RUN.id(), Instant.parse("2026-09-12T05:00:00Z"))));
      Files.writeString(
          f.attempts.resolve(ACT_ID + ".done"),
          DONE0.replace("2026-09-12T05:06:07.234567Z", "2026-09-12T07:06:07.234567Z"));
      assertThrows(
          IOException.class,
          () ->
              f.files.execute(
                  s -> s.completedSuccessReferenceRun(done, RUN.id(), current.cutoff())));
      f.files.execute(
          s -> s.start(new BatchRun(OTHER, Instant.parse("2026-09-12T08:00:00Z")), NEXT));
      assertThrows(
          IOException.class,
          () ->
              f.files.execute(
                  s -> s.completedSuccessReferenceRun(done, RUN.id(), current.cutoff())));
    }
  }

  /** RLOOK852005: full second graph, no cached anchor-only completed proof. */
  @Test
  void completedReferenceRejectsPendingGraphAndDifferentCurrentCutoff() throws Exception {
    try (var f = fixture()) {
      f.seed(true, false, true);
      var done = completion(MaintenanceCompletion.Outcome.SUCCESS);
      var wrongRun = new BatchRun(RUN.id(), RUN.cutoff().plusNanos(1000));
      var wrong =
          new MaintenanceCompletion(
              new MaintenanceActivation(wrongRun, ACTIVATION.id()), done.endedAt(), done.outcome());
      assertThrows(
          IOException.class,
          () ->
              f.files.execute(s -> s.completedSuccessReferenceRun(wrong, RUN.id(), RUN.cutoff())));
      Files.writeString(f.runs.resolve(OTHER + ".run"), ANCHOR.replace(RUN_ID, OTHER.toString()));
      assertThrows(
          IOException.class,
          () -> f.files.execute(s -> s.completedSuccessReferenceRun(done, RUN.id(), RUN.cutoff())));
      assertThrows(
          IOException.class,
          () -> f.files.execute(s -> s.completedSuccessReferenceRun(done, OTHER, RUN.cutoff())));
      assertEquals(DONE0, Files.readString(f.attempts.resolve(ACT_ID + ".done")));
    }
  }

  /** RLOOK852005: full second graph, no cached anchor-only completed proof. */
  @Test
  void completedReferenceRejectsWholeGraphDriftWithoutMutation() throws Exception {
    for (String fault :
        List.of("none", "unrelated", "prior", "namespace", "listing", "close", "interrupt"))
      try (var f = fixture()) {
        f.seed(true, false, true);
        var done = completion(MaintenanceCompletion.Outcome.SUCCESS);
        Action operation =
            () ->
                f.files.execute(
                    s -> {
                      f.reset();
                      if (fault.equals("unrelated")) f.on("namesOpen", 4, f::otherCompleted);
                      if (fault.equals("prior"))
                        f.on(
                            "namesOpen",
                            4,
                            () -> Files.writeString(f.attempts.resolve(ACT_ID + ".done"), DONE10));
                      if (fault.equals("namespace")) f.on("namesOpen", 4, () -> f.replace("runs"));
                      if (fault.equals("listing") || fault.equals("close")) {
                        f.fail = fault.equals("listing") ? "namesOpen" : "namesClose";
                        f.failAt = 4;
                      }
                      if (fault.equals("interrupt"))
                        f.on("namesOpen", 4, () -> Thread.currentThread().interrupt());
                      try {
                        if (fault.equals("none")) {
                          assertEquals(
                              RUN, s.completedSuccessReferenceRun(done, RUN.id(), RUN.cutoff()));
                          assertEquals(6, f.count("namesOpen"));
                          assertEquals(6, f.count("namesClose"));
                        } else
                          failure(
                              () -> s.completedSuccessReferenceRun(done, RUN.id(), RUN.cutoff()));
                      } finally {
                        Thread.interrupted();
                      }
                      for (String write : List.of("create", "publish", "unlink", "write", "sync"))
                        assertEquals(0, f.count(write));
                      return RUN;
                    });
        if (fault.equals("namespace")) failure(operation::execute);
        else operation.execute();
      }
  }

  /** RLOOK200001: independent retained bytes/cutoff, not a DB-derived original. */
  @Test
  void successReferenceReadsRetainedSameDayOriginalWithoutChangingActive() throws Exception {
    try (var f = fixture()) {
      f.files.execute(s -> s.start(RUN, ACTIVATION.id()));
      f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS)));
      var current = new BatchRun(NEXT, Instant.parse("2026-09-12T06:00:00Z"));
      var activation = new MaintenanceActivation(current, OTHER);
      f.files.execute(s -> s.start(current, OTHER));
      var before = new MaintenanceRunFiles.StartupOriginal(activation, Optional.empty());
      assertEquals(before, f.files.execute(s -> s.observeStartup(activation)));
      assertEquals(
          RUN, f.files.execute(s -> s.successReferenceRun(activation, RUN.id(), current.cutoff())));
      assertEquals(
          current, f.files.execute(s -> s.successReferenceRun(activation, NEXT, current.cutoff())));
      assertEquals(before, f.files.execute(s -> s.observeStartup(activation)));
      for (Instant time :
          List.of(
              current.cutoff().minusNanos(1000),
              current.cutoff().plusNanos(1),
              Instant.parse("9999-12-31T23:59:59.999999Z").plusNanos(1000)))
        assertThrows(
            IOException.class,
            () -> f.files.execute(s -> s.successReferenceRun(activation, RUN.id(), time)));
      assertThrows(
          IOException.class,
          () ->
              f.files.execute(
                  s ->
                      s.successReferenceRun(
                          activation,
                          UUID.fromString("22222222-2222-4222-8222-222222222222"),
                          current.cutoff())));
      assertThrows(
          IOException.class,
          () ->
              f.files.execute(s -> s.successReferenceRun(ACTIVATION, RUN.id(), current.cutoff())));
      assertThrows(
          NullPointerException.class,
          () -> f.files.execute(s -> s.successReferenceRun(null, RUN.id(), current.cutoff())));
      assertThrows(
          NullPointerException.class,
          () -> f.files.execute(s -> s.successReferenceRun(activation, null, current.cutoff())));
      assertThrows(
          NullPointerException.class,
          () -> f.files.execute(s -> s.successReferenceRun(activation, RUN.id(), null)));
    }
  }

  /** RLOOK493001/BUG799/YKT570: independent graph/listing and no-write oracle. */
  @Test
  void comp203004RetainedNamespaceChecksReadNoGraphAndRejectReplacementOrExpiredSession()
      throws Exception {
    for (String mode : List.of("normal", "replaced", "interrupt"))
      try (var f = fixture()) {
        var held = new java.util.concurrent.atomic.AtomicReference<MaintenanceRunFiles.Session>();
        Action operation =
            () ->
                f.files.execute(
                    s -> {
                      held.set(s);
                      f.reset();
                      if (mode.equals("replaced")) f.replace("runs");
                      if (mode.equals("interrupt")) Thread.currentThread().interrupt();
                      try {
                        if (mode.equals("normal")) s.verifyRetained();
                        else failure(s::verifyRetained);
                      } finally {
                        Thread.interrupted();
                      }
                      for (String io :
                          List.of("namesOpen", "openRead", "create", "write", "unlink", "sync"))
                        assertEquals(0, f.count(io), io);
                      return true;
                    });
        if (mode.equals("replaced")) failure(operation::execute);
        else operation.execute();
        failure(held.get()::verifyRetained);
        assertEquals(0, f.live.size());
      }
  }

  /** RLOOK493001/BUG799/YKT570: independent graph/listing and no-write oracle. */
  @Test
  void successReferenceUsesTwoWholeSnapshotsAndRejectsSecondSnapshotDrift() throws Exception {
    for (String fault :
        List.of("none", "unrelated", "prior", "namespace", "listing", "close", "interrupt"))
      try (var f = fixture()) {
        f.seed(true, false, true);
        var current = new BatchRun(NEXT, Instant.parse("2026-09-12T06:00:00Z"));
        var activation = new MaintenanceActivation(current, OTHER);
        f.files.execute(s -> s.start(current, OTHER));
        Action operation =
            () ->
                f.files.execute(
                    s -> {
                      for (var requested : List.of(RUN, current)) {
                        f.reset();
                        if (fault.equals("unrelated")) f.on("namesOpen", 4, f::otherCompleted);
                        if (fault.equals("prior"))
                          f.on(
                              "namesOpen",
                              4,
                              () ->
                                  Files.writeString(f.attempts.resolve(ACT_ID + ".done"), DONE10));
                        if (fault.equals("namespace"))
                          f.on("namesOpen", 4, () -> f.replace("runs"));
                        if (fault.equals("listing") || fault.equals("close")) {
                          f.fail = fault.equals("listing") ? "namesOpen" : "namesClose";
                          f.failAt = 4;
                        }
                        if (fault.equals("interrupt"))
                          f.on("namesOpen", 4, () -> Thread.currentThread().interrupt());
                        if (fault.equals("none")) {
                          assertEquals(
                              requested,
                              s.successReferenceRun(activation, requested.id(), current.cutoff()));
                          assertEquals(6, f.count("namesOpen"));
                          assertEquals(6, f.count("namesClose"));
                        } else {
                          try {
                            failure(
                                () ->
                                    s.successReferenceRun(
                                        activation, requested.id(), current.cutoff()));
                          } finally {
                            Thread.interrupted();
                          }
                        }
                        for (String write : List.of("create", "publish", "write", "unlink", "sync"))
                          assertEquals(0, f.count(write), write);
                        // Mutation cases change the fixture once; never reuse that graph as a fresh
                        // success.
                        if (!fault.equals("none")) break;
                      }
                      return true;
                    });
        if (fault.equals("namespace")) failure(operation::execute);
        else operation.execute();
        assertEquals(0, f.live.size());
      }
  }

  @Test
  void successReferenceRejectsDifferentBusinessDayAndFutureCompletion() throws Exception {
    for (boolean future : List.of(false, true))
      try (var f = fixture()) {
        f.files.execute(s -> s.start(RUN, ACTIVATION.id()));
        var done =
            new MaintenanceCompletion(
                ACTIVATION,
                Instant.parse("2026-09-12T07:00:00Z"),
                MaintenanceCompletion.Outcome.WARNING);
        f.files.execute(s -> s.complete(done));
        var current =
            new BatchRun(
                NEXT, Instant.parse(future ? "2026-09-12T06:00:00Z" : "2026-09-13T06:00:00Z"));
        var activation = new MaintenanceActivation(current, OTHER);
        f.files.execute(s -> s.start(current, OTHER));
        assertThrows(
            IOException.class,
            () ->
                f.files.execute(
                    s -> s.successReferenceRun(activation, RUN.id(), current.cutoff())));
      }
  }

  @Test
  void startupOriginalWholeGraphPendingCompletedAndForeignNeverAuthorizeMutation()
      throws Exception {
    try (var f = fixture()) {
      assertThrows(IOException.class, () -> f.files.execute(s -> s.observeStartup(ACTIVATION)));
      f.files.execute(s -> s.start(RUN, ACTIVATION.id()));
      var pending = f.files.execute(s -> s.observeStartup(ACTIVATION));
      assertEquals(ACTIVATION, pending.activation());
      assertTrue(pending.completed().isEmpty());
      var completion = completion(MaintenanceCompletion.Outcome.SUCCESS);
      f.files.execute(s -> s.complete(completion));
      var completed = f.files.execute(s -> s.observeStartup(ACTIVATION));
      assertEquals(ACTIVATION, completed.activation());
      assertEquals(Optional.of(completion), completed.completed());
      assertEquals("StartupOriginal[identity=<redacted>]", completed.toString());
      assertThrows(
          IOException.class,
          () -> f.files.execute(s -> s.observeStartup(new MaintenanceActivation(RUN, OTHER))));
      assertThrows(NullPointerException.class, () -> f.files.execute(s -> s.observeStartup(null)));
      assertThrows(
          NullPointerException.class,
          () -> new MaintenanceRunFiles.StartupOriginal(null, Optional.empty()));
      assertThrows(
          NullPointerException.class,
          () -> new MaintenanceRunFiles.StartupOriginal(ACTIVATION, null));
      var wrong =
          new MaintenanceCompletion(
              new MaintenanceActivation(RUN, OTHER), completion.endedAt(), completion.outcome());
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRunFiles.StartupOriginal(ACTIVATION, Optional.of(wrong)));
    }
  }

  /** SSC109/BUG327/PT-OPS-MNAMESPACE002: paired RO ancestors never authorize RO records. */
  @Test
  void hostAncestorPairingKeepsDurableWritesPrivate() throws Exception {
    for (String condition :
        List.of("shared-ro", "host-ro", "maintenance-ro", "runs-ro", "attempts-ro", "drift")) {
      try (var f = fixture()) {
        var hostFds = ConcurrentHashMap.<Integer>newKeySet();
        var hostCalls =
            (DirectoryCalls)
                Proxy.newProxyInstance(
                    getClass().getClassLoader(),
                    new Class<?>[] {DirectoryCalls.class},
                    (proxy, method, args) -> {
                      try {
                        Object value = method.invoke(f.calls, args);
                        if (Set.of("openRoot", "openDirectory", "openEntry")
                            .contains(method.getName())) assertTrue(hostFds.add((Integer) value));
                        if (method.getName().equals("close"))
                          assertTrue(hostFds.remove((Integer) args[0]));
                        return value;
                      } catch (InvocationTargetException failure) {
                        throw failure.getCause();
                      }
                    });
        var io =
            (MaintenanceRunFiles.Io)
                Proxy.newProxyInstance(
                    getClass().getClassLoader(),
                    new Class<?>[] {MaintenanceRunFiles.Io.class},
                    (proxy, method, args) -> {
                      try {
                        Object result = method.invoke(f, args);
                        if (method.getName().equals("attributes")
                            && condition.equals("drift")
                            && hostFds.contains(
                                Integer.parseInt(((Path) args[0]).getFileName().toString()))) {
                          @SuppressWarnings("unchecked")
                          var values = (Map<String, Object>) result;
                          values.put("ino", Long.MAX_VALUE);
                        }
                        return result;
                      } catch (InvocationTargetException failure) {
                        throw failure.getCause();
                      }
                    });
        var security =
            new InodeSecurityCalls() {
              public long effectiveUid() {
                return 0;
              }

              public byte[] accessAcl(Path held, int maximum) throws StorageIoException {
                return f.accessAcl(held, maximum);
              }

              public boolean readOnlyFilesystem(Path held) throws StorageIoException {
                if (hostFds.contains(Integer.parseInt(held.getFileName().toString())))
                  return condition.equals("host-ro");
                try {
                  String role = f.role(held);
                  return Set.of("var", "lib", "app").contains(role)
                      || condition.equals(role + "-ro");
                } catch (IOException failure) {
                  throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                }
              }
            };
        var files =
            new MaintenanceRunFiles(
                f.varPath,
                f.calls,
                security,
                io,
                f::part,
                () -> java.security.MessageDigest.getInstance("SHA-256"),
                Optional.of(hostCalls));
        var invoked = new java.util.concurrent.atomic.AtomicInteger();
        if (condition.equals("shared-ro"))
          assertEquals(Integer.valueOf(1), files.execute(s -> invoked.incrementAndGet()));
        else {
          failure(() -> files.execute(s -> invoked.incrementAndGet()));
          assertEquals(0, invoked.get());
        }
        assertEquals(0, f.count("publish"));
        assertEquals(0, f.count("write"));
        assertTrue(hostFds.isEmpty());
        f.released();
      }
    }
  }

  private static MaintenanceCompletion completion(MaintenanceCompletion.Outcome outcome) {
    return new MaintenanceCompletion(
        ACTIVATION, Instant.parse("2026-09-12T05:06:07.234567Z"), outcome);
  }

  private static Map<String, String> activeFiles() {
    return Map.of(
        "runs/" + RUN_ID + ".run", ANCHOR, "attempts/" + ACT_ID + ".begin", BEGIN, "active", BEGIN);
  }

  private static CleanupWorkerRequest cleanupRequest() {
    return new CleanupWorkerRequest(RUN.id(), ACTIVATION.id(), RUN.cutoff(), "0".repeat(64));
  }

  /** PG330/SSC104/PT-OPS-MRF001: independent literal durable graph, no republish. */
  @Test
  void cleanupObservationIsReadOnly() throws Exception {
    try (var f = fixture()) {
      f.seed(true, true, false);
      var original = disk(f);
      assertEquals(ACTIVATION, f.files.execute(s -> s.observeCleanup(cleanupRequest())));
      assertEquals(original, disk(f));
      for (String operation : List.of("create", "write", "force", "publish", "unlink", "sync"))
        assertEquals(0, f.count(operation), operation);
      f.released();
    }
  }

  /** PG330/SSC104/PT-OPS-MRF002: no mismatched child run, activation or cutoff. */
  @Test
  void cleanupObservationRefusesOtherIdentity() throws Exception {
    try (var f = fixture()) {
      f.seed(true, true, false);
      for (var request :
          List.of(
              new CleanupWorkerRequest(OTHER, ACTIVATION.id(), RUN.cutoff(), "0".repeat(64)),
              new CleanupWorkerRequest(RUN.id(), NEXT, RUN.cutoff(), "0".repeat(64)),
              new CleanupWorkerRequest(
                  RUN.id(), ACTIVATION.id(), RUN.cutoff().plusSeconds(1), "0".repeat(64))))
        failure(() -> f.files.execute(s -> s.observeCleanup(request)));
      assertEquals(activeFiles(), disk(f));
      assertEquals(0, f.count("publish"));
      f.released();
    }
  }

  /** PG330/SSC104/PT-OPS-MRF003: absent, orphan and completed graphs cannot authorize cleanup. */
  @Test
  void cleanupObservationRefusesNonActive() throws Exception {
    for (boolean begin : List.of(false, true))
      for (boolean active : List.of(false, true))
        if (!begin || !active)
          try (var f = fixture()) {
            f.seed(begin, active, false);
            failure(() -> f.files.execute(s -> s.observeCleanup(cleanupRequest())));
            assertEquals(0, f.count("publish"));
            f.released();
          }
    try (var f = fixture()) {
      f.seed(true, true, true);
      failure(() -> f.files.execute(s -> s.observeCleanup(cleanupRequest())));
      assertEquals(0, f.count("publish"));
      f.released();
    }
  }

  /** PG330/SSC104/PT-OPS-MRF004: null/graph drift and owned-close uncertainty fail closed. */
  @Test
  void cleanupObservationRefusesDriftAndCloseFault() throws Exception {
    try (var f = fixture()) {
      f.seed(true, true, false);
      assertThrows(NullPointerException.class, () -> f.files.execute(s -> s.observeCleanup(null)));
      assertEquals(activeFiles(), disk(f));
      f.released();
    }
    try (var f = fixture()) {
      f.seed(true, true, false);
      f.on(
          "namesOpen",
          4,
          () ->
              Files.writeString(
                  f.maintenance.resolve("active"), BEGIN.replace(ACT_ID, NEXT.toString())));
      failure(() -> f.files.execute(s -> s.observeCleanup(cleanupRequest())));
      assertEquals(0, f.count("publish"));
      f.released();
    }
    try (var f = fixture()) {
      f.seed(true, true, false);
      f.rawCloses = true;
      failure(() -> f.files.execute(s -> s.observeCleanup(cleanupRequest())));
      assertEquals(0, f.count("publish"));
      f.released();
    }
  }

  private static Map<String, String> completedFiles(String done) {
    return Map.of(
        "runs/" + RUN_ID + ".run",
        ANCHOR,
        "attempts/" + ACT_ID + ".begin",
        BEGIN,
        "attempts/" + ACT_ID + ".done",
        done);
  }

  private static Map<String, String> disk(Fixture f) throws IOException {
    Map<String, String> result = new TreeMap<>();
    try (var stream = Files.walk(f.maintenance)) {
      for (Path p : stream.filter(Files::isRegularFile).toList())
        result.put(f.maintenance.relativize(p).toString(), Files.readString(p));
    }
    return result;
  }

  private static void state(
      MaintenanceRunState state, MaintenanceActivation expected, boolean done) {
    assertEquals(expected, state.activation());
    assertEquals(done, state.completion().isPresent());
    if (done)
      assertEquals(
          completion(MaintenanceCompletion.Outcome.SUCCESS), state.completion().orElseThrow());
  }

  @Test
  void newRunPublication() throws Exception {
    try (var f = fixture()) {
      state(f.files.execute(s -> s.start(RUN, ACTIVATION.id())), ACTIVATION, false);
      assertEquals(activeFiles(), disk(f));
      trace("PT-BAT-058-anchor.txt", Files.readString(f.runs.resolve(RUN_ID + ".run")));
      trace("PT-BAT-058-begin.txt", Files.readString(f.attempts.resolve(ACT_ID + ".begin")));
      trace("PT-BAT-058-active.txt", Files.readString(f.maintenance.resolve("active")));
      assertEquals(3, f.count("create"));
      assertEquals(3, f.count("force"));
      assertEquals(3, f.count("publish"));
      assertEquals(3, f.count("sync"));
      f.released();
    }
  }

  @Test
  void resumeActive() throws Exception {
    try (var f = fixture()) {
      f.seed(true, true, false);
      var original = disk(f);
      state(f.files.execute(s -> s.resume(RUN.id(), NEXT)), ACTIVATION, false);
      assertEquals(original, disk(f));
      assertEquals(0, f.count("create"));
      assertEquals(0, f.count("write"));
      assertEquals(
          3, f.count("force"), "BUG159: visible chain needs re-sync before recovery succeeds");
      assertEquals(3, f.count("sync"));
      f.released();
    }
  }

  @Test
  void resumeOrphanAnchor() throws Exception {
    try (var f = fixture()) {
      f.seed(false, false, false);
      var original = f.nativeIo.attributes(f.runs.resolve(RUN_ID + ".run"));
      state(f.files.execute(s -> s.resume(RUN.id(), ACTIVATION.id())), ACTIVATION, false);
      assertEquals(original, f.nativeIo.attributes(f.runs.resolve(RUN_ID + ".run")));
      assertEquals(activeFiles(), disk(f));
      assertEquals(2, f.count("create"));
      assertEquals(3, f.count("force"));
      f.released();
    }
  }

  @Test
  void resumePendingBegin() throws Exception {
    try (var f = fixture()) {
      f.seed(true, false, false);
      state(f.files.execute(s -> s.resume(RUN.id(), NEXT)), ACTIVATION, false);
      assertEquals(activeFiles(), disk(f));
      assertEquals(1, f.count("create"));
      assertEquals(3, f.count("force"));
      f.released();
    }
  }

  @Test
  void resumeCompletedHistory() throws Exception {
    try (var f = fixture()) {
      f.seed(true, false, true);
      var expected = new HashMap<>(completedFiles(DONE0));
      expected.put("attempts/" + NEXT + ".begin", BEGIN.replace(ACT_ID, NEXT.toString()));
      expected.put("active", BEGIN.replace(ACT_ID, NEXT.toString()));
      state(
          f.files.execute(s -> s.resume(RUN.id(), NEXT)),
          new MaintenanceActivation(RUN, NEXT),
          false);
      assertEquals(expected, disk(f));
      assertEquals(2, f.count("create"));
      assertEquals(3, f.count("force"));
      f.released();
    }
  }

  @Test
  void completedActiveRecovery() throws Exception {
    try (var f = fixture()) {
      f.seed(true, true, true);
      var original = disk(f);
      state(f.files.execute(s -> s.resume(RUN.id(), NEXT)), ACTIVATION, true);
      assertEquals(original, disk(f));
      assertEquals(0, f.count("write"));
      assertEquals(4, f.count("force"));
      f.released();
    }
  }

  @Test
  void completeSuccessAndWarning() throws Exception {
    for (var outcome : MaintenanceCompletion.Outcome.values())
      try (var f = fixture()) {
        f.seed(true, true, false);
        var expected = completion(outcome);
        assertEquals(expected, f.files.execute(s -> s.complete(expected)));
        assertEquals(
            completedFiles(outcome == MaintenanceCompletion.Outcome.SUCCESS ? DONE0 : DONE10),
            disk(f));
        String code = outcome == MaintenanceCompletion.Outcome.SUCCESS ? "0" : "10";
        trace(
            "PT-BAT-064-done-" + code + ".txt",
            Files.readString(f.attempts.resolve(ACT_ID + ".done")));
        trace(
            "PT-BAT-064-names-" + code + ".txt",
            String.join("\n", new TreeSet<>(disk(f).keySet())) + "\n");
        assertEquals(1, f.count("create"));
        assertEquals(1, f.count("unlink"));
        assertEquals(4, f.count("force"));
        f.released();
      }
  }

  @Test
  void completionRetryAndMismatch() throws Exception {
    try (var f = fixture()) {
      f.seed(true, false, true);
      f.otherCompleted();
      Files.writeString(
          f.maintenance.resolve("active"),
          BEGIN.replace(RUN_ID, OTHER.toString()).replace(ACT_ID, NEXT.toString()));
      var before = disk(f);
      failure(
          () ->
              f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
      assertEquals(before, disk(f));
      assertEquals(0, f.count("force"));
      f.released();
    }
    for (boolean active : List.of(false, true))
      try (var f = fixture()) {
        f.seed(true, active, true);
        assertEquals(
            completion(MaintenanceCompletion.Outcome.SUCCESS),
            f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
        assertEquals(completedFiles(DONE0), disk(f));
        assertEquals(0, f.count("create"));
        f.released();
      }
    for (var wrong :
        List.of(
            completion(MaintenanceCompletion.Outcome.WARNING),
            new MaintenanceCompletion(
                ACTIVATION,
                Instant.parse("2026-09-12T05:06:07.234568Z"),
                MaintenanceCompletion.Outcome.SUCCESS),
            new MaintenanceCompletion(
                new MaintenanceActivation(RUN, NEXT),
                Instant.parse("2026-09-12T05:06:07.234567Z"),
                MaintenanceCompletion.Outcome.SUCCESS)))
      try (var f = fixture()) {
        f.seed(true, true, true);
        var original = disk(f);
        failure(() -> f.files.execute(s -> s.complete(wrong)));
        assertEquals(original, disk(f));
        f.released();
      }
    try (var f = fixture()) {
      f.seed(true, false, false);
      failure(
          () ->
              f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
      f.released();
    }
  }

  @Test
  void noImplicitNewIdentity() throws Exception {
    for (int mode = 0; mode < 4; mode++)
      try (var f = fixture()) {
        f.seed(mode != 0, mode == 1, mode >= 2);
        var original = disk(f);
        BatchRun requested = mode == 3 ? new BatchRun(OTHER, RUN.cutoff()) : RUN;
        failure(() -> f.files.execute(s -> s.start(requested, ACTIVATION.id())));
        assertEquals(original, disk(f));
        assertEquals(0, f.count("write"));
        f.released();
      }
    try (var f = fixture()) {
      f.seed(true, true, false);
      failure(() -> f.files.execute(s -> s.resume(OTHER, NEXT)));
      f.released();
    }
    try (var f = fixture()) {
      f.seed(true, false, true);
      failure(() -> f.files.execute(s -> s.resume(RUN.id(), ACTIVATION.id())));
      f.released();
    }
    try (var f = fixture()) {
      f.seed(true, true, false);
      Files.writeString(f.runs.resolve(OTHER + ".run"), ANCHOR.replace(RUN_ID, OTHER.toString()));
      Files.writeString(
          f.attempts.resolve(NEXT + ".begin"),
          BEGIN.replace(RUN_ID, OTHER.toString()).replace(ACT_ID, NEXT.toString()));
      Files.writeString(
          f.attempts.resolve(NEXT + ".done"),
          DONE0.replace(RUN_ID, OTHER.toString()).replace(ACT_ID, NEXT.toString()));
      failure(() -> f.files.execute(s -> s.resume(OTHER, NEXT)));
      f.released();
    }
  }

  @Test
  void malformedGraphReferences() throws Exception {
    for (String action :
        List.of(
            "missingAnchor",
            "missingBegin",
            "wrongCutoff",
            "wrongDone",
            "wrongActive",
            "wrongName"))
      try (var f = fixture()) {
        f.seed(true, true, true);
        switch (action) {
          case "missingAnchor" -> Files.delete(f.runs.resolve(RUN_ID + ".run"));
          case "missingBegin" -> Files.delete(f.attempts.resolve(ACT_ID + ".begin"));
          case "wrongCutoff" ->
              Files.writeString(
                  f.attempts.resolve(ACT_ID + ".begin"), BEGIN.replace("123456Z", "123457Z"));
          case "wrongDone" ->
              Files.writeString(
                  f.attempts.resolve(ACT_ID + ".done"), DONE0.replace("123456Z", "123457Z"));
          case "wrongActive" ->
              Files.writeString(
                  f.maintenance.resolve("active"), BEGIN.replace(ACT_ID, NEXT.toString()));
          case "wrongName" ->
              Files.move(f.runs.resolve(RUN_ID + ".run"), f.runs.resolve(OTHER + ".run"));
          default -> throw new AssertionError(action);
        }
        var before = disk(f);
        failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
        assertEquals(before, disk(f));
        assertEquals(0, f.count("write"));
        f.released();
      }
    try (var f = fixture()) {
      f.seed(false, false, true);
      failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
      f.released();
    }
  }

  @Test
  void ambiguousPendingStates() throws Exception {
    // BUG-162: a completed target plus exactly one OTHER pending run passes the earlier count
    // guard.
    for (boolean active : List.of(false, true))
      try (var f = fixture()) {
        f.seed(true, active, true);
        Files.writeString(f.runs.resolve(OTHER + ".run"), ANCHOR.replace(RUN_ID, OTHER.toString()));
        var before = disk(f);
        failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
        assertEquals(before, disk(f));
        assertEquals(0, f.count("write"));
        f.released();
      }
    for (int mode = 0; mode < 5; mode++)
      try (var f = fixture()) {
        f.seed(mode != 0, mode >= 2, mode == 4);
        if (mode == 0 || mode == 1 || mode == 2)
          Files.writeString(
              f.runs.resolve(OTHER + ".run"), ANCHOR.replace(RUN_ID, OTHER.toString()));
        else
          Files.writeString(
              f.attempts.resolve(NEXT + ".begin"), BEGIN.replace(ACT_ID, NEXT.toString()));
        var before = disk(f);
        failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
        assertEquals(before, disk(f));
        f.released();
      }
  }

  @Test
  void inventoryUnknownAndPartial() throws Exception {
    for (String role : List.of("maintenance", "runs", "attempts"))
      for (String name :
          List.of(
              "unknown",
              OTHER + ".part",
              OTHER + ".gc",
              RUN_ID.toUpperCase(Locale.ROOT) + ".run",
              "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz.run",
              RUN_ID + ".done"))
        try (var f = fixture()) {
          f.seed(true, true, false);
          Files.writeString(f.path(role).resolve(name), "preserve");
          var original = disk(f);
          failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
          assertEquals(original, disk(f));
          f.released();
        }
  }

  @Test
  void namespacePermissions() throws Exception {
    try (var f = fixture()) {
      f.seed(true, true, false);
      f.change =
          (role, values) -> {
            if (role.equals("file")) values.put("dev", -1L);
          };
      failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
      assertEquals(0, f.count("openRead"));
      f.released();
    }
    for (String role : List.of("var", "lib", "app", "maintenance", "runs", "attempts"))
      for (String bad :
          List.of(
              "nullAttributes",
              "nullFilesystem",
              "filesystem",
              "tmpfs",
              "nullAcl",
              "acl",
              "readonly"))
        try (var f = fixture()) {
          f.badRole = role;
          f.invalid = bad;
          failure(() -> f.files.execute(s -> true));
          f.released();
        }
    for (String role : List.of("var", "lib", "app", "maintenance", "runs", "attempts"))
      for (var bad :
          Map.<String, Object>of("mode", 040777, "uid", 1, "gid", 1, "nlink", 0, "size", -1L)
              .entrySet())
        try (var f = fixture()) {
          f.change =
              (r, m) -> {
                if (r.equals(role)) m.put(bad.getKey(), bad.getValue());
              };
          failure(() -> f.files.execute(s -> true));
          f.released();
        }
    for (String role : List.of("runs", "attempts"))
      try (var f = fixture()) {
        f.change =
            (r, m) -> {
              if (r.equals(role)) m.put("dev", -1L);
            };
        failure(() -> f.files.execute(s -> true));
        f.released();
      }
    try (var f = fixture()) {
      f.change =
          (r, m) -> {
            if (Set.of("var", "lib", "app").contains(r)) m.put("dev", (long) r.length());
          };
      boolean accepted = f.files.execute(s -> true);
      assertTrue(accepted);
      f.released();
    }
  }

  @Test
  void namespaceReplacement() throws Exception {
    for (String role : List.of("var", "lib", "app", "maintenance", "runs", "attempts"))
      try (var f = fixture()) {
        failure(
            () ->
                f.files.execute(
                    s -> {
                      f.replace(role);
                      return true;
                    }));
        f.released();
      }
    try (var f = fixture()) {
      Files.move(f.runs, f.maintenance.resolve("original"));
      Files.createSymbolicLink(f.runs, f.maintenance.resolve("original"));
      failure(() -> f.files.execute(s -> true));
      f.released();
    }
  }

  @Test
  void recordReplacementDuringScan() throws Exception {
    try (var f = fixture()) {
      f.on("namesClose", 3, () -> Files.setLastModifiedTime(f.maintenance, FileTime.fromMillis(1)));
      failure(() -> f.files.execute(s -> s.start(RUN, ACTIVATION.id())));
      assertTrue(disk(f).isEmpty());
      f.released();
    }
    try (var f = fixture()) {
      f.seed(true, true, false);
      f.on(
          "openEntry",
          5,
          () -> {
            Path original = f.runs.resolve(RUN_ID + ".run");
            Files.move(original, f.base.resolve("retained-original"));
            Files.writeString(original, ANCHOR);
          });
      failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
      assertEquals(ANCHOR, Files.readString(f.base.resolve("retained-original")));
      f.released();
    }
    for (String mutation : List.of("rename", "content", "delete", "time"))
      try (var f = fixture()) {
        f.seed(true, true, false);
        f.on(
            "namesClose",
            3,
            () -> {
              Path anchor = f.runs.resolve(RUN_ID + ".run");
              switch (mutation) {
                case "rename" -> {
                  Files.move(anchor, f.base.resolve("saved"));
                  Files.writeString(anchor, ANCHOR);
                }
                case "content" -> Files.writeString(anchor, ANCHOR.replace("123456Z", "123457Z"));
                case "delete" -> Files.delete(anchor);
                case "time" -> Files.setLastModifiedTime(anchor, FileTime.fromMillis(1));
                default -> throw new AssertionError(mutation);
              }
            });
        failure(() -> f.files.execute(s -> s.resume(RUN.id(), NEXT)));
        f.released();
      }
  }

  @Test
  void listingAndIoFailures() throws Exception {
    for (String bad : List.of("nullStream", "nullEntry", "otherParent", "duplicate", "rootOnly"))
      try (var f = fixture()) {
        f.listingFault = bad;
        failure(() -> f.files.execute(s -> s.start(RUN, ACTIVATION.id())));
        f.released();
      }
    faultMatrix("active", false);
  }

  @Test
  void rootAcquisitionAndCloseFailures() throws Exception {
    faultMatrix("start", true);
    try (var f = fixture()) {
      f.rawCloses = true;
      failure(
          () ->
              f.files.execute(
                  s -> {
                    throw new IOException("synthetic callback");
                  }));
      f.released();
    }
  }

  @Test
  void startCrashBoundaries() throws Exception {
    try (var f = fixture()) {
      f.on("sync", 3, f::otherCompleted);
      failure(() -> f.files.execute(s -> s.start(RUN, ACTIVATION.id())));
      assertEquals(6, disk(f).size());
      f.released();
    }
    for (String point : List.of("force", "publish", "sync"))
      for (int at = 1; at <= 3; at++)
        try (var f = fixture()) {
          f.fail = point;
          f.failAt = at;
          failure(() -> f.files.execute(s -> s.start(RUN, ACTIVATION.id())));
          f.released();
          var state = disk(f);
          assertFalse(state.isEmpty());
          f.reset();
          if (point.equals("sync")) {
            state(f.files.execute(s -> s.resume(RUN.id(), ACTIVATION.id())), ACTIVATION, false);
            assertEquals(activeFiles(), disk(f));
          } else {
            failure(() -> f.files.execute(s -> s.resume(RUN.id(), ACTIVATION.id())));
            assertEquals(state, disk(f));
          }
          f.released();
        }
    faultMatrix("start", false);
  }

  @Test
  void resumeCrashBoundaries() throws Exception {
    for (boolean active : List.of(false, true))
      try (var f = fixture()) {
        f.seed(active, active, false);
        f.on("sync", 3, f::otherCompleted);
        failure(() -> f.files.execute(s -> s.resume(RUN.id(), ACTIVATION.id())));
        assertEquals(6, disk(f).size());
        f.released();
      }
    for (int mode = 0; mode < 4; mode++)
      for (String point : List.of("force", "sync"))
        for (int at = 1; at <= (mode == 3 ? 4 : 3); at++)
          try (var f = fixture()) {
            f.seed(mode != 0, mode >= 2, mode == 3);
            var before = disk(f);
            f.fail = point;
            f.failAt = at;
            UUID next = mode == 0 ? ACTIVATION.id() : NEXT;
            failure(() -> f.files.execute(s -> s.resume(RUN.id(), next)));
            assertEquals(ANCHOR, Files.readString(f.runs.resolve(RUN_ID + ".run")));
            if (mode >= 2) assertEquals(before, disk(f));
            f.released();
          }
  }

  @Test
  void completionCrashBoundaries() throws Exception {
    try (var f = fixture()) {
      f.seed(true, true, false);
      f.on("sync", 5, f::otherCompleted);
      failure(
          () ->
              f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
      assertEquals(6, disk(f).size());
      f.released();
    }
    for (String point : List.of("force", "sync"))
      for (int at = 1; at <= 4; at++)
        try (var f = fixture()) {
          f.seed(true, true, false);
          f.fail = point;
          f.failAt = at;
          failure(
              () ->
                  f.files.execute(
                      s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
          assertEquals(BEGIN, Files.readString(f.maintenance.resolve("active")));
          f.released();
        }
    try (var f = fixture()) {
      f.seed(true, true, false);
      f.fail = "sync";
      f.failAt = 5;
      failure(
          () ->
              f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
      assertEquals(completedFiles(DONE0), disk(f));
      f.reset();
      f.fail = "sync";
      f.failAt = 4;
      failure(
          () ->
              f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
      assertEquals(completedFiles(DONE0), disk(f));
      f.reset();
      assertEquals(
          completion(MaintenanceCompletion.Outcome.SUCCESS),
          f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS))));
      f.released();
    }
    faultMatrix("complete", false);
  }

  @Test
  void nullAndClosedContracts() throws Exception {
    try (var f = fixture()) {
      assertThrows(
          NullPointerException.class, () -> new MaintenanceRunFiles(null, f.calls, f, f, f::part));
      assertThrows(
          NullPointerException.class,
          () -> new MaintenanceRunFiles(f.varPath, null, f, f, f::part));
      assertThrows(
          NullPointerException.class,
          () -> new MaintenanceRunFiles(f.varPath, f.calls, null, f, f::part));
      assertThrows(
          NullPointerException.class,
          () -> new MaintenanceRunFiles(f.varPath, f.calls, f, null, f::part));
      assertThrows(
          NullPointerException.class,
          () -> new MaintenanceRunFiles(f.varPath, f.calls, f, f, null));
      for (Path p : List.of(Path.of("/"), Path.of("relative"), f.varPath.resolve("..")))
        assertThrows(
            IllegalArgumentException.class,
            () -> new MaintenanceRunFiles(p, f.calls, f, f, f::part));
      assertThrows(NullPointerException.class, () -> f.files.execute(null));
      assertThrows(NullPointerException.class, () -> f.files.execute(s -> null));
      var captured = new AtomicReference<MaintenanceRunFiles.Session>();
      f.files.execute(
          s -> {
            captured.set(s);
            assertThrows(NullPointerException.class, () -> s.start(null, ACTIVATION.id()));
            assertThrows(NullPointerException.class, () -> s.start(RUN, null));
            assertThrows(NullPointerException.class, () -> s.resume(null, NEXT));
            assertThrows(NullPointerException.class, () -> s.resume(RUN.id(), null));
            assertThrows(NullPointerException.class, () -> s.complete(null));
            return true;
          });
      failure(() -> captured.get().start(RUN, ACTIVATION.id()));
      failure(() -> captured.get().resume(RUN.id(), NEXT));
      failure(() -> captured.get().complete(completion(MaintenanceCompletion.Outcome.SUCCESS)));
      f.nullPart = true;
      assertThrows(
          NullPointerException.class, () -> f.files.execute(s -> s.start(RUN, ACTIVATION.id())));
      f.released();
    }
    assertThrows(NullPointerException.class, () -> new MaintenanceRunState(null, Optional.empty()));
    assertThrows(NullPointerException.class, () -> new MaintenanceRunState(ACTIVATION, null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MaintenanceRunState(
                new MaintenanceActivation(RUN, NEXT),
                Optional.of(completion(MaintenanceCompletion.Outcome.SUCCESS))));
  }

  private static void throwCompound(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static void assertCompound(Throwable expected, Throwable actual, boolean known) {
    assertSame(expected, actual);
    assertEquals(known ? 0 : 1, actual.getSuppressed().length);
    if (!known) {
      var fixed = assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
      assertEquals(StorageIoException.Reason.UNAVAILABLE, fixed.reason());
      assertNull(fixed.getCause());
      assertEquals(0, fixed.getSuppressed().length);
    }
  }

  @Test
  void interruptionAndRuntime() throws Exception {

    // PG172/SSC063, BUG195/YKT154; close offsets independently follow reverse acquisition.
    for (int position = 1; position <= 6; position++) {
      int offset = position;
      for (boolean known : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("synthetic compound"),
                new NullPointerException("synthetic compound"),
                new AssertionError("synthetic compound"))) {
          try (var f = fixture()) {
            int[] closes = {0};
            int[] injected = {0};
            int[] callbacks = {0};
            var retained =
                new java.util.concurrent.atomic.AtomicReference<MaintenanceRunFiles.Session>();
            Throwable actual =
                assertThrows(
                    unknown.getClass(),
                    () ->
                        f.files.execute(
                            session -> {
                              callbacks[0]++;
                              retained.set(session);
                              closes[0] = f.count("close");
                              f.on(
                                  "close",
                                  closes[0] + offset,
                                  () -> {
                                    injected[0]++;
                                    throwCompound(unknown);
                                  });
                              if (known) throw new IOException("synthetic primary");
                              throwCompound(unknown);
                              return true;
                            }));
            assertCompound(unknown, actual, known);
            assertEquals(1, injected[0]);
            assertEquals(1, callbacks[0]);
            assertEquals(closes[0] + 6, f.count("close"));
            failure(() -> retained.get().start(RUN, ACTIVATION.id()));
            assertTrue(disk(f).isEmpty());
            f.released();
          }
        }
    }

    for (boolean known : List.of(false, true))
      for (Throwable unknown :
          List.of(
              new IllegalStateException("synthetic compound"),
              new NullPointerException("synthetic compound"),
              new AssertionError("synthetic compound")))
        try (var f = fixture()) {
          int[] injected = {0};
          int[] bodies = {0};
          f.on(
              "namesIterator",
              1,
              () -> {
                bodies[0]++;
                f.on(
                    "namesClose",
                    1,
                    () -> {
                      injected[0]++;
                      throwCompound(unknown);
                    });
                if (known) throw new IOException("synthetic iterator primary");
                throwCompound(unknown);
              });
          Throwable actual =
              assertThrows(
                  unknown.getClass(),
                  () -> f.files.execute(session -> session.start(RUN, ACTIVATION.id())));
          assertCompound(unknown, actual, known);
          assertEquals(1, bodies[0]);
          assertEquals(1, injected[0]);
          assertEquals(1, f.count("namesClose"));
          assertTrue(disk(f).isEmpty());
          f.released();
        }
    // Independently counted final closes: stop after operation IO, then after all scope roots.
    for (boolean wholeScope : List.of(false, true))
      try (var f = fixture()) {
        int total = inventory(f, "start").get("close");
        int at = wholeScope ? total : total - f.varPath.getNameCount() - 12;
        f.on("close", at, () -> Thread.currentThread().interrupt());
        try {
          failure(() -> f.files.execute(s -> s.start(RUN, ACTIVATION.id())));
          assertTrue(Thread.currentThread().isInterrupted());
          assertEquals(activeFiles(), disk(f));
          f.released();
        } finally {
          Thread.interrupted();
        }
      }
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        failure(() -> f.files.execute(s -> true));
        assertTrue(Thread.currentThread().isInterrupted());
        assertTrue(f.counts.isEmpty());
      } finally {
        Thread.interrupted();
      }
      f.uid = 1;
      failure(() -> f.files.execute(s -> true));
      assertTrue(f.counts.isEmpty());
      f.released();
    }
    try (var f = fixture()) {
      failure(
          () ->
              f.files.execute(
                  s -> {
                    Thread.currentThread().interrupt();
                    return true;
                  }));
      assertTrue(Thread.interrupted());
      f.released();
    }
    for (RuntimeException error :
        List.of(new IllegalStateException("synthetic"), new NullPointerException("synthetic")))
      try (var f = fixture()) {
        assertSame(
            error,
            assertThrows(
                error.getClass(),
                () ->
                    f.files.execute(
                        s -> {
                          throw error;
                        })));
        f.released();
      }
    try (var f = fixture()) {
      failure(
          () ->
              f.files.execute(
                  s -> {
                    throw new IOException("synthetic");
                  }));
      f.released();
    }
  }

  @Test
  void concurrentScopeOwnership() throws Exception {
    try (var f = fixture();
        var pool = Executors.newFixedThreadPool(2)) {
      var entered = new CountDownLatch(1);
      var release = new CountDownLatch(1);
      var returning = new CountDownLatch(1);
      var session = new AtomicReference<MaintenanceRunFiles.Session>();
      var worker = new AtomicReference<Future<MaintenanceRunState>>();
      f.on(
          "namesOpen",
          1,
          () -> {
            entered.countDown();
            await(release);
          });
      Future<Boolean> scope =
          pool.submit(
              () ->
                  f.files.execute(
                      s -> {
                        session.set(s);
                        worker.set(pool.submit(() -> s.start(RUN, ACTIVATION.id())));
                        await(entered);
                        returning.countDown();
                        return true;
                      }));
      try {
        await(returning);
        assertFalse(scope.isDone(), "scope must wait for its already executing session operation");
      } finally {
        release.countDown();
      }
      boolean completed = scope.get(10, TimeUnit.SECONDS);
      assertTrue(completed);
      state(worker.get().get(10, TimeUnit.SECONDS), ACTIVATION, false);
      failure(() -> session.get().resume(RUN.id(), NEXT));
      assertEquals(activeFiles(), disk(f));
      f.released();
    }
    try (var f = fixture();
        var pool = Executors.newFixedThreadPool(4)) {
      List<Future<Boolean>> results = new ArrayList<>();
      for (int i = 0; i < 16; i++)
        results.add(
            pool.submit(
                () -> {
                  try {
                    f.files.execute(s -> s.start(RUN, ACTIVATION.id()));
                    return true;
                  } catch (StorageIoException e) {
                    return false;
                  }
                }));
      int success = 0;
      for (var result : results) if (result.get(10, TimeUnit.SECONDS)) success++;
      assertEquals(1, success);
      assertEquals(activeFiles(), disk(f));
      f.released();
    }
  }

  @Test
  void fixedFactoryAndReopen() throws Exception {
    failure(() -> MaintenanceRunFiles.create().execute(s -> true));
    try (var f = fixture()) {
      f.files.execute(s -> s.start(RUN, ACTIVATION.id()));
      var reopened = new MaintenanceRunFiles(f.varPath, f.calls, f, f, f::part);
      state(reopened.execute(s -> s.resume(RUN.id(), NEXT)), ACTIVATION, false);
      var model =
          new MaintenanceRunState(
              ACTIVATION, Optional.of(completion(MaintenanceCompletion.Outcome.SUCCESS)));
      assertEquals(
          model,
          new MaintenanceRunState(
              ACTIVATION, Optional.of(completion(MaintenanceCompletion.Outcome.SUCCESS))));
      assertEquals("MaintenanceRunState[redacted]", model.toString());
      assertEquals(activeFiles(), disk(f));
      f.released();
    }
  }

  private void faultMatrix(String operation, boolean nativeRoots) throws Exception {
    Map<String, Integer> expected;
    try (var f = fixture()) {
      if (!operation.equals("start")) f.seed(true, true, false);
      operate(f, operation);
      expected = inventory(f, operation);
      assertEquals(expected, f.counts, operation + " independent call inventory");
      f.released();
    }
    for (var point : expected.entrySet()) {
      boolean root = Set.of("openRoot", "openDirectory", "close").contains(point.getKey());
      if (root != nativeRoots) continue;
      for (int at = 1; at <= point.getValue(); at++)
        try (var f = fixture()) {
          if (!operation.equals("start")) f.seed(true, true, false);
          f.fail = point.getKey();
          f.failAt = at;
          failure(() -> operate(f, operation));
          assertTrue(f.triggered);
          f.released();
          if (Files.exists(f.runs.resolve(RUN_ID + ".run")))
            assertEquals(ANCHOR, Files.readString(f.runs.resolve(RUN_ID + ".run")));
        }
    }
  }

  private static Map<String, Integer> inventory(Fixture f, String operation) {
    int attrs;
    int roots;
    int entries;
    int readers;
    int writers;
    int creates;
    int writes;
    int syncs;
    int unlinks;
    int next;
    int has;
    switch (operation) {
      case "start" -> {
        attrs = 171;
        roots = 13;
        entries = 42;
        readers = 9;
        writers = 3;
        creates = 3;
        writes = 3;
        syncs = 3;
        unlinks = 0;
        next = 7;
        has = 13;
      }
      case "active" -> {
        attrs = 201;
        roots = 13;
        entries = 60;
        readers = 12;
        writers = 3;
        creates = 0;
        writes = 0;
        syncs = 3;
        unlinks = 0;
        next = 10;
        has = 16;
      }
      case "complete" -> {
        attrs = 239;
        roots = 16;
        entries = 72;
        readers = 15;
        writers = 4;
        creates = 1;
        writes = 1;
        syncs = 5;
        unlinks = 1;
        next = 10;
        has = 16;
      }
      default -> throw new AssertionError(operation);
    }
    Map<String, Integer> result = new HashMap<>();
    for (String name : List.of("attributes", "acl", "filesystem", "readonly"))
      result.put(name, attrs);
    result.put("openRoot", roots);
    result.put("openDirectory", roots * (f.varPath.getNameCount() + 5));
    result.put("close", roots * (f.varPath.getNameCount() + 6) + entries);
    result.put("openEntry", entries);
    result.put("openRead", readers);
    result.put("readClose", readers);
    result.put("read", 2 * readers);
    result.put("readSize", 2 * readers);
    result.put("openWriter", writers);
    result.put("writerClose", writers);
    result.put("force", writers);
    result.put("writeSize", 2 * writers);
    result.put("sync", syncs);
    if (creates > 0) {
      result.put("create", creates);
      result.put("publish", creates);
    }
    if (writes > 0) result.put("write", writes);
    if (unlinks > 0) result.put("unlink", unlinks);
    result.put("namesOpen", 6);
    result.put("namesClose", 6);
    result.put("namesIterator", 6);
    result.put("namesNext", next);
    result.put("namesHasNext", has);
    return result;
  }

  private static void operate(Fixture f, String operation) throws IOException {
    switch (operation) {
      case "start" -> f.files.execute(s -> s.start(RUN, ACTIVATION.id()));
      case "active" -> f.files.execute(s -> s.resume(RUN.id(), NEXT));
      case "complete" ->
          f.files.execute(s -> s.complete(completion(MaintenanceCompletion.Outcome.SUCCESS)));
      default -> throw new AssertionError(operation);
    }
  }

  private static void trace(String name, String actual) throws IOException {
    Path root = Path.of("target/run-lifecycle-traces");
    Files.createDirectories(root);
    Files.writeString(root.resolve(name), actual);
  }

  private static void await(CountDownLatch latch) throws IOException {
    try {
      if (!latch.await(10, TimeUnit.SECONDS)) throw new IOException("fixture timeout");
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new IOException("fixture interrupted");
    }
  }

  private Fixture fixture() throws Exception {
    return new Fixture(Files.createTempDirectory(temporary, "lifecycle-"));
  }

  private static void failure(Executable action) {
    var e = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, e.reason());
    assertEquals("transfer storage operation failed", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  @FunctionalInterface
  interface Action {
    void execute() throws IOException;
  }

  static final class Fixture implements AutoCloseable, InodeSecurityCalls, MaintenanceRunFiles.Io {
    final Path base;
    final Path varPath;
    final Path lib;
    final Path app;
    final Path maintenance;
    final Path runs;
    final Path attempts;
    final DirectoryCalls calls;
    final MaintenanceRunFiles files;
    final MaintenanceRunFiles.NioIo nativeIo = new MaintenanceRunFiles.NioIo();
    final Set<Integer> live = ConcurrentHashMap.newKeySet();
    final Map<Long, String> originalRoles = new HashMap<>();
    final Map<String, Integer> counts = new ConcurrentHashMap<>();
    final List<String> syncTargets = Collections.synchronizedList(new ArrayList<>());
    long uid;
    int readers;
    int writers;
    int listings;
    int failAt = 1;
    int hookAt = 1;
    int partSequence;
    String fail = "";
    String hookName = "";
    String invalid = "";
    String badRole = "";
    String listingFault = "";
    boolean triggered;
    boolean rawCloses;
    boolean nullPart;
    boolean overfillReader;
    RuntimeException runtimeFailure;
    Action hook = () -> {};
    BiConsumer<String, Map<String, Object>> change = (role, values) -> {};

    Fixture(Path base) throws Exception {
      this.base = base;
      varPath = base.resolve("var");
      lib = varPath.resolve("lib");
      app = lib.resolve("schubert-nk");
      maintenance = app.resolve("maintenance");
      runs = maintenance.resolve("runs");
      attempts = maintenance.resolve("attempts");
      Files.createDirectories(runs);
      Files.createDirectories(attempts);
      for (String role : List.of("var", "lib", "app", "maintenance", "runs", "attempts"))
        originalRoles.put((Long) Files.getAttribute(path(role), "unix:ino"), role);
      DirectoryCalls delegate = LinuxDirectoryCalls.create();
      calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    if (!name.equals("close"))
                      point(name.equals("createPrivateFile") ? "create" : name);
                    Object result;
                    try {
                      result = method.invoke(delegate, args);
                      if (name.equals("sync"))
                        syncTargets.add(
                            base.relativize(
                                    Path.of("/proc/self/fd", args[0].toString()).toRealPath())
                                .toString());
                    } catch (InvocationTargetException e) {
                      throw e.getCause();
                    }
                    if (Set.of("openRoot", "openDirectory", "openEntry", "createPrivateFile")
                        .contains(name)) assertTrue(live.add((Integer) result));
                    if (name.equals("close")) {
                      assertTrue(live.remove((Integer) args[0]));
                      point("close");
                      if (rawCloses)
                        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                    }
                    return result;
                  });
      files = new MaintenanceRunFiles(varPath, calls, this, this, this::part);
    }

    UUID part() {
      if (nullPart) return null;
      return new UUID(0x157L, ++partSequence);
    }

    Path path(String role) {
      return switch (role) {
        case "var" -> varPath;
        case "lib" -> lib;
        case "app" -> app;
        case "maintenance" -> maintenance;
        case "runs" -> runs;
        case "attempts" -> attempts;
        default -> throw new AssertionError(role);
      };
    }

    void seed(boolean begin, boolean active, boolean done) throws IOException {
      Files.writeString(runs.resolve(RUN_ID + ".run"), ANCHOR);
      if (begin) Files.writeString(attempts.resolve(ACT_ID + ".begin"), BEGIN);
      if (active) Files.writeString(maintenance.resolve("active"), BEGIN);
      if (done) Files.writeString(attempts.resolve(ACT_ID + ".done"), DONE0);
      reset();
    }

    void reset() {
      counts.clear();
      syncTargets.clear();
      fail = "";
      hookName = "";
      triggered = false;
    }

    void otherCompleted() throws IOException {
      Files.writeString(runs.resolve(OTHER + ".run"), ANCHOR.replace(RUN_ID, OTHER.toString()));
      Files.writeString(
          attempts.resolve(NEXT + ".begin"),
          BEGIN.replace(RUN_ID, OTHER.toString()).replace(ACT_ID, NEXT.toString()));
      Files.writeString(
          attempts.resolve(NEXT + ".done"),
          DONE0.replace(RUN_ID, OTHER.toString()).replace(ACT_ID, NEXT.toString()));
    }

    int count(String name) {
      return counts.getOrDefault(name, 0);
    }

    void on(String name, int at, Action action) {
      hookName = name;
      hookAt = at;
      hook = action;
    }

    void point(String name) throws StorageIoException {
      int at = counts.merge(name, 1, Integer::sum);
      if (hookName.equals(name) && hookAt == at) {
        try {
          hook.execute();
        } catch (IOException e) {
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        }
      }
      if (fail.equals(name) && failAt == at) {
        triggered = true;
        if (runtimeFailure != null) throw runtimeFailure;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    void replace(String role) throws IOException {
      Path old = path(role);
      Files.move(old, old.resolveSibling(old.getFileName() + "-saved"));
      Files.createDirectories(runs);
      Files.createDirectories(attempts);
    }

    String role(Path held) throws IOException {
      var attributes = nativeIo.attributes(held);
      String original = originalRoles.get((Long) attributes.get("ino"));
      if (original != null) return original;
      Path resolved = held.toRealPath();
      for (String role : List.of("var", "lib", "app", "maintenance", "runs", "attempts"))
        if (resolved.equals(path(role))) return role;
      return "file";
    }

    boolean selected(Path held) throws IOException {
      return badRole.equals(role(held));
    }

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      point("attributes");
      String role = role(held);
      if (invalid.equals("nullAttributes") && selected(held)) return null;
      var values = new HashMap<>(nativeIo.attributes(held));
      int permission =
          Set.of("var", "lib", "app").contains(role) ? 0755 : role.equals("file") ? 0600 : 0700;
      values.put("mode", ((Integer) values.get("mode") & 0170000) | permission);
      values.put("uid", 0);
      values.put("gid", 0);
      change.accept(role, values);
      return values;
    }

    @Override
    public String filesystem(Path held) throws IOException {
      point("filesystem");
      assertNotNull(nativeIo.filesystem(held));
      if (selected(held)) {
        if (invalid.equals("nullFilesystem")) return null;
        if (invalid.equals("filesystem")) return "nfs";
        if (invalid.equals("tmpfs")) return "tmpfs";
      }
      return "ext4";
    }

    @Override
    public byte[] accessAcl(Path held, int max) throws StorageIoException {
      point("acl");
      assertEquals(44, max);
      try {
        if (selected(held)) {
          if (invalid.equals("nullAcl")) return null;
          if (invalid.equals("acl")) return new byte[] {2, 0, 0, 0};
        }
      } catch (IOException e) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      return new byte[0];
    }

    @Override
    public boolean readOnlyFilesystem(Path held) throws StorageIoException {
      point("readonly");
      try {
        return selected(held) && invalid.equals("readonly");
      } catch (IOException e) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public DirectoryStream<Path> openNames(Path held) throws IOException {
      point("namesOpen");
      if (listingFault.equals("nullStream")) return null;
      DirectoryStream<Path> delegate = nativeIo.openNames(held);
      listings++;
      return new DirectoryStream<>() {
        @Override
        public Iterator<Path> iterator() {
          step("namesIterator");
          Iterator<Path> actual = delegate.iterator();
          if (listingFault.equals("nullEntry"))
            actual = Arrays.<Path>asList((Path) null).iterator();
          if (listingFault.equals("otherParent"))
            actual = List.of(held.resolveSibling("alien")).iterator();
          if (listingFault.equals("duplicate"))
            actual = List.of(held.resolve("runs"), held.resolve("runs")).iterator();
          if (listingFault.equals("rootOnly")) actual = List.of(Path.of("/")).iterator();
          Iterator<Path> chosen = actual;
          return new Iterator<>() {
            @Override
            public boolean hasNext() {
              step("namesHasNext");
              return chosen.hasNext();
            }

            @Override
            public Path next() {
              step("namesNext");
              return chosen.next();
            }
          };
        }

        private void step(String name) {
          try {
            point(name);
          } catch (IOException e) {
            throw new DirectoryIteratorException(e);
          }
        }

        @Override
        public void close() throws IOException {
          delegate.close();
          listings--;
          point("namesClose");
        }
      };
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      point("openRead");
      var channel = nativeIo.open(held);
      readers++;
      return new SeekableByteChannel() {
        @Override
        public int read(ByteBuffer bytes) throws IOException {
          point("read");
          if (overfillReader) {
            int count = bytes.remaining();
            bytes.put(new byte[count]);
            return count;
          }
          return channel.read(bytes);
        }

        @Override
        public long size() throws IOException {
          point("readSize");
          return channel.size();
        }

        @Override
        public void close() throws IOException {
          channel.close();
          readers--;
          point("readClose");
        }

        @Override
        public boolean isOpen() {
          return channel.isOpen();
        }

        @Override
        public int write(ByteBuffer bytes) {
          throw new AssertionError("readonly");
        }

        @Override
        public long position() {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel position(long value) {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel truncate(long value) {
          throw new AssertionError("no truncate");
        }
      };
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path held) throws IOException {
      point("openWriter");
      var writer = nativeIo.openWriter(held);
      writers++;
      return new InspectorEnvironmentPublisher.Writer() {
        @Override
        public int write(ByteBuffer bytes) throws IOException {
          point("write");
          return writer.write(bytes);
        }

        @Override
        public long size() throws IOException {
          point("writeSize");
          return writer.size();
        }

        @Override
        public void force() throws IOException {
          point("force");
          writer.force();
        }

        @Override
        public void close() throws IOException {
          writer.close();
          writers--;
          point("writerClose");
        }
      };
    }

    void released() {
      assertTrue(live.isEmpty());
      assertEquals(0, readers);
      assertEquals(0, writers);
      assertEquals(0, listings);
    }

    @Override
    public void close() {
      released();
    }
  }
}
