package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * NK-OPS-001 old closed generation, not a cold-success placeholder or startup authority. RD
 * operational safety; UI operations; SS343 §6.17/SSC131/132/166; PT ISSSTOP001..007,
 * ISSCOLD001..007.
 */
@NullMarked
public final class MorningPreviousBroker {
  private static final int MAX = 4 * 1024 * 1024;

  @FunctionalInterface
  interface Query {
    byte[] read(List<String> command, int limit, long remainingNanos) throws IOException;
  }

  public sealed interface Evidence permits Closed, NoPrior {
    UUID boot();

    void recheck(MorningBrokerUnitCycle.Live fresh) throws IOException;
  }

  /** SSC166: actual current-boot absence, never an invented old clean-stop Summary. */
  public static final class NoPrior implements Evidence {
    private final UUID retainedBoot;
    private final InspectorUnitSnapshot baseline;
    private final Query query;
    private final MaintenanceOwnerFrame.Guard parent;
    private final long thread = Thread.currentThread().threadId();

    private NoPrior(
        UUID boot,
        InspectorUnitSnapshot baseline,
        Query query,
        MaintenanceOwnerFrame.Guard parent) {
      this.retainedBoot = boot;
      this.baseline = baseline;
      this.query = query;
      this.parent = parent;
    }

    public UUID boot() {
      return retainedBoot;
    }

    public void recheck(MorningBrokerUnitCycle.Live fresh) throws IOException {
      Objects.requireNonNull(fresh);
      require(thread == Thread.currentThread().threadId());
      parent.check();
      fresh.recheck();
      require(baseline.matches(fresh.previousObservation()));
      byte[] bytes = read(query, base(retainedBoot), MAX, parent);
      try {
        BrokerJournalEvidence.consume(
            bytes, retainedBoot, fresh.invocation(), fresh.startedMonotonicMicros());
        BrokerJournalEvidence.contentSha256(bytes);
        fresh.recheck();
        parent.check();
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }

    @Override
    public String toString() {
      return "PreviousBroker[no-prior-current-boot]";
    }
  }

  public static final class Closed implements Evidence {
    private final UUID retainedBootState;
    private final String retainedSource;
    private final String retainedInvocation;
    private final Optional<BigInteger> retainedNativeStart;
    private final Optional<BigInteger> retainedNativeEnd;
    private final BigInteger retainedUpper;
    private final BrokerJournalEvidence.Summary retainedJournal;
    private final String retainedContentSha256;
    private final Query query;
    private final MaintenanceOwnerFrame.Guard parent;
    private final long thread = Thread.currentThread().threadId();

    private Closed(
        UUID boot,
        String source,
        String invocation,
        Optional<BigInteger> nativeStart,
        Optional<BigInteger> nativeEnd,
        BigInteger upper,
        BrokerJournalEvidence.Summary journal,
        String contentSha256,
        Query query,
        MaintenanceOwnerFrame.Guard parent) {
      this.retainedBootState = boot;
      this.retainedSource = source;
      this.retainedInvocation = invocation;
      this.retainedNativeStart = nativeStart;
      this.retainedNativeEnd = nativeEnd;
      this.retainedUpper = upper;
      this.retainedJournal = journal;
      this.retainedContentSha256 = contentSha256;
      this.query = query;
      this.parent = parent;
    }

    public UUID boot() {
      return retainedBootState;
    }

    public String source() {
      return retainedSource;
    }

    public String invocation() {
      return retainedInvocation;
    }

    public Optional<BigInteger> nativeStart() {
      return retainedNativeStart;
    }

    public Optional<BigInteger> nativeEnd() {
      return retainedNativeEnd;
    }

    public BigInteger upper() {
      return retainedUpper;
    }

    public BrokerJournalEvidence.Summary journal() {
      return retainedJournal;
    }

    public String contentSha256() {
      return retainedContentSha256;
    }

    public void recheck(MorningBrokerUnitCycle.Live fresh) throws IOException {
      Objects.requireNonNull(fresh);
      fresh.recheck();
      recheck();
      fresh.recheck();
    }

    /** After fresh start, reread only the saved old generation, not the new latest anchor. */
    public void recheck() throws IOException {
      require(thread == Thread.currentThread().threadId());
      parent.check();
      byte[] bytes = read(query, full(retainedBootState, retainedInvocation), MAX, parent);
      try {
        var actual =
            BrokerJournalEvidence.consumeStopped(
                bytes,
                retainedBootState,
                retainedInvocation,
                retainedNativeStart.orElse(BigInteger.ONE),
                retainedUpper);
        if (retainedNativeStart.isEmpty())
          BrokerJournalEvidence.consume(
              bytes, retainedBootState, retainedInvocation, BigInteger.ONE);
        require(
            retainedJournal.entries() == actual.entries()
                && retainedContentSha256.equals(BrokerJournalEvidence.contentSha256(bytes)));
        parent.check();
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }

    @Override
    public String toString() {
      return "PreviousBroker[actual=<redacted>]";
    }
  }

  private MorningPreviousBroker() {}

  public static Evidence capture(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MorningUnitTerminals.Snapshot initial,
      MorningBrokerUnitCycle.ParentProof original)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(initial);
    Objects.requireNonNull(original);
    require(
        expected.service() == RootStartupContext.Service.MORNING
            && expected.equals(initial.parent()));
    var recorded =
        initial.units().stream()
            .filter(row -> row.manager().unit() == MaintenanceUnit.ARTEMIS)
            .findFirst()
            .orElseThrow(MorningPreviousBroker::unavailable);
    var terminal = MaintenanceUnitTermination.create(root, expected, MaintenanceUnit.ARTEMIS);
    MaintenanceOwnerFrame.Guard guard =
        () -> {
          budget.requireWithin();
          root.recheck(expected);
          original.verify();
          return budget.remainingNanos();
        };
    guard.check();
    require(
        same(
            recorded,
            terminal.quiescentObservation().orElseThrow(MorningPreviousBroker::unavailable)));
    var probe = InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.ARTEMIS);
    var before = probe.read();
    Query query =
        InspectorUnitProbe.NativeReader.forTarget(InspectorUnitSnapshot.Target.ARTEMIS)
            ::executeStreaming;
    var result = collectForStartup(UUID.fromString(expected.boot()), before, query, guard);
    require(before.matches(probe.read()));
    require(
        same(
            recorded,
            terminal.quiescentObservation().orElseThrow(MorningPreviousBroker::unavailable)));
    guard.check();
    return result;
  }

  static Evidence collectForStartup(
      UUID boot, InspectorUnitSnapshot previous, Query query, MaintenanceOwnerFrame.Guard parent)
      throws IOException {
    Objects.requireNonNull(boot);
    Objects.requireNonNull(previous);
    Objects.requireNonNull(query);
    Objects.requireNonNull(parent);
    parent.check();
    require(previous.isTarget(InspectorUnitSnapshot.Target.ARTEMIS));
    if (previous.brokerStoppedNormally()) return collect(boot, previous, query, parent);
    require(
        previous.inactiveBaseline()
            && previous.invocationId().isEmpty()
            && previous.executionStart().signum() == 0
            && previous.executionEnd().signum() == 0);
    byte[] first = read(query, base(boot), MAX, parent);
    try {
      if (first.length != 0) return collect(boot, previous, query, parent);
      require(previous.coldStopped());
      byte[] second = read(query, base(boot), MAX, parent);
      try {
        require(second.length == 0);
        parent.check();
        return new NoPrior(boot, previous, query, parent);
      } finally {
        Arrays.fill(second, (byte) 0);
      }
    } finally {
      Arrays.fill(first, (byte) 0);
    }
  }

  static Closed collect(
      UUID boot, InspectorUnitSnapshot previous, Query query, MaintenanceOwnerFrame.Guard parent)
      throws IOException {
    Objects.requireNonNull(boot);
    Objects.requireNonNull(previous);
    Objects.requireNonNull(query);
    Objects.requireNonNull(parent);
    parent.check();
    require(previous.isTarget(InspectorUnitSnapshot.Target.ARTEMIS));
    if (previous.brokerStoppedNormally()) {
      String invocation = previous.invocationId().orElseThrow().toString().replace("-", "");
      byte[] bytes = read(query, full(boot, invocation), MAX, parent);
      try {
        var actual =
            BrokerJournalEvidence.consumeStopped(
                bytes, boot, invocation, previous.executionStart(), previous.executionEnd());
        parent.check();
        return new Closed(
            boot,
            "NATIVE_TERMINAL",
            invocation,
            Optional.of(previous.executionStart()),
            Optional.of(previous.executionEnd()),
            previous.executionEnd(),
            actual,
            BrokerJournalEvidence.contentSha256(bytes),
            query,
            parent);
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }
    require(
        previous.inactiveBaseline()
            && previous.invocationId().isEmpty()
            && previous.executionStart().signum() == 0
            && previous.executionEnd().signum() == 0);
    var latest = anchor(query, boot, false, parent);
    var started = anchor(query, boot, true, parent);
    require(
        latest.invocation().equals(started.invocation())
            && latest.monotonic().compareTo(started.monotonic()) >= 0);
    byte[] bytes = read(query, full(boot, latest.invocation()), MAX, parent);
    try {
      var actual = BrokerJournalEvidence.consumeClosedHistory(bytes, boot, latest);
      require(
          latest.equals(anchor(query, boot, false, parent))
              && started.equals(anchor(query, boot, true, parent)));
      parent.check();
      return new Closed(
          boot,
          "BOOT_JOURNAL",
          latest.invocation(),
          Optional.empty(),
          Optional.empty(),
          latest.monotonic(),
          actual,
          BrokerJournalEvidence.contentSha256(bytes),
          query,
          parent);
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static BrokerJournalEvidence.Anchor anchor(
      Query query, UUID boot, boolean started, MaintenanceOwnerFrame.Guard parent)
      throws IOException {
    var command = new ArrayList<>(base(boot));
    command.add("--reverse");
    command.add("--lines=1");
    if (started)
      command.add(
          "--grep=AMQ221001: Apache Artemis Message Broker version 2[.]56[.]0.*schubert-nk-broker");
    byte[] bytes = read(query, List.copyOf(command), 65536, parent);
    try {
      return BrokerJournalEvidence.anchor(bytes, boot, started);
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static List<String> base(UUID boot) {
    return List.of(
        "/usr/bin/journalctl",
        "--no-pager",
        "--quiet",
        "--all",
        "--output=json",
        "--output-fields=MESSAGE,PRIORITY,_SYSTEMD_INVOCATION_ID,_BOOT_ID,_SYSTEMD_UNIT",
        "_SYSTEMD_UNIT=artemis.service",
        "_BOOT_ID=" + boot.toString().replace("-", ""));
  }

  private static List<String> full(UUID boot, String invocation) {
    var command = new ArrayList<>(base(boot));
    command.add("_SYSTEMD_INVOCATION_ID=" + invocation);
    return List.copyOf(command);
  }

  private static byte[] read(
      Query query, List<String> command, int limit, MaintenanceOwnerFrame.Guard parent)
      throws IOException {
    byte[] bytes =
        Objects.requireNonNull(
            query.read(command, limit, parent.remainingNanos()), "owned previous journal bytes");
    try {
      require(bytes.length <= limit);
      parent.check();
      return bytes;
    } catch (IOException | RuntimeException | Error failure) {
      Arrays.fill(bytes, (byte) 0);
      throw failure;
    }
  }

  private static boolean same(
      MaintenanceUnitTermination.Observation left, MaintenanceUnitTermination.Observation right) {
    return left.manager().matches(right.manager())
        && left.leafPresent() == right.leafPresent()
        && left.directories().equals(right.directories());
  }

  private static void require(boolean ok) throws IOException {
    if (!ok) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("Previous Broker unavailable");
  }
}
