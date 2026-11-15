package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BAT-MVALUE001002; SS331/341/343: immutable public data only, never operational permission. */
final class MaintenanceDataValueContractTest {
  private static final UUID ID = new UUID(0, 1);
  private static final UUID OTHER_ID = new UUID(0, 2);
  private static final Instant CUTOFF = Instant.parse("2024-01-01T00:00:00Z");
  private static final Instant END = Instant.parse("2024-01-02T00:00:00Z");
  private static final Instant PREPARED = Instant.parse("2025-02-06T00:00:00Z");
  private static final Instant AGE400 = Instant.parse("2025-02-05T00:00:00Z");
  private static final BatchRun RUN = new BatchRun(ID, CUTOFF);
  private static final MaintenanceActivation ACTIVE = new MaintenanceActivation(RUN, ID);
  private static final String HASH = "a".repeat(64);
  private static final String OTHER_HASH = "f".repeat(64);
  private static final String UNKNOWN = "PUBLIC_UNKNOWN";

  private static <T> void values(T actual, T equal, List<T> different) {
    assertEquals(actual, actual);
    assertEquals(actual, equal);
    assertEquals(equal, actual);
    assertEquals(actual.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(actual, "found").get(equal));
    assertNotEquals(actual, null);
    assertNotEquals(actual, UNKNOWN);
    for (T other : different) {
      assertNotEquals(actual, other);
      assertNotEquals(other, actual);
    }
  }

  @Test
  void mvalue001RunActivationCompletionAndStateKeepAllComponentsAndClosedOutcome() {
    values(
        RUN,
        new BatchRun(ID, CUTOFF),
        List.of(new BatchRun(OTHER_ID, CUTOFF), new BatchRun(ID, CUTOFF.plusNanos(1000))));
    assertEquals(ID, RUN.id());
    assertEquals(CUTOFF, RUN.cutoff());
    assertEquals("BatchRun[identity/cutoff=<redacted>]", RUN.toString());
    for (String valid : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      Instant at = Instant.parse(valid);
      assertEquals(at, new BatchRun(ID, at).cutoff());
    }
    for (String invalid :
        List.of(
            "0000-12-31T23:59:59.999999Z",
            "+10000-01-01T00:00:00Z",
            "2024-01-01T00:00:00.000000001Z")) {
      Instant at = Instant.parse(invalid);
      assertThrows(IllegalArgumentException.class, () -> new BatchRun(ID, at));
    }
    assertThrows(NullPointerException.class, () -> new BatchRun(null, CUTOFF));
    assertThrows(NullPointerException.class, () -> new BatchRun(ID, null));
    values(
        ACTIVE,
        new MaintenanceActivation(new BatchRun(ID, CUTOFF), ID),
        List.of(
            new MaintenanceActivation(new BatchRun(OTHER_ID, CUTOFF), ID),
            new MaintenanceActivation(RUN, OTHER_ID)));
    assertSame(RUN, ACTIVE.run());
    assertEquals(ID, ACTIVE.id());
    assertEquals(LocalDate.of(2024, 1, 1), ACTIVE.businessDate());
    assertEquals(
        LocalDate.of(2026, 9, 13),
        new MaintenanceActivation(new BatchRun(ID, Instant.parse("2026-09-12T15:00:00Z")), ID)
            .businessDate());
    assertEquals("MaintenanceActivation[identity/cutoff=<redacted>]", ACTIVE.toString());
    assertThrows(NullPointerException.class, () -> new MaintenanceActivation(null, ID));
    assertThrows(NullPointerException.class, () -> new MaintenanceActivation(RUN, null));
    var completed = new MaintenanceCompletion(ACTIVE, END, MaintenanceCompletion.Outcome.SUCCESS);
    values(
        completed,
        new MaintenanceCompletion(
            new MaintenanceActivation(new BatchRun(ID, CUTOFF), ID),
            END,
            MaintenanceCompletion.Outcome.SUCCESS),
        List.of(
            new MaintenanceCompletion(
                new MaintenanceActivation(RUN, OTHER_ID),
                END,
                MaintenanceCompletion.Outcome.SUCCESS),
            new MaintenanceCompletion(
                ACTIVE, END.plusNanos(1000), MaintenanceCompletion.Outcome.SUCCESS),
            new MaintenanceCompletion(ACTIVE, END, MaintenanceCompletion.Outcome.WARNING)));
    var pending = new MaintenanceRunState(ACTIVE, Optional.empty());
    values(
        pending,
        new MaintenanceRunState(
            new MaintenanceActivation(new BatchRun(ID, CUTOFF), ID), Optional.empty()),
        List.of(
            new MaintenanceRunState(new MaintenanceActivation(RUN, OTHER_ID), Optional.empty()),
            new MaintenanceRunState(ACTIVE, Optional.of(completed))));
    var doneData = new MaintenanceRunState(ACTIVE, Optional.of(completed));
    values(
        doneData,
        new MaintenanceRunState(
            ACTIVE,
            Optional.of(
                new MaintenanceCompletion(ACTIVE, END, MaintenanceCompletion.Outcome.SUCCESS))),
        List.of(
            new MaintenanceRunState(
                ACTIVE,
                Optional.of(
                    new MaintenanceCompletion(
                        ACTIVE, END.plusNanos(1000), MaintenanceCompletion.Outcome.SUCCESS)))));
    assertSame(ACTIVE, doneData.activation());
    assertSame(completed, doneData.completion().orElseThrow());
    assertEquals("MaintenanceRunState[redacted]", doneData.toString());
    assertArrayEquals(
        new String[] {"SUCCESS", "WARNING"},
        Arrays.stream(MaintenanceCompletion.Outcome.values())
            .map(Enum::name)
            .toArray(String[]::new));
    assertSame(
        MaintenanceCompletion.Outcome.SUCCESS, MaintenanceCompletion.Outcome.valueOf("SUCCESS"));
    assertSame(
        MaintenanceCompletion.Outcome.WARNING, MaintenanceCompletion.Outcome.valueOf("WARNING"));
    var outcomes = MaintenanceCompletion.Outcome.values();
    outcomes[0] = MaintenanceCompletion.Outcome.WARNING;
    assertSame(MaintenanceCompletion.Outcome.SUCCESS, MaintenanceCompletion.Outcome.values()[0]);
    assertEquals(0, MaintenanceCompletion.Outcome.SUCCESS.exitCode());
    assertEquals(10, MaintenanceCompletion.Outcome.WARNING.exitCode());
    for (String invalid : List.of("", "success", UNKNOWN))
      assertThrows(
          IllegalArgumentException.class, () -> MaintenanceCompletion.Outcome.valueOf(invalid));
    assertThrows(NullPointerException.class, () -> MaintenanceCompletion.Outcome.valueOf(null));
  }

  @Test
  void mvalue002RetirementDataStrictAgePrecisionCountDigestAndValueBoundsAreIndependent() {
    var actual = new MaintenanceRetirement(RUN, END, PREPARED, 1, HASH);
    values(
        actual,
        new MaintenanceRetirement(new BatchRun(ID, CUTOFF), END, PREPARED, 1, HASH),
        List.of(
            new MaintenanceRetirement(new BatchRun(OTHER_ID, CUTOFF), END, PREPARED, 1, HASH),
            new MaintenanceRetirement(RUN, END.plusNanos(1000), PREPARED, 1, HASH),
            new MaintenanceRetirement(RUN, END, PREPARED.plusNanos(1000), 1, HASH),
            new MaintenanceRetirement(RUN, END, PREPARED, 2, HASH),
            new MaintenanceRetirement(RUN, END, PREPARED, 1, OTHER_HASH)));
    assertSame(RUN, actual.run());
    assertEquals(END, actual.latestEnded());
    assertEquals(PREPARED, actual.preparedAt());
    assertEquals(1, actual.count());
    assertEquals(HASH, actual.digest());
    assertEquals("MaintenanceRetirement[identity/time/plan=<redacted>]", actual.toString());
    for (int count : List.of(1, Integer.MAX_VALUE))
      for (String hash : List.of("0".repeat(64), OTHER_HASH)) {
        var valid = new MaintenanceRetirement(RUN, END, AGE400.plusNanos(1000), count, hash);
        assertEquals(count, valid.count());
        assertEquals(hash, valid.digest());
        assertEquals(Instant.parse("2025-02-05T00:00:00.000001Z"), valid.preparedAt());
      }
    Instant maximum = Instant.parse("9999-12-31T23:59:59.999999Z");
    assertEquals(maximum, new MaintenanceRetirement(RUN, END, maximum, 1, HASH).preparedAt());
    for (Instant latest :
        List.of(CUTOFF.minusNanos(1000), Instant.parse("+10000-01-01T00:00:00Z"), END.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, latest, PREPARED, 1, HASH));
    for (Instant prepared :
        List.of(
            Instant.parse("+10000-01-01T00:00:00Z"),
            PREPARED.plusNanos(1),
            AGE400,
            AGE400.minusNanos(1000),
            END.minusNanos(1000)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, END, prepared, 1, HASH));
    for (int count : List.of(Integer.MIN_VALUE, -1, 0))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, END, PREPARED, count, HASH));
    for (String hash :
        List.of(
            "",
            "a".repeat(63),
            "a".repeat(65),
            "A".repeat(64),
            "g".repeat(64),
            " " + HASH,
            HASH + "\n"))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceRetirement(RUN, END, PREPARED, 1, hash));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(null, END, PREPARED, 1, HASH));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(RUN, null, PREPARED, 1, HASH));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(RUN, END, null, 1, HASH));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceRetirement(RUN, END, PREPARED, 1, null));
  }
}
