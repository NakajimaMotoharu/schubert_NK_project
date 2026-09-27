import dev.codex.schubert.nk.batch.file.MaintenanceFileLock;
import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitTermination;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * NATIVE029 isolated read-only genuine root/M/A probe, not the full eight-Unit parent barrier.
 * NK-OPS-001/UI251/253/SS341/343/SSC100/PT-OPS-MSTOP008/MTERM008/BUG308.
 */
public final class NativeMaintenanceUnitTerminationProbe {
  public static void main(String[] arguments) throws Exception {
    if (arguments.length != 0
        || LinuxInodeSecurity.create().effectiveUid() != 0
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id"))
            .trim()
            .equals("pgpt-r2-20260927-01")) {
      throw new AssertionError("isolated root VM only");
    }
    var context = RootStartupContext.create();
    var expected = context.capture(RootStartupContext.Service.MORNING);
    boolean complete =
        MaintenanceFileLock.create()
            .tryExclusive(
                () -> {
                  context.recheck(expected);
                  var admitted =
                      StartupAdmissionFile.create()
                          .tryExclusive(
                              ignored -> {
                                context.recheck(expected);
                                var cold =
                                    MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.BACKUP)
                                        .quiescent();
                                if (cold.isEmpty()) {
                                  throw new AssertionError("fixed backup not quiescent");
                                }
                                var running =
                                    MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.CADDY)
                                        .quiescent();
                                if (running.isPresent()) {
                                  throw new AssertionError("running Caddy accepted");
                                }
                                context.recheck(expected);
                                return Boolean.TRUE;
                              });
                  if (admitted.isEmpty()) {
                    throw new AssertionError("A contention");
                  }
                  context.recheck(expected);
                  return admitted.orElseThrow();
                })
            .orElseThrow();
    if (!complete) {
      throw new AssertionError("M/A result");
    }
    context.recheck(expected);
    System.out.println(
        "PT-OPS-NATIVE-029 PASS actualRootMorningContext=true actualMaintenanceAndAdmissionLocks=true coldBackupQuiescent=true activeCaddyRefused=true allOwnersClosed=true wholeEightTerminal=false stopIssued=false fullParentBackup=false businessStartup=false");
  }
}
