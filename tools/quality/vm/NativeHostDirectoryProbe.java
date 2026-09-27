import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;

/** PT-OPS-NATIVE-010: Production host SPI under real sandbox, not full root admission. */
public final class NativeHostDirectoryProbe {
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || LinuxInodeSecurity.create().effectiveUid() != 0
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new AssertionError("isolated root fixture required");
    var security = LinuxInodeSecurity.create();
    try (var host = OwnedTransferDirectory.open(LinuxHostDirectoryCalls.create(), Path.of("/run"));
        var service = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of("/run"))) {
      boolean hostReadOnly = host.atDirectory(security::readOnlyFilesystem);
      boolean privateReadOnly = service.atDirectory(security::readOnlyFilesystem);
      var actual = host.atDirectory(p -> Files.readAttributes(p, "unix:dev,ino,uid,gid,mode"));
      var local = service.atDirectory(p -> Files.readAttributes(p, "unix:dev,ino,uid,gid,mode"));
      if (hostReadOnly || !privateReadOnly || !actual.equals(local))
        throw new AssertionError("host/private mismatch");
      System.out.println("PT-OPS-NATIVE-010 PASS productionHostSpi=true hostReadOnly=false privateReadOnly=true sameIdentity=true fullGate=false");
    }
  }
}
