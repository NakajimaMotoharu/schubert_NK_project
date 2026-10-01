package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Same-current public correlation, never a lock or live-parent grant. SSC137/PT297. */
@NullMarked
final class StartupLaunchFiles {
  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final InspectorEnvironmentPublisher.Io io;
  private final StartupPermitRecords.Epoch expected;
  private final boolean recovery;

  StartupLaunchFiles(
      OwnedTransferDirectory root, InodeSecurityCalls security, StartupPermitRecords.Epoch expected)
      throws IOException {
    this(root, security, new InspectorEnvironmentPublisher.NioIo(), expected);
  }

  StartupLaunchFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io io,
      StartupPermitRecords.Epoch expected)
      throws IOException {
    this(root, security, io, expected, false);
  }

  StartupLaunchFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io io,
      StartupPermitRecords.Epoch expected,
      boolean recovery)
      throws IOException {
    this.root = Objects.requireNonNull(root);
    this.security = Objects.requireNonNull(security);
    this.io = Objects.requireNonNull(io);
    this.expected = Objects.requireNonNull(expected);
    this.recovery = recovery;
    require(expected.state() == StartupPermitRecords.State.ISSUED);
  }

  void requireNamespace() throws IOException {
    require(security.effectiveUid() == 0 && !Thread.currentThread().isInterrupted());
    var policy = new EnvironmentInodePolicy(security, io);
    var before = root.atDirectory(p -> policy.snapshot(p, true, true, 4096, 0, 0));
    root.atDirectory(
        held -> {
          var names = new HashSet<String>();
          try (var entries = java.nio.file.Files.newDirectoryStream(held)) {
            for (var entry : entries) {
              var leaf = entry.getFileName();
              if (leaf == null) throw new IOException("startup namespace unavailable");
              String name = leaf.toString();
              require(names.add(name));
              if (name.equals("epoch.current")) continue;
              if (recovery && name.equals("permit-start.intent")) continue;
              if (name.equals(expected.epoch() + ".API.start.intent")
                  || name.equals(expected.epoch() + ".WEB.start.intent")) continue;
              require(
                  name.matches(
                      "(?!00000000-0000-0000-0000-000000000000\\.)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\.(permit|owner|API\\.launch|WEB\\.launch)"));
            }
          } catch (java.nio.file.DirectoryIteratorException invalid) {
            throw new IOException("startup namespace unavailable");
          }
          require(names.contains("epoch.current") && names.contains(expected.epoch() + ".permit"));
          return Boolean.TRUE;
        });
    require(before.equals(root.atDirectory(p -> policy.snapshot(p, true, true, 4096, 0, 0))));
  }

  /** Under next M, before DB/original/stop; all old service intents stay quarantined. */
  static void requireNoServiceResidue(OwnedTransferDirectory root, InodeSecurityCalls security)
      throws IOException {
    requireNoServiceResidue(root, security, new InspectorEnvironmentPublisher.NioIo());
  }

  static void requireNoServiceResidue(
      OwnedTransferDirectory root, InodeSecurityCalls security, InspectorEnvironmentPublisher.Io io)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(security);
    var policy = new EnvironmentInodePolicy(security, Objects.requireNonNull(io));
    var before = root.atDirectory(p -> policy.snapshot(p, true, true, 4096, 0, 0));
    root.atDirectory(
        held -> {
          try (var entries = java.nio.file.Files.newDirectoryStream(held)) {
            for (var entry : entries) {
              var leaf = entry.getFileName();
              require(leaf != null);
              String name = Objects.requireNonNull(leaf).toString();
              require(
                  name.equals("epoch.current")
                      || name.matches(
                          "(?!00000000-0000-0000-0000-000000000000\\.)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\.(permit|owner|API\\.launch|WEB\\.launch)"));
            }
          } catch (java.nio.file.DirectoryIteratorException invalid) {
            throw new IOException("startup namespace unavailable");
          }
          return Boolean.TRUE;
        });
    require(before.equals(root.atDirectory(p -> policy.snapshot(p, true, true, 4096, 0, 0))));
  }

  void prepareOwner(MaintenanceOwnerFrame owner, UUID part) throws IOException {
    verifyOwner(owner);
    requireNamespace();
    source(CleanupWorkerRequestFiles.StartupSource.OWNER).prepareStartup(owner.encode(), part);
    require(owner.equals(readOwner()));
  }

  MaintenanceOwnerFrame readOwner() throws IOException {
    requireNamespace();
    byte[] bytes = source(CleanupWorkerRequestFiles.StartupSource.OWNER).readStartup();
    try {
      var owner = MaintenanceOwnerFrame.consume(bytes);
      verifyOwner(owner);
      return owner;
    } catch (IllegalArgumentException invalidClaim) {
      throw new IOException("startup owner unavailable");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  void requireStartIntent(ServiceConfigFiles.Service service) throws IOException {
    Objects.requireNonNull(service);
    requireNamespace();
    var policy = new EnvironmentInodePolicy(security, io);
    var directory = root.atDirectory(p -> policy.snapshot(p, true, true, 4096, 0, 0));
    root.atExistingEntryHandle(
        expected.epoch() + "." + service.name() + ".start.intent",
        held -> {
          var file = policy.snapshot(held, true, false, 0, 0, 0);
          require(file.metadata().device() == directory.metadata().device());
          require(file.equals(policy.snapshot(held, true, false, 0, 0, 0)));
          return Boolean.TRUE;
        });
    require(directory.equals(root.atDirectory(p -> policy.snapshot(p, true, true, 4096, 0, 0))));
  }

  void prepareLaunch(StartupLaunchRecord record, UUID part) throws IOException {
    Objects.requireNonNull(record);
    verifyLaunch(record, readOwner());
    source(profile(record.service())).prepareStartup(record.encode(), part);
    require(record.equals(readLaunch(record.service())));
  }

  StartupLaunchRecord readLaunch(ServiceConfigFiles.Service service) throws IOException {
    Objects.requireNonNull(service);
    var owner = readOwner();
    byte[] bytes = source(profile(service)).readStartup();
    try {
      var record = StartupLaunchRecord.consume(bytes);
      require(record.service() == service);
      verifyLaunch(record, owner);
      require(owner.equals(readOwner()));
      return record;
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private void verifyOwner(MaintenanceOwnerFrame owner) throws IOException {
    Objects.requireNonNull(owner);
    var activation = expected.activation();
    require(
        owner.cleanup().isEmpty()
            && owner.boot().equals(expected.boot())
            && owner.epoch().equals(expected.epoch())
            && owner.run().equals(activation.run().id())
            && owner.cutoff().equals(activation.run().cutoff())
            && owner.activation().equals(activation.id()));
  }

  private void verifyLaunch(StartupLaunchRecord record, MaintenanceOwnerFrame owner)
      throws IOException {
    require(
        record.boot().equals(expected.boot())
            && record.epoch().equals(expected.epoch())
            && record.permitSha256().equals(expected.permitDigest().orElseThrow())
            && record.ownerSha256().equals(StartupLaunchRecord.sha256(owner.encode()))
            && record.child().pid() != owner.morning().pid()
            && !record.child().invocation().equals(owner.morning().invocation()));
  }

  private CleanupWorkerRequestFiles source(CleanupWorkerRequestFiles.StartupSource profile)
      throws IOException {
    return CleanupWorkerRequestFiles.forStartup(root, security, io, expected, profile);
  }

  private static CleanupWorkerRequestFiles.StartupSource profile(
      ServiceConfigFiles.Service service) {
    return switch (service) {
      case API -> CleanupWorkerRequestFiles.StartupSource.API;
      case WEB -> CleanupWorkerRequestFiles.StartupSource.WEB;
    };
  }
}
