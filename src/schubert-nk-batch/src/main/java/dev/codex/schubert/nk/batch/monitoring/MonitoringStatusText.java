package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Objects;

/**
 * Supplied values only: not a structured-log event, readiness, owner or actual observation proof.
 * No I/O or arbitrary text input. NK-OPS-001/P018-09; MON005..013; UI252; SS351 §7;
 * PG-D522/PT-OPS-MONSTATUS-001..006.
 */
public final class MonitoringStatusText {
  private static final DateTimeFormatter TIME =
      new DateTimeFormatterBuilder().appendInstant(3).toFormatter(Locale.ROOT);

  /** Return a deterministic active-snapshot view; never modify or acquire a live owner. */
  public String render(MonitoringModePolicy mode, List<Event> events) {
    Objects.requireNonNull(mode, "monitoring mode");
    var ordered = new ArrayList<>(List.copyOf(Objects.requireNonNull(events, "alert snapshots")));
    var keys = new HashSet<String>();
    for (var event : ordered) {
      String key = event.condition().name() + ":" + event.service().name();
      if (!event.isOpen() || !keys.add(key))
        throw new IllegalArgumentException("invalid monitoring status input");
    }
    ordered.sort(
        Comparator.comparingInt((Event event) -> event.condition().ordinal())
            .thenComparingInt(event -> event.service().ordinal()));
    var text =
        new StringBuilder("# SUPPLIED_MONITORING_STATE_V1 MODE=")
            .append(mode.name())
            .append('\n')
            .append("condition\tservice\tseverity\tcount\tfirstSeen\tlastSeen\n");
    for (var event : ordered) {
      text.append(event.condition().name())
          .append('\t')
          .append(event.service().name())
          .append('\t')
          .append(event.severity().name())
          .append('\t')
          .append(event.count())
          .append('\t')
          .append(TIME.format(event.firstSeen()))
          .append('\t')
          .append(TIME.format(event.lastSeen()))
          .append('\n');
    }
    return text.toString();
  }
}
