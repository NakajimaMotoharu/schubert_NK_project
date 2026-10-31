import java.nio.file.Path;
import java.util.Arrays;
import java.util.Set;
import java.util.jar.JarFile;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.data.ExecutionData;
import org.jacoco.core.tools.ExecFileLoader;

/** Reads exec/class bytes only. Never loads or invokes Product classes, even in negative modes. */
public final class PublicLaunchValueProbeAuditV1 {
  private static final String ROOT = "dev/codex/schubert/nk/";
  private static final String PARENT = ROOT + "bootstrap/MaintenanceOwnerFrame";
  private static final Set<String> ALLOWED = Set.of(
      ROOT + "batch/file/StartupLaunchRecord",
      ROOT + "batch/file/StartupLaunchRecord$DigestFactory",
      ROOT + "batch/file/StartupLaunchRecordTest",
      ROOT + "batch/file/PublicLaunchFramingBoundaryTest",
      PARENT,
      PARENT + "$Parent",
      ROOT + "storage/ServiceConfigFiles$Service");

  private PublicLaunchValueProbeAuditV1() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 4 || !args[2].equals("PG16219-PUBLIC-LAUNCH-FIVE")
        || !Set.of("ORIGINAL", "FORGED_CLASS", "FORGED_PARENT").contains(args[3]))
      throw new IllegalArgumentException("exact public launch session and metadata mode required");
    var loader = new ExecFileLoader();
    loader.load(Path.of(args[0]).toFile());
    var sessions = loader.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals(args[2]))
      throw new IllegalStateException("single exact session required");
    var store = loader.getExecutionDataStore();
    var parent = store.getContents().stream().filter(v -> v.getName().equals(PARENT))
        .findFirst().orElseThrow();
    if (args[3].equals("FORGED_CLASS"))
      store.put(new ExecutionData(1L, ROOT + "metadata/UnknownScope", new boolean[] {true}));
    if (args[3].equals("FORGED_PARENT")) Arrays.fill(parent.getProbes(), true);
    for (var value : store.getContents()) {
      if (value.getName().startsWith(ROOT) && !ALLOWED.contains(value.getName())) {
        for (boolean probe : value.getProbes()) {
          if (probe) throw new IllegalStateException("UNREVIEWED_TRUE_PROBE");
        }
      }
    }
    var coverage = new CoverageBuilder();
    try (var jar = new JarFile(args[1]);
        var input = jar.getInputStream(jar.getJarEntry(PARENT + ".class"))) {
      new Analyzer(store, coverage).analyzeClass(input, PARENT + ".class");
    }
    if (coverage.getClasses().size() != 1 || !coverage.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("exact parent class CRC required");
    var type = coverage.getClasses().iterator().next();
    if (!type.getName().equals(PARENT) || type.getId() != parent.getId())
      throw new IllegalStateException("exact parent identity required");
    int methods = 0;
    for (var method : type.getMethods()) {
      if (!Set.of("<clinit>", "invalid").contains(method.getName())) {
        methods++;
        if (method.getInstructionCounter().getCoveredCount() != 0)
          throw new IllegalStateException("NONVALUE_PARENT_RECORDED_INSTRUCTION");
      }
    }
    if (methods == 0) throw new IllegalStateException("nonvalue denominator required");
    System.out.println("PUBLIC_LAUNCH_RECORDED_SCOPE_OK\t" + methods);
  }
}
