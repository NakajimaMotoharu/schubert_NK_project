package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * PGPT-only root tmpfs probe. Does not authenticate a Morning Unit, own M/A, start Backup, or
 * certify a parent recovery. Never include in a Production JAR.
 */
public final class NativeBackupStartIntentProbe {
  private static final Path ROOT = Path.of("/run/schubert-nk/backup-request");
  private static final Path INSTANCE = Path.of("/var/lib/cloud/data/instance-id");

  private NativeBackupStartIntentProbe() {}

  public static void main(String[] args) throws IOException {
    var security = LinuxInodeSecurity.create();
    if (args.length != 0
        || security.effectiveUid() != 0
        || !Files.readString(INSTANCE).trim().equals("pgpt-r2-20260927-01")) {
      throw new IOException("isolated root probe unavailable");
    }
    empty();
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), ROOT)) {
      var intent =
          new BackupStartIntentFiles(
              directory,
              security,
              () -> {
                if (security.effectiveUid() != 0)
                  throw new IOException("isolated root probe unavailable");
              });
      intent.requireClear();
      var token = intent.begin();
      if (Files.size(ROOT.resolve("backup-start.intent")) != 0)
        throw new IOException("intent nonempty");
      try {
        intent.requireClear();
      } catch (IOException expected) {
        intent.retire(token);
        intent.requireClear();
        empty();
        System.out.println("INTENT_CREATED_RESIDUAL_REJECTED_RETIRED");
        return;
      }
      throw new IOException("residual intent accepted");
    }
  }

  private static void empty() throws IOException {
    try (var entries = Files.list(ROOT)) {
      if (entries.findAny().isPresent()) throw new IOException("fixed root not empty");
    }
  }
}
