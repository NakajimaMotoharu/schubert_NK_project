package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.BatchMetricContract.Status;
import dev.codex.schubert.nk.batch.monitoring.BatchMetricContract.Step;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

/** Literal canonical labels, not production-generated expected values. SS341/351/spec1611. */
class BatchMetricContractTest {
  private static final String INVALID_CONFIG_CODE = "CONFIG_INVALID";
  static final String[] STEPS = {
    "BACKUP_DB",
    "BACKUP_CONFIG",
    "CLEAN_NOTIFICATION",
    "CLEAN_QUESTION",
    "CLEAN_SESSION",
    "CLEAN_INBOX_OUTBOX",
    "CLEAN_LOG",
    "CLEAN_BATCH_RUN",
    "CLEAN_TRANSFER",
    "CLEAN_EXPIRY"
  };
  static final String[] STATUSES = {"SUCCESS", "WARNING", "FAILED", "SKIPPED"};

  @Test
  void batchMet001CanonicalNamesTypesAndClosedValuesMatchLiteralCatalogue() {
    var contract = new BatchMetricContract();
    assertEquals("nk_batch_runs_total", contract.runsName());
    assertEquals("nk_batch_last_success_timestamp_seconds", contract.lastSuccessName());
    assertEquals(
        Set.of(STEPS), Arrays.stream(Step.values()).map(Enum::name).collect(Collectors.toSet()));
    assertEquals(
        Set.of(STATUSES),
        Arrays.stream(Status.values()).map(Enum::name).collect(Collectors.toSet()));
    assertEquals(MetricContract.Kind.COUNTER, MetricContract.parse("nk_batch_runs_total").type());
    assertEquals(
        MetricContract.Kind.GAUGE,
        MetricContract.parse("nk_batch_last_success_timestamp_seconds").type());
  }

  @Test
  void batchMet002EveryLiteralLookupHasItsOwnCanonicalIdentity() {
    var contract = new BatchMetricContract();
    for (String step : STEPS) assertEquals(step, contract.step(step).name());
    for (String status : STATUSES) assertEquals(status, contract.status(status).name());
  }

  @Test
  void batchMet003NullUnknownAndCanaryInputsCannotBeEchoedOrAccepted() {
    var contract = new BatchMetricContract();
    assertThrows(NullPointerException.class, () -> contract.step(null));
    assertThrows(NullPointerException.class, () -> contract.status(null));
    for (String value :
        List.of("", "SUCCESS ", "success", "MORNING", "RUNNING", "PT_SECRET_CANARY_ONLY")) {
      assertEquals(
          INVALID_CONFIG_CODE,
          assertThrows(IllegalArgumentException.class, () -> contract.step(value)).getMessage());
      assertEquals(
          INVALID_CONFIG_CODE,
          assertThrows(IllegalArgumentException.class, () -> contract.status(value)).getMessage());
    }
    for (int i = 0; i < 1000; i++) {
      String value = "PT_CANARY_ONLY_" + i;
      assertEquals(
          INVALID_CONFIG_CODE,
          assertThrows(IllegalArgumentException.class, () -> contract.step(value)).getMessage());
      assertEquals(
          INVALID_CONFIG_CODE,
          assertThrows(IllegalArgumentException.class, () -> contract.status(value)).getMessage());
    }
  }

  @Test
  void batchMet004ModesRemainStrictWithoutServiceOperations() {
    var contract = new BatchMetricContract();
    assertFalse(contract.detailedMetricsEnabled("STANDARD"));
    assertTrue(contract.detailedMetricsEnabled("DEBUG"));
    assertThrows(NullPointerException.class, () -> contract.detailedMetricsEnabled(null));
    for (String invalid : List.of("debug", "", " DEBUG", "PT_CANARY_ONLY"))
      assertThrows(IllegalArgumentException.class, () -> contract.detailedMetricsEnabled(invalid));
  }

  @Test
  void batchMet005AllFortyImmutableLabelsHaveOnlyFixedKeysAndValues() {
    var contract = new BatchMetricContract();
    int count = 0;
    for (String step : STEPS) {
      var success = contract.successLabels(contract.step(step));
      assertEquals(Map.of("step", step), success);
      assertThrows(
          UnsupportedOperationException.class, () -> success.put("actor", "PT_CANARY_ONLY"));
      for (String status : STATUSES) {
        var labels = contract.runLabels(contract.step(step), contract.status(status));
        assertEquals(Map.of("step", step, "status", status), labels);
        assertThrows(
            UnsupportedOperationException.class, () -> labels.put("run", "PT_CANARY_ONLY"));
        count++;
      }
    }
    assertEquals(40, count);
    assertThrows(NullPointerException.class, () -> contract.successLabels(null));
    assertThrows(NullPointerException.class, () -> contract.runLabels(null, Status.SUCCESS));
    assertThrows(NullPointerException.class, () -> contract.runLabels(Step.BACKUP_DB, null));
  }
}
