package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.batch.file.BackupStartIntentFiles;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.Closeable;
import java.io.IOException;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed root Morning client for queuing the dedicated Backup Unit. Client exit zero is only a
 * successful systemctl request, not a fresh worker Invocation, receipt, cgroup termination, or
 * archive proof. The caller must hold M/A, the same run originals and source request through all
 * those later observations. UNKNOWN must not normally unwind those owners. NK-OPS-001/BAK-001;
 * UI251/SS341§5-6/343§6.15; SSC092/093/105; PG352/PT-OPS-BSTART001-008.
 */
@NullMarked
public final class BackupUnitStartClient {
  /** Closed phase selection, never an arbitrary Unit/path. SSC117. */
  public enum Target {
    BACKUP(
        MaintenanceUnit.BACKUP,
        InspectorUnitSnapshot.Target.BACKUP,
        "/run/schubert-nk/backup-request",
        "backup-start.intent"),
    CLEANUP(
        MaintenanceUnit.CLEANUP,
        InspectorUnitSnapshot.Target.CLEANUP,
        "/run/schubert-nk/cleanup-request",
        "cleanup-start.intent"),
    INSPECTOR(
        MaintenanceUnit.INSPECTOR,
        InspectorUnitSnapshot.Target.INSPECTOR,
        "/run/schubert-nk/cleanup-request",
        "inspector-start.intent"),
    EXPIRY(
        MaintenanceUnit.EXPIRY,
        InspectorUnitSnapshot.Target.EXPIRY,
        "/run/schubert-nk/expiry-request",
        "expiry-start.intent"),
    BROKER(
        MaintenanceUnit.ARTEMIS,
        InspectorUnitSnapshot.Target.ARTEMIS,
        "/run/schubert-nk/startup",
        "broker-start.intent");
    private final MaintenanceUnit systemUnit;
    private final InspectorUnitSnapshot.Target observedTarget;
    private final String requestPath;
    private final String intentFileName;

    Target(
        MaintenanceUnit unit,
        InspectorUnitSnapshot.Target observation,
        String directory,
        String marker) {
      this.systemUnit = unit;
      this.observedTarget = observation;
      this.requestPath = directory;
      this.intentFileName = marker;
    }

    public MaintenanceUnit unit() {
      return systemUnit;
    }

    public InspectorUnitSnapshot.Target observation() {
      return observedTarget;
    }

    public String requestDirectory() {
      return requestPath;
    }

    public String marker() {
      return intentFileName;
    }

    /** Only Cleanup controls Inspector; the four other fixed starts are Morning-owned. */
    public boolean ownedBy(RootStartupContext.Service service) {
      return service
          == (this == INSPECTOR
              ? RootStartupContext.Service.CLEANUP
              : RootStartupContext.Service.MORNING);
    }
  }

  @FunctionalInterface
  interface Context {
    void recheck() throws IOException;
  }

  @FunctionalInterface
  interface Policy {
    void requireSafe() throws IOException;
  }

  @FunctionalInterface
  interface Start {
    Process execute(List<String> command) throws IOException;
  }

  @FunctionalInterface
  interface Intent {
    MarkerLease begin() throws IOException;
  }

  @FunctionalInterface
  interface MarkerLease {
    void retire() throws IOException;

    default void closeObservation() throws IOException {
      throw new IOException("service observation close unavailable");
    }

    default void requireRetained() throws IOException {
      throw new IOException("service intent proof unavailable");
    }
  }

  /** Parent-supplied proof, evaluated while its M/A/original/request owners are still held. */
  @FunctionalInterface
  public interface RetirementGate {
    void verify() throws IOException;
  }

  public enum Status {
    CLIENT_EXITED_ZERO,
    CLIENT_EXITED_NONZERO,
    UNKNOWN
  }

  private static final List<String> COMMAND =
      List.of(
          "/usr/bin/systemctl",
          "--system",
          "--no-pager",
          "--no-ask-password",
          "--no-block",
          "start",
          "schubert-nk-backup.service");

  private final Context context;
  private final Policy policy;
  private final Start retainedStart;
  private final Intent intent;
  private final MaintenanceUnit unit;
  private final Optional<MorningParentBudget> budget;

  public static BackupUnitStartClient create(
      RootStartupContext root, RootStartupContext.Snapshot expected) throws IOException {
    return create(root, expected, Target.BACKUP);
  }

  public static BackupUnitStartClient create(
      RootStartupContext root, RootStartupContext.Snapshot expected, Target target)
      throws IOException {
    return createWithBudget(root, expected, target, Optional.empty());
  }

  public static BackupUnitStartClient create(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      Target target,
      MorningParentBudget budget)
      throws IOException {
    return createWithBudget(
        root, expected, target, Optional.of(Objects.requireNonNull(budget, "same parent budget")));
  }

  private static BackupUnitStartClient createWithBudget(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      Target target,
      Optional<MorningParentBudget> budget)
      throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(target, "closed phase");
    if (!target.ownedBy(expected.service())) throw new IOException("backup start unavailable");
    root.recheck(expected);
    var policy = MaintenanceUnitStopPolicy.create();
    return new BackupUnitStartClient(
        () -> root.recheck(expected),
        () -> policy.requireSafe(target.unit()),
        new MaintenanceUnitStopClient.NativeStart()::execute,
        () -> beginNative(root, expected, target),
        target,
        budget);
  }

  private static MarkerLease beginNative(
      RootStartupContext root, RootStartupContext.Snapshot expected, Target target)
      throws IOException {
    return ResourceScope.<BackupStartIntentFiles, MarkerLease, IOException>handoff(
        () -> BackupStartIntentFiles.create(root, expected, target),
        BackupStartIntentFiles::close,
        marker -> {
          var token = marker.begin();
          // This owner and exact token must survive the external start and the whole parent cycle.
          return () -> {
            marker.retire(token);
            marker.close();
          };
        });
  }

  static BackupUnitStartClient create(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      MaintenanceUnitStopPolicy unitPolicy,
      Start start)
      throws IOException {
    return create(root, expected, unitPolicy, start, () -> () -> {});
  }

  static BackupUnitStartClient create(
      RootStartupContext root,
      RootStartupContext.Snapshot expected,
      MaintenanceUnitStopPolicy unitPolicy,
      Start start,
      Intent intent)
      throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(unitPolicy, "fixed Backup policy");
    Objects.requireNonNull(start, "fixed start port");
    Objects.requireNonNull(intent, "same-boot start intent");
    if (expected.service() != RootStartupContext.Service.MORNING)
      throw new IOException("backup start unavailable");
    root.recheck(expected);
    return new BackupUnitStartClient(
        () -> root.recheck(expected),
        () -> unitPolicy.requireSafe(MaintenanceUnit.BACKUP),
        start,
        intent);
  }

  /**
   * Synthetic port used by pre-existing fixed-client PT; Production factory always supplies a
   * marker.
   */
  BackupUnitStartClient(Context context, Policy policy, Start start) {
    this(context, policy, start, () -> () -> {});
  }

  BackupUnitStartClient(Context context, Policy policy, Start start, Intent intent) {
    this(context, policy, start, intent, Target.BACKUP);
  }

  BackupUnitStartClient(Context context, Policy policy, Start start, Intent intent, Target target) {
    this(context, policy, start, intent, target, Optional.empty());
  }

  BackupUnitStartClient(
      Context context,
      Policy policy,
      Start start,
      Intent intent,
      Target target,
      Optional<MorningParentBudget> budget) {
    this(
        context,
        policy,
        start,
        intent,
        Objects.requireNonNull(target, "closed phase").unit(),
        budget);
  }

  BackupUnitStartClient(
      Context context,
      Policy policy,
      Start start,
      Intent intent,
      MaintenanceUnit unit,
      Optional<MorningParentBudget> budget) {
    this.context = Objects.requireNonNull(context, "Morning root context");
    this.policy = Objects.requireNonNull(policy, "fixed Backup policy");
    this.retainedStart = Objects.requireNonNull(start, "fixed start port");
    this.intent = Objects.requireNonNull(intent, "same-boot start intent");
    this.unit = Objects.requireNonNull(unit, "closed Unit");
    this.budget = Objects.requireNonNull(budget, "parent budget binding");
  }

  /** Same client/UNKNOWN rules; only Morning's two fixed service starts. SSC137. */
  public static BackupUnitStartClient createService(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      dev.codex.schubert.nk.storage.ServiceConfigFiles.Service service,
      dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch issued,
      MorningParentBudget budget)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(service);
    Objects.requireNonNull(issued);
    Objects.requireNonNull(budget);
    if (morning.service() != RootStartupContext.Service.MORNING)
      throw new IOException("service start unavailable");
    root.recheck(morning);
    budget.requireWithin();
    var unit =
        service == dev.codex.schubert.nk.storage.ServiceConfigFiles.Service.API
            ? MaintenanceUnit.API
            : MaintenanceUnit.WEB;
    var policy = MaintenanceUnitStopPolicy.create();
    return new BackupUnitStartClient(
        () -> root.recheck(morning),
        () -> policy.requireSafe(unit),
        new MaintenanceUnitStopClient.NativeStart()::execute,
        () ->
            ResourceScope.<BackupStartIntentFiles, MarkerLease, IOException>handoff(
                () -> BackupStartIntentFiles.createService(root, morning, service, issued),
                BackupStartIntentFiles::close,
                marker -> {
                  var token = marker.begin();
                  return new MarkerLease() {
                    public void retire() throws IOException {
                      marker.retire(token);
                      marker.close();
                    }

                    public void closeObservation() throws IOException {
                      marker.close();
                    }

                    public void requireRetained() throws IOException {
                      marker.requirePresent(token);
                    }
                  };
                }),
        unit,
        Optional.of(budget));
  }

  /**
   * Only the fixed Backup Unit can be queued. Once the native start call is invoked, any missing
   * handle or exception has unknown delivery and must remain opaque to the parent.
   */
  public Attempt start() throws IOException {
    if (budget.isPresent()) budget.orElseThrow().requireWithin();
    interrupted();
    context.recheck();
    policy.requireSafe();
    context.recheck();
    interrupted();
    // SSC106: a failed or uncertain publication is pre-start and issues no systemctl request.
    // Once published, all unknown delivery paths leave the marker for the next M admission.
    // BUG1459: caller-visible Attempt cannot be its own lock. Allocate before any intent/process.
    Object stateLock = new Object();
    MarkerLease marker = Objects.requireNonNull(intent.begin(), "retained start marker");
    if (Thread.currentThread().isInterrupted())
      return new Attempt(context, null, marker, budget, unit, stateLock);
    @Nullable Process process;
    try {
      var command = new java.util.ArrayList<>(COMMAND);
      command.set(command.size() - 1, unit.serviceName());
      process = retainedStart.execute(List.copyOf(command));
    } catch (IOException | RuntimeException | Error uncertainStart) {
      return new Attempt(context, null, marker, budget, unit, stateLock);
    }
    var attempt = new Attempt(context, process, marker, budget, unit, stateLock);
    attempt.awaitClient();
    return attempt;
  }

  /** SSC178: fixed daemon; API/Web's still-owned intents are the delivery fence, not receipts. */
  public static BackupUnitStartClient createCaddy(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      Attempt api,
      Attempt web,
      RetirementGate parent)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(api);
    Objects.requireNonNull(web);
    Objects.requireNonNull(parent);
    return createCaddy(
        root,
        morning,
        budget,
        api,
        web,
        parent,
        MorningCaddyReadiness.coldInvocation(root, morning));
  }

  public static BackupUnitStartClient createCaddy(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      Attempt api,
      Attempt web,
      RetirementGate parent,
      String previousInvocation)
      throws IOException {
    return createCaddy(root, morning, budget, api, web, parent, parent, previousInvocation);
  }

  /** SSC186: full peer/DB checks bracket the pair; each intent borrows a pure owner gate. */
  public static BackupUnitStartClient createCaddy(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      Attempt api,
      Attempt web,
      RetirementGate parent,
      RetirementGate owner,
      String previousInvocation)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(budget);
    Objects.requireNonNull(api);
    Objects.requireNonNull(web);
    Objects.requireNonNull(parent);
    Objects.requireNonNull(owner);
    Objects.requireNonNull(previousInvocation);
    if (morning.service() != RootStartupContext.Service.MORNING
        || api.unit != MaintenanceUnit.API
        || web.unit != MaintenanceUnit.WEB) throw new IOException("Caddy start unavailable");
    root.recheck(morning);
    budget.requireWithin();
    var policy = MaintenanceUnitStopPolicy.create();
    var admission = caddyAdmissionFence(parent, owner, api, web);
    RetirementGate fence =
        () -> {
          budget.requireWithin();
          root.recheck(morning);
          admission.verify();
          root.recheck(morning);
          budget.requireWithin();
        };
    return new BackupUnitStartClient(
        () -> {
          root.recheck(morning);
          fence.verify();
        },
        () -> {
          if (!previousInvocation.equals(MorningCaddyReadiness.coldInvocation(root, morning)))
            throw new IOException("Caddy cold generation changed");
          policy.requireSafe(MaintenanceUnit.CADDY);
        },
        new MaintenanceUnitStopClient.NativeStart()::execute,
        () -> {
          fence.verify();
          return caddyFence(fence);
        },
        MaintenanceUnit.CADDY,
        Optional.of(budget));
  }

  /** PT-OPS-CADDYFENCE001..003: preserve BOTH full checks and each local same-inode check. */
  static RetirementGate caddyAdmissionFence(
      RetirementGate parent, RetirementGate owner, Attempt api, Attempt web) throws IOException {
    Objects.requireNonNull(parent);
    Objects.requireNonNull(owner);
    Objects.requireNonNull(api);
    Objects.requireNonNull(web);
    if (api.unit != MaintenanceUnit.API || web.unit != MaintenanceUnit.WEB)
      throw new IOException("Caddy start unavailable");
    return () -> {
      parent.verify();
      api.requireRetained(owner);
      web.requireRetained(owner);
      parent.verify();
    };
  }

  /**
   * BUG673: no owned Caddy marker exists; only the live API/Web fence is borrowed. Close-only
   * verifies that fence, never retires either service intent or releases an owner.
   */
  static MarkerLease caddyFence(RetirementGate fence) {
    Objects.requireNonNull(fence, "same live service fence");
    return new MarkerLease() {
      public void retire() throws IOException {
        fence.verify();
      }

      public void requireRetained() throws IOException {
        fence.verify();
      }

      public void closeObservation() throws IOException {
        fence.verify();
      }
    };
  }

  private static void interrupted() {
    if (Thread.currentThread().isInterrupted())
      throw new StopGateException(StopGateFailure.INTERRUPTED);
  }

  /** Opaque owner of a possibly live start client; never destroys or silently closes it. */
  public static final class Attempt {
    private final Object stateLock;
    private final Context context;
    private final @Nullable Process process;
    private final MarkerLease marker;
    private final Optional<MorningParentBudget> budget;
    private final MaintenanceUnit unit;
    private Status retainedStatus = Status.UNKNOWN;
    private boolean retired;
    private boolean retiring;
    private boolean retireUncertain;
    private boolean stdinClosed;
    private boolean streamsClosed;
    private boolean poisoned;

    private Attempt(
        Context context,
        @Nullable Process process,
        MarkerLease marker,
        Optional<MorningParentBudget> budget,
        MaintenanceUnit unit,
        Object stateLock) {
      this.stateLock = stateLock;
      this.context = context;
      this.process = process;
      this.marker = marker;
      this.budget = budget;
      this.unit = unit;
    }

    public Status status() {
      synchronized (stateLock) {
        return retainedStatus;
      }
    }

    /** Same inode owners and confirmed client release; neither ready nor retirement authority. */
    public void requireRetained(RetirementGate gate) throws IOException {
      synchronized (stateLock) {
        Objects.requireNonNull(gate);
        if ((unit != MaintenanceUnit.API && unit != MaintenanceUnit.WEB)
            || retainedStatus != Status.CLIENT_EXITED_ZERO
            || !stdinClosed
            || !streamsClosed
            || retired
            || retiring
            || retireUncertain) throw new IOException("service intent proof unavailable");
        context.recheck();
        gate.verify();
        marker.requireRetained();
        gate.verify();
        context.recheck();
      }
    }

    /** Live daemon profile/ordinary peer gates are distinct from the worker terminus contract. */
    public void retireReadyAfter(RetirementGate before, RetirementGate after) throws IOException {
      synchronized (stateLock) {
        Objects.requireNonNull(before);
        Objects.requireNonNull(after);
        if ((unit != MaintenanceUnit.API
                && unit != MaintenanceUnit.WEB
                && unit != MaintenanceUnit.CADDY)
            || !stdinClosed
            || !streamsClosed) throw new IOException("live intent retirement unavailable");
        retireAfter(before);
        // Failure after unlink/close is UNKNOWN and must be retained by the enclosing parent.
        context.recheck();
        after.verify();
        context.recheck();
      }
    }

    /** Close-only: marker stays durable, no receipt/retirement/unlock authority is granted. */
    public void preserveObservation() throws IOException {
      synchronized (stateLock) {
        if ((unit != MaintenanceUnit.API
                && unit != MaintenanceUnit.WEB
                && unit != MaintenanceUnit.CADDY)
            || retired
            || retiring
            || retireUncertain) throw new IOException("service observation close unavailable");
        retireUncertain = true;
        marker.closeObservation();
      }
    }

    /**
     * Only the still-owned parent may retire after fresh worker receipt, explicit stop, whole-Unit
     * termination, and original identity have been checked. Client exit zero alone is insufficient.
     * An exception leaves the marker unrepaired; UNKNOWN and nonzero cannot retire.
     */
    void retireAfter(RetirementGate gate) throws IOException {
      synchronized (stateLock) {
        Objects.requireNonNull(gate, "parent completion proof");
        if (retainedStatus != Status.CLIENT_EXITED_ZERO || retired || retiring || retireUncertain)
          throw new IOException("backup intent retirement unavailable");
        retiring = true;
        try {
          context.recheck();
          gate.verify();
          context.recheck();
          retireUncertain = true;
          marker.retire();
          retired = true;
        } finally {
          retiring = false;
        }
      }
    }

    /** Reap under still-held parent owners; UNKNOWN is never a worker or unlock receipt. */
    public Status awaitClient() {
      synchronized (stateLock) {
        if (retainedStatus != Status.UNKNOWN || streamsClosed || poisoned) return retainedStatus;
        if (process == null) return Status.UNKNOWN;
        try {
          context.recheck();
          if (Thread.currentThread().isInterrupted()) return Status.UNKNOWN;
          if (!stdinClosed) {
            stdinClosed = true;
            Objects.requireNonNull(process.getOutputStream(), "start stdin").close();
          }
          if (budget.isPresent()) {
            long remaining = budget.orElseThrow().remainingNanos();
            if (!process.waitFor(
                Math.min(TimeUnit.SECONDS.toNanos(120), remaining), TimeUnit.NANOSECONDS))
              return Status.UNKNOWN;
            budget.orElseThrow().requireWithin();
          } else if (!process.waitFor(120, TimeUnit.SECONDS)) return Status.UNKNOWN;
          if (Thread.currentThread().isInterrupted()) return Status.UNKNOWN;
          var stdout = Objects.requireNonNull(process.getInputStream(), "start stdout");
          Closeable stderr;
          try {
            stderr = Objects.requireNonNull(process.getErrorStream(), "start stderr");
          } catch (RuntimeException | Error failure) {
            closeOne(stdout);
            throw failure;
          }
          boolean closed = closeBoth(stdout, stderr);
          streamsClosed = true;
          if (!closed) return Status.UNKNOWN;
          context.recheck();
          retainedStatus =
              process.exitValue() == 0 ? Status.CLIENT_EXITED_ZERO : Status.CLIENT_EXITED_NONZERO;
          return retainedStatus;
        } catch (InterruptedException interrupted) {
          Thread.currentThread().interrupt();
          return Status.UNKNOWN;
        } catch (IOException | RuntimeException | Error failure) {
          poisoned = true;
          return Status.UNKNOWN;
        }
      }
    }

    private static boolean closeBoth(Closeable stdout, Closeable stderr) {
      boolean clean = closeOne(stdout);
      return closeOne(stderr) && clean;
    }

    private static boolean closeOne(Closeable stream) {
      try {
        stream.close();
        return true;
      } catch (IOException | RuntimeException | Error failure) {
        return false;
      }
    }
  }
}
