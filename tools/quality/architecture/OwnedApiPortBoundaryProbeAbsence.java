import java.io.File;
import java.util.List;
import org.jacoco.core.tools.ExecFileLoader;

/** Passive same owned exec only; no Product load/init/invoke or services. */
public final class OwnedApiPortBoundaryProbeAbsence {
  private static final List<String> PREFIXES = List.of(
      "dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeGate",
      "dev/codex/schubert/nk/bootstrap/ServiceStartupAdmission$NativeObservation",
      "dev/codex/schubert/nk/bootstrap/ChildStartupContext$NativeIo",
      "dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime",
      "dev/codex/schubert/nk/api/file/ServiceProcessResources",
      "dev/codex/schubert/nk/storage/ServiceConfigFiles$NioIo");
  private OwnedApiPortBoundaryProbeAbsence() {}
  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("owned exec and session only");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    var sessions = loader.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals(args[1]))
      throw new IllegalStateException("one exact owned coverage session required");
    for (String prefix : PREFIXES) {
      int records = 0;
      for (var value : loader.getExecutionDataStore().getContents()) {
        if (!value.getName().equals(prefix) && !value.getName().startsWith(prefix + "$")) continue;
        records++;
        for (boolean probe : value.getProbes())
          if (probe) throw new IllegalStateException("native boundary has recorded execution");
      }
      System.out.println("OWNED_API_PORT_NATIVE_PREFIX_NO_TRUE_PROBES\t" + prefix + "\t" + records + "\t0");
    }
  }
}
