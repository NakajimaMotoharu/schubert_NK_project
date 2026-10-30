import java.io.File;
import java.util.List;
import org.jacoco.core.tools.ExecFileLoader;

/** Passive official owned-exec inspection only; no Product load/init/invoke. */
public final class OwnedProfileNativeProbeAbsence {
  private static final List<String> PREFIXES = List.of(
      "dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile",
      "dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent",
      "dev/codex/schubert/nk/bootstrap/FixedServiceIdentity$NativeQuery");
  private OwnedProfileNativeProbeAbsence() {}
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
      System.out.println("OWNED_PROFILE_NATIVE_PREFIX_NO_TRUE_PROBES\t" + prefix + "\t" + records + "\t0");
    }
  }
}
