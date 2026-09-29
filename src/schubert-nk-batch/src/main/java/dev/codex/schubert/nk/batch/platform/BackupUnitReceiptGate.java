package dev.codex.schubert.nk.batch.platform;

import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only fresh Backup receipt gate for one continuously owned parent run. The pre-start token
 * binds a bus snapshot to the kernel whole-Unit terminal observation; after start, receipt0 from a
 * different Invocation must match a fresh kernel observation and a second bus read. It neither
 * starts/stops a Unit nor proves the archive or releases M/A. NK-OPS-001/BAK-001; UI251/SS341§5-6
 * /343§6.15; SSC092/093/105; PG353/PT-OPS-BGATE001-008.
 */
@NullMarked
public final class BackupUnitReceiptGate {
  @FunctionalInterface
  interface Context {
    void recheck() throws IOException;
  }

  @FunctionalInterface
  interface Probe {
    Optional<InspectorUnitSnapshot> quiescent();
  }

  @FunctionalInterface
  interface Terminal {
    Optional<InspectorUnitSnapshot> quiescent() throws IOException;
  }

  /** A nonforgeable same-gate pre-start observation; never a worker success token. */
  public static final class Baseline {
    private final BackupUnitReceiptGate owner;
    private final Optional<UUID> previous;

    private Baseline(BackupUnitReceiptGate owner, Optional<UUID> previous) {
      this.owner = owner;
      this.previous = previous;
    }
  }

  private final Context context;
  private final Probe probe;
  private final Terminal terminal;

  public static BackupUnitReceiptGate create(
      RootStartupContext root, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    root.recheck(expected);
    return create(
        root,
        expected,
        InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.BACKUP)::quiescent,
        BackupUnitTermination.create(root, expected)::quiescent);
  }

  static BackupUnitReceiptGate create(
      RootStartupContext root, RootStartupContext.Snapshot expected, Probe probe, Terminal terminal)
      throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(probe, "fixed Backup Unit projection");
    Objects.requireNonNull(terminal, "kernel whole-Unit terminal");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    root.recheck(expected);
    return new BackupUnitReceiptGate(() -> root.recheck(expected), probe, terminal);
  }

  BackupUnitReceiptGate(Context context, Probe probe, Terminal terminal) {
    this.context = Objects.requireNonNull(context, "Morning root recheck");
    this.probe = Objects.requireNonNull(probe, "fixed Backup Unit projection");
    this.terminal = Objects.requireNonNull(terminal, "kernel whole-Unit terminal");
  }

  /** Capture before issuing the fixed start client, while the parent still owns M/A. */
  public Baseline capture() throws IOException {
    check();
    try {
      InspectorUnitSnapshot first = present(probe.quiescent());
      InspectorUnitSnapshot whole = present(terminal.quiescent());
      if (!first.matches(whole) || !first.matches(present(probe.quiescent()))) throw unavailable();
      return new Baseline(this, first.invocationId());
    } finally {
      check();
    }
  }

  /**
   * One bounded observation step; empty means not proven and the caller must retain its owners.
   * Polling, the 30-minute parent budget, and failure quarantine belong to the enclosing cycle.
   */
  public Optional<InspectorUnitSnapshot> observe(Baseline baseline) throws IOException {
    return observe(baseline, false);
  }

  /** Genuine fresh normal terminal result; FAILED does not prove valid archives. BUG325. */
  public Optional<InspectorUnitSnapshot> observeTerminal(Baseline baseline) throws IOException {
    return observe(baseline, true);
  }

  private Optional<InspectorUnitSnapshot> observe(Baseline baseline, boolean includeFailure)
      throws IOException {
    Objects.requireNonNull(baseline, "same-run Backup baseline");
    if (baseline.owner != this) throw unavailable();
    check();
    try {
      Optional<InspectorUnitSnapshot> first = known(probe.quiescent());
      if (first.isEmpty()
          || (includeFailure
              ? first.orElseThrow().backupTerminalAfter(baseline.previous).isEmpty()
              : first.orElseThrow().receiptAfter(baseline.previous).orElse(-1) != 0))
        return Optional.empty();
      Optional<InspectorUnitSnapshot> whole = known(terminal.quiescent());
      if (whole.isEmpty() || !first.orElseThrow().matches(whole.orElseThrow()))
        return Optional.empty();
      Optional<InspectorUnitSnapshot> after = known(probe.quiescent());
      if (after.isEmpty() || !first.orElseThrow().matches(after.orElseThrow()))
        return Optional.empty();
      return first;
    } finally {
      check();
    }
  }

  private void check() throws IOException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    context.recheck();
  }

  private static Optional<InspectorUnitSnapshot> known(Optional<InspectorUnitSnapshot> observed)
      throws IOException {
    if (observed == null) throw unavailable();
    return observed;
  }

  private static InspectorUnitSnapshot present(Optional<InspectorUnitSnapshot> observed)
      throws IOException {
    Optional<InspectorUnitSnapshot> known = known(observed);
    if (known.isEmpty()) throw unavailable();
    return known.orElseThrow();
  }

  private static IOException unavailable() {
    return new IOException("backup receipt unavailable");
  }
}
