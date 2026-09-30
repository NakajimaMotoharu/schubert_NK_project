package dev.codex.schubert.nk.batch.mq;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Read-only six-Queue stored count/byte pressure. No startup decision or business message mutation.
 * NK-OPS-001; RD MQ-001/002/009/010,SYS-004; UI231/251/253; SS321 §5.2/5.3/10/13,342 §4;
 * QA-042/UIC-002/SSC-075; PG242/PT-OPS-MQ-019..021.
 */
@NullMarked
public final class ArtemisQueuePressureClient {
  @FunctionalInterface
  interface Reader {
    @Nullable Object read(ClientSession session, String queue, String attribute);
  }

  public enum Pressure {
    NORMAL,
    WARNING,
    ALERT,
    CRITICAL
  }

  private static final long MIB = 1024L * 1024L;
  private static final Map<String, Limits> LIMITS = limits();
  private final Reader reader;

  public ArtemisQueuePressureClient() {
    this(ArtemisManagementReadinessClient::queueMetric);
  }

  ArtemisQueuePressureClient(Reader reader) {
    this.reader = Objects.requireNonNull(reader, "queue metric reader");
  }

  /** Returns approved match names; caller owns Ops session and decides startup policy. */
  public Map<String, Pressure> inspect(ClientSession session) {
    var states = new LinkedHashMap<String, Pressure>();
    inspectValues(session).forEach((address, actual) -> states.put(address, actual.state()));
    return Map.copyOf(states);
  }

  public record Value(long count, long bytes, Pressure state) {
    public Value {
      Objects.requireNonNull(state);
      if (count < 0 || bytes < 0)
        throw new IllegalArgumentException("queue observation unavailable");
    }
  }

  /** SSC130: actual count/bytes and derived policy; same two queries per Queue. */
  public Map<String, Value> inspectValues(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    {
      var states = new LinkedHashMap<String, Value>();
      for (var entry : LIMITS.entrySet()) {
        String queue = entry.getKey() + ".q";
        long count = nonNegative(reader.read(session, queue, "messageCount"));
        long bytes = nonNegative(reader.read(session, queue, "persistentSize"));
        Limits limits = entry.getValue();
        Pressure pressure;
        if (bytes >= fraction(limits.bytes(), 90)
            || (!limits.deadLetter() && count >= limits.criticalCount())) {
          pressure = Pressure.CRITICAL;
        } else if (limits.deadLetter() && count >= 1) {
          pressure = Pressure.ALERT;
        } else if (bytes >= fraction(limits.bytes(), 70)
            || (!limits.deadLetter() && count >= limits.warningCount())) {
          pressure = Pressure.WARNING;
        } else {
          pressure = Pressure.NORMAL;
        }
        states.put(entry.getKey(), new Value(count, bytes, pressure));
      }
      return Map.copyOf(states);
    }
  }

  private static long nonNegative(@Nullable Object value) {
    long number;
    if (value instanceof Integer integer) number = integer.longValue();
    else if (value instanceof Long large) number = large;
    else throw new ArtemisManagementReadinessException();
    if (number < 0) throw new ArtemisManagementReadinessException();
    return number;
  }

  private static long fraction(long total, int percent) {
    return (total * percent + 99) / 100;
  }

  private static Map<String, Limits> limits() {
    var values = new LinkedHashMap<String, Limits>();
    values.put("nk.sync.request", new Limits(256 * MIB, 250, 450, false));
    values.put("nk.sync.reply.web", new Limits(256 * MIB, 250, 450, false));
    values.put("nk.async.work", new Limits(1024 * MIB, 5_000, 9_000, false));
    values.put("nk.web.log", new Limits(256 * MIB, 5_000, 9_000, false));
    values.put("nk.dead.letter", new Limits(2048 * MIB, 0, 0, true));
    values.put("nk.expiry", new Limits(1024 * MIB, 1_000, 5_000, false));
    return Map.copyOf(values);
  }

  private record Limits(long bytes, long warningCount, long criticalCount, boolean deadLetter) {}
}
