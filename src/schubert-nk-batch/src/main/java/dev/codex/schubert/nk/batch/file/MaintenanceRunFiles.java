package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceRetirement;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.security.MessageDigest;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed durable run-file scope. Caller MUST hold maintenance OS flock, prohibit administrative
 * namespace changes, verify legacy DB identity and confirm parent/child termination before
 * complete. NK-BAT-001; OPS-009/UI251/SS311/341/343 6.15; SSC-055/PG-D-158; PT-BAT-058..081.
 */
// PG172/SSC063, BUG195/YKT154; resource precedence and PT evidence/01_PT/017/050.
@NullMarked
public final class MaintenanceRunFiles {
  private static final int FIXED_ROOT_FILE_COUNT = 5;

  private static final java.lang.String LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME =
      "DMI_HARDCODED_ABSOLUTE_FILENAME";

  private static final java.lang.String LITERAL_VAR = "/var";

  private static final java.lang.String LITERAL_SHA_256 = "SHA-256";

  private static final java.lang.String LITERAL_LIB = "lib";

  private static final java.lang.String LITERAL_SCHUBERT_NK = "schubert-nk";

  private static final java.lang.String LITERAL_RUNS = "runs";

  private static final java.lang.String LITERAL_ATTEMPTS = "attempts";

  private static final java.lang.String LITERAL_RUN = ".run";

  private static final java.lang.String LITERAL_BEGIN = ".begin";

  private static final java.lang.String LITERAL_ACTIVE = "active";

  private static final java.lang.String LITERAL_DONE = ".done";

  private static final java.lang.String LITERAL_RETIRE = ".retire";

  private final Object scopeLock = new Object();
  private final Path varPath;
  private final DirectoryCalls directories;
  private final Optional<DirectoryCalls> host;
  private final InodeSecurityCalls security;
  private final Io io;
  private final Supplier<UUID> parts;
  private final EnvironmentInodePolicy policy;
  private final Digests digests;

  @FunctionalInterface
  interface Digests {
    MessageDigest create() throws GeneralSecurityException;
  }

  /** SS343 6.16; an initial absence is never certified as completed retirement. */
  public enum RetirementResult {
    ABSENT,
    TOO_YOUNG,
    PROTECTED,
    RETIRED
  }

  @FunctionalInterface
  public interface Operation<T> {
    T execute(Session session) throws IOException;
  }

  @FunctionalInterface
  private interface Work<T> {
    T execute() throws IOException, GeneralSecurityException;
  }

  @FunctionalInterface
  private interface Decoder<T> {
    T decode(byte[] bytes) throws IOException;
  }

  interface Io extends InspectorEnvironmentPublisher.Io {
    @Nullable DirectoryStream<Path> openNames(Path held) throws IOException;
  }

  // Fixed Linux namespace is deliberate. Re-review at PG gate or OS/path/SS change.
  // Owner NK-BAT-001; no coverage/null/security exclusion; PT-BAT-081.
  @SuppressFBWarnings(
      value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
      matchType = SuppressMatchType.EXACT,
      justification = "UI251/SS343 require fixed Linux /var; PG-D-158/PT-BAT-081")
  public static MaintenanceRunFiles create() {
    return new MaintenanceRunFiles(
        Path.of(LITERAL_VAR),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new NioIo(),
        UUID::randomUUID,
        () -> MessageDigest.getInstance(LITERAL_SHA_256),
        Optional.of(LinuxHostDirectoryCalls.create()));
  }

  /** Fixed child observer only. Host RW is policy, not a child mutation capability. SSC109/111. */
  @SuppressFBWarnings(
      value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed authoritative host /var, readonly child observation")
  static MaintenanceActivation observeHost(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MaintenanceActivation activation)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(activation);
    require(
        expected.service() == RootStartupContext.Service.CLEANUP
            || expected.service() == RootStartupContext.Service.EXPIRY);
    context.recheck(expected);
    var files =
        new MaintenanceRunFiles(
            Path.of(LITERAL_VAR),
            LinuxHostDirectoryCalls.create(),
            LinuxInodeSecurity.create(),
            new NioIo(),
            UUID::randomUUID,
            () -> MessageDigest.getInstance(LITERAL_SHA_256));
    MaintenanceActivation observed = files.execute(session -> session.observe(activation));
    context.recheck(expected);
    return observed;
  }

  /** SSC137: fixed service Root reads the whole original graph; never resumes or mutates it. */
  @SuppressFBWarnings(
      value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
      matchType = SuppressMatchType.EXACT,
      justification = "SSC200 fixed authoritative /var readonly Expiry original lookup")
  static BatchRun observeSuccessReferenceHost(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MaintenanceActivation current,
      UUID priorId,
      Instant observed)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(expected);
    Objects.requireNonNull(current);
    Objects.requireNonNull(priorId);
    Objects.requireNonNull(observed);
    require(expected.service() == RootStartupContext.Service.EXPIRY);
    context.recheck(expected);
    var files =
        new MaintenanceRunFiles(
            Path.of(LITERAL_VAR),
            LinuxHostDirectoryCalls.create(),
            LinuxInodeSecurity.create(),
            new NioIo(),
            UUID::randomUUID,
            () -> MessageDigest.getInstance(LITERAL_SHA_256));
    var prior = files.execute(session -> session.successReferenceRun(current, priorId, observed));
    context.recheck(expected);
    return prior;
  }

  /** SSC137: fixed service Root reads the whole original graph; never resumes or mutates it. */
  @SuppressFBWarnings(
      value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
      matchType = SuppressMatchType.EXACT,
      justification =
          "SSC137 fixed host/private /var original observation, no caller path or M capability")
  static StartupOriginal observeStartup(
      RootStartupContext context,
      RootStartupContext.Snapshot self,
      MaintenanceActivation activation)
      throws IOException {
    Objects.requireNonNull(context);
    Objects.requireNonNull(self);
    Objects.requireNonNull(activation);
    require(
        self.service() == RootStartupContext.Service.API
            || self.service() == RootStartupContext.Service.WEB);
    context.recheck(self);
    var files =
        new MaintenanceRunFiles(
            Path.of(LITERAL_VAR),
            LinuxHostDirectoryCalls.create(),
            LinuxInodeSecurity.create(),
            new NioIo(),
            UUID::randomUUID);
    var observed =
        files.execute(
            session -> {
              session.verifyStartupPrivate(LinuxDirectoryCalls.create());
              var value = session.observeStartup(activation);
              session.verifyStartupPrivate(LinuxDirectoryCalls.create());
              require(value.equals(session.observeStartup(activation)));
              return value;
            });
    context.recheck(self);
    return observed;
  }

  public record StartupOriginal(
      MaintenanceActivation activation, Optional<MaintenanceCompletion> completed) {
    public StartupOriginal {
      Objects.requireNonNull(activation);
      Objects.requireNonNull(completed);
      if (completed.isPresent() && !completed.orElseThrow().activation().equals(activation))
        throw new IllegalArgumentException("startup original binding");
    }

    @Override
    public String toString() {
      return "StartupOriginal[identity=<redacted>]";
    }
  }

  MaintenanceRunFiles(
      Path varPath,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      Io io,
      Supplier<UUID> parts) {
    this(
        varPath,
        directories,
        security,
        io,
        parts,
        () -> MessageDigest.getInstance(LITERAL_SHA_256));
  }

  MaintenanceRunFiles(
      Path varPath,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      Io io,
      Supplier<UUID> parts,
      Digests digests) {
    this(varPath, directories, security, io, parts, digests, Optional.empty());
  }

  MaintenanceRunFiles(
      Path varPath,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      Io io,
      Supplier<UUID> parts,
      Digests digests,
      Optional<DirectoryCalls> host) {
    this.varPath = Objects.requireNonNull(varPath, "durable ancestor");
    this.directories = Objects.requireNonNull(directories, "directory operations");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "record IO");
    this.parts = Objects.requireNonNull(parts, "part identities");
    this.digests = Objects.requireNonNull(digests, "plan digests");
    this.host = Objects.requireNonNull(host, "host ancestor view");
    if (!varPath.isAbsolute()
        || varPath.getNameCount() == 0
        || !varPath.equals(varPath.normalize()))
      throw new IllegalArgumentException("invalid durable ancestor");
    policy = new EnvironmentInodePolicy(security, io);
  }

  /** Session may not escape the callback; it is disabled before all six owned roots close. */
  public <T> T execute(Operation<T> operation) throws StorageIoException {
    Objects.requireNonNull(operation, "run operation");
    synchronized (scopeLock) {
      begin();
      try {
        T result;
        {
          result =
              ResourceScope.acquire(
                  () -> OwnedTransferDirectory.open(directories, varPath),
                  OwnedTransferDirectory::close,
                  var -> {
                    return ResourceScope.acquire(
                        () -> var.openExistingChild(LITERAL_LIB),
                        OwnedTransferDirectory::close,
                        lib -> {
                          return ResourceScope.acquire(
                              () -> lib.openExistingChild(LITERAL_SCHUBERT_NK),
                              OwnedTransferDirectory::close,
                              app -> {
                                return ResourceScope.acquire(
                                    () -> app.openExistingChild("maintenance"),
                                    OwnedTransferDirectory::close,
                                    maintenance -> {
                                      return ResourceScope.acquire(
                                          () -> maintenance.openExistingChild(LITERAL_RUNS),
                                          OwnedTransferDirectory::close,
                                          runs -> {
                                            return ResourceScope.acquire(
                                                () ->
                                                    maintenance.openExistingChild(LITERAL_ATTEMPTS),
                                                OwnedTransferDirectory::close,
                                                attempts -> {
                                                  var roots =
                                                      List.of(
                                                          var,
                                                          lib,
                                                          app,
                                                          maintenance,
                                                          runs,
                                                          attempts);
                                                  var session = new Session(roots, capture(roots));
                                                  try {
                                                    session.verifyNamespace();
                                                    T completed =
                                                        Objects.requireNonNull(
                                                            operation.execute(session),
                                                            "run operation result");
                                                    session.finish();
                                                    return completed;
                                                  } finally {
                                                    session.invalidate();
                                                  }
                                                });
                                          });
                                    });
                              });
                        });
                  });
        }
        require(!Thread.currentThread().isInterrupted());
        return result;
      } catch (IOException failure) {
        throw unavailable();
      }
    }
  }

  private void begin() throws StorageIoException {
    require(!Thread.currentThread().isInterrupted());
    require(security.effectiveUid() == 0);
  }

  private List<Snapshot> capture(List<OwnedTransferDirectory> roots) throws StorageIoException {
    List<Snapshot> values = new ArrayList<>();
    for (int index = 0; index < roots.size(); index++) {
      boolean shared = index < 3;
      values.add(
          roots
              .get(index)
              .atDirectory(
                  p ->
                      shared
                          ? policy.durableAncestor(p, host.isPresent())
                          : policy.durable(p, true, 0)));
    }
    if (host.isPresent()) verifyHostAncestors(values);
    require(values.get(3).metadata().device() == values.get(4).metadata().device());
    require(values.get(3).metadata().device() == values.get(5).metadata().device());
    return List.copyOf(values);
  }

  private void verifyHostAncestors(List<Snapshot> privateValues) throws StorageIoException {
    ResourceScope.acquire(
        () -> OwnedTransferDirectory.open(host.orElseThrow(), varPath),
        OwnedTransferDirectory::close,
        var -> {
          return ResourceScope.acquire(
              () -> var.openExistingChild(LITERAL_LIB),
              OwnedTransferDirectory::close,
              lib -> {
                return ResourceScope.acquire(
                    () -> lib.openExistingChild(LITERAL_SCHUBERT_NK),
                    OwnedTransferDirectory::close,
                    app -> {
                      var hostRoots = List.of(var, lib, app);
                      var before = new ArrayList<Snapshot>();
                      for (int index = 0; index < hostRoots.size(); index++) {
                        Snapshot actual = hostRoots.get(index).atDirectory(policy::durableAncestor);
                        Snapshot service = privateValues.get(index);
                        require(
                            actual.metadata().equals(service.metadata())
                                && actual.filesystem().equals(service.filesystem()));
                        before.add(actual);
                      }
                      for (int index = 0; index < hostRoots.size(); index++)
                        require(
                            before
                                .get(index)
                                .equals(hostRoots.get(index).atDirectory(policy::durableAncestor)));
                      return Boolean.TRUE;
                    });
              });
        });
  }

  /** Scope-bound serialized operations, never an OS lock or completed-parent certificate. */
  public final class Session {
    private final Object stateLock = new Object();
    private final List<OwnedTransferDirectory> roots;
    private final List<Snapshot> expectedRoots;
    private final DurableRecordFiles maintenanceFiles;
    private final DurableRecordFiles runFiles;
    private final DurableRecordFiles attemptFiles;
    private boolean open = true;

    private Session(List<OwnedTransferDirectory> roots, List<Snapshot> expectedRoots) {
      this.roots = List.copyOf(roots);
      this.expectedRoots = List.copyOf(expectedRoots);
      maintenanceFiles = new DurableRecordFiles(roots.get(3), security, io);
      runFiles = new DurableRecordFiles(roots.get(4), security, io);
      attemptFiles = new DurableRecordFiles(roots.get(5), security, io);
    }

    /** SSC203: retained namespace/owner only; never a graph or completion certificate. */
    public void verifyRetained() throws StorageIoException {
      perform(
          () -> {
            verifyNamespace();
            return Boolean.TRUE;
          });
    }

    public MaintenanceRunState start(BatchRun run, UUID activationId) throws StorageIoException {
      Objects.requireNonNull(run, "fixed run");
      Objects.requireNonNull(activationId, "activation identity");
      return perform(
          () -> {
            Graph before = scan();
            require(before.active().isEmpty() && before.pending().isEmpty());
            require(!before.runs().containsKey(run.id()));
            require(!before.begins().containsKey(activationId));
            var activation = new MaintenanceActivation(run, activationId);
            publish(runFiles, run.id() + LITERAL_RUN, MaintenanceRecords.anchor(run));
            publish(
                attemptFiles,
                activationId + LITERAL_BEGIN,
                MaintenanceRecords.activation(activation));
            publish(maintenanceFiles, LITERAL_ACTIVE, MaintenanceRecords.activation(activation));
            var runs = new HashMap<>(before.runs());
            runs.put(run.id(), run);
            var begins = new HashMap<>(before.begins());
            begins.put(activationId, activation);
            require(graph(runs, begins, before.done(), Optional.of(activation)).equals(scan()));
            return new MaintenanceRunState(activation, Optional.empty());
          });
    }

    public MaintenanceRunState resume(UUID runId, UUID nextActivationId) throws StorageIoException {
      Objects.requireNonNull(runId, "run identity");
      Objects.requireNonNull(nextActivationId, "next activation");
      return perform(
          () -> {
            Graph before = scan();
            BatchRun run = before.runs().get(runId);
            if (run == null) throw unavailable();
            if (before.active().isPresent()) {
              MaintenanceActivation active = before.active().orElseThrow();
              require(active.run().equals(run));
              sealIdentity(active);
              MaintenanceCompletion previous = before.done().get(active.id());
              if (previous != null)
                publish(
                    attemptFiles,
                    active.id() + LITERAL_DONE,
                    MaintenanceRecords.completion(previous));
              publish(maintenanceFiles, LITERAL_ACTIVE, MaintenanceRecords.activation(active));
              require(before.equals(scan()));
              return new MaintenanceRunState(
                  active, Optional.ofNullable(before.done().get(active.id())));
            }
            require(before.pending().isEmpty() || before.pending().orElseThrow().equals(runId));
            MaintenanceActivation activation = null;
            for (var candidate : before.begins().values())
              if (!before.done().containsKey(candidate.id())) activation = candidate;
            var begins = new HashMap<>(before.begins());
            if (activation == null) {
              require(!begins.containsKey(nextActivationId));
              activation = new MaintenanceActivation(run, nextActivationId);
              begins.put(nextActivationId, activation);
            }
            // The validated single pending graph and selected run above already bind this
            // activation.
            sealIdentity(activation);
            publish(maintenanceFiles, LITERAL_ACTIVE, MaintenanceRecords.activation(activation));
            require(
                graph(before.runs(), begins, before.done(), Optional.of(activation))
                    .equals(scan()));
            return new MaintenanceRunState(activation, Optional.empty());
          });
    }

    /**
     * Cleanup child correlation only. This read-only observation is not M/A, backup, DB lock or
     * DELETE authority. NK-OPS-001/OPS009/UI251/SS343/SSC104/PG330; PT-OPS-MRF001..004.
     */
    public MaintenanceActivation observeCleanup(CleanupWorkerRequest request)
        throws StorageIoException {
      Objects.requireNonNull(request, "fixed cleanup request");
      return observe(
          new MaintenanceActivation(
              new BatchRun(request.run(), request.cutoff()), request.activation()));
    }

    /** Read-only original proof using the SAME retained owner, never a resume or fresh trust. */
    public MaintenanceActivation observe(MaintenanceActivation expected) throws StorageIoException {
      Objects.requireNonNull(expected, "expected owned original");
      return perform(
          () -> {
            Graph first = scan();
            require(first.equals(scan()));
            require(first.active().isPresent());
            MaintenanceActivation active = first.active().orElseThrow();
            require(active.equals(expected));
            // graph() places this run in pending iff its current activation has no done record.
            require(first.pending().equals(Optional.of(expected.run().id())));
            return active;
          });
    }

    /**
     * SSC200 / RLOOK200001: data only, exact retained anchor under this SAME live Session.
     * Current-run references may use the owned pending anchor; a different run must be completed.
     * Never derive cutoff from a DB timestamp, change active, resume or grant authority.
     */
    public BatchRun successReferenceRun(
        MaintenanceActivation current, UUID priorId, Instant observed) throws StorageIoException {
      return referenceRun(current, Optional.empty(), priorId, observed);
    }

    /** SSC240/RLOOK852001: exact DONE is data proof, never startup/DB authority. */
    public BatchRun completedSuccessReferenceRun(
        MaintenanceCompletion expected, UUID priorId, Instant observed) throws StorageIoException {
      Objects.requireNonNull(expected);
      return referenceRun(expected.activation(), Optional.of(expected), priorId, observed);
    }

    private BatchRun referenceRun(
        MaintenanceActivation current,
        Optional<MaintenanceCompletion> completion,
        UUID priorId,
        Instant observed)
        throws StorageIoException {
      Objects.requireNonNull(current);
      Objects.requireNonNull(priorId);
      Objects.requireNonNull(observed);
      return perform(
          () -> {
            Graph first = scan();
            // BUG799/RLOOK493001: bracket pure validation with two complete retained scans.
            // No cached graph or anchor-only read: the final scan rejects unrelated drift too.
            if (completion.isEmpty()) require(first.active().equals(Optional.of(current)));
            else {
              MaintenanceCompletion expected = completion.orElseThrow();
              require(
                  first.active().isEmpty()
                      && first.pending().isEmpty()
                      && current.run().equals(first.runs().get(current.run().id()))
                      && current.equals(first.begins().get(current.id()))
                      && expected.equals(first.done().get(current.id())));
              // observed is the historical SKIP start; current DONE normally ends later.
              // The referenced prior run's end <= observed check below is unchanged.
            }
            require(
                !observed.isBefore(current.run().cutoff())
                    && !observed.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
                    && observed.getNano() % 1000 == 0);
            BatchRun prior = first.runs().get(priorId);
            if (prior == null) throw unavailable();
            require(
                prior
                    .cutoff()
                    .atZone(java.time.ZoneId.of("Asia/Tokyo"))
                    .toLocalDate()
                    .equals(
                        current
                            .run()
                            .cutoff()
                            .atZone(java.time.ZoneId.of("Asia/Tokyo"))
                            .toLocalDate()));
            if (!priorId.equals(current.run().id())) {
              // Graph permits at most one pending run. The pending capability requires active
              // current, whose Graph invariant excludes a different pending run; completed
              // capability above requires no pending run at all. Keep the independent prior DONE
              // check below, without re-testing a condition already proved by the phase/Graph.
              require(
                  first.done().values().stream()
                      .anyMatch(
                          value ->
                              value.activation().run().equals(prior)
                                  && !value.endedAt().isAfter(observed)));
            } else require(prior.equals(current.run()));
            require(first.equals(scan()));
            return prior;
          });
    }

    /** Pending and completed are disjoint whole-graph observations, not parent terminal proof. */
    public StartupOriginal observeStartup(MaintenanceActivation expected)
        throws StorageIoException {
      Objects.requireNonNull(expected);
      return perform(
          () -> {
            Graph first = scan();
            require(first.equals(scan()));
            require(
                expected.run().equals(first.runs().get(expected.run().id()))
                    && expected.equals(first.begins().get(expected.id())));
            var completion = Optional.ofNullable(first.done().get(expected.id()));
            if (completion.isEmpty()) {
              require(
                  first.active().equals(Optional.of(expected))
                      && first.pending().equals(Optional.of(expected.run().id())));
            } else {
              require(first.active().isEmpty() && first.pending().isEmpty());
            }
            return new StartupOriginal(expected, completion);
          });
    }

    private void verifyStartupPrivate(DirectoryCalls privateCalls) throws IOException {
      ResourceScope.acquire(
          () -> OwnedTransferDirectory.open(privateCalls, varPath),
          OwnedTransferDirectory::close,
          var -> verifyStartupPrivate(List.of(var), 0));
    }

    private Boolean verifyStartupPrivate(List<OwnedTransferDirectory> views, int index)
        throws IOException {
      var current = views.get(index);
      var observed =
          current.atDirectory(
              p ->
                  index < 3
                      ? policy.durableAncestor(p, true)
                      : policy.roleDirectory(p, 0, 0, 0x1c0, false));
      var actual = expectedRoots.get(index);
      require(
          !observed.filesystem().equals("tmpfs")
              && observed.metadata().equals(actual.metadata())
              && observed.filesystem().equals(actual.filesystem()));
      if (index < FIXED_ROOT_FILE_COUNT) {
        String[] names = {
          LITERAL_LIB, LITERAL_SCHUBERT_NK, "maintenance", LITERAL_RUNS, LITERAL_ATTEMPTS
        };
        var parent = index == 4 ? views.get(3) : current;
        ResourceScope.acquire(
            () -> parent.openExistingChild(names[index]),
            OwnedTransferDirectory::close,
            next -> {
              var added = new ArrayList<>(views);
              added.add(next);
              return verifyStartupPrivate(List.copyOf(added), index + 1);
            });
      }
      require(
          observed.equals(
              current.atDirectory(
                  p ->
                      index < 3
                          ? policy.durableAncestor(p, true)
                          : policy.roleDirectory(p, 0, 0, 0x1c0, false))));
      return Boolean.TRUE;
    }

    public MaintenanceCompletion complete(MaintenanceCompletion completion)
        throws StorageIoException {
      Objects.requireNonNull(completion, "completion");
      return perform(
          () -> {
            Graph before = scan();
            MaintenanceActivation activation = completion.activation();
            require(activation.equals(before.begins().get(activation.id())));
            MaintenanceCompletion previous = before.done().get(activation.id());
            if (previous != null) require(previous.equals(completion));
            if (before.active().isPresent())
              require(before.active().orElseThrow().equals(activation));
            else require(previous != null);
            sealIdentity(activation);
            if (before.active().isPresent())
              publish(maintenanceFiles, LITERAL_ACTIVE, MaintenanceRecords.activation(activation));
            publish(
                attemptFiles,
                activation.id() + LITERAL_DONE,
                MaintenanceRecords.completion(completion));
            maintenanceFiles.remove(LITERAL_ACTIVE, MaintenanceRecords.activation(activation));
            verifyNamespace();
            var done = new HashMap<>(before.done());
            done.put(activation.id(), completion);
            require(graph(before.runs(), before.begins(), done, Optional.empty()).equals(scan()));
            return completion;
          });
    }

    /** SS343 6.16; PT-BAT-098..113. Enumeration is not a DB/age authorization. */
    public List<BatchRun> retirementCandidates() throws StorageIoException {
      return perform(
          () -> {
            Inventory inventory = retirementScan();
            Graph graph = validateRetirement(inventory);
            Optional<BatchRun> target = inventory.target();
            if (target.isPresent()) return List.of(target.orElseThrow());
            return graph.runs().values().stream()
                .filter(run -> !graph.pending().filter(run.id()::equals).isPresent())
                .filter(run -> !graph.active().filter(a -> a.run().equals(run)).isPresent())
                .sorted(Comparator.comparing(run -> run.id().toString()))
                .toList();
          });
    }

    /** Caller owns continuous OS/DB exclusion; this never acquires or releases either lock. */
    public RetirementResult retire(BatchRun run, Instant now, RunReferenceRepository references)
        throws StorageIoException {
      Objects.requireNonNull(run, "retiring run");
      Objects.requireNonNull(now, "retirement time");
      Objects.requireNonNull(references, "run reference repository");
      // Reuse the exact established timestamp invariant without creating a fresh identity.
      new BatchRun(run.id(), now);
      return perform(
          () -> {
            Inventory state = retirementScan();
            Graph graph = validateRetirement(state);
            Optional<BatchRun> pending = state.target();
            if (pending.isPresent()) require(pending.orElseThrow().equals(run));
            BatchRun anchor = state.runs().get(run.id());
            if (anchor == null && state.marker().isEmpty()) return RetirementResult.ABSENT;
            if (anchor != null) require(anchor.equals(run));
            if (graph.pending().filter(run.id()::equals).isPresent()
                || graph.active().filter(a -> a.run().equals(run)).isPresent())
              return RetirementResult.PROTECTED;
            List<MaintenanceCompletion> completions =
                ordered(state.marker().isPresent() ? state.plans() : state.done()).stream()
                    .filter(value -> value.activation().run().equals(run))
                    .toList();
            Instant latest =
                state.marker().isPresent()
                    ? state.marker().orElseThrow().latestEnded()
                    : completions.stream()
                        .map(MaintenanceCompletion::endedAt)
                        .max(Instant::compareTo)
                        .orElseThrow(EnvironmentInodePolicy::unavailable);
            if (Duration.between(latest, now).compareTo(Duration.ofDays(400)) <= 0) {
              require(pending.isEmpty());
              return RetirementResult.TOO_YOUNG;
            }
            if (!unreferenced(references, run)) {
              require(pending.isEmpty());
              return RetirementResult.PROTECTED;
            }
            if (state.marker().isEmpty()) {
              for (var completion : completions) {
                var plans = new HashMap<>(state.plans());
                plans.put(completion.activation().id(), completion);
                Inventory expected = state.withPlans(plans);
                state =
                    retirementChange(
                        state,
                        expected,
                        references,
                        run,
                        () ->
                            publish(
                                attemptFiles,
                                completion.activation().id() + ".plan",
                                MaintenanceRecords.completion(completion)));
              }
              var marker =
                  new MaintenanceRetirement(
                      run, latest, now, completions.size(), digest(state.plans()));
              Inventory expected = state.withMarker(Optional.of(marker));
              state =
                  retirementChange(
                      state,
                      expected,
                      references,
                      run,
                      () ->
                          publish(
                              maintenanceFiles,
                              run.id() + LITERAL_RETIRE,
                              MaintenanceRecords.retirement(marker)));
            } else {
              // A visible marker may be the residue of publication followed by a failed fsync.
              var marker = state.marker().orElseThrow();
              state =
                  retirementChange(
                      state,
                      state,
                      references,
                      run,
                      () ->
                          publish(
                              maintenanceFiles,
                              run.id() + LITERAL_RETIRE,
                              MaintenanceRecords.retirement(marker)));
            }
            MaintenanceRetirement marker = state.marker().orElseThrow();
            if (state.runs().containsKey(run.id())) {
              // ALL plan copies remain until ALL original records, including the anchor, are
              // durable absent.
              for (var completion : ordered(state.plans())) {
                UUID id = completion.activation().id();
                var done = new HashMap<>(state.done());
                done.remove(id);
                Inventory expected = state.withOriginals(state.runs(), state.begins(), done);
                state =
                    retirementChange(
                        state,
                        expected,
                        references,
                        run,
                        () ->
                            remove(
                                attemptFiles,
                                id + LITERAL_DONE,
                                MaintenanceRecords.completion(completion)));
                var begins = new HashMap<>(state.begins());
                begins.remove(id);
                expected = state.withOriginals(state.runs(), begins, state.done());
                state =
                    retirementChange(
                        state,
                        expected,
                        references,
                        run,
                        () ->
                            remove(
                                attemptFiles,
                                id + LITERAL_BEGIN,
                                MaintenanceRecords.activation(completion.activation())));
              }
              var runs = new HashMap<>(state.runs());
              runs.remove(run.id());
              Inventory expected = state.withOriginals(runs, state.begins(), state.done());
              state =
                  retirementChange(
                      state,
                      expected,
                      references,
                      run,
                      () ->
                          remove(runFiles, run.id() + LITERAL_RUN, MaintenanceRecords.anchor(run)));
            }
            // BUG172/YKT133: visible absence after a prior failed unlink barrier is not durable.
            // Seal ALL original directories before discarding any recovery plan, even on retry.
            state =
                retirementChange(
                    state,
                    state,
                    references,
                    run,
                    () -> {
                      for (int index = 3; index < 6; index++) roots.get(index).sync();
                    });
            for (var completion : ordered(state.plans())) {
              var plans = new HashMap<>(state.plans());
              plans.remove(completion.activation().id());
              Inventory expected = state.withPlans(plans);
              state =
                  retirementChange(
                      state,
                      expected,
                      references,
                      run,
                      () ->
                          remove(
                              attemptFiles,
                              completion.activation().id() + ".plan",
                              MaintenanceRecords.completion(completion)));
            }
            Inventory expected = state.withMarker(Optional.empty());
            state =
                retirementChange(
                    state,
                    expected,
                    references,
                    run,
                    () ->
                        remove(
                            maintenanceFiles,
                            run.id() + LITERAL_RETIRE,
                            MaintenanceRecords.retirement(marker)));
            // Also re-establish barriers for initially absent originals/plans after a previous
            // crash.
            for (int index = 3; index < 6; index++) roots.get(index).sync();
            require(state.equals(retirementScan()));
            require(unreferenced(references, run));
            return RetirementResult.RETIRED;
          });
    }

    private boolean unreferenced(RunReferenceRepository references, BatchRun run)
        throws StorageIoException {
      var result = references.read(run);
      require(result.identityConsistent());
      return !result.anyReference();
    }

    private Inventory retirementChange(
        Inventory before,
        Inventory expected,
        RunReferenceRepository references,
        BatchRun run,
        Mutation mutation)
        throws IOException, GeneralSecurityException {
      require(before.equals(retirementScan()));
      validateRetirement(before);
      require(unreferenced(references, run));
      mutation.execute();
      Inventory actual = retirementScan();
      require(expected.equals(actual));
      validateRetirement(actual);
      return actual;
    }

    private void remove(DurableRecordFiles files, String name, byte[] bytes) throws IOException {
      try {
        verifyNamespace();
        files.remove(name, bytes);
        verifyNamespace();
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }

    private String digest(Map<UUID, MaintenanceCompletion> plans) throws GeneralSecurityException {
      var hash = Objects.requireNonNull(digests.create(), "plan digest");
      hash.update("NKPLAN1\n".getBytes(StandardCharsets.US_ASCII));
      for (var completion : ordered(plans)) {
        byte[] bytes = MaintenanceRecords.completion(completion);
        try {
          hash.update(bytes);
        } finally {
          Arrays.fill(bytes, (byte) 0);
        }
      }
      return HexFormat.of().formatHex(hash.digest());
    }

    private Graph validateRetirement(Inventory state) throws IOException, GeneralSecurityException {
      Optional<BatchRun> target = state.target();
      for (var completion : state.plans().values())
        require(completion.activation().run().equals(target.orElseThrow()));
      var begins = new HashMap<>(state.begins());
      var done = new HashMap<>(state.done());
      if (state.marker().isPresent()) {
        var marker = state.marker().orElseThrow();
        BatchRun anchor = state.runs().get(marker.run().id());
        for (var completion : state.plans().values())
          require(!completion.endedAt().isAfter(marker.latestEnded()));
        if (anchor != null) {
          require(anchor.equals(marker.run()));
          require(state.plans().size() == marker.count());
          require(digest(state.plans()).equals(marker.digest()));
          require(
              state.plans().values().stream()
                  .map(MaintenanceCompletion::endedAt)
                  .max(Instant::compareTo)
                  .orElseThrow(EnvironmentInodePolicy::unavailable)
                  .equals(marker.latestEnded()));
          for (var begin : state.begins().values())
            if (begin.run().id().equals(marker.run().id())) {
              var plan = state.plans().get(begin.id());
              require(plan != null && plan.activation().equals(begin));
            }
          for (var completion : state.done().values())
            if (completion.activation().run().id().equals(marker.run().id()))
              require(completion.equals(state.plans().get(completion.activation().id())));
          for (var completion : state.plans().values()) {
            // Never overwrite a different-run activation that happens to reuse the same ID.
            var priorBegin =
                begins.putIfAbsent(completion.activation().id(), completion.activation());
            require(priorBegin == null || priorBegin.equals(completion.activation()));
            var priorDone = done.putIfAbsent(completion.activation().id(), completion);
            require(priorDone == null || priorDone.equals(completion));
          }
        } else {
          for (var begin : state.begins().values())
            require(!begin.run().id().equals(marker.run().id()));
          for (var completion : state.done().values())
            require(!completion.activation().run().id().equals(marker.run().id()));
        }
      } else {
        for (var completion : state.plans().values())
          require(completion.equals(state.done().get(completion.activation().id())));
      }
      Graph result = graph(state.runs(), begins, done, state.active());
      if (target.isPresent()) {
        UUID id = target.orElseThrow().id();
        require(result.pending().filter(id::equals).isEmpty());
        require(result.active().filter(a -> a.run().id().equals(id)).isEmpty());
      }
      return result;
    }

    private Inventory retirementScan() throws IOException {
      verifyNamespace();
      List<Snapshot> before = capture(roots);
      Set<String> rootNames = names(roots.get(3));
      require(rootNames.containsAll(Set.of(LITERAL_RUNS, LITERAL_ATTEMPTS)));
      Map<UUID, BatchRun> runs = new HashMap<>();
      Map<UUID, MaintenanceActivation> begins = new HashMap<>();
      Map<UUID, MaintenanceCompletion> done = new HashMap<>();
      Map<UUID, MaintenanceCompletion> plans = new HashMap<>();
      List<CapturedFile> files = new ArrayList<>();
      Optional<MaintenanceRetirement> marker = Optional.empty();
      Optional<MaintenanceActivation> active = Optional.empty();
      for (String name : rootNames) {
        if (name.equals(LITERAL_RUNS) || name.equals(LITERAL_ATTEMPTS)) continue;
        if (name.equals(LITERAL_ACTIVE))
          active =
              Optional.of(
                  read(3, maintenanceFiles, name, MaintenanceRecords::readActivation, files));
        else {
          identity(name, LITERAL_RETIRE);
          require(marker.isEmpty());
          marker =
              Optional.of(
                  read(3, maintenanceFiles, name, MaintenanceRecords::readRetirement, files));
        }
      }
      for (String name : names(roots.get(4))) {
        UUID id = identity(name, LITERAL_RUN);
        runs.put(id, read(4, runFiles, name, MaintenanceRecords::readAnchor, files));
      }
      for (String name : names(roots.get(5))) {
        if (name.endsWith(LITERAL_BEGIN)) {
          UUID id = identity(name, LITERAL_BEGIN);
          begins.put(id, read(5, attemptFiles, name, MaintenanceRecords::readActivation, files));
        } else if (name.endsWith(LITERAL_DONE)) {
          UUID id = identity(name, LITERAL_DONE);
          done.put(id, read(5, attemptFiles, name, MaintenanceRecords::readCompletion, files));
        } else {
          UUID id = identity(name, ".plan");
          plans.put(id, read(5, attemptFiles, name, MaintenanceRecords::readCompletion, files));
        }
      }
      for (CapturedFile file : files)
        require(
            file.snapshot()
                .equals(
                    file.root()
                        .atExistingEntryHandle(file.name(), p -> policy.durable(p, false, 1))));
      require(before.equals(capture(roots)));
      verifyNamespace();
      return new Inventory(runs, begins, done, active, plans, marker);
    }

    /** Re-establish durability of the selected identity before publishing or reusing its state. */
    private void sealIdentity(MaintenanceActivation activation) throws IOException {
      publish(
          runFiles,
          activation.run().id() + LITERAL_RUN,
          MaintenanceRecords.anchor(activation.run()));
      publish(
          attemptFiles, activation.id() + LITERAL_BEGIN, MaintenanceRecords.activation(activation));
    }

    private <T> T perform(Work<T> operation) throws StorageIoException {
      synchronized (stateLock) {
        require(open);
        begin();
        try {
          T value = operation.execute();
          require(!Thread.currentThread().isInterrupted());
          return value;
        } catch (IOException | GeneralSecurityException failure) {
          throw unavailable();
        }
      }
    }

    private void publish(DurableRecordFiles files, String name, byte[] bytes) throws IOException {
      try {
        verifyNamespace();
        files.publish(name, bytes, Objects.requireNonNull(parts.get(), "part identity"));
        verifyNamespace();
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }

    private Graph scan() throws IOException {
      verifyNamespace();
      List<Snapshot> before = capture(roots);
      Set<String> rootNames = names(roots.get(3));
      require(
          rootNames.equals(Set.of(LITERAL_RUNS, LITERAL_ATTEMPTS))
              || rootNames.equals(Set.of(LITERAL_RUNS, LITERAL_ATTEMPTS, LITERAL_ACTIVE)));
      Map<UUID, BatchRun> runs = new HashMap<>();
      Map<UUID, MaintenanceActivation> begins = new HashMap<>();
      Map<UUID, MaintenanceCompletion> done = new HashMap<>();
      List<CapturedFile> files = new ArrayList<>();
      for (String name : names(roots.get(4))) {
        UUID id = identity(name, LITERAL_RUN);
        BatchRun run = read(4, runFiles, name, MaintenanceRecords::readAnchor, files);
        // DurableRecordFiles already binds the canonical filename to the decoded record ID.
        runs.put(id, run);
      }
      for (String name : names(roots.get(5))) {
        if (name.endsWith(LITERAL_BEGIN)) {
          UUID id = identity(name, LITERAL_BEGIN);
          MaintenanceActivation activation =
              read(5, attemptFiles, name, MaintenanceRecords::readActivation, files);
          begins.put(id, activation);
        } else {
          UUID id = identity(name, LITERAL_DONE);
          MaintenanceCompletion completion =
              read(5, attemptFiles, name, MaintenanceRecords::readCompletion, files);
          done.put(id, completion);
        }
      }
      Optional<MaintenanceActivation> active =
          rootNames.contains(LITERAL_ACTIVE)
              ? Optional.of(
                  read(
                      3,
                      maintenanceFiles,
                      LITERAL_ACTIVE,
                      MaintenanceRecords::readActivation,
                      files))
              : Optional.empty();
      // A per-file reader's own stability does not prove stability through the whole graph scan.
      for (CapturedFile file : files)
        require(
            file.snapshot()
                .equals(
                    file.root()
                        .atExistingEntryHandle(file.name(), p -> policy.durable(p, false, 1))));
      require(before.equals(capture(roots)));
      verifyNamespace();
      return graph(runs, begins, done, active);
    }

    private <T> T read(
        int rootIndex,
        DurableRecordFiles records,
        String name,
        Decoder<T> decoder,
        List<CapturedFile> captured)
        throws IOException {
      OwnedTransferDirectory root = roots.get(rootIndex);
      Snapshot original = root.atExistingEntryHandle(name, p -> policy.durable(p, false, 1));
      require(original.metadata().device() == expectedRoots.get(rootIndex).metadata().device());
      byte[] bytes = records.read(name).orElseThrow(EnvironmentInodePolicy::unavailable);
      try {
        require(
            original.equals(root.atExistingEntryHandle(name, p -> policy.durable(p, false, 1))));
        T value = decoder.decode(bytes);
        captured.add(new CapturedFile(root, name, original));
        return value;
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }

    private void verifyNamespace() throws StorageIoException {
      {
        ResourceScope.acquire(
            () -> OwnedTransferDirectory.open(directories, varPath),
            OwnedTransferDirectory::close,
            var -> {
              return ResourceScope.acquire(
                  () -> var.openExistingChild(LITERAL_LIB),
                  OwnedTransferDirectory::close,
                  lib -> {
                    return ResourceScope.acquire(
                        () -> lib.openExistingChild(LITERAL_SCHUBERT_NK),
                        OwnedTransferDirectory::close,
                        app -> {
                          return ResourceScope.acquire(
                              () -> app.openExistingChild("maintenance"),
                              OwnedTransferDirectory::close,
                              maintenance -> {
                                return ResourceScope.acquire(
                                    () -> maintenance.openExistingChild(LITERAL_RUNS),
                                    OwnedTransferDirectory::close,
                                    runs -> {
                                      return ResourceScope.acquire(
                                          () -> maintenance.openExistingChild(LITERAL_ATTEMPTS),
                                          OwnedTransferDirectory::close,
                                          attempts -> {
                                            List<Snapshot> actual =
                                                capture(
                                                    List.of(
                                                        var,
                                                        lib,
                                                        app,
                                                        maintenance,
                                                        runs,
                                                        attempts));
                                            for (int index = 0;
                                                index < expectedRoots.size();
                                                index++)
                                              require(
                                                  expectedRoots
                                                      .get(index)
                                                      .sameIdentity(actual.get(index)));

                                            return Boolean.TRUE;
                                          });
                                    });
                              });
                        });
                  });
            });
      }
    }

    private void finish() throws StorageIoException {
      synchronized (stateLock) {
        try {
          begin();
          verifyNamespace();
        } finally {
          open = false;
        }
      }
    }

    private void invalidate() {
      synchronized (stateLock) {
        open = false;
      }
    }
  }

  private Set<String> names(OwnedTransferDirectory root) throws StorageIoException {
    return root.atDirectory(
        held -> {
          Set<String> names = new HashSet<>();
          ResourceScope.acquire(
              () -> {
                var entries = io.openNames(held);
                if (entries == null) throw unavailable();
                return entries;
              },
              DirectoryStream::close,
              entries -> {
                try {

                  for (Path child : entries) {
                    if (child == null) throw unavailable();
                    require(held.equals(child.getParent()));
                    // Equal nonnull parent admits exactly one relative child; a root-only path is
                    // excluded.
                    require(names.add(held.relativize(child).toString()));
                  }

                } catch (DirectoryIteratorException failure) {
                  throw unavailable();
                }
                return Boolean.TRUE;
              });
          return Set.copyOf(names);
        });
  }

  private static UUID identity(String name, String suffix) throws IOException {
    if (name.length() != 36 + suffix.length() || !name.endsWith(suffix)) throw unavailable();
    try {
      UUID id = UUID.fromString(name.substring(0, 36));
      require(name.equals(id + suffix));
      return id;
    } catch (IllegalArgumentException failure) {
      throw unavailable();
    }
  }

  private static Graph graph(
      Map<UUID, BatchRun> runs,
      Map<UUID, MaintenanceActivation> begins,
      Map<UUID, MaintenanceCompletion> done,
      Optional<MaintenanceActivation> active)
      throws StorageIoException {
    Set<UUID> pending = new HashSet<>(runs.keySet());
    Set<UUID> unfinished = new HashSet<>();
    for (var begin : begins.values()) {
      require(begin.run().equals(runs.get(begin.run().id())));
      pending.remove(begin.run().id());
      if (!done.containsKey(begin.id())) {
        require(unfinished.isEmpty());
        unfinished.add(begin.run().id());
      }
    }
    pending.addAll(unfinished);
    require(pending.size() <= 1);
    for (var completion : done.values())
      require(completion.activation().equals(begins.get(completion.activation().id())));
    if (active.isPresent()) {
      MaintenanceActivation activation = active.orElseThrow();
      require(activation.equals(begins.get(activation.id())));
      require(pending.isEmpty() || pending.contains(activation.run().id()));
      if (done.containsKey(activation.id())) require(unfinished.isEmpty());
    }
    return new Graph(
        Map.copyOf(runs),
        Map.copyOf(begins),
        Map.copyOf(done),
        active,
        pending.stream().findFirst());
  }

  @FunctionalInterface
  private interface Mutation {
    void execute() throws IOException;
  }

  private static List<MaintenanceCompletion> ordered(Map<UUID, MaintenanceCompletion> plans) {
    return plans.values().stream()
        .sorted(Comparator.comparing(value -> value.activation().id().toString()))
        .toList();
  }

  private record Inventory(
      Map<UUID, BatchRun> runs,
      Map<UUID, MaintenanceActivation> begins,
      Map<UUID, MaintenanceCompletion> done,
      Optional<MaintenanceActivation> active,
      Map<UUID, MaintenanceCompletion> plans,
      Optional<MaintenanceRetirement> marker) {
    Inventory {
      runs = Map.copyOf(runs);
      begins = Map.copyOf(begins);
      done = Map.copyOf(done);
      plans = Map.copyOf(plans);
    }

    Optional<BatchRun> target() {
      if (marker.isPresent()) return Optional.of(marker.orElseThrow().run());
      return plans.values().stream().findFirst().map(value -> value.activation().run());
    }

    Inventory withPlans(Map<UUID, MaintenanceCompletion> values) {
      return new Inventory(runs, begins, done, active, values, marker);
    }

    Inventory withMarker(Optional<MaintenanceRetirement> value) {
      return new Inventory(runs, begins, done, active, plans, value);
    }

    Inventory withOriginals(
        Map<UUID, BatchRun> newRuns,
        Map<UUID, MaintenanceActivation> newBegins,
        Map<UUID, MaintenanceCompletion> newDone) {
      return new Inventory(newRuns, newBegins, newDone, active, plans, marker);
    }
  }

  private record CapturedFile(OwnedTransferDirectory root, String name, Snapshot snapshot) {}

  private record Graph(
      Map<UUID, BatchRun> runs,
      Map<UUID, MaintenanceActivation> begins,
      Map<UUID, MaintenanceCompletion> done,
      Optional<MaintenanceActivation> active,
      Optional<UUID> pending) {}

  static final class NioIo implements Io {
    private final InspectorEnvironmentPublisher.NioIo files =
        new InspectorEnvironmentPublisher.NioIo();

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return files.attributes(held);
    }

    @Override
    public String filesystem(Path held) throws IOException {
      return files.filesystem(held);
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      return files.open(held);
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path held) throws IOException {
      return files.openWriter(held);
    }

    @Override
    public DirectoryStream<Path> openNames(Path held) throws IOException {
      return Files.newDirectoryStream(held);
    }
  }
}
