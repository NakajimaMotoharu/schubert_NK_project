import dev.codex.schubert.nk.batch.file.MaintenanceFileLock;
import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClient;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitTermination;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.nio.file.Files;
import java.nio.file.Path;

/** NATIVE032: stop real active Caddy using the fixed Production client under root Morning/M/A. */
public final class NativeMaintenanceActiveStopProbe {
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
                                if (MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.CADDY)
                                        .quiescent()
                                        .isPresent()) {
                                  throw new AssertionError("Caddy must be active before stop");
                                }
                                var attempt =
                                    MaintenanceUnitStopClient.create(context, expected)
                                        .stop(MaintenanceUnit.CADDY);
                                if (attempt.status()
                                    != MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO) {
                                  throw new AssertionError("Caddy stop client did not exit zero");
                                }
                                if (MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.CADDY)
                                        .quiescent()
                                        .isEmpty()) {
                                  throw new AssertionError("Caddy did not reach terminal state");
                                }
                                if (MaintenanceUnitTermination.create(
                                            context, expected, MaintenanceUnit.BACKUP)
                                        .quiescent()
                                        .isEmpty()) {
                                  throw new AssertionError("cold Backup changed");
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
        "PT-OPS-NATIVE-032 PASS activeCaddyStopClientExitZero=true freshCaddyTerminal=true coldBackupUnchanged=true rootMorningAndMA=true wholeEightTerminal=false businessStartup=false");
  }
}
