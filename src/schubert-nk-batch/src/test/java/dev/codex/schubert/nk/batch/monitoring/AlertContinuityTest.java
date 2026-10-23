package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.time.Duration;
import java.time.Instant;
import org.junit.jupiter.api.Test;

/** Explicit recovery interruption contract, fixed elapsed literals. Spec1563/ALERTCONT001..002. */
class AlertContinuityTest {
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  @Test
  void alertContinuity001InvalidInterruptionHasNoStateChange() {
    var owner = new AlertLifecycle(Condition.FILESYSTEM, Service.WEB);
    assertThrows(NullPointerException.class, () -> owner.interruptContinuity(null));
    assertThrows(
        IllegalArgumentException.class, () -> owner.interruptContinuity(Duration.ofNanos(-1)));
    owner.interruptContinuity(Duration.ZERO);
    assertTrue(owner.snapshot().isEmpty());
    owner.interruptContinuity(Duration.ZERO);
    var opened =
        owner.observe(Severity.WARNING, CauseClearance.UNCONFIRMED, AT, Duration.ofSeconds(1));
    assertEquals(
        "invalid alert elapsed time",
        assertThrows(IllegalArgumentException.class, () -> owner.interruptContinuity(Duration.ZERO))
            .getMessage());
    assertThrows(NullPointerException.class, () -> owner.interruptContinuity(null));
    assertEquals(opened, owner.snapshot());
    owner.interruptContinuity(Duration.ofSeconds(2));
    assertEquals(opened, owner.snapshot());
  }

  @Test
  void alertContinuity002WarningAndCriticalRecoveryCannotBridgeGap() {
    for (var level : new Severity[] {Severity.WARNING, Severity.CRITICAL}) {
      var owner = new AlertLifecycle(Condition.FILESYSTEM, Service.API);
      owner.observe(level, CauseClearance.UNCONFIRMED, AT, Duration.ZERO);
      owner.observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, AT, Duration.ofSeconds(1));
      owner.interruptContinuity(Duration.ofSeconds(300));
      long period = level == Severity.WARNING ? 300 : 600;
      assertTrue(
          owner
              .observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, AT, Duration.ofSeconds(301))
              .orElseThrow()
              .isOpen());
      assertTrue(
          owner
              .observe(
                  Severity.NORMAL,
                  CauseClearance.CONFIRMED,
                  AT,
                  Duration.ofSeconds(301 + period).minusNanos(1))
              .orElseThrow()
              .isOpen());
      if (level == Severity.CRITICAL)
        assertTrue(
            owner
                .observe(
                    Severity.NORMAL,
                    CauseClearance.UNCONFIRMED,
                    AT,
                    Duration.ofSeconds(301 + period))
                .orElseThrow()
                .isOpen());
      assertEquals(
          false,
          owner
              .observe(
                  Severity.NORMAL, CauseClearance.CONFIRMED, AT, Duration.ofSeconds(301 + period))
              .orElseThrow()
              .isOpen());
      assertTrue(owner.snapshot().isEmpty());
      owner.interruptContinuity(Duration.ofSeconds(301 + period));
      assertTrue(owner.snapshot().isEmpty());
    }
  }
}
