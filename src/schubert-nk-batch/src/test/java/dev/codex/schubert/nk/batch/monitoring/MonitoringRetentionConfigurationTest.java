package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicy.DetailService;
import dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicy.RetentionConfiguration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * RETCONF001..008/1700. Independent UI252/SS351 decimal configuration oracle, no service/storage
 * I/O.
 */
class MonitoringRetentionConfigurationTest {
  private static final String CONFIGURATION_DRIFT_CODE = "CONFIG_DRIFT";

  @Test
  void retConf001ExactApprovedDebugAndStandardConfigurationsPassWithoutMutation() {
    assertDoesNotThrow(
        () ->
            MonitoringModePolicy.DEBUG.verifyObservedRetention(
                Optional.of(new RetentionConfiguration(15, 5_000_000_000L))));
    assertDoesNotThrow(
        () ->
            MonitoringModePolicy.STANDARD.verifyObservedRetention(
                Optional.of(new RetentionConfiguration(0, 0))));
    assertEquals(15, MonitoringModePolicy.DEBUG.retentionDays());
    assertEquals(5_000_000_000L, MonitoringModePolicy.DEBUG.retentionBytes());
    assertEquals(0, MonitoringModePolicy.STANDARD.retentionDays());
    assertEquals(0, MonitoringModePolicy.STANDARD.retentionBytes());
  }

  @Test
  void retConf002DebugRejectsEachIndependentDayAndByteMismatchWithoutRounding() {
    for (var wrong :
        List.of(
            new RetentionConfiguration(14, 5_000_000_000L),
            new RetentionConfiguration(16, 5_000_000_000L),
            new RetentionConfiguration(0, 5_000_000_000L),
            new RetentionConfiguration(15, 4_999_999_999L),
            new RetentionConfiguration(15, 5_000_000_001L),
            new RetentionConfiguration(15, 5_368_709_120L),
            new RetentionConfiguration(15, 0),
            new RetentionConfiguration(0, 0))) {
      assertEquals(
          CONFIGURATION_DRIFT_CODE,
          assertThrows(
                  IllegalStateException.class,
                  () -> MonitoringModePolicy.DEBUG.verifyObservedRetention(Optional.of(wrong)))
              .getMessage());
    }
  }

  @Test
  void retConf003MissingNeverBecomesValidStandardZeroAndNonzeroStandardIsDrift() {
    for (var policy : MonitoringModePolicy.values())
      assertEquals(
          CONFIGURATION_DRIFT_CODE,
          assertThrows(
                  IllegalStateException.class,
                  () -> policy.verifyObservedRetention(Optional.empty()))
              .getMessage());
    for (var wrong :
        List.of(
            new RetentionConfiguration(1, 0),
            new RetentionConfiguration(0, 1),
            new RetentionConfiguration(15, 5_000_000_000L)))
      assertEquals(
          CONFIGURATION_DRIFT_CODE,
          assertThrows(
                  IllegalStateException.class,
                  () -> MonitoringModePolicy.STANDARD.verifyObservedRetention(Optional.of(wrong)))
              .getMessage());
    assertDoesNotThrow(
        () ->
            MonitoringModePolicy.STANDARD.verifyObservedRetention(
                Optional.of(new RetentionConfiguration(0, 0))));
  }

  @Test
  void retConf004NegativeInvariantsAndNullOptionalAreRejectedNotUnknownSuccess() {
    for (int days : List.of(-1, Integer.MIN_VALUE))
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(IllegalArgumentException.class, () -> new RetentionConfiguration(days, 0))
              .getMessage());
    for (long bytes : List.of(-1L, Long.MIN_VALUE))
      assertEquals(
          "CONFIG_INVALID",
          assertThrows(IllegalArgumentException.class, () -> new RetentionConfiguration(0, bytes))
              .getMessage());
    assertThrows(IllegalArgumentException.class, () -> new RetentionConfiguration(-1, -1));
    for (var policy : MonitoringModePolicy.values())
      assertEquals(
          "retention configuration observation",
          assertThrows(NullPointerException.class, () -> policy.verifyObservedRetention(null))
              .getMessage());
  }

  @Test
  void retConf005MaximumValuesRemainExactAndCannotOverflowIntoApprovedLimits() {
    var maximum = new RetentionConfiguration(Integer.MAX_VALUE, Long.MAX_VALUE);
    assertEquals(2_147_483_647, maximum.days());
    assertEquals(9_223_372_036_854_775_807L, maximum.bytes());
    for (var policy : MonitoringModePolicy.values())
      for (var wrong :
          List.of(
              maximum,
              new RetentionConfiguration(Integer.MAX_VALUE, 5_000_000_000L),
              new RetentionConfiguration(15, Long.MAX_VALUE)))
        assertEquals(
            CONFIGURATION_DRIFT_CODE,
            assertThrows(
                    IllegalStateException.class,
                    () -> policy.verifyObservedRetention(Optional.of(wrong)))
                .getMessage());
  }

  @Test
  void retConf006RetentionAndCompleteServiceObservationsRemainSeparateImmutableContracts() {
    for (var input :
        Map.of(MonitoringModePolicy.DEBUG, true, MonitoringModePolicy.STANDARD, false).entrySet()) {
      var policy = input.getKey();
      boolean detail = input.getValue();
      var services =
          Map.of(
              DetailService.ACTUATOR,
              detail,
              DetailService.PROMETHEUS,
              detail,
              DetailService.GRAFANA,
              detail,
              DetailService.EXPORTERS,
              detail);
      policy.verifyObserved(services);
      var configuration =
          detail
              ? new RetentionConfiguration(15, 5_000_000_000L)
              : new RetentionConfiguration(0, 0);
      policy.verifyObservedRetention(Optional.of(configuration));
      policy.verifyObserved(services);
      assertEquals(detail, policy.detailedMetricsEnabled());
      assertEquals(detail ? 15 : 0, policy.retentionDays());
      assertEquals(detail ? 5_000_000_000L : 0L, policy.retentionBytes());
      assertEquals(4, services.size());
      assertTrue(services.values().stream().allMatch(value -> value == detail));
    }
  }

  @Test
  void retConf007ParallelModeVerificationCannotMutateOrShareOtherModesConfiguration()
      throws Exception {
    var tasks = new ArrayList<Callable<String>>();
    var debug = new RetentionConfiguration(15, 5_000_000_000L);
    var standard = new RetentionConfiguration(0, 0);
    for (int i = 0; i < 64; i++) {
      boolean detail = i % 2 == 0;
      tasks.add(
          () -> {
            var policy = detail ? MonitoringModePolicy.DEBUG : MonitoringModePolicy.STANDARD;
            policy.verifyObservedRetention(Optional.of(detail ? debug : standard));
            assertEquals(detail ? 15 : 0, policy.retentionDays());
            assertEquals(detail ? 5_000_000_000L : 0L, policy.retentionBytes());
            return "verified";
          });
    }
    var executor = Executors.newFixedThreadPool(8);
    try {
      for (var result : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals("verified", result.get());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS), "retention executor terminated");
    }
    assertEquals(15, debug.days());
    assertEquals(5_000_000_000L, debug.bytes());
    assertEquals(0, standard.days());
    assertEquals(0, standard.bytes());
  }

  @Test
  void retConf008GeneratedConfigurationUsesIndependentIntegerLongHashAndFixedTextOracles() {
    var value = new RetentionConfiguration(15, 5_000_000_000L);
    var equal = new RetentionConfiguration(15, 5_000_000_000L);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertFalse(value.equals(null));
    assertFalse(value.equals("other type"));
    assertNotEquals(value, new RetentionConfiguration(14, 5_000_000_000L));
    assertNotEquals(value, new RetentionConfiguration(15, 5_000_000_001L));
    assertEquals(705033170, value.hashCode());
    assertEquals(0, new RetentionConfiguration(0, 0).hashCode());
    assertEquals(-31, new RetentionConfiguration(Integer.MAX_VALUE, Long.MAX_VALUE).hashCode());
    var one = new RetentionConfiguration(15, 1);
    var collision = new RetentionConfiguration(15, 1L << 32);
    assertEquals(466, one.hashCode());
    assertEquals(466, collision.hashCode());
    assertNotEquals(one, collision);
    assertEquals("RetentionConfiguration[days=15, bytes=5000000000]", value.toString());
    assertEquals(15, value.days());
    assertEquals(5_000_000_000L, value.bytes());
  }
}
