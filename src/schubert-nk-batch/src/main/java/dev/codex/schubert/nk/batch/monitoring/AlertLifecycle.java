package dev.codex.schubert.nk.batch.monitoring;

import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;

/**
 * One pure alert key, never a live observer/controller. NK-OPS-001/P018-09; MON005..009/013; UI252
 * §6; SS351 §7/SS-D044; PG-D519/PT-OPS-ALERT-001..010.
 */
public final class AlertLifecycle {
  public enum Condition {
    FILESYSTEM,
    TRANSFER,
    ASYNC_QUEUE,
    WEB_LOG,
    DLQ,
    EXPIRY,
    DB_POOL,
    JVM_HEAP,
    SYNC_P95,
    BACKUP,
    RESTART,
    INTEGRITY_CONFIG
  }

  public enum Service {
    WEB,
    API,
    BATCH,
    BROKER,
    DB,
    CADDY
  }

  public enum Severity {
    NORMAL,
    WARNING,
    CRITICAL
  }

  public enum CauseClearance {
    UNCONFIRMED,
    CONFIRMED
  }

  /** Immutable public projection; only the validated lifecycle can create it. */
  public static final class Event {
    private final Condition conditionKey;
    private final Service serviceKey;
    private final Severity eventSeverity;
    private final Instant openedAt;
    private final Instant lastViolationAt;
    private final BigInteger occurrences;
    private final boolean activeFlag;

    private Event(
        Condition condition,
        Service service,
        Severity severity,
        Instant firstSeen,
        Instant lastSeen,
        BigInteger count,
        boolean open) {
      this.conditionKey = condition;
      this.serviceKey = service;
      this.eventSeverity = severity;
      this.openedAt = firstSeen;
      this.lastViolationAt = lastSeen;
      this.occurrences = count;
      this.activeFlag = open;
    }

    public Condition condition() {
      return conditionKey;
    }

    public Service service() {
      return serviceKey;
    }

    public Severity severity() {
      return eventSeverity;
    }

    public Instant firstSeen() {
      return openedAt;
    }

    public Instant lastSeen() {
      return lastViolationAt;
    }

    public BigInteger count() {
      return occurrences;
    }

    public boolean isOpen() {
      return activeFlag;
    }
  }

  private static final String INVALID_ELAPSED = "invalid alert elapsed time";
  private static final Duration WARNING_RECOVERY = Duration.ofMinutes(5);
  private static final Duration CRITICAL_RECOVERY = Duration.ofMinutes(10);
  private final State state;

  public AlertLifecycle(Condition condition, Service service) {
    state =
        new State(
            Objects.requireNonNull(condition, "alert condition"),
            Objects.requireNonNull(service, "alert service"));
  }

  /**
   * Caller supplies the same-owner monotonic elapsed time and explicit cause evidence. UTC display
   * time does not determine recovery duration. Rejected inputs leave state unchanged.
   */
  public Optional<Event> observe(
      Severity observed, CauseClearance clearance, Instant at, Duration elapsed) {
    Objects.requireNonNull(observed, "alert severity");
    Objects.requireNonNull(clearance, "cause clearance");
    Objects.requireNonNull(at, "observation time");
    Objects.requireNonNull(elapsed, "monotonic elapsed");
    if (elapsed.isNegative()) throw new IllegalArgumentException(INVALID_ELAPSED);
    return observed == Severity.NORMAL
        ? state.normal(clearance, elapsed)
        : state.violation(observed, at, elapsed);
  }

  /** Missing samples/gaps preserve the open event but never bridge a normal recovery period. */
  public void interruptContinuity(Duration elapsed) {
    interruptRecovery(elapsed);
  }

  /** An exceeded threshold awaiting its trigger window cannot establish normal recovery. */
  Optional<Event> observeWindowed(Severity severity, boolean aboveWarning, ObservationContext at) {
    Objects.requireNonNull(at, "observation context");
    if (severity == Severity.NORMAL && aboveWarning) return interruptRecovery(at.elapsed());
    return observe(severity, at.clearance(), at.at(), at.elapsed());
  }

  private Optional<Event> interruptRecovery(Duration elapsed) {
    Objects.requireNonNull(elapsed, "monotonic elapsed");
    if (elapsed.isNegative()) throw new IllegalArgumentException(INVALID_ELAPSED);
    return state.interrupt(elapsed);
  }

  public Optional<Event> snapshot() {
    return state.snapshot();
  }

  /** Each transition and snapshot takes the same private state monitor. */
  private static final class State {
    private final Condition conditionKey;
    private final Service serviceKey;
    private Optional<Event> active = Optional.empty();
    private Optional<Duration> recoveringSince = Optional.empty();
    private Optional<Duration> lastElapsed = Optional.empty();

    private State(Condition condition, Service service) {
      conditionKey = condition;
      serviceKey = service;
    }

    private synchronized Optional<Event> snapshot() {
      return active;
    }

    private synchronized Optional<Event> interrupt(Duration elapsed) {
      advance(elapsed);
      recoveringSince = Optional.empty();
      return active;
    }

    private synchronized Optional<Event> violation(
        Severity observed, Instant at, Duration elapsed) {
      advance(elapsed);
      recoveringSince = Optional.empty();
      Instant first = active.map(Event::firstSeen).orElse(at);
      BigInteger count = active.map(Event::count).orElse(BigInteger.ZERO).add(BigInteger.ONE);
      Severity level = observed;
      if (active.isPresent() && active.orElseThrow().severity() == Severity.CRITICAL)
        level = Severity.CRITICAL;
      active = Optional.of(new Event(conditionKey, serviceKey, level, first, at, count, true));
      return active;
    }

    private synchronized Optional<Event> normal(CauseClearance clearance, Duration elapsed) {
      advance(elapsed);
      if (active.isEmpty()) return Optional.empty();
      // SS351 §12: routine normal samples/cause flags cannot retire investigation-required alerts.
      if (conditionKey == Condition.DLQ || conditionKey == Condition.INTEGRITY_CONFIG)
        return active;
      Duration since = recoveringSince.orElse(elapsed);
      recoveringSince = Optional.of(since);
      Event event = active.orElseThrow();
      Duration recovery =
          event.severity() == Severity.CRITICAL ? CRITICAL_RECOVERY : WARNING_RECOVERY;
      boolean enough = elapsed.minus(since).compareTo(recovery) >= 0;
      if (enough
          && (event.severity() != Severity.CRITICAL || clearance == CauseClearance.CONFIRMED)) {
        var closed =
            new Event(
                conditionKey,
                serviceKey,
                event.severity(),
                event.firstSeen(),
                event.lastSeen(),
                event.count(),
                false);
        active = Optional.empty();
        recoveringSince = Optional.empty();
        return Optional.of(closed);
      }
      return active;
    }

    /** Called with the state monitor held. */
    private void advance(Duration elapsed) {
      if (lastElapsed.isPresent() && elapsed.compareTo(lastElapsed.orElseThrow()) < 0)
        throw new IllegalArgumentException(INVALID_ELAPSED);
      lastElapsed = Optional.of(elapsed);
    }
  }
}
