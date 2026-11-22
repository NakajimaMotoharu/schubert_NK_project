package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicy.DetailService;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Independent SS351 truth table/literals. PT-OPS-MONMODE-001..007, specification1541. */
class MonitoringModePolicyTest {
  private static final List<DetailService> SERVICES =
      List.of(
          DetailService.ACTUATOR,
          DetailService.PROMETHEUS,
          DetailService.GRAFANA,
          DetailService.EXPORTERS);

  private static Map<DetailService, Boolean> observation(int mask) {
    var result = new EnumMap<DetailService, Boolean>(DetailService.class);
    for (int index = 0; index < 4; index++)
      result.put(SERVICES.get(index), (mask & (1 << index)) != 0);
    return result;
  }

  @Test
  void monMode001ApprovedLiteralSettings() {
    assertEquals(MonitoringModePolicy.DEBUG, MonitoringModePolicy.parse("DEBUG"));
    assertEquals(MonitoringModePolicy.STANDARD, MonitoringModePolicy.parse("STANDARD"));
    assertTrue(MonitoringModePolicy.DEBUG.detailedMetricsEnabled());
    assertEquals(15, MonitoringModePolicy.DEBUG.retentionDays());
    assertEquals(5_000_000_000L, MonitoringModePolicy.DEBUG.retentionBytes());
    assertFalse(MonitoringModePolicy.STANDARD.detailedMetricsEnabled());
    assertEquals(0, MonitoringModePolicy.STANDARD.retentionDays());
    assertEquals(0, MonitoringModePolicy.STANDARD.retentionBytes());
  }

  @Test
  void monMode002MatchingObservationsNotMutated() {
    var debug = observation(15);
    var standard = observation(0);
    assertDoesNotThrow(() -> MonitoringModePolicy.DEBUG.verifyObserved(debug));
    assertDoesNotThrow(() -> MonitoringModePolicy.STANDARD.verifyObserved(standard));
    assertEquals(
        Map.of(
            DetailService.ACTUATOR,
            true,
            DetailService.PROMETHEUS,
            true,
            DetailService.GRAFANA,
            true,
            DetailService.EXPORTERS,
            true),
        debug);
    assertEquals(
        Map.of(
            DetailService.ACTUATOR,
            false,
            DetailService.PROMETHEUS,
            false,
            DetailService.GRAFANA,
            false,
            DetailService.EXPORTERS,
            false),
        standard);
  }

  @Test
  void monMode003AllThirtyTwoServiceStates() {
    for (int mask = 0; mask < 16; mask++) {
      var observed = observation(mask);
      for (var mode : MonitoringModePolicy.values()) {
        boolean expectedSuccess = mode == MonitoringModePolicy.DEBUG ? mask == 15 : mask == 0;
        if (expectedSuccess) assertDoesNotThrow(() -> mode.verifyObserved(observed));
        else
          assertEquals(
              "CONFIG_DRIFT",
              assertThrows(IllegalStateException.class, () -> mode.verifyObserved(observed))
                  .getMessage());
      }
    }
  }

  @Test
  void monMode004MissingObservationNeverMeansHealthy() {
    for (var mode : MonitoringModePolicy.values()) {
      assertEquals(
          "CONFIG_DRIFT",
          assertThrows(IllegalStateException.class, () -> mode.verifyObserved(Map.of()))
              .getMessage());
      for (var service : SERVICES) {
        var missing = observation(mode == MonitoringModePolicy.DEBUG ? 15 : 0);
        missing.remove(service);
        assertEquals(
            "CONFIG_DRIFT",
            assertThrows(IllegalStateException.class, () -> mode.verifyObserved(missing))
                .getMessage());
      }
    }
  }

  @Test
  void monMode005NullContractsAreNotNormalObservations() {
    assertThrows(NullPointerException.class, () -> MonitoringModePolicy.parse(null));
    assertThrows(NullPointerException.class, () -> MonitoringModePolicy.DEBUG.verifyObserved(null));
    var nullKey = new HashMap<DetailService, Boolean>();
    nullKey.put(null, true);
    assertThrows(
        NullPointerException.class, () -> MonitoringModePolicy.DEBUG.verifyObserved(nullKey));
    var nullValue = observation(0);
    nullValue.put(DetailService.ACTUATOR, null);
    assertThrows(
        NullPointerException.class, () -> MonitoringModePolicy.STANDARD.verifyObserved(nullValue));
  }

  @Test
  void monMode006UnknownAndAliasedInputIsRedacted() {
    for (String value :
        List.of(
            "",
            "debug",
            "standard",
            " DEBUG",
            "DEBUG ",
            "TEST",
            "synthetic-private-canary",
            "DEBUG\n",
            "STANDARD\t")) {
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(IllegalArgumentException.class, () -> MonitoringModePolicy.parse(value))
              .getMessage());
    }
  }

  @Test
  void monMode007ConcurrentCallersCannotChangePolicy()
      throws InterruptedException, ExecutionException {
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<String>>();
      for (int index = 0; index < 64; index++) {
        tasks.add(
            () -> {
              MonitoringModePolicy.DEBUG.verifyObserved(observation(15));
              MonitoringModePolicy.STANDARD.verifyObserved(observation(0));
              assertEquals(15, MonitoringModePolicy.DEBUG.retentionDays());
              assertEquals(5_000_000_000L, MonitoringModePolicy.DEBUG.retentionBytes());
              assertEquals(0, MonitoringModePolicy.STANDARD.retentionBytes());
              return "verified";
            });
      }
      for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals("verified", future.get());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
