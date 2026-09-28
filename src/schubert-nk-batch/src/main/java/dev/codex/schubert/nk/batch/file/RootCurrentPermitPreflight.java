package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only current permit correlation in the root Web/API preflight. This is not startup
 * authority: the trusted issuer must still recheck the same current/actual prestart facts while A
 * and all admitted root capabilities remain held, immediately before a same-PID exec. NK-OPS-001;
 * SYS002/004,OPS009; UI212/251/253; SS341/342/343§6.15; SSC086..089; PG371/PT-OPS-RPERMIT001..006;
 * 471 R1/D04/D05.
 */
@NullMarked
final class RootCurrentPermitPreflight {
  private RootCurrentPermitPreflight() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 §6.15 fixes root-owned /run/schubert-nk/startup; no caller path")
  static void verifyNative(
      RootStartupContext root, RootStartupContext.Snapshot expected, String releaseHash)
      throws IOException {
    Objects.requireNonNull(root, "root context");
    Objects.requireNonNull(expected, "root actor");
    Objects.requireNonNull(releaseHash, "actual release hash");
    root.recheck(expected);
    var directory =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
    var permit =
        ResourceScope.use(
            directory::close,
            () -> new StartupPermitFiles(directory, LinuxInodeSecurity.create()).readIssued());
    verify(expected, releaseHash, permit);
    root.recheck(expected);
  }

  static void verify(
      RootStartupContext.Snapshot expected, String releaseHash, StartupPermitRecords.Permit permit)
      throws IOException {
    Objects.requireNonNull(expected, "root actor");
    Objects.requireNonNull(releaseHash, "actual release hash");
    Objects.requireNonNull(permit, "issued current permit");
    if ((expected.service() != RootStartupContext.Service.WEB
            && expected.service() != RootStartupContext.Service.API)
        || !permit.boot().toString().equals(expected.boot())
        || !permit.releaseDigest().equals(releaseHash))
      throw new IOException("root current permit unavailable");
  }
}
