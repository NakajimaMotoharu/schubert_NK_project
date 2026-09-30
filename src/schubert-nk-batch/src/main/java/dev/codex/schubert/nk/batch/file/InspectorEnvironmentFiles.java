package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.platform.ConfigurationGroupResolver;
import dev.codex.schubert.nk.batch.platform.InspectorStaticEnvironment;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed namespace and environment resource lifetime. NK-OPS-001; OPS-009/UI251/SS343 6.12;
 * SSC-049/PG-D-155; PT-OPS-NS-001..008. Caller holds OS flock and independently admits backup,
 * authoritative run, stable root administration and the terminal child. The callback must await its
 * child's terminal state before returning and never mutate/export these filesystem resources.
 */
// PG172/SSC063, BUG195/YKT154; resource precedence and PT evidence/01_PT/017/050.
@NullMarked
public final class InspectorEnvironmentFiles {
  private static final String CONFIG = "schubert-nk",
      MAINTENANCE = "maintenance",
      NAME = "inbox-inspector.env";
  private final Object lifecycleLock = new Object();
  private final Path etcPath, runPath;
  private final DirectoryCalls directories;
  private final InodeSecurityCalls security;
  private final GroupLookup groups;
  private final InspectorEnvironmentPublisher.Io io;
  private final EnvironmentInodePolicy policy;

  @FunctionalInterface
  public interface Operation<T> {
    T execute() throws IOException;
  }

  @FunctionalInterface
  public interface Retirement {
    void retire() throws IOException;
  }

  @FunctionalInterface
  public interface OwnedOperation<T> {
    T execute(Retirement retirement) throws IOException;
  }

  @FunctionalInterface
  interface GroupLookup {
    long resolve() throws IOException;
  }

  // Same reviewed portability rationale as BUG-142/YKT-112; owner NK-OPS-001.
  // Re-review at PG gate or any OS/path/SS change. No coverage, null or security exclusion.
  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "UI251/SS343 require fixed Linux /etc and /run; PG-D-155/PT-OPS-NS-008")
  public static InspectorEnvironmentFiles create() {
    return new InspectorEnvironmentFiles(
        Path.of("/etc"),
        Path.of("/run"),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new ConfigurationGroupResolver()::resolve,
        new InspectorEnvironmentPublisher.NioIo());
  }

  InspectorEnvironmentFiles(
      Path etcPath,
      Path runPath,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      GroupLookup groups,
      InspectorEnvironmentPublisher.Io io) {
    this.etcPath = Objects.requireNonNull(etcPath, "configuration ancestor");
    this.runPath = Objects.requireNonNull(runPath, "runtime ancestor");
    this.directories = Objects.requireNonNull(directories, "directory operations");
    this.security = Objects.requireNonNull(security, "inode security");
    this.groups = Objects.requireNonNull(groups, "trusted group lookup");
    this.io = Objects.requireNonNull(io, "environment IO");
    for (Path path : List.of(etcPath, runPath)) {
      if (!path.isAbsolute() || path.getNameCount() == 0 || !path.equals(path.normalize()))
        throw new IllegalArgumentException("invalid environment ancestor");
    }
    policy = new EnvironmentInodePolicy(security, io);
  }

  /** Publish, execute once, revalidate and retire only on normal nonnull callback completion. */
  public <T> T execute(BatchRun run, Operation<T> operation) throws StorageIoException {
    Objects.requireNonNull(operation, "environment operation");
    return execute(
        run,
        retirement -> {
          var result = Objects.requireNonNull(operation.execute(), "environment operation result");
          retirement.retire();
          return result;
        },
        false);
  }

  /** Callback-scoped one-shot retirement: after DB reacquire/readback, BEFORE intent removal. */
  public <T> T executeOwned(BatchRun run, OwnedOperation<T> operation) throws StorageIoException {
    return execute(run, operation, true);
  }

  private <T> T execute(BatchRun run, OwnedOperation<T> operation, boolean freshOnly)
      throws StorageIoException {
    Objects.requireNonNull(run, "run");
    Objects.requireNonNull(operation, "environment operation");
    synchronized (lifecycleLock) {
      require(!Thread.currentThread().isInterrupted());
      require(security.effectiveUid() == 0);
      byte[][] reference = {new byte[0]};
      try {
        long group = groups.resolve();
        require(group >= 1 && group <= 0xffff_ffffL);
        T result;
        {
          var etc = OwnedTransferDirectory.open(directories, etcPath);
          result =
              ResourceScope.use(
                  etc::close,
                  () -> {
                    var config = etc.openExistingChild(CONFIG);
                    return ResourceScope.use(
                        config::close,
                        () -> {
                          var runtime = OwnedTransferDirectory.open(directories, runPath);
                          return ResourceScope.use(
                              runtime::close,
                              () -> {
                                var app = runtime.openExistingChild(CONFIG);
                                return ResourceScope.use(
                                    app::close,
                                    () -> {
                                      var maintenance = app.openExistingChild(MAINTENANCE);
                                      return ResourceScope.use(
                                          maintenance::close,
                                          () -> {
                                            var roots =
                                                new Roots(etc, config, runtime, app, maintenance);
                                            List<Snapshot> expectedRoots = capture(roots, group);
                                            Snapshot expectedFile =
                                                staticFile(roots, group, expectedRoots.get(1));
                                            var staticReader =
                                                new InspectorEnvironmentReader(
                                                    config, security, group, io);
                                            reference[0] = staticReader.readStatic();
                                            require(
                                                expectedFile.equals(
                                                    staticFile(
                                                        roots, group, expectedRoots.get(1))));
                                            var publisher =
                                                new InspectorEnvironmentPublisher(
                                                    maintenance, security, io);
                                            if (freshOnly) publisher.prepareNew(run);
                                            else publisher.prepare(run);
                                            verify(
                                                roots,
                                                group,
                                                expectedRoots,
                                                expectedFile,
                                                reference[0],
                                                run);
                                            boolean[] active = {true}, retired = {false};
                                            Thread ownerThread = Thread.currentThread();
                                            try {
                                              T completed =
                                                  Objects.requireNonNull(
                                                      operation.execute(
                                                          () -> {
                                                            require(
                                                                Thread.currentThread()
                                                                        == ownerThread
                                                                    && active[0]
                                                                    && !retired[0]);
                                                            verify(
                                                                roots,
                                                                group,
                                                                expectedRoots,
                                                                expectedFile,
                                                                reference[0],
                                                                run);
                                                            publisher.retire(run);
                                                            retired[0] = true;
                                                          }),
                                                      "environment operation result");
                                              require(retired[0]);
                                              return completed;
                                            } finally {
                                              active[0] = false;
                                            }
                                          });
                                    });
                              });
                        });
                  });
        }
        require(!Thread.currentThread().isInterrupted());
        return result;
      } catch (IOException failure) {
        // All root/entry/channel scopes have ended, even when close compounded a callback failure.
        throw unavailable();
      } finally {
        Arrays.fill(reference[0], (byte) 0);
      }
    }
  }

  private List<Snapshot> capture(Roots roots, long group) throws StorageIoException {
    Snapshot etc = roots.etc().atDirectory(p -> policy.ancestor(p, false));
    Snapshot config =
        roots.config().atDirectory(p -> policy.snapshot(p, false, true, 65848, 0, group));
    Snapshot runtime = roots.runtime().atDirectory(p -> policy.ancestor(p, true));
    Snapshot app = roots.app().atDirectory(p -> policy.ancestor(p, true));
    Snapshot maintenance =
        roots.maintenance().atDirectory(p -> policy.snapshot(p, true, true, 110, 0, 0));
    require(etc.metadata().device() == config.metadata().device());
    require(runtime.metadata().device() == app.metadata().device());
    require(app.metadata().device() == maintenance.metadata().device());
    return List.of(etc, config, runtime, app, maintenance);
  }

  private Snapshot staticFile(Roots roots, long group, Snapshot config) throws StorageIoException {
    return roots
        .config()
        .atExistingEntryHandle(
            NAME,
            p -> {
              Snapshot result =
                  policy.snapshot(
                      p, false, false, InspectorStaticEnvironment.MAXIMUM_BYTES, 1, group);
              require(result.metadata().device() == config.metadata().device());
              return result;
            });
  }

  private void verify(
      Roots roots,
      long group,
      List<Snapshot> expectedRoots,
      Snapshot expectedFile,
      byte[] reference,
      BatchRun run)
      throws IOException {
    require(groups.resolve() == group);
    {
      var etc = OwnedTransferDirectory.open(directories, etcPath);
      ResourceScope.use(
          etc::close,
          () -> {
            var config = etc.openExistingChild(CONFIG);
            return ResourceScope.use(
                config::close,
                () -> {
                  var runtime = OwnedTransferDirectory.open(directories, runPath);
                  return ResourceScope.use(
                      runtime::close,
                      () -> {
                        var app = runtime.openExistingChild(CONFIG);
                        return ResourceScope.use(
                            app::close,
                            () -> {
                              var maintenance = app.openExistingChild(MAINTENANCE);
                              return ResourceScope.use(
                                  maintenance::close,
                                  () -> {
                                    List<Snapshot> actual =
                                        capture(
                                            new Roots(etc, config, runtime, app, maintenance),
                                            group);
                                    for (int index = 0; index < expectedRoots.size(); index++)
                                      require(
                                          expectedRoots.get(index).sameIdentity(actual.get(index)));

                                    return Boolean.TRUE;
                                  });
                            });
                      });
                });
          });
    }
    byte[] actual =
        new InspectorEnvironmentReader(roots.config(), security, group, io).readStatic();
    try {
      require(Arrays.equals(reference, actual));
    } finally {
      Arrays.fill(actual, (byte) 0);
    }
    require(expectedFile.equals(staticFile(roots, group, expectedRoots.get(1))));
    byte[] runtime =
        new InspectorEnvironmentReader(roots.maintenance(), security, group, io).readRun(run);
    Arrays.fill(runtime, (byte) 0);
  }

  private record Roots(
      OwnedTransferDirectory etc,
      OwnedTransferDirectory config,
      OwnedTransferDirectory runtime,
      OwnedTransferDirectory app,
      OwnedTransferDirectory maintenance) {}
}
