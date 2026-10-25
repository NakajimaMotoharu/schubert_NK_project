package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** OPS-009/BAK-001/UI251/SS341/343/SSC104/PG333; CPR001..004 independent order oracle. */
final class CleanupPreflightTest {
  private static final UUID RUN = UUID.fromString("12345678-9abc-def0-8123-456789abcdef");
  private static final UUID ACTIVATION = UUID.fromString("11111111-2222-4333-8444-555555555555");
  private static final Instant CUTOFF = Instant.parse("2026-09-12T15:00:00Z");
  private static final Instant NOW = Instant.parse("2026-09-12T15:00:06.123456789Z");
  private static final String SHA =
      "bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370";
  private static final List<String> EXPECTED =
      List.of("gate", "request", "original", "database", "request", "original", "gate");

  private static CleanupWorkerRequest request() {
    return new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, SHA);
  }

  private static MaintenanceActivation activation() {
    return new MaintenanceActivation(new BatchRun(RUN, CUTOFF), ACTIVATION);
  }

  private static BackupManifest manifest() {
    return BackupArtifactFixture.expected();
  }

  private static Clock clock() {
    return Clock.fixed(NOW, ZoneOffset.UTC);
  }

  private static final class Case {
    final List<String> events = new ArrayList<>();
    int requestReads;
    int originalReads;
    int gates;
    int databaseReads;
    String fail = "";
    CleanupWorkerRequest secondRequest = request();
    MaintenanceActivation secondOriginal = activation();
    BackupManifest verified = manifest();
    Clock time = clock();
    final AtomicInteger interruptChecks = new AtomicInteger();
    int stopAt;

    CleanupPreflight subject() {
      return new CleanupPreflight(
          () -> {
            events.add("gate");
            gates++;
            if (fail.equals("gate" + gates)) throw new IOException("PUBLIC_CANARY");
          },
          () -> {
            events.add("request");
            requestReads++;
            if (fail.equals("request" + requestReads)) throw new IOException("PUBLIC_CANARY");
            return requestReads == 1 ? request() : secondRequest;
          },
          value -> {
            events.add("original");
            originalReads++;
            assertEquals(request(), value);
            if (fail.equals("original" + originalReads)) throw new IOException("PUBLIC_CANARY");
            return originalReads == 1 ? activation() : secondOriginal;
          },
          (value, observed) -> {
            events.add("database");
            databaseReads++;
            assertEquals(request(), value);
            assertEquals(Instant.parse("2026-09-12T15:00:06.123456Z"), observed);
            if (fail.equals("database")) throw new IOException("PUBLIC_CANARY");
            return verified;
          },
          time,
          () -> stopAt != 0 && interruptChecks.incrementAndGet() == stopAt);
    }
  }

  @Test
  void fixedSequenceAndReplayNeverClaimDelete() throws Exception { // CPR001/004
    var c = new Case();
    var subject = c.subject();
    assertEquals(manifest(), subject.verify());
    assertEquals(EXPECTED, c.events);
    assertEquals(1, c.databaseReads);
    assertEquals(2, c.requestReads);
    assertEquals(2, c.originalReads);
    assertEquals(2, c.gates);
    var replay = new Case();
    assertEquals(manifest(), replay.subject().verify());
    assertEquals(EXPECTED, replay.events);
  }

  @Test
  void changedRequestOrOriginalOrManifestCannotPass() { // CPR002
    var altered = new Case();
    altered.secondRequest = new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, "a".repeat(64));
    denied(altered);
    assertEquals(EXPECTED.subList(0, 5), altered.events);

    var original = new Case();
    original.secondOriginal =
        new MaintenanceActivation(
            new BatchRun(RUN, CUTOFF), UUID.fromString("22222222-3333-4444-8555-666666666666"));
    denied(original);
    assertEquals(EXPECTED.subList(0, 6), original.events);

    var wrongRun = new Case();
    wrongRun.verified = shifted(UUID.fromString("aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"), CUTOFF);
    denied(wrongRun);
    assertEquals(EXPECTED.subList(0, 4), wrongRun.events);

    var wrongCutoff = new Case();
    wrongCutoff.verified = shifted(RUN, CUTOFF.plusSeconds(1));
    denied(wrongCutoff);
    assertEquals(EXPECTED.subList(0, 4), wrongCutoff.events);
  }

  @Test
  void everyKnownStageFailureIsFixedAndStopsDownstream() { // CPR003
    for (String stage :
        List.of("gate1", "request1", "original1", "database", "request2", "original2", "gate2")) {
      var c = new Case();
      c.fail = stage;
      denied(c);
      int position =
          switch (stage) {
            case "gate1" -> 1;
            case "request1" -> 2;
            case "original1" -> 3;
            case "database" -> 4;
            case "request2" -> 5;
            case "original2" -> 6;
            default -> 7;
          };
      assertEquals(EXPECTED.subList(0, position), c.events, stage);
    }
  }

  @Test
  void cutoffAndFourInterruptBarriersAreNonSuccess() { // CPR004
    var early = new Case();
    early.time = Clock.fixed(CUTOFF.minusSeconds(1), ZoneOffset.UTC);
    denied(early);
    assertEquals(EXPECTED.subList(0, 3), early.events);

    for (int stop = 1; stop <= 4; stop++) {
      var c = new Case();
      c.stopAt = stop;
      denied(c);
      assertEquals(stop, c.interruptChecks.get());
      assertTrue(c.events.size() <= 7);
      assertTrue(c.databaseReads <= 1);
    }
  }

  @Test
  void nullContractsDoNotBecomeNormalFailure() { // CPR004
    CleanupPreflight.Gate gate = () -> {};
    CleanupPreflight.Request request = CleanupPreflightTest::request;
    CleanupPreflight.Original original = ignored -> activation();
    CleanupPreflight.Database database = (ignored, time) -> manifest();
    assertThrows(
        NullPointerException.class,
        () -> new CleanupPreflight(null, request, original, database, clock()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupPreflight(gate, null, original, database, clock()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupPreflight(gate, request, null, database, clock()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupPreflight(gate, request, original, null, clock()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupPreflight(gate, request, original, database, null));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupPreflight(gate, request, original, database, clock(), null));
    assertEquals(
        manifest(),
        assertDoesNotThrow(
            () -> new CleanupPreflight(gate, request, original, database, clock()).verify()));
  }

  private static void denied(Case c) {
    IOException failure = assertThrows(IOException.class, () -> c.subject().verify());
    assertEquals("root cleanup preflight unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static BackupManifest shifted(UUID runId, Instant cutoff) {
    BackupManifest baseline = manifest();
    BatchRun run = new BatchRun(runId, cutoff);
    BatchStepAttempt database = baseline.databaseStep();
    BatchStepAttempt configuration = baseline.configurationStep();
    return new BackupManifest(
        new BatchStepAttempt(
            database.id(), run, database.step(), database.attempt(), cutoff, database.skipped()),
        new BatchStepAttempt(
            configuration.id(),
            run,
            configuration.step(),
            configuration.attempt(),
            cutoff.plusSeconds(1),
            configuration.skipped()),
        cutoff.plusSeconds(2),
        cutoff.plusSeconds(3),
        baseline.versions(),
        baseline.recipientSha256(),
        baseline.dump(),
        baseline.configuration(),
        baseline.credentials());
  }
}
