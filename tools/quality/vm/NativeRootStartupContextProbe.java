import dev.codex.schubert.nk.batch.file.StartupAdmissionFile;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.nio.file.*;

/** PT-OPS-NATIVE-014: actual fixed API Unit context and A; not whole business startup. */
public final class NativeRootStartupContextProbe {
  public static void main(String[] args) throws Exception {
    if (args.length != 0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new AssertionError("isolated fixture required");
    var context = RootStartupContext.create();
    var before = context.capture(RootStartupContext.Service.API);
    var result = StartupAdmissionFile.create().tryExclusive(fd -> {
      context.recheck(before);
      if (fd < 128 || fd > 65535) throw new AssertionError("reserved A required");
      return Boolean.TRUE;
    });
    context.recheck(before);
    if (!result.equals(java.util.Optional.of(Boolean.TRUE))) throw new AssertionError("isolated A contended");
    System.out.println("PT-OPS-NATIVE-014 PASS rootKernelProcInit=true fixedSystemUnitMainPidInvocationCgroup=true bootAndStartTicksStable=true beforeAndAfterARechecked=true fullGate=false");
  }
}
