package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/**
 * GENB001..007: public value contracts only; no real observation, runtime gate or process
 * operation.
 */
class GeneratedBatchValueContractTest {
  private record Expected<E extends Enum<E>>(String literal, E constant) {}

  private static <E extends Enum<E>> Expected<E> e(String literal, E constant) {
    return new Expected<>(literal, constant);
  }

  private static <E extends Enum<E>> void enumeration(
      Supplier<E[]> values, Function<String, E> lookup, List<Expected<E>> expected) {
    var actual = values.get();
    assertEquals(
        expected.stream().map(Expected::literal).toList(),
        Arrays.stream(actual).map(Enum::name).toList());
    assertEquals(expected.size(), actual.length);
    for (var item : expected) assertSame(item.constant(), lookup.apply(item.literal()));
    assertThrows(IllegalArgumentException.class, () -> lookup.apply("UNKNOWN_ENUM"));
    assertThrows(NullPointerException.class, () -> lookup.apply(null));
    actual[0] = expected.getLast().constant();
    assertSame(expected.getFirst().constant(), values.get()[0]);
  }

  @Test
  void genBatch001LifecycleEnumFactoriesAreClosedAndArraysAreIndependent() {
    enumeration(
        Condition::values,
        Condition::valueOf,
        List.of(
            e("FILESYSTEM", Condition.FILESYSTEM),
            e("TRANSFER", Condition.TRANSFER),
            e("ASYNC_QUEUE", Condition.ASYNC_QUEUE),
            e("WEB_LOG", Condition.WEB_LOG),
            e("DLQ", Condition.DLQ),
            e("EXPIRY", Condition.EXPIRY),
            e("DB_POOL", Condition.DB_POOL),
            e("JVM_HEAP", Condition.JVM_HEAP),
            e("SYNC_P95", Condition.SYNC_P95),
            e("BACKUP", Condition.BACKUP),
            e("RESTART", Condition.RESTART),
            e("INTEGRITY_CONFIG", Condition.INTEGRITY_CONFIG)));
    enumeration(
        Service::values,
        Service::valueOf,
        List.of(
            e("WEB", Service.WEB),
            e("API", Service.API),
            e("BATCH", Service.BATCH),
            e("BROKER", Service.BROKER),
            e("DB", Service.DB),
            e("CADDY", Service.CADDY)));
    enumeration(
        Severity::values,
        Severity::valueOf,
        List.of(
            e("NORMAL", Severity.NORMAL),
            e("WARNING", Severity.WARNING),
            e("CRITICAL", Severity.CRITICAL)));
    enumeration(
        CauseClearance::values,
        CauseClearance::valueOf,
        List.of(
            e("UNCONFIRMED", CauseClearance.UNCONFIRMED),
            e("CONFIRMED", CauseClearance.CONFIRMED)));
  }

  @Test
  void genBatch002BatchStepAndTerminalFactoriesUseIndependentLiteralVectors() {
    enumeration(
        BatchMetricContract.Step::values,
        BatchMetricContract.Step::valueOf,
        List.of(
            e("BACKUP_DB", BatchMetricContract.Step.BACKUP_DB),
                e("BACKUP_CONFIG", BatchMetricContract.Step.BACKUP_CONFIG),
            e("CLEAN_NOTIFICATION", BatchMetricContract.Step.CLEAN_NOTIFICATION),
                e("CLEAN_QUESTION", BatchMetricContract.Step.CLEAN_QUESTION),
            e("CLEAN_SESSION", BatchMetricContract.Step.CLEAN_SESSION),
                e("CLEAN_INBOX_OUTBOX", BatchMetricContract.Step.CLEAN_INBOX_OUTBOX),
            e("CLEAN_LOG", BatchMetricContract.Step.CLEAN_LOG),
                e("CLEAN_BATCH_RUN", BatchMetricContract.Step.CLEAN_BATCH_RUN),
            e("CLEAN_TRANSFER", BatchMetricContract.Step.CLEAN_TRANSFER),
                e("CLEAN_EXPIRY", BatchMetricContract.Step.CLEAN_EXPIRY)));
    enumeration(
        BatchMetricContract.Status::values,
        BatchMetricContract.Status::valueOf,
        List.of(
            e("SUCCESS", BatchMetricContract.Status.SUCCESS),
                e("WARNING", BatchMetricContract.Status.WARNING),
            e("FAILED", BatchMetricContract.Status.FAILED),
                e("SKIPPED", BatchMetricContract.Status.SKIPPED)));
  }

  @Test
  void genBatch003MetricCatalogAndKindFactoriesHaveExactCanonicalValues() {
    enumeration(
        MetricContract::values,
        MetricContract::valueOf,
        List.of(
            e("HTTP_REQUESTS", MetricContract.HTTP_REQUESTS),
                e("HTTP_DURATION", MetricContract.HTTP_DURATION),
            e("MQ_MESSAGES", MetricContract.MQ_MESSAGES),
                e("MQ_DURATION", MetricContract.MQ_DURATION),
            e("MQ_QUEUE_MESSAGES", MetricContract.MQ_QUEUE_MESSAGES),
                e("MQ_QUEUE_BYTES", MetricContract.MQ_QUEUE_BYTES),
            e("MQ_ADDRESS_MEMORY", MetricContract.MQ_ADDRESS_MEMORY),
                e("MQ_ADDRESS_PAGED", MetricContract.MQ_ADDRESS_PAGED),
            e("MQ_PAGING_ACTIVE", MetricContract.MQ_PAGING_ACTIVE),
                e("MQ_PAGE_FILES", MetricContract.MQ_PAGE_FILES),
            e("MQ_REDELIVERIES", MetricContract.MQ_REDELIVERIES),
                e("OUTBOX_ROWS", MetricContract.OUTBOX_ROWS),
            e("OUTBOX_OLDEST", MetricContract.OUTBOX_OLDEST),
                e("INBOX_REPLAYS", MetricContract.INBOX_REPLAYS),
            e("OPERATION_TOKEN_MISMATCH", MetricContract.OPERATION_TOKEN_MISMATCH),
                e("ASYNC_JOBS", MetricContract.ASYNC_JOBS),
            e("DB_POOL_CONNECTIONS", MetricContract.DB_POOL_CONNECTIONS),
                e("DB_QUERY_DURATION", MetricContract.DB_QUERY_DURATION),
            e("FILE_TRANSFER_FILES", MetricContract.FILE_TRANSFER_FILES),
                e("FILE_TRANSFER_BYTES", MetricContract.FILE_TRANSFER_BYTES),
            e("MEDIA_STREAMS", MetricContract.MEDIA_STREAMS),
                e("MEDIA_BYTES", MetricContract.MEDIA_BYTES),
            e("INTEGRITY_FAILURES", MetricContract.INTEGRITY_FAILURES),
                e("BATCH_RUNS", MetricContract.BATCH_RUNS),
            e("BATCH_LAST_SUCCESS", MetricContract.BATCH_LAST_SUCCESS),
                e("PROCESS_RESTARTS", MetricContract.PROCESS_RESTARTS)));
    enumeration(
        MetricContract.Kind::values,
        MetricContract.Kind::valueOf,
        List.of(
            e("COUNTER", MetricContract.Kind.COUNTER),
            e("GAUGE", MetricContract.Kind.GAUGE),
            e("HISTOGRAM", MetricContract.Kind.HISTOGRAM)));
  }

  @Test
  void genBatch004ModeContinuityAndSuffixFactoriesCannotShareReturnedArrays() {
    enumeration(
        MonitoringModePolicy::values,
        MonitoringModePolicy::valueOf,
        List.of(
            e("DEBUG", MonitoringModePolicy.DEBUG), e("STANDARD", MonitoringModePolicy.STANDARD)));
    enumeration(
        MonitoringModePolicy.DetailService::values,
        MonitoringModePolicy.DetailService::valueOf,
        List.of(
            e("ACTUATOR", MonitoringModePolicy.DetailService.ACTUATOR),
                e("PROMETHEUS", MonitoringModePolicy.DetailService.PROMETHEUS),
            e("GRAFANA", MonitoringModePolicy.DetailService.GRAFANA),
                e("EXPORTERS", MonitoringModePolicy.DetailService.EXPORTERS)));
    enumeration(
        ContinuousConditionWindow.State::values,
        ContinuousConditionWindow.State::valueOf,
        List.of(
            e("VIOLATING", ContinuousConditionWindow.State.VIOLATING),
            e("NORMAL", ContinuousConditionWindow.State.NORMAL),
            e("UNKNOWN", ContinuousConditionWindow.State.UNKNOWN)));
    enumeration(
        TransferMetricRecorder.Suffix::values,
        TransferMetricRecorder.Suffix::valueOf,
        List.of(
            e("PART", TransferMetricRecorder.Suffix.PART),
            e("READY", TransferMetricRecorder.Suffix.READY)));
  }

  @Test
  void genBatch005ObservationContextGeneratedContractsUseIndependentPlatformHashes() {
    var actual = new ObservationContext(CauseClearance.UNCONFIRMED, Instant.EPOCH, Duration.ZERO);
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not a context";
    assertTrue(actual.equals(sameInstance));
    assertTrue(
        actual.equals(
            new ObservationContext(CauseClearance.UNCONFIRMED, Instant.EPOCH, Duration.ZERO)));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    for (var changed :
        List.of(
            new ObservationContext(CauseClearance.CONFIRMED, Instant.EPOCH, Duration.ZERO),
            new ObservationContext(
                CauseClearance.UNCONFIRMED, Instant.ofEpochSecond(1), Duration.ZERO),
            new ObservationContext(CauseClearance.UNCONFIRMED, Instant.EPOCH, Duration.ofNanos(1))))
      assertFalse(actual.equals(changed));
    // Enum hash is the platform identity, EPOCH/ZERO component hashes are independently zero.
    assertEquals(
        31 * (31 * System.identityHashCode(CauseClearance.UNCONFIRMED)), actual.hashCode());
    assertEquals(
        "ObservationContext[clearance=UNCONFIRMED, at=1970-01-01T00:00:00Z, elapsed=PT0S]",
        actual.toString());
    assertSame(CauseClearance.UNCONFIRMED, actual.clearance());
    assertEquals(Instant.EPOCH, actual.at());
    assertEquals(Duration.ZERO, actual.elapsed());
  }

  private static Event event() {
    return new AlertLifecycle(Condition.FILESYSTEM, Service.BATCH)
        .observe(Severity.WARNING, CauseClearance.UNCONFIRMED, Instant.EPOCH, Duration.ZERO)
        .orElseThrow();
  }

  private static <T> void evaluation(
      BiFunction<Boolean, Optional<Event>, T> factory,
      Function<T, Boolean> supplied,
      Function<T, Optional<Event>> eventAccessor) {
    T actual = factory.apply(true, Optional.empty());
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not an evaluation";
    assertTrue(actual.equals(sameInstance));
    assertTrue(actual.equals(factory.apply(true, Optional.empty())));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    assertFalse(actual.equals(factory.apply(false, Optional.empty())));
    Event first = event();
    Event second = event();
    assertFalse(actual.equals(factory.apply(true, Optional.of(first))));
    T populated = factory.apply(true, Optional.of(first));
    assertTrue(populated.equals(factory.apply(true, Optional.of(first))));
    assertFalse(populated.equals(factory.apply(true, Optional.of(second))));
    assertEquals(31 * 1231, actual.hashCode());
    assertEquals(31 * 1231 + System.identityHashCode(first), populated.hashCode());
    assertEquals("Evaluation[suppliedValuePresent=true, event=Optional.empty]", actual.toString());
    assertEquals(
        "Evaluation[suppliedValuePresent=true,"
            + " event=Optional[dev.codex.schubert.nk.batch.monitoring.AlertLifecycle$Event@"
            + Integer.toHexString(System.identityHashCode(first))
            + "]]",
        populated.toString());
    assertTrue(supplied.apply(actual));
    assertFalse(supplied.apply(factory.apply(false, Optional.empty())));
    assertEquals(Optional.empty(), eventAccessor.apply(actual));
    assertSame(first, eventAccessor.apply(populated).orElseThrow());
    assertThrows(NullPointerException.class, () -> factory.apply(true, null));
  }

  @Test
  void genBatch006AllFiveEvaluationRecordsHaveEveryFieldInValueContracts() {
    evaluation(
        TimedFilesystemMonitor.Evaluation::new,
        TimedFilesystemMonitor.Evaluation::suppliedValuePresent,
        TimedFilesystemMonitor.Evaluation::event);
    evaluation(
        TimedJvmHeapMonitor.Evaluation::new,
        TimedJvmHeapMonitor.Evaluation::suppliedValuePresent,
        TimedJvmHeapMonitor.Evaluation::event);
    evaluation(
        TimedDbPoolMonitor.Evaluation::new,
        TimedDbPoolMonitor.Evaluation::suppliedValuePresent,
        TimedDbPoolMonitor.Evaluation::event);
    evaluation(
        TimedSyncLatencyMonitor.Evaluation::new,
        TimedSyncLatencyMonitor.Evaluation::suppliedValuePresent,
        TimedSyncLatencyMonitor.Evaluation::event);
    evaluation(
        TransferHealthMonitor.Evaluation::new,
        TransferHealthMonitor.Evaluation::suppliedValuePresent,
        TransferHealthMonitor.Evaluation::event);
  }

  @Test
  void genBatch007TransferCountsHaveExactPrimitiveGeneratedValueContracts() {
    var actual = new TransferMetricRecorder.Counts(3, 5);
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not transfer counts";
    assertTrue(actual.equals(sameInstance));
    assertTrue(actual.equals(new TransferMetricRecorder.Counts(3, 5)));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    assertFalse(actual.equals(new TransferMetricRecorder.Counts(4, 5)));
    assertFalse(actual.equals(new TransferMetricRecorder.Counts(3, 6)));
    assertEquals(3, actual.files());
    assertEquals(5, actual.bytes());
    assertEquals(98, actual.hashCode());
    assertEquals("Counts[files=3, bytes=5]", actual.toString());
    var maximum = new TransferMetricRecorder.Counts(Long.MAX_VALUE, Long.MAX_VALUE);
    assertEquals(0, maximum.hashCode());
    assertEquals(
        "Counts[files=9223372036854775807, bytes=9223372036854775807]", maximum.toString());
  }
}
