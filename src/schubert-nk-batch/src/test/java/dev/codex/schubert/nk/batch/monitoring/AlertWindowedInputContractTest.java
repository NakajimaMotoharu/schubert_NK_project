package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS351 §7 and UI252, PT-TIMED-RECOVERY-011 through 013. */
final class AlertWindowedInputContractTest {
  private static final Instant EPOCH = Instant.parse("2026-10-23T00:00:00Z");

  @Test
  void pendingBeforeFirstTriggerDoesNotCreateAnAlert() {
    var owner = new AlertLifecycle(Condition.FILESYSTEM, Service.WEB);
    assertTrue(owner.observeWindowed(Severity.NORMAL, true, sampleAt(30)).isEmpty());
    assertTrue(owner.snapshot().isEmpty());
    var alert = owner.observeWindowed(Severity.WARNING, true, sampleAt(330)).orElseThrow();
    assertTrue(alert.isOpen());
    assertEquals(BigInteger.ONE, alert.count());
    assertEquals(Instant.parse("2026-10-23T00:05:30Z"), alert.firstSeen());
    assertEquals(Instant.parse("2026-10-23T00:05:30Z"), alert.lastSeen());
  }

  @Test
  void invalidPendingObservationCannotResetAnExistingRecovery() {
    var owner = new AlertLifecycle(Condition.DB_POOL, Service.API);
    var open = owner.observeWindowed(Severity.WARNING, true, sampleAt(10)).orElseThrow();
    assertSame(open, owner.observeWindowed(Severity.NORMAL, false, sampleAt(11)).orElseThrow());
    assertThrows(
        NullPointerException.class, () -> owner.observeWindowed(Severity.NORMAL, true, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> owner.observeWindowed(Severity.NORMAL, true, sampleAt(10)));
    assertSame(open, owner.snapshot().orElseThrow());
    assertSame(open, owner.observeWindowed(Severity.NORMAL, false, sampleAt(310)).orElseThrow());
    var closed = owner.observeWindowed(Severity.NORMAL, false, sampleAt(311)).orElseThrow();
    assertFalse(closed.isOpen());
    assertEquals(BigInteger.ONE, closed.count());
    assertEquals(EPOCH.plusSeconds(10), closed.lastSeen());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void diagnosticNamesRoundTripThroughTheClosedAlertVocabulary() {
    assertEquals(
        List.of(
            "FILESYSTEM",
            "TRANSFER",
            "ASYNC_QUEUE",
            "WEB_LOG",
            "DLQ",
            "EXPIRY",
            "DB_POOL",
            "JVM_HEAP",
            "SYNC_P95",
            "BACKUP",
            "RESTART",
            "INTEGRITY_CONFIG"),
        names(Condition.values()));
    assertEquals(List.of("WEB", "API", "BATCH", "BROKER", "DB", "CADDY"), names(Service.values()));
    assertEquals(List.of("NORMAL", "WARNING", "CRITICAL"), names(Severity.values()));
    assertEquals(List.of("UNCONFIRMED", "CONFIRMED"), names(CauseClearance.values()));
    assertSame(Condition.DB_POOL, Condition.valueOf("DB_POOL"));
    assertSame(Service.WEB, Service.valueOf("WEB"));
    assertSame(Severity.CRITICAL, Severity.valueOf("CRITICAL"));
    assertSame(CauseClearance.CONFIRMED, CauseClearance.valueOf("CONFIRMED"));
    assertThrows(IllegalArgumentException.class, () -> Condition.valueOf("OTHER"));
    assertThrows(IllegalArgumentException.class, () -> Service.valueOf("OTHER"));
    assertThrows(IllegalArgumentException.class, () -> Severity.valueOf("OTHER"));
    assertThrows(IllegalArgumentException.class, () -> CauseClearance.valueOf("OTHER"));
  }

  private static List<String> names(Enum<?>[] values) {
    return Arrays.stream(values).map(Enum::name).toList();
  }

  private static ObservationContext sampleAt(long seconds) {
    return new ObservationContext(
        CauseClearance.UNCONFIRMED, EPOCH.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }
}
