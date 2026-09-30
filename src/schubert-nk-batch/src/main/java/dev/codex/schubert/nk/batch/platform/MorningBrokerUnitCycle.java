package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed same-owner daemon start, NOT a worker receipt or permit. SS321/341/343 SSC125.
 * BROKERSTART001..004. Actual Ops/journal readiness is supplied by the native caller. Any
 * uncertainty after publication retains the marker and parent owners until outer quarantine.
 */
@NullMarked
public final class MorningBrokerUnitCycle {
  @FunctionalInterface
  public interface ParentProof {
    void verify() throws IOException;
  }

  @FunctionalInterface
  public interface Readiness {
    void verify(Live actual) throws IOException;
  }

  @FunctionalInterface
  interface Baseline {
    InspectorUnitSnapshot read() throws IOException;

    default Optional<BrokerJournalEvidence.Summary> stoppedProof(InspectorUnitSnapshot actual)
        throws IOException {
      return Optional.empty();
    }
  }

  @FunctionalInterface
  interface Projection {
    Optional<Observation> read() throws IOException;
  }

  @FunctionalInterface
  interface Start {
    BackupUnitStartClient.Attempt execute() throws IOException;
  }

  @FunctionalInterface
  interface Retain {
    void indefinitely();
  }

  record Observation(InspectorUnitSnapshot manager, ChildStartupContext.Observed kernel) {}

  public static final class Live {
    private final MorningBrokerUnitCycle owner;
    private final Observation actual;
    private final InspectorUnitSnapshot previous;
    private final Optional<BrokerJournalEvidence.Summary> stoppedJournal;

    private Live(
        MorningBrokerUnitCycle owner,
        Observation actual,
        InspectorUnitSnapshot previous,
        Optional<BrokerJournalEvidence.Summary> stoppedJournal) {
      this.owner = owner;
      this.actual = actual;
      this.previous = previous;
      this.stoppedJournal = stoppedJournal;
    }

    public InspectorUnitSnapshot previousObservation() throws IOException {
      owner.check();
      return previous;
    }

    public Optional<BrokerJournalEvidence.Summary> stoppedJournal() throws IOException {
      owner.check();
      return stoppedJournal;
    }

    public String invocation() {
      return actual.manager().invocationId().orElseThrow().toString().replace("-", "");
    }

    public java.math.BigInteger startedMonotonicMicros() {
      return actual.manager().executionStart();
    }

    /** Same generation and parent lifetime, never a detached daemon-readiness credential. */
    public void recheck() throws IOException {
      owner.check();
      var now = owner.projection.read().orElseThrow(MorningBrokerUnitCycle::unavailable);
      if (!actual.manager().matches(now.manager()) || !actual.kernel().equals(now.kernel()))
        throw unavailable();
      owner.check();
    }

    @Override
    public String toString() {
      return "BrokerLive[observations=<redacted>]";
    }
  }

  private final ParentProof parent;
  private final Baseline baseline;
  private final Projection projection;
  private final Start start;
  private final Retain retain;
  private final long thread = Thread.currentThread().threadId();
  private boolean attempted;

  public static MorningBrokerUnitCycle create(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      ParentProof parent)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(parent);
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    ParentProof guard =
        () -> {
          budget.requireWithin();
          root.recheck(expected);
          parent.verify();
          budget.requireWithin();
        };
    guard.verify();
    var before = BackupUnitTermination.create(root, expected, BackupUnitStartClient.Target.BROKER);
    var probe = InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.ARTEMIS);
    var starter =
        BackupUnitStartClient.create(root, expected, BackupUnitStartClient.Target.BROKER, budget);
    return new MorningBrokerUnitCycle(
        guard,
        new Baseline() {
          public InspectorUnitSnapshot read() throws IOException {
            return before.quiescent().orElseThrow(MorningBrokerUnitCycle::unavailable);
          }

          public Optional<BrokerJournalEvidence.Summary> stoppedProof(InspectorUnitSnapshot actual)
              throws IOException {
            if (!actual.brokerStoppedNormally()) return Optional.empty();
            guard.verify();
            var observed =
                BrokerJournalEvidence.inspectStopped(
                    actual,
                    UUID.fromString(expected.boot()),
                    () -> {
                      guard.verify();
                      return budget.remainingNanos();
                    });
            if (!actual.matches(
                before.quiescent().orElseThrow(MorningBrokerUnitCycle::unavailable)))
              throw unavailable();
            guard.verify();
            return Optional.of(observed);
          }
        },
        () -> {
          guard.verify();
          var first = probe.read();
          var invocation = first.invocationId();
          if (invocation.isEmpty()) return Optional.empty();
          String id = invocation.orElseThrow().toString().replace("-", "");
          if (!first.brokerRunningInvocation(id)) return Optional.empty();
          var actor =
              new ChildStartupContext()
                  .verifyBroker(
                      UUID.fromString(expected.boot()),
                      id,
                      new FixedServiceIdentity().resolveArtemis());
          if (!first.running(actor.pid(), id) || !first.matches(probe.read())) throw unavailable();
          guard.verify();
          return Optional.of(new Observation(first, actor));
        },
        starter::start,
        () -> {
          for (; ; ) pause();
        });
  }

  MorningBrokerUnitCycle(
      ParentProof parent, Baseline baseline, Projection projection, Start start, Retain retain) {
    this.parent = Objects.requireNonNull(parent);
    this.baseline = Objects.requireNonNull(baseline);
    this.projection = Objects.requireNonNull(projection);
    this.start = Objects.requireNonNull(start);
    this.retain = Objects.requireNonNull(retain);
  }

  public Live execute(Readiness readiness) throws IOException {
    Objects.requireNonNull(readiness, "actual Ops and recovery readiness");
    check();
    if (attempted) throw unavailable();
    attempted = true;
    var before = baseline.read();
    if (!before.isTarget(InspectorUnitSnapshot.Target.ARTEMIS)
        || (!before.inactiveBaseline() && !before.brokerStoppedNormally())) throw unavailable();
    check();
    var stopped = Objects.requireNonNull(baseline.stoppedProof(before), "actual stopped journal");
    if (before.brokerStoppedNormally() && stopped.isEmpty()) throw unavailable();
    check();
    // From this point any exception may leave an intent or delivered start. Never unwind M/A.
    try {
      var pending = Objects.requireNonNull(start.execute(), "owned fixed broker start");
      if (pending.status() != BackupUnitStartClient.Status.CLIENT_EXITED_ZERO) throw unavailable();
      Optional<Observation> observed;
      do {
        check();
        observed = projection.read();
        if (observed.isEmpty()) pause();
      } while (observed.isEmpty());
      var actual = observed.orElseThrow();
      if (actual.manager().invocationId().equals(before.invocationId())) throw unavailable();
      var live = new Live(this, actual, before, stopped);
      live.recheck();
      readiness.verify(live);
      live.recheck();
      pending.retireAfter(
          () -> {
            live.recheck();
            readiness.verify(live);
            live.recheck();
          });
      check();
      return live;
    } catch (IOException | RuntimeException | Error uncertain) {
      retain.indefinitely();
      throw new AssertionError("unresolved Broker retention returned");
    }
  }

  private void check() throws IOException {
    if (thread != Thread.currentThread().threadId() || Thread.currentThread().isInterrupted())
      throw unavailable();
    parent.verify();
  }

  private static void pause() {
    boolean interrupted = Thread.interrupted();
    try {
      TimeUnit.MILLISECONDS.sleep(100);
    } catch (InterruptedException known) {
      interrupted = true;
    } finally {
      if (interrupted) Thread.currentThread().interrupt();
    }
  }

  private static IOException unavailable() {
    return new IOException("Broker startup unavailable");
  }
}
