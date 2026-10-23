package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;

/** Supplied mismatch observation only, no token/HMAC/key/authentication access. PG-D544/1643. */
public final class OperationMismatchMetricRecorder {
  public enum Operation {
    UCRREQ01,
    USTREQ01,
    URLREQ01,
    UPWREQ01,
    ULKREQ01,
    QSBREQ01,
    NTCREQ01,
    QDLREQ01
  }

  private final boolean detailed;
  private final Map<Operation, Counter> mismatchCounters;

  /** One caller-owned registry namespace; initial registration failures are never retried here. */
  public OperationMismatchMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    var counters = new EnumMap<Operation, Counter>(Operation.class);
    if (detailed)
      for (var operation : Operation.values())
        counters.put(
            operation,
            Counter.builder("nk_operation_token_mismatch_total")
                .tag("operation", operation.name())
                .register(registry));
    mismatchCounters = Map.copyOf(counters);
  }

  public static Operation operation(String supplied) {
    Objects.requireNonNull(supplied, "metric operation");
    for (var operation : Operation.values())
      if (operation.name().equals(supplied)) return operation;
    throw new IllegalArgumentException("CONFIG_INVALID");
  }

  public void record(Operation operation) {
    Objects.requireNonNull(operation, "metric operation");
    if (detailed)
      Objects.requireNonNull(mismatchCounters.get(operation), "closed operation counter")
          .increment();
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
