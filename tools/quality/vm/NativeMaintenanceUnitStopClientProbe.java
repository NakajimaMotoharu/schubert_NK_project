import dev.codex.schubert.nk.batch.file.MaintenanceFileLock;
import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClient;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitTermination;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.nio.file.Files;
import java.nio.file.Path;

/** NATIVE031: real fixed systemctl stop of cold Backup under genuine root Morning/M/A. */
public final class NativeMaintenanceUnitStopClientProbe {
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
                                var before =
                                    MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.BACKUP)
                                        .quiescent();
                                if (before.isEmpty()) {
                                  throw new AssertionError("backup must start cold");
                                }
                                var attempt =
                                    MaintenanceUnitStopClient.create(context, expected)
                                        .stop(MaintenanceUnit.BACKUP);
                                if (attempt.status()
                                    != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) {
                                  throw new AssertionError("fixed stop client did not exit zero");
                                }
                                var after =
                                    MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.BACKUP)
                                        .quiescent();
                                if (after.isEmpty()) {
                                  throw new AssertionError("backup Unit did not reach terminal state");
                                }
                                if (MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.CADDY)
                                        .quiescent()
                                        .isPresent()) {
                                  throw new AssertionError("running Caddy was accepted as terminal");
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
        "PT-OPS-NATIVE-031 PASS actualRootMorningContext=true actualMaintenanceAndAdmissionLocks=true coldBackupStopClientExitZero=true coldBackupTerminalAfter=true activeCaddyUnchanged=true wholeEightTerminal=false businessStartup=false");
  }
}
