import dev.codex.schubert.nk.batch.file.MaintenanceFileLock;
import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopClient;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import dev.codex.schubert.nk.batch.platform.StopGateFailure;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import java.nio.file.Files;
import java.nio.file.Path;

/** NATIVE035: genuine Morning M/A, real fixed-eight preflight refusal; no stop is issued. */
public final class NativeMaintenancePreflightProbe {
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
    boolean refused =
        MaintenanceFileLock.create()
            .tryExclusive(
                () -> {
                  context.recheck(expected);
                  var admitted =
                      StartupAdmissionFile.create()
                          .tryExclusive(
                              ignored -> {
                                context.recheck(expected);
                                try {
                                  MaintenanceUnitStopClient.create(context, expected)
                                      .preflightAll();
                                  throw new AssertionError("all eight must not pass with Web missing");
                                } catch (StopGateException failure) {
                                  if (failure.reason() != StopGateFailure.MALFORMED_STATE)
                                    throw failure;
                                }
                                context.recheck(expected);
                                return Boolean.TRUE;
                              });
                  if (admitted.isEmpty()) throw new AssertionError("A contention");
                  context.recheck(expected);
                  return admitted.orElseThrow();
                })
            .orElseThrow();
    if (!refused) throw new AssertionError("M/A result");
    context.recheck(expected);
    System.out.println(
        "PT-OPS-NATIVE-035 PASS actualRootMorningContext=true actualMaintenanceAndAdmissionLocks=true wholeEightPolicyRefused=true stopIssued=false wholeEightTerminal=false businessStartup=false");
  }
}
