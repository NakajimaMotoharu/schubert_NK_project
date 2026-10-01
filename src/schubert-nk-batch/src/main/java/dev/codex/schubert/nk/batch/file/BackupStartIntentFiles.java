package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;
import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.unavailable;

import dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.Snapshot;
import dev.codex.schubert.nk.batch.platform.BackupUnitStartClient.Target;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Same-boot fail-closed marker around the fixed Backup start request. This is neither a worker
 * receipt nor authority to retire the marker: the enclosing parent must still own M/A, the request,
 * original and full Unit termination. An uncertain creation never proceeds to systemctl, and an
 * uncertain start never clears this marker. NK-OPS-001/BAK-001; UI251/SS341§5-6/343§6.15;
 * SSC105/106; PG355/PT-OPS-BFENCE001 onward.
 */
@NullMarked
public final class BackupStartIntentFiles implements AutoCloseable {
  private static final String NAME = "backup-start.intent";

  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  /** Same open root and inode only; not a proof that the child or archive succeeded. */
  public static final class Intent {
    private final BackupStartIntentFiles owner;
    private final Snapshot marker;

    private Intent(BackupStartIntentFiles owner, Snapshot marker) {
      this.owner = owner;
      this.marker = marker;
    }
  }

  private final OwnedTransferDirectory root;
  private final InodeSecurityCalls security;
  private final EnvironmentInodePolicy policy;
  private final Gate gate;
  private final Object lock = new Object();
  private boolean begun;
  private final String name;

  public static BackupStartIntentFiles create(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    return create(context, expected, Target.BACKUP);
  }

  public static BackupStartIntentFiles create(
      RootStartupContext context, RootStartupContext.Snapshot expected, Target target)
      throws IOException {
    Objects.requireNonNull(context, "Morning root context");
    Objects.requireNonNull(expected, "Morning root snapshot");
    Objects.requireNonNull(target, "closed phase");
    if (!target.ownedBy(expected.service())) throw unavailable();
    context.recheck(expected);
    var root =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of(target.requestDirectory()));
    return new BackupStartIntentFiles(
        root,
        LinuxInodeSecurity.create(),
        new InspectorEnvironmentPublisher.NioIo(),
        () -> context.recheck(expected),
        target);
  }

  /** SSC136: the same strict marker primitive, fixed publication namespace, not a Unit selector. */
  @edu.umd.cs.findbugs.annotations.SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = edu.umd.cs.findbugs.annotations.SuppressMatchType.EXACT,
      justification =
          "SS343 SSC136 fixes the root-only publication intent namespace; no configurable path")
  public static BackupStartIntentFiles createPublication(
      RootStartupContext context, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(context, "Morning publication context");
    Objects.requireNonNull(expected, "Morning publication identity");
    require(expected.service() == RootStartupContext.Service.MORNING);
    context.recheck(expected);
    var root =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
    return new BackupStartIntentFiles(
        root,
        LinuxInodeSecurity.create(),
        new InspectorEnvironmentPublisher.NioIo(),
        () -> context.recheck(expected),
        "permit-start.intent");
  }

  BackupStartIntentFiles(OwnedTransferDirectory root, InodeSecurityCalls security, Gate gate) {
    this(root, security, new InspectorEnvironmentPublisher.NioIo(), gate);
  }

  BackupStartIntentFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      EnvironmentInodePolicy.Source source,
      Gate gate) {
    this(root, security, source, gate, Target.BACKUP);
  }

  BackupStartIntentFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      EnvironmentInodePolicy.Source source,
      Gate gate,
      Target target) {
    this(root, security, source, gate, Objects.requireNonNull(target, "closed phase").marker());
  }

  // Package-only inode/fault port; the public native factory still fixes its one marker name.
  BackupStartIntentFiles(
      OwnedTransferDirectory root,
      InodeSecurityCalls security,
      EnvironmentInodePolicy.Source source,
      Gate gate,
      String name) {
    this.root = Objects.requireNonNull(root, "fixed Backup request root");
    this.security = Objects.requireNonNull(security, "inode security");
    this.policy =
        new EnvironmentInodePolicy(security, Objects.requireNonNull(source, "inode source"));
    this.gate = Objects.requireNonNull(gate, "Morning root recheck");
    this.name = Objects.requireNonNull(name, "fixed marker");
  }

  /** Must run after M acquisition, before any new original, stop, or Backup start. */
  public void requireClear() throws IOException {
    synchronized (lock) {
      gate.verify();
      Snapshot directory = directory();
      try {
        root.atExistingEntryHandle(name, held -> file(held, directory));
      } catch (StorageIoException missing) {
        if (missing.reason() != StorageIoException.Reason.MISSING) throw unavailable();
        require(directory.sameIdentity(directory()));
        gate.verify();
        return;
      }
      throw unavailable();
    }
  }

  /** Durable within the current boot before the very first start-client call. Never rolls back. */
  public Intent begin() throws IOException {
    synchronized (lock) {
      requireClear();
      Snapshot directory = directory();
      root.atDirectory(
          held -> {
            Path marker = held.resolve(name);
            try (FileChannel channel =
                FileChannel.open(
                    marker,
                    Set.of(
                        StandardOpenOption.CREATE_NEW,
                        StandardOpenOption.WRITE,
                        LinkOption.NOFOLLOW_LINKS),
                    PosixFilePermissions.asFileAttribute(
                        PosixFilePermissions.fromString("rw-------")))) {
              channel.force(true);
            } catch (FileAlreadyExistsException collision) {
              throw unavailable();
            }
            return true;
          });
      // Failure from here onward leaves the marker behind and forbids a start request.
      root.sync();
      Snapshot created = root.atExistingEntryHandle(name, held -> file(held, directory));
      require(directory.sameIdentity(directory()));
      gate.verify();
      begun = true;
      return new Intent(this, created);
    }
  }

  /**
   * Only the enclosing verified parent may call this after fresh worker receipt, explicit stop,
   * whole-Unit termination and same-original verification. Failure is never repaired in place.
   */
  public void retire(Intent intent) throws IOException {
    synchronized (lock) {
      Objects.requireNonNull(intent, "same-start marker");
      if (!begun || intent.owner != this) throw unavailable();
      gate.verify();
      Snapshot directory = directory();
      Snapshot actual = root.atExistingEntryHandle(name, held -> file(held, directory));
      require(intent.marker.equals(actual));
      root.unlinkEntry(name);
      require(directory.sameIdentity(directory()));
      begun = false;
      requireClear();
    }
  }

  /** Same owner token; re-read before any publication boundary. SSC136. */
  public void requirePresent(Intent intent) throws IOException {
    synchronized (lock) {
      Objects.requireNonNull(intent, "same publication marker");
      require(begun && intent.owner == this);
      gate.verify();
      var directory = directory();
      require(intent.marker.equals(root.atExistingEntryHandle(name, p -> file(p, directory))));
      require(directory.sameIdentity(directory()));
      gate.verify();
    }
  }

  /** Recovery only: preserve a strict existing quarantine, or create one. Never retire/reuse it. */
  void quarantinePublication() throws IOException {
    synchronized (lock) {
      require(name.equals("permit-start.intent"));
      gate.verify();
      var directory = directory();
      boolean[] entered = {false};
      try {
        root.atExistingEntryHandle(
            name,
            p -> {
              entered[0] = true;
              return file(p, directory);
            });
        require(directory.sameIdentity(directory()));
        gate.verify();
      } catch (StorageIoException missing) {
        require(!entered[0] && missing.reason() == StorageIoException.Reason.MISSING);
        begin();
      }
    }
  }

  private Snapshot directory() throws StorageIoException {
    require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
    return root.atDirectory(held -> policy.snapshot(held, true, true, 0, 0, 0));
  }

  private Snapshot file(Path held, Snapshot directory) throws IOException {
    require(!Thread.currentThread().isInterrupted() && security.effectiveUid() == 0);
    Snapshot result = policy.snapshot(held, true, false, 0, 0, 0);
    require(result.metadata().device() == directory.metadata().device());
    return result;
  }

  @Override
  public void close() throws IOException {
    synchronized (lock) {
      root.close();
    }
  }
}
