package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.LinuxMonotonicClock;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.DateTimeException;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Root-issued nonsecret correlation, NEVER a lock/parent-liveness/Epoch capability. The fixed
 * private reader and actual mutation guard must independently establish those facts.
 * NK-OPS-001/NK-DAT-001; OPS009/DAT009/UI251/SS341§7.3/343§6.17; SSC119/289 COWNER001..004.
 */
@NullMarked
public record MaintenanceOwnerFrame(
    UUID boot,
    UUID run,
    UUID activation,
    Instant cutoff,
    UUID epoch,
    Parent morning,
    Optional<Parent> cleanup,
    long deadlineNanos) {
  public static final int MAXIMUM_BYTES = 1024;
  private static final UUID NIL = new UUID(0, 0);

  /** A borrowed live check, not transferable authority. Native callers also prove own actor. */
  @FunctionalInterface
  public interface Guard {
    long remainingNanos() throws IOException;

    default void check() throws IOException {
      if (remainingNanos() <= 0) throw unavailable();
    }

    /** JDBC integer seconds are rounded DOWN, never beyond the common parent deadline. */
    default int queryTimeoutSeconds() throws IOException {
      long remaining = remainingNanos();
      if (remaining < 1_000_000_000L) throw unavailable();
      return (int) Math.min(5L, remaining / 1_000_000_000L);
    }
  }

  private static final String[] KEYS = {
    "boot",
    "run",
    "activation",
    "cutoff",
    "epoch",
    "morning_invocation",
    "morning_pid",
    "morning_start_ticks",
    "cleanup_invocation",
    "cleanup_pid",
    "cleanup_start_ticks",
    "deadline_nanos"
  };

  public record Parent(String invocation, long pid, long startTicks) {
    public Parent {
      Objects.requireNonNull(invocation, "parent Invocation");
      if (!invocation.matches("(?!0{32}$)[0-9a-f]{32}")
          || pid < 2
          || pid > Integer.MAX_VALUE
          || startTicks < 1) throw invalid();
    }

    @Override
    public String toString() {
      return "MaintenanceParent[identity=<redacted>]";
    }
  }

  public MaintenanceOwnerFrame {
    Objects.requireNonNull(boot, "same boot");
    Objects.requireNonNull(run, "original run");
    Objects.requireNonNull(activation, "current activation");
    Objects.requireNonNull(cutoff, "original cutoff");
    Objects.requireNonNull(epoch, "current INVALID Epoch");
    Objects.requireNonNull(morning, "actual Morning parent");
    Objects.requireNonNull(cleanup, "optional actual Cleanup parent");
    if (boot.equals(NIL)
        || run.equals(NIL)
        || activation.equals(NIL)
        || epoch.equals(NIL)
        || run.equals(activation)
        || deadlineNanos < 1
        || cutoff.isBefore(Instant.parse("0001-01-01T00:00:00Z"))
        || cutoff.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
        || cutoff.getNano() % 1000 != 0) throw invalid();
    if (cleanup.isPresent()) {
      var child = cleanup.orElseThrow();
      if (child.pid() == morning.pid() || child.invocation().equals(morning.invocation()))
        throw invalid();
    }
  }

  /** One transition by the actual Cleanup caller; claims still confer no authority. */
  public MaintenanceOwnerFrame forInspector(Parent actualCleanup) {
    Objects.requireNonNull(actualCleanup, "actual Cleanup snapshot");
    if (cleanup.isPresent()) throw invalid();
    return new MaintenanceOwnerFrame(
        boot, run, activation, cutoff, epoch, morning, Optional.of(actualCleanup), deadlineNanos);
  }

  /** Fixed native observations; private-file and own-child authentication stay at the caller. */
  public Guard parentsGuard() {
    var context = new ChildStartupContext();
    var clock = LinuxMonotonicClock.create();
    return () -> {
      if (Thread.currentThread().isInterrupted()) throw unavailable();
      long before = clock.nowNanos();
      if (before >= deadlineNanos) throw unavailable();
      context.verifyMaintenanceParent(ChildStartupContext.MaintenanceParent.MORNING, this);
      if (cleanup.isPresent())
        context.verifyMaintenanceParent(ChildStartupContext.MaintenanceParent.CLEANUP, this);
      long after = clock.nowNanos();
      if (Thread.currentThread().isInterrupted() || after < before || after >= deadlineNanos)
        throw unavailable();
      return deadlineNanos - after;
    };
  }

  public byte[] encode() {
    String[] values = {
      boot.toString(),
      run.toString(),
      activation.toString(),
      cutoff.toString(),
      epoch.toString(),
      morning.invocation(),
      Long.toString(morning.pid()),
      Long.toString(morning.startTicks()),
      cleanup.map(Parent::invocation).orElse("-"),
      cleanup.map(value -> Long.toString(value.pid())).orElse("-"),
      cleanup.map(value -> Long.toString(value.startTicks())).orElse("-"),
      Long.toString(deadlineNanos)
    };
    var text = new StringBuilder("NKMAINTOWNER1\n");
    for (int index = 0; index < KEYS.length; index++)
      text.append(KEYS[index]).append('=').append(values[index]).append('\n');
    return text.toString().getBytes(StandardCharsets.US_ASCII);
  }

  /** Consumes input bytes even on bad ordering/overflow/unknown fields. */
  public static MaintenanceOwnerFrame consume(byte[] owned) {
    Objects.requireNonNull(owned, "owned private claim");
    byte[] canonical = new byte[0];
    try {
      if (owned.length < 1 || owned.length > MAXIMUM_BYTES) throw invalid();
      for (byte value : owned) if (value != 10 && (value < 32 || value > 126)) throw invalid();
      String[] rows = new String(owned, StandardCharsets.US_ASCII).split("\n", -1);
      if (rows.length != KEYS.length + 2
          || !rows[0].equals("NKMAINTOWNER1")
          || !rows[rows.length - 1].isEmpty()) throw invalid();
      String[] values = new String[KEYS.length];
      for (int index = 0; index < KEYS.length; index++) {
        String prefix = KEYS[index] + '=';
        if (!rows[index + 1].startsWith(prefix)) throw invalid();
        values[index] = rows[index + 1].substring(prefix.length());
      }
      Optional<Parent> cleanup;
      if (values[8].equals("-")) {
        if (!values[9].equals("-") || !values[10].equals("-")) throw invalid();
        cleanup = Optional.empty();
      } else {
        cleanup =
            Optional.of(
                new Parent(values[8], Long.parseLong(values[9]), Long.parseLong(values[10])));
      }
      var frame =
          new MaintenanceOwnerFrame(
              UUID.fromString(values[0]),
              UUID.fromString(values[1]),
              UUID.fromString(values[2]),
              Instant.parse(values[3]),
              UUID.fromString(values[4]),
              new Parent(values[5], Long.parseLong(values[6]), Long.parseLong(values[7])),
              cleanup,
              Long.parseLong(values[11]));
      canonical = frame.encode();
      if (!Arrays.equals(owned, canonical)) throw invalid();
      return frame;
    } catch (DateTimeException | IllegalArgumentException invalid) {
      throw invalid();
    } finally {
      Arrays.fill(owned, (byte) 0);
      Arrays.fill(canonical, (byte) 0);
    }
  }

  @Override
  public String toString() {
    return "MaintenanceOwnerFrame[claims=<redacted>]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("maintenance owner claim invalid");
  }

  private static IOException unavailable() {
    return new IOException("maintenance owner unavailable");
  }
}
