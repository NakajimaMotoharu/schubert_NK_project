package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** PGPT-only isolated tmpfs probe; never package into Production or run against its marker root. */
public final class NativeBackupTimeoutResidualProbe {
  private static final Path ROOT = Path.of("/run/schubert-nk/pgpt-374-backup-intent");
  private static final Path INSTANCE = Path.of("/var/lib/cloud/data/instance-id");

  private NativeBackupTimeoutResidualProbe() {}

  public static void main(String[] args) throws Exception {
    var security = LinuxInodeSecurity.create();
    if (args.length != 1
        || security.effectiveUid() != 0
        || !Files.readString(INSTANCE).trim().equals("pgpt-r2-20260927-01"))
      throw new IOException("isolated probe unavailable");
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), ROOT)) {
      var intent =
          new BackupStartIntentFiles(
              directory,
              security,
              () -> {
                if (security.effectiveUid() != 0)
                  throw new IOException("isolated probe unavailable");
              });
      switch (args[0]) {
        case "hold" -> {
          intent.requireClear();
          intent.begin();
          System.out.println("MARKER_PUBLISHED");
          System.out.flush();
          Thread.sleep(12_000);
          throw new IOException("test-only parent was not terminated by systemd");
        }
        case "check" -> {
          try {
            intent.requireClear();
          } catch (IOException refused) {
            System.out.println("RESIDUAL_REFUSED");
            return;
          }
          throw new IOException("residual marker was accepted");
        }
        default -> throw new IOException("fixed probe mode unavailable");
      }
    }
  }
}
