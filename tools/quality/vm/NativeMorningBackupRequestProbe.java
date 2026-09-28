package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.util.UUID;

/**
 * PGPT-only native fixed-request IO probe. It does not authenticate the Morning Unit, hold M/A,
 * start a worker or assert backup success. Never place this class in a Production JAR.
 */
public final class NativeMorningBackupRequestProbe {
  private static final Path ROOT = Path.of("/run/schubert-nk/backup-request");
  private static final BackupWorkerRequest REQUEST =
      new BackupWorkerRequest(
          UUID.fromString("11111111-1111-4111-8111-111111111111"),
          Instant.parse("2026-09-28T01:00:01.123456Z"));
  private static final UUID PART = UUID.fromString("33333333-3333-4333-8333-333333333333");

  private NativeMorningBackupRequestProbe() {}

  public static void main(String[] arguments) throws IOException {
    if (arguments.length != 1 || !(arguments[0].equals("missing") || arguments[0].equals("present")))
      throw new IOException("probe mode refused");
    if (LinuxInodeSecurity.create().effectiveUid() != 0)
      throw new IOException("probe root actor unavailable");
    var publisher = new MorningBackupRequestPublication(
        () -> {
          if (LinuxInodeSecurity.create().effectiveUid() != 0)
            throw new IOException("probe root actor unavailable");
        },
        MorningBackupRequestPublication::openNative);
    if (arguments[0].equals("missing")) {
      try {
        publisher.publish(REQUEST, PART);
      } catch (IOException expected) {
        if (!"Morning backup request unavailable".equals(expected.getMessage())) throw expected;
        System.out.println("MISSING_REFUSED");
        return;
      }
      throw new IOException("missing root accepted");
    }
    publisher.publish(REQUEST, PART);
    var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), ROOT);
    ResourceScope.use(
        directory::close,
        () -> {
          var files = new BackupWorkerRequestFiles(directory, LinuxInodeSecurity.create());
          if (!REQUEST.equals(files.read())) throw new IOException("request readback mismatch");
          files.retire(REQUEST);
          System.out.println("PUBLICATION_READBACK_RETIRED");
          return Boolean.TRUE;
        });
  }
}
