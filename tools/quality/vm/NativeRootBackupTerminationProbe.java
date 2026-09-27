import dev.codex.schubert.nk.batch.file.MaintenanceFileLock;
import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.BackupUnitTermination;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.nio.file.Files;
import java.nio.file.Path;

/** NATIVE026 read-only root M/A/cold-Unit path; no DB/run/backup/permit success claim. */
public final class NativeRootBackupTerminationProbe {
  public static void main(String[] arguments) throws Exception {
    if (arguments.length != 0 || LinuxInodeSecurity.create().effectiveUid() != 0
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
            .equals("pgpt-r2-20260927-01")) throw new AssertionError("isolated root VM only");
    var context = RootStartupContext.create();
    boolean initReadable;
    try {
      initReadable = Files.readSymbolicLink(Path.of("/proc/1/exe"))
          .equals(Path.of("/usr/lib/systemd/systemd"));
    } catch (java.io.IOException refused) { initReadable = false; }
    System.out.println("PT-OPS-NATIVE-026 diagnostic fixedPid1ExecutableReadable=" + initReadable
        + " kernelProc=" + Files.getFileStore(Path.of("/proc")).type().equals("proc")
        + " fixedSelfCgroup=" + Files.readString(Path.of("/proc/self/cgroup"))
            .equals("0::/system.slice/schubert-nk-morning-controller.service\n")
        + " managerInvocationFormat=" + System.getenv().getOrDefault("INVOCATION_ID", "")
            .matches("(?!0{32}$)[0-9a-f]{32}"));
    var expected = context.capture(RootStartupContext.Service.MORNING);
    var result = MaintenanceFileLock.create().tryExclusive(() -> {
      context.recheck(expected);
      var admission = StartupAdmissionFile.create().tryExclusive(fd -> {
        context.recheck(expected);
        var terminal = BackupUnitTermination.create(context, expected).quiescent();
        if (terminal.isEmpty()) throw new AssertionError("fixed backup not quiescent");
        context.recheck(expected);
        return Boolean.TRUE;
      });
      if (admission.isEmpty()) throw new AssertionError("A contention");
      context.recheck(expected);
      return admission.orElseThrow();
    });
    if (!result.orElseThrow()) throw new AssertionError("M/A result");
    context.recheck(expected);
    System.out.println("PT-OPS-NATIVE-026 PASS actualRootMorningContext=true actualMaintenanceAndAdmissionLocks=true actualHostNoFollowCgroup=true coldBackupQuiescent=true allOwnersClosed=true fullParentBackup=false fullRunAndDbGate=false fullBusinessGate=false");
  }
}
