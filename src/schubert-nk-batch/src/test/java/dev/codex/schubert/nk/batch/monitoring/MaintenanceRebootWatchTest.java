package dev.codex.schubert.nk.batch.monitoring;

import static dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch.Decision.COMPLETE;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch.Decision.CRITICAL;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch.Decision.INVALID_OBSERVATION;
import static dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch.Decision.WAITING;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch.Decision;
import dev.codex.schubert.nk.batch.monitoring.MaintenanceRebootWatch.Marker;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.ResourceLock;
import org.junit.jupiter.api.parallel.Resources;

/** Independent boundary literals derived from SS341 §4.2. */
final class MaintenanceRebootWatchTest {
  private static final String START_TIME = "2026-11-21T20:00:00Z";
  private static final String EXACT_TIME = "2026-11-21T21:00:00Z";
  private static final UUID RUN = new UUID(0, 1);
  private static final UUID OTHER_RUN = new UUID(0, 2);
  private static final UUID OLD_BOOT = new UUID(0, 3);
  private static final UUID NEW_BOOT = new UUID(0, 4);

  @Test
  void waitBeforeTheExactSixtyMinuteBoundary() {
    assertEquals(WAITING, read(START_TIME, null));
    assertEquals(WAITING, read("2026-11-21T20:59:59.999999999Z", null));
  }

  @Test
  void missingMarkerIsCriticalAtTheDeadlineAndAfter() {
    assertEquals(CRITICAL, read(EXACT_TIME, null));
    assertEquals(CRITICAL, read("2026-11-21T21:00:00.000000001Z", null));
  }

  @Test
  void acceptsSameRunNewBootAtTheDeadlineIncludingLaterReview() {
    Marker marker = new Marker(RUN, NEW_BOOT, Instant.parse(EXACT_TIME));
    assertEquals(COMPLETE, read(EXACT_TIME, marker));
    assertEquals(COMPLETE, read("2026-11-21T21:05:00Z", marker));
  }

  @Test
  void wrongRunOrSameBootDoesNotQualify() {
    Instant recording = Instant.parse("2026-11-21T20:40:00Z");
    assertEquals(WAITING, read("2026-11-21T20:45:00Z", new Marker(OTHER_RUN, NEW_BOOT, recording)));
    assertEquals(CRITICAL, read(EXACT_TIME, new Marker(OTHER_RUN, NEW_BOOT, recording)));
    assertEquals(CRITICAL, read(EXACT_TIME, new Marker(RUN, OLD_BOOT, recording)));
  }

  @Test
  void staleFutureAndLateMarkersDoNotQualifyAtTheDeadline() {
    assertEquals(CRITICAL, read(EXACT_TIME, new Marker(RUN, NEW_BOOT, Instant.parse(START_TIME))));
    Instant later = Instant.parse("2026-11-21T21:00:01Z");
    assertEquals(CRITICAL, read(EXACT_TIME, new Marker(RUN, NEW_BOOT, later)));
    assertEquals(CRITICAL, read("2026-11-21T21:01:00Z", new Marker(RUN, NEW_BOOT, later)));
  }

  @Test
  void backwardObservationIsInvalid() {
    assertEquals(INVALID_OBSERVATION, read("2026-11-21T19:59:59Z", null));
  }

  @Test
  void malformedOperandsProduceOnlyTheFixedInvalidDecision() {
    assertEquals(INVALID_OBSERVATION, MaintenanceRebootWatch.parseObservation(null));
    assertEquals(INVALID_OBSERVATION, MaintenanceRebootWatch.parseObservation(new String[0]));
    assertEquals(INVALID_OBSERVATION, MaintenanceRebootWatch.parseObservation(new String[5]));
    assertEquals(
        INVALID_OBSERVATION,
        MaintenanceRebootWatch.parseObservation(
            new String[] {RUN.toString(), OLD_BOOT.toString(), null, EXACT_TIME}));
    assertEquals(
        INVALID_OBSERVATION,
        MaintenanceRebootWatch.parseObservation(
            new String[] {"0-0-0-0-1", OLD_BOOT.toString(), START_TIME, EXACT_TIME}));
    assertEquals(
        INVALID_OBSERVATION,
        MaintenanceRebootWatch.parseObservation(
            new String[] {RUN.toString(), OLD_BOOT.toString(), "unknown", EXACT_TIME}));
    Instant time = Instant.parse(START_TIME);
    assertThrows(NullPointerException.class, () -> new Marker(null, NEW_BOOT, time));
    assertThrows(NullPointerException.class, () -> new Marker(RUN, null, time));
    assertThrows(NullPointerException.class, () -> new Marker(RUN, NEW_BOOT, null));
  }

  @Test
  @ResourceLock(Resources.SYSTEM_OUT)
  void commandPrintsOneDecisionForEachAcceptedOperandShape() {
    var bytes = new ByteArrayOutputStream();
    PrintStream original = System.out;
    try (var output = new PrintStream(bytes, true, StandardCharsets.UTF_8)) {
      System.setOut(output);
      MaintenanceRebootWatch.main(
          new String[] {RUN.toString(), OLD_BOOT.toString(), START_TIME, EXACT_TIME});
      MaintenanceRebootWatch.main(
          new String[] {
            RUN.toString(),
            OLD_BOOT.toString(),
            START_TIME,
            EXACT_TIME,
            RUN.toString(),
            NEW_BOOT.toString(),
            "2026-11-21T20:40:00Z"
          });
    } finally {
      System.setOut(original);
    }
    assertEquals(
        "CRITICAL\nCOMPLETE\n", bytes.toString(StandardCharsets.UTF_8).replace("\r\n", "\n"));
  }

  private static Decision read(String observation, @Nullable Marker marker) {
    return MaintenanceRebootWatch.evaluate(
        RUN,
        OLD_BOOT,
        Instant.parse(START_TIME),
        Instant.parse(observation),
        Optional.ofNullable(marker));
  }
}
