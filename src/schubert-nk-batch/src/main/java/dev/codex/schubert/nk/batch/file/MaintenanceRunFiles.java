package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
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
@NullMarked
public final class MaintenanceRunFiles {
  private final Object scopeLock = new Object();
  private final Path varPath;
  private final DirectoryCalls directories;
  private final InodeSecurityCalls security;
  private final Io io;
  private final Supplier<UUID> parts;
  private final EnvironmentInodePolicy policy;

  @FunctionalInterface
  public interface Operation<T> {
    T execute(Session session) throws IOException;
  }

  @FunctionalInterface
  private interface Work<T> {
    T execute() throws IOException;
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
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "UI251/SS343 require fixed Linux /var; PG-D-158/PT-BAT-081")
  public static MaintenanceRunFiles create() {
    return new MaintenanceRunFiles(
        Path.of("/var"),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new NioIo(),
        UUID::randomUUID);
  }

  MaintenanceRunFiles(
      Path varPath,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      Io io,
      Supplier<UUID> parts) {
    this.varPath = Objects.requireNonNull(varPath, "durable ancestor");
    this.directories = Objects.requireNonNull(directories, "directory operations");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "record IO");
    this.parts = Objects.requireNonNull(parts, "part identities");
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
        try (var var = OwnedTransferDirectory.open(directories, varPath);
            var lib = var.openExistingChild("lib");
            var app = lib.openExistingChild("schubert-nk");
            var maintenance = app.openExistingChild("maintenance");
            var runs = maintenance.openExistingChild("runs");
            var attempts = maintenance.openExistingChild("attempts")) {
          var roots = List.of(var, lib, app, maintenance, runs, attempts);
          var session = new Session(roots, capture(roots));
          try {
            session.verifyNamespace();
            result = Objects.requireNonNull(operation.execute(session), "run operation result");
            session.finish();
          } finally {
            session.invalidate();
          }
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
              .atDirectory(p -> shared ? policy.durableAncestor(p) : policy.durable(p, true, 0)));
    }
    require(values.get(3).metadata().device() == values.get(4).metadata().device());
    require(values.get(3).metadata().device() == values.get(5).metadata().device());
    return List.copyOf(values);
  }

  /** Scope-bound serialized operations, never an OS lock or completed-parent certificate. */
  public final class Session {
    private final Object stateLock = new Object();
    private final List<OwnedTransferDirectory> roots;
    private final List<Snapshot> expectedRoots;
    private final DurableRecordFiles maintenanceFiles, runFiles, attemptFiles;
    private boolean open = true;

    private Session(List<OwnedTransferDirectory> roots, List<Snapshot> expectedRoots) {
      this.roots = List.copyOf(roots);
      this.expectedRoots = List.copyOf(expectedRoots);
      maintenanceFiles = new DurableRecordFiles(roots.get(3), security, io);
      runFiles = new DurableRecordFiles(roots.get(4), security, io);
      attemptFiles = new DurableRecordFiles(roots.get(5), security, io);
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
            publish(runFiles, run.id() + ".run", MaintenanceRecords.anchor(run));
            publish(
                attemptFiles, activationId + ".begin", MaintenanceRecords.activation(activation));
            publish(maintenanceFiles, "active", MaintenanceRecords.activation(activation));
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
                    attemptFiles, active.id() + ".done", MaintenanceRecords.completion(previous));
              publish(maintenanceFiles, "active", MaintenanceRecords.activation(active));
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
            publish(maintenanceFiles, "active", MaintenanceRecords.activation(activation));
            require(
                graph(before.runs(), begins, before.done(), Optional.of(activation))
                    .equals(scan()));
            return new MaintenanceRunState(activation, Optional.empty());
          });
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
              publish(maintenanceFiles, "active", MaintenanceRecords.activation(activation));
            publish(
                attemptFiles, activation.id() + ".done", MaintenanceRecords.completion(completion));
            maintenanceFiles.remove("active", MaintenanceRecords.activation(activation));
            verifyNamespace();
            var done = new HashMap<>(before.done());
            done.put(activation.id(), completion);
            require(graph(before.runs(), before.begins(), done, Optional.empty()).equals(scan()));
            return completion;
          });
    }

    /** Re-establish durability of the selected identity before publishing or reusing its state. */
    private void sealIdentity(MaintenanceActivation activation) throws IOException {
      publish(
          runFiles, activation.run().id() + ".run", MaintenanceRecords.anchor(activation.run()));
      publish(attemptFiles, activation.id() + ".begin", MaintenanceRecords.activation(activation));
    }

    private <T> T perform(Work<T> operation) throws StorageIoException {
      synchronized (stateLock) {
        require(open);
        begin();
        try {
          T value = operation.execute();
          require(!Thread.currentThread().isInterrupted());
          return value;
        } catch (IOException failure) {
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
          rootNames.equals(Set.of("runs", "attempts"))
              || rootNames.equals(Set.of("runs", "attempts", "active")));
      Map<UUID, BatchRun> runs = new HashMap<>();
      Map<UUID, MaintenanceActivation> begins = new HashMap<>();
      Map<UUID, MaintenanceCompletion> done = new HashMap<>();
      List<CapturedFile> files = new ArrayList<>();
      for (String name : names(roots.get(4))) {
        UUID id = identity(name, ".run");
        BatchRun run = read(4, runFiles, name, MaintenanceRecords::readAnchor, files);
        // DurableRecordFiles already binds the canonical filename to the decoded record ID.
        runs.put(id, run);
      }
      for (String name : names(roots.get(5))) {
        if (name.endsWith(".begin")) {
          UUID id = identity(name, ".begin");
          MaintenanceActivation activation =
              read(5, attemptFiles, name, MaintenanceRecords::readActivation, files);
          begins.put(id, activation);
        } else {
          UUID id = identity(name, ".done");
          MaintenanceCompletion completion =
              read(5, attemptFiles, name, MaintenanceRecords::readCompletion, files);
          done.put(id, completion);
        }
      }
      Optional<MaintenanceActivation> active =
          rootNames.contains("active")
              ? Optional.of(
                  read(3, maintenanceFiles, "active", MaintenanceRecords::readActivation, files))
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
      try (var var = OwnedTransferDirectory.open(directories, varPath);
          var lib = var.openExistingChild("lib");
          var app = lib.openExistingChild("schubert-nk");
          var maintenance = app.openExistingChild("maintenance");
          var runs = maintenance.openExistingChild("runs");
          var attempts = maintenance.openExistingChild("attempts")) {
        List<Snapshot> actual = capture(List.of(var, lib, app, maintenance, runs, attempts));
        for (int index = 0; index < expectedRoots.size(); index++)
          require(expectedRoots.get(index).sameIdentity(actual.get(index)));
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
          try (var entries = io.openNames(held)) {
            if (entries == null) throw unavailable();
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
