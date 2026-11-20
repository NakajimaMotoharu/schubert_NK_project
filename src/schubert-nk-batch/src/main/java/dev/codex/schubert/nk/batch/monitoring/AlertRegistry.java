package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * Finite72-key owner, no dynamic labels/targets. NK-OPS-001/P018-09; MON005..009/013; UI252; SS351
 * §7; PG-D519/PT-OPS-ALERTREG-001..004.
 */
public final class AlertRegistry {
  private final Map<Condition, Map<Service, AlertLifecycle>> states;

  public AlertRegistry() {
    var conditions = new EnumMap<Condition, Map<Service, AlertLifecycle>>(Condition.class);
    for (var condition : Condition.values()) {
      var services = new EnumMap<Service, AlertLifecycle>(Service.class);
      for (var service : Service.values())
        services.put(service, new AlertLifecycle(condition, service));
      conditions.put(condition, Map.copyOf(services));
    }
    states = Map.copyOf(conditions);
  }

  public Optional<Event> observe(
      Condition condition,
      Service service,
      Severity observed,
      CauseClearance clearance,
      Instant at,
      Duration elapsed) {
    return state(condition, service).observe(observed, clearance, at, elapsed);
  }

  /** Missing input must preserve the event and break any continuous-normal recovery period. */
  public void interruptContinuity(Condition condition, Service service, Duration elapsed) {
    state(condition, service).interruptContinuity(elapsed);
  }

  Optional<Event> observeWindowed(
      Condition condition,
      Service service,
      Severity severity,
      boolean aboveWarning,
      ObservationContext context) {
    Objects.requireNonNull(context, "observation context");
    return state(condition, service).observeWindowed(severity, aboveWarning, context);
  }

  private AlertLifecycle state(Condition condition, Service service) {
    Objects.requireNonNull(condition, "alert condition");
    Objects.requireNonNull(service, "alert service");
    var services = Objects.requireNonNull(states.get(condition), "closed condition registry");
    return Objects.requireNonNull(services.get(service), "closed service registry");
  }

  /** Per-key consistent immutable snapshots, not a cross-service transactional observation. */
  public List<Event> activeEvents() {
    var events = new ArrayList<Event>();
    for (var condition : Condition.values()) {
      for (var service : Service.values())
        state(condition, service).snapshot().ifPresent(events::add);
    }
    return List.copyOf(events);
  }
}
