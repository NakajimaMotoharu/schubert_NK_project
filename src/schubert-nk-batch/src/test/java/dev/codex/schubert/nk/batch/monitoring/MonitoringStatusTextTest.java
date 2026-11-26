package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.fixture.BoundedBatchFixtureWorkers;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Independent fixed frames, no expected value from render. PT-OPS-MONSTATUS-001..006/spec1558. */
class MonitoringStatusTextTest {
  private static final String STANDARD =
      "# SUPPLIED_MONITORING_STATE_V1 MODE=STANDARD\n"
          + "condition\tservice\tseverity\tcount\tfirstSeen\tlastSeen\n";
  private static final String DEBUG =
      "# SUPPLIED_MONITORING_STATE_V1 MODE=DEBUG\n"
          + "condition\tservice\tseverity\tcount\tfirstSeen\tlastSeen\n";
  private static final Instant TIME = Instant.parse("2026-10-23T00:00:00.123456789Z");
  private static final String SINGLE =
      "FILESYSTEM\tWEB\tWARNING\t1\t2026-10-23T00:00:00.123Z\t2026-10-23T00:00:00.123Z\n";
  private final MonitoringStatusText renderer = new MonitoringStatusText();

  private static Event event(Condition condition, Service service, Severity severity, Instant at) {
    return new AlertLifecycle(condition, service)
        .observe(severity, CauseClearance.UNCONFIRMED, at, Duration.ZERO)
        .orElseThrow();
  }

  @Test
  void monStatus001EmptyModesHaveOnlySuppliedScopeAndColumns() {
    assertEquals(STANDARD, renderer.render(MonitoringModePolicy.STANDARD, List.of()));
    assertEquals(DEBUG, renderer.render(MonitoringModePolicy.DEBUG, List.of()));
  }

  @Test
  void monStatus002LiteralSingleFrameAndNoRetainedCallerState() {
    var events =
        new ArrayList<>(List.of(event(Condition.FILESYSTEM, Service.WEB, Severity.WARNING, TIME)));
    assertEquals(STANDARD + SINGLE, renderer.render(MonitoringModePolicy.STANDARD, events));
    assertEquals(1, events.size());
    events.clear();
    assertEquals(STANDARD, renderer.render(MonitoringModePolicy.STANDARD, events));
  }

  @Test
  void monStatus003CanonicalOrderCountSeverityAndLastSeen() {
    Instant zero = Instant.parse("2026-10-23T00:00:00Z");
    var owner = new AlertLifecycle(Condition.FILESYSTEM, Service.WEB);
    owner.observe(Severity.WARNING, CauseClearance.UNCONFIRMED, zero, Duration.ZERO);
    var web =
        owner
            .observe(
                Severity.WARNING,
                CauseClearance.UNCONFIRMED,
                zero.plusSeconds(1),
                Duration.ofSeconds(1))
            .orElseThrow();
    var api = event(Condition.FILESYSTEM, Service.API, Severity.CRITICAL, zero);
    var transfer = event(Condition.TRANSFER, Service.WEB, Severity.WARNING, zero);
    var events = new ArrayList<>(List.of(transfer, api, web));
    String expected =
        DEBUG
            + "FILESYSTEM\tWEB\tWARNING\t2\t2026-10-23T00:00:00.000Z\t2026-10-23T00:00:01.000Z\n"
            + "FILESYSTEM\tAPI\tCRITICAL\t1\t2026-10-23T00:00:00.000Z\t2026-10-23T00:00:00.000Z\n"
            + "TRANSFER\tWEB\tWARNING\t1\t2026-10-23T00:00:00.000Z\t2026-10-23T00:00:00.000Z\n";
    assertEquals(expected, renderer.render(MonitoringModePolicy.DEBUG, events));
    assertEquals(List.of(transfer, api, web), events);
  }

  @Test
  void monStatus004NullDuplicateClosedRejectedWithoutOwnerMutation() {
    var owner = new AlertLifecycle(Condition.FILESYSTEM, Service.WEB);
    var open =
        owner
            .observe(Severity.WARNING, CauseClearance.UNCONFIRMED, TIME, Duration.ZERO)
            .orElseThrow();
    assertThrows(NullPointerException.class, () -> renderer.render(null, List.of(open)));
    assertThrows(
        NullPointerException.class, () -> renderer.render(MonitoringModePolicy.STANDARD, null));
    var withNull = new ArrayList<Event>();
    withNull.add(null);
    assertThrows(
        NullPointerException.class, () -> renderer.render(MonitoringModePolicy.STANDARD, withNull));
    assertEquals(
        "invalid monitoring status input",
        assertThrows(
                IllegalArgumentException.class,
                () -> renderer.render(MonitoringModePolicy.STANDARD, List.of(open, open)))
            .getMessage());
    assertEquals(BigInteger.ONE, owner.snapshot().orElseThrow().count());
    owner.observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, TIME, Duration.ZERO);
    var closed =
        owner
            .observe(Severity.NORMAL, CauseClearance.UNCONFIRMED, TIME, Duration.ofMinutes(5))
            .orElseThrow();
    assertEquals(
        "invalid monitoring status input",
        assertThrows(
                IllegalArgumentException.class,
                () -> renderer.render(MonitoringModePolicy.STANDARD, List.of(closed)))
            .getMessage());
    assertTrue(owner.snapshot().isEmpty());
  }

  @Test
  void monStatus005FullInstantBoundaryGoldenVectors() {
    var first = event(Condition.FILESYSTEM, Service.WEB, Severity.WARNING, Instant.MIN);
    var last = event(Condition.TRANSFER, Service.API, Severity.CRITICAL, Instant.MAX);
    String expected =
        STANDARD
            + "FILESYSTEM\tWEB\tWARNING\t1\t-1000000000-01-01T00:00:00.000Z\t-1000000000-01-01T00:00:00.000Z\n"
            + "TRANSFER\tAPI\tCRITICAL\t1\t+1000000000-12-31T23:59:59.999Z\t+1000000000-12-31T23:59:59.999Z\n";
    assertEquals(expected, renderer.render(MonitoringModePolicy.STANDARD, List.of(last, first)));
  }

  @Test
  void monStatus006ConcurrentStatelessFormatting() throws Exception {
    var events = List.of(event(Condition.FILESYSTEM, Service.WEB, Severity.WARNING, TIME));
    try (var workers =
        new BoundedBatchFixtureWorkers(Executors.newFixedThreadPool(4), 10, "status rendering")) {
      var tasks = new ArrayList<Callable<String>>();
      for (int index = 0; index < 64; index++)
        tasks.add(() -> renderer.render(MonitoringModePolicy.STANDARD, events));
      for (var future : workers.executor().invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals(STANDARD + SINGLE, future.get());
    }
  }
}
