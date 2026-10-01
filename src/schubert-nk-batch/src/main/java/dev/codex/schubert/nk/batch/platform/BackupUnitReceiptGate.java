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
  private final BackupUnitStartClient.Target target;

  /** Only this gate constructs a fresh, kernel-checked receipt; claim parsers cannot forge it. */
  public static final class TerminalReceipt {
    private final BackupUnitReceiptGate owner;
    private final Baseline baseline;
    private final InspectorUnitSnapshot snapshot;

    private TerminalReceipt(
        BackupUnitReceiptGate owner, Baseline baseline, InspectorUnitSnapshot snapshot) {
      this.owner = owner;
      this.baseline = baseline;
      this.snapshot = snapshot;
    }

    public BackupUnitStartClient.Target target() {
      return owner.target;
    }

    public UUID invocation() {
      return snapshot.invocationId().orElseThrow();
    }

    public int exitCode() {
      return snapshot.normalExitCode();
    }

    public java.math.BigInteger startedMonotonic() {
      return snapshot.executionStart();
    }

    public java.math.BigInteger endedMonotonic() {
      return snapshot.executionEnd();
    }

    @Override
    public String toString() {
      return "TerminalReceipt[observations=<redacted>]";
    }
  }

  public static BackupUnitReceiptGate create(
      RootStartupContext root, RootStartupContext.Snapshot expected) throws IOException {
    return create(root, expected, BackupUnitStartClient.Target.BACKUP);
  }

  public static BackupUnitReceiptGate create(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      BackupUnitStartClient.Target target)
      throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(target, "closed phase");
    if (!target.ownedBy(expected.service()) || target == BackupUnitStartClient.Target.BROKER)
      throw unavailable(); // Long-lived daemon has no oneshot completion receipt.
    root.recheck(expected);
    return new BackupUnitReceiptGate(
        () -> root.recheck(expected),
        stateProjection(InspectorUnitProbe.forTarget(target.observation())),
        BackupUnitTermination.create(root, expected, target)::quiescent,
        target);
  }

  /** Manager projection only; create/capture/observe always require the separate host terminal. */
  static Probe stateProjection(InspectorUnitProbe probe) {
    Objects.requireNonNull(probe, "fixed Backup state projection");
    return () -> {
      var state = probe.read();
      return state.quiescent() ? Optional.of(state) : Optional.empty();
    };
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
    this(context, probe, terminal, BackupUnitStartClient.Target.BACKUP);
  }

  BackupUnitReceiptGate(
      Context context, Probe probe, Terminal terminal, BackupUnitStartClient.Target target) {
    this.context = Objects.requireNonNull(context, "Morning root recheck");
    this.probe = Objects.requireNonNull(probe, "fixed Backup Unit projection");
    this.terminal = Objects.requireNonNull(terminal, "kernel whole-Unit terminal");
    this.target = Objects.requireNonNull(target, "closed phase");
  }

  /** Capture before issuing the fixed start client, while the parent still owns M/A. */
  public Baseline capture() throws IOException {
    check();
    try {
      InspectorUnitSnapshot first = present(probe.quiescent());
      if (!first.isTarget(target.observation())
          || (target != BackupUnitStartClient.Target.BACKUP
              && !first.inactiveBaseline()
              // SSC123/BUG368: a prior known rejection is only a baseline, never this result.
              && !(target == BackupUnitStartClient.Target.CLEANUP
                  && first.cleanupRejectedAfter(Optional.empty()))
              && !(target == BackupUnitStartClient.Target.EXPIRY
                  && first.expiryRejectedAfter(Optional.empty())))) throw unavailable();
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
    return observe(
        baseline,
        target == BackupUnitStartClient.Target.BACKUP
            || target == BackupUnitStartClient.Target.CLEANUP
            || target == BackupUnitStartClient.Target.EXPIRY);
  }

  public Optional<TerminalReceipt> observeResult(Baseline baseline) throws IOException {
    return observeTerminal(baseline).map(snapshot -> new TerminalReceipt(this, baseline, snapshot));
  }

  /** KEEP_ACTIVE only: same fresh receipt, full kernel empty and same owner, not cached success. */
  public void requireStillPresent(TerminalReceipt receipt) throws IOException {
    Objects.requireNonNull(receipt, "same-owner receipt");
    if (receipt.owner != this
        || !receipt.snapshot.matches(present(observeTerminal(receipt.baseline))))
      throw unavailable();
  }

  /**
   * SSC135: only the enclosing controller's confirmed explicit stop uses this path. The private
   * before receipt already proved a fresh normal result; cold GC is a separate stopped condition,
   * never a new zero result. No arbitrary target or earlier baseline can reuse that capability.
   */
  public void requireStoppedResult(Baseline baseline, TerminalReceipt before) throws IOException {
    Objects.requireNonNull(baseline, "actual cycle baseline");
    Objects.requireNonNull(before, "fresh result before explicit stop");
    check();
    if (target != BackupUnitStartClient.Target.BACKUP
        || baseline.owner != this
        || before.owner != this
        || before.baseline != baseline) throw unavailable();
    var first = present(known(probe.quiescent()));
    var whole = present(known(terminal.quiescent()));
    var after = present(known(probe.quiescent()));
    check();
    if (!first.isTarget(target.observation())
        || !first.quiescent()
        || !first.matches(whole)
        || !first.matches(after)
        || (!first.coldStopped() && !first.sameStoppedExecution(before.snapshot)))
      throw unavailable();
  }

  private Optional<InspectorUnitSnapshot> observe(Baseline baseline, boolean includeFailure)
      throws IOException {
    Objects.requireNonNull(baseline, "same-run Backup baseline");
    if (baseline.owner != this) throw unavailable();
    check();
    try {
      Optional<InspectorUnitSnapshot> first = known(probe.quiescent());
      if (first.isEmpty()
          || !first.orElseThrow().isTarget(target.observation())
          || (target != BackupUnitStartClient.Target.BACKUP
              && !first.orElseThrow().heldMaintenance()
              && !(includeFailure
                  && (first.orElseThrow().cleanupRejectedAfter(baseline.previous)
                      || first.orElseThrow().expiryRejectedAfter(baseline.previous))))
          || !eligible(first.orElseThrow(), baseline.previous, includeFailure))
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

  private boolean eligible(
      InspectorUnitSnapshot state, Optional<UUID> previous, boolean includeFailure) {
    if (target == BackupUnitStartClient.Target.BACKUP)
      return includeFailure
          ? state.backupTerminalAfter(previous).isPresent()
          : state.receiptAfter(previous).orElse(-1) == 0;
    return state.receiptAfter(previous).isPresent()
        || (includeFailure
            && (state.cleanupRejectedAfter(previous) || state.expiryRejectedAfter(previous)));
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
