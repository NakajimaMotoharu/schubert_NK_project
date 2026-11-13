package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.LinuxMonotonicClock;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Pending original + actual live parent only; ticket/full preflight/exec remain additional gates.
 */
@NullMarked
final class RootStartupPending {
  /** SSC307/PT-ROOTWAIT-SSC307-001..010: internal observations, never a native grant. */
  interface WaitIo {
    long nowNanos() throws IOException;

    void requireOwner() throws IOException;

    Optional<StartupLaunchRecord> readLaunch() throws IOException;

    void pause() throws InterruptedException;
  }

  /** SSC307/PT-ROOTWAIT-SSC307-011..012: missing launch only, not missing intent or close. */
  @FunctionalInterface
  interface LaunchRead {
    StartupLaunchRecord read() throws IOException;
  }

  private RootStartupPending() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC137 fixed current epoch launch, no arbitrary request file")
  static void awaitLaunch(
      RootStartupContext root,
      RootStartupContext.Snapshot self,
      RootCurrentPermitPreflight.Observed issued,
      MaintenanceOwnerFrame owner)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(self);
    Objects.requireNonNull(issued);
    Objects.requireNonNull(owner);
    long deadline = root.serviceRootDeadline(self, owner.deadlineNanos());
    var clock = LinuxMonotonicClock.create();
    var service =
        self.service() == RootStartupContext.Service.API
            ? ServiceConfigFiles.Service.API
            : ServiceConfigFiles.Service.WEB;
    Path startup = Path.of("/run/schubert-nk/startup");
    awaitLaunch(
        self,
        deadline,
        new WaitIo() {
          @Override
          public long nowNanos() throws IOException {
            return clock.nowNanos();
          }

          @Override
          public void requireOwner() throws IOException {
            require(owner.equals(observe(root, self, issued)));
          }

          @Override
          public Optional<StartupLaunchRecord> readLaunch() throws IOException {
            return ResourceScope.acquire(
                () -> OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), startup),
                OwnedTransferDirectory::close,
                directory -> {
                  var files =
                      new StartupLaunchFiles(
                          directory, LinuxInodeSecurity.create(), issued.current());
                  files.requireStartIntent(service);
                  return RootStartupPending.readLaunch(() -> files.readLaunch(service));
                });
          }

          @Override
          public void pause() throws InterruptedException {
            Thread.sleep(25);
          }
        });
  }

  /** Same absolute deadline and original observation order; caller retains all native owners. */
  static void awaitLaunch(RootStartupContext.Snapshot self, long deadline, WaitIo io)
      throws IOException {
    Objects.requireNonNull(self);
    Objects.requireNonNull(io);
    while (true) {
      require(io.nowNanos() < deadline);
      io.requireOwner();
      Optional<StartupLaunchRecord> launch = Objects.requireNonNull(io.readLaunch());
      if (launch.isPresent()) {
        verifySelf(launch.orElseThrow(), self);
        io.requireOwner();
        require(io.nowNanos() < deadline);
        return;
      }
      try {
        io.pause();
      } catch (InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        throw new IOException("root launch unavailable");
      }
    }
  }

  static Optional<StartupLaunchRecord> readLaunch(LaunchRead read) throws IOException {
    Objects.requireNonNull(read);
    try {
      return Optional.of(Objects.requireNonNull(read.read()));
    } catch (StorageIoException absent) {
      if (absent.reason() != StorageIoException.Reason.MISSING) throw absent;
      return Optional.empty();
    }
  }

  static void verifySelf(StartupLaunchRecord launch, RootStartupContext.Snapshot self)
      throws IOException {
    Objects.requireNonNull(launch);
    Objects.requireNonNull(self);
    require(
        (self.service() == RootStartupContext.Service.API
                || self.service() == RootStartupContext.Service.WEB)
            && launch.service().name().equals(self.service().name())
            && launch.boot().toString().equals(self.boot())
            && launch.child().invocation().equals(self.invocation())
            && launch.child().pid() == self.pid()
            && launch.child().startTicks() == self.startTicks());
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SSC137 fixed startup root, actual issued epoch only")
  static MaintenanceOwnerFrame observe(
      RootStartupContext root,
      RootStartupContext.Snapshot self,
      RootCurrentPermitPreflight.Observed issued)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(self);
    Objects.requireNonNull(issued);
    require(
        self.service() == RootStartupContext.Service.API
            || self.service() == RootStartupContext.Service.WEB);
    root.recheck(self);
    Path startup = Path.of("/run/schubert-nk/startup");
    var owner =
        ResourceScope.acquire(
            () -> OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), startup),
            OwnedTransferDirectory::close,
            directory -> {
              var current = new StartupPermitFiles(directory, LinuxInodeSecurity.create());
              require(
                  issued.current().equals(current.current())
                      && issued.permit().equals(current.readIssued()));
              var value =
                  new StartupLaunchFiles(directory, LinuxInodeSecurity.create(), issued.current())
                      .readOwner();
              value.parentsGuard().check();
              require(
                  issued.current().equals(current.current())
                      && issued.permit().equals(current.readIssued()));
              return value;
            });
    var original = MaintenanceRunFiles.observeStartup(root, self, issued.current().activation());
    // Completed restart needs a true normal Morning receipt; until connected it fails closed.
    require(original.completed().isEmpty());
    owner.parentsGuard().check();
    root.recheck(self);
    return owner;
  }
}
