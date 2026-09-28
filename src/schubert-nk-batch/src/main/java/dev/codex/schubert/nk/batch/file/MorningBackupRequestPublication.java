package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.Closeable;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Root parent's fixed backup-request publication inside continuous M/A/original/DB ownership. Uses
 * the existing new-only, root0600, fsync/readback file contract; never repairs an old request or
 * treats publication as worker/backup success. NK-OPS-001; OPS009/BAK001/UI251/SS341§6.2,
 * 343§6.15/SSC092/094/104; PG348/PT-OPS-MBPUB001-006.
 */
@NullMarked
final class MorningBackupRequestPublication implements MorningBackupPreparation.Publisher {
  @FunctionalInterface
  interface Gate {
    void verify() throws IOException;
  }

  interface Owner extends Closeable {
    void prepare(BackupWorkerRequest request, UUID part) throws IOException;
  }

  @FunctionalInterface
  interface Open {
    Owner open() throws IOException;
  }

  private final Gate gate;
  private final Open open;

  MorningBackupRequestPublication(Gate gate, Open open) {
    this.gate = Objects.requireNonNull(gate, "Morning root recheck");
    this.open = Objects.requireNonNull(open, "fixed backup request root");
  }

  static MorningBackupRequestPublication create(
      RootStartupContext root, RootStartupContext.Snapshot expected) throws IOException {
    Objects.requireNonNull(root, "Morning root context");
    Objects.requireNonNull(expected, "Morning root identity");
    if (expected.service() != RootStartupContext.Service.MORNING) throw unavailable();
    root.recheck(expected);
    return new MorningBackupRequestPublication(
        () -> root.recheck(expected), MorningBackupRequestPublication::openNative);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 6.15 fixes the root-only backup request tmpfs namespace")
  static Owner openNative() throws IOException {
    OwnedTransferDirectory directory =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/backup-request"));
    BackupWorkerRequestFiles files =
        new BackupWorkerRequestFiles(directory, LinuxInodeSecurity.create());
    return new Owner() {
      @Override
      public void prepare(BackupWorkerRequest request, UUID part) throws IOException {
        files.prepare(request, part);
      }

      @Override
      public void close() throws IOException {
        directory.close();
      }
    };
  }

  @Override
  public void publish(BackupWorkerRequest request, UUID part) throws IOException {
    Objects.requireNonNull(request, "nonsecret backup request");
    Objects.requireNonNull(part, "new-only request part");
    try {
      check();
      Owner owner = Objects.requireNonNull(open.open(), "owned request root");
      ResourceScope.use(
          owner::close,
          () -> {
            check();
            owner.prepare(request, part);
            check();
            return Boolean.TRUE;
          });
      check();
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  private void check() throws IOException {
    if (Thread.currentThread().isInterrupted()) throw unavailable();
    gate.verify();
  }

  private static IOException unavailable() {
    return new IOException("Morning backup request unavailable");
  }
}
