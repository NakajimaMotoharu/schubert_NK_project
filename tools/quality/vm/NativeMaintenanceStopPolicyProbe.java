import dev.codex.schubert.nk.batch.file.MaintenanceFileLock;
import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopPolicy;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import dev.codex.schubert.nk.batch.platform.StopGateFailure;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.nio.file.Files;
import java.nio.file.Path;

/** NATIVE030 genuine root/M/A fixed Caddy policy refusal/acceptance, no stop command. */
public final class NativeMaintenanceStopPolicyProbe {
  public static void main(String[] arguments) throws Exception {
    if (arguments.length != 1
        || !(arguments[0].equals("reject") || arguments[0].equals("accept"))
        || LinuxInodeSecurity.create().effectiveUid() != 0
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id"))
            .trim()
            .equals("pgpt-r2-20260927-01")) {
      throw new AssertionError("isolated root VM and fixed mode only");
    }
    boolean expectedSafe = arguments[0].equals("accept");
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
                                boolean safe;
                                try {
                                  MaintenanceUnitStopPolicy.create().requireSafe(MaintenanceUnit.CADDY);
                                  safe = true;
                                } catch (StopGateException refused) {
                                  if (refused.reason() != StopGateFailure.MALFORMED_STATE) {
                                    throw refused;
                                  }
                                  safe = false;
                                }
                                if (safe != expectedSafe) {
                                  throw new AssertionError("effective Caddy policy changed unexpectedly");
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
        "PT-OPS-NATIVE-030 PASS actualRootMorningContext=true actualMaintenanceAndAdmissionLocks=true caddyPolicySafe="
            + expectedSafe
            + " stopIssued=false wholeEightTerminal=false businessStartup=false");
  }
}
