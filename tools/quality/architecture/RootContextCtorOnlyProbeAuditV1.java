import java.nio.file.Path;
import java.util.Arrays;
import java.util.Set;
import java.util.jar.JarFile;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.tools.ExecFileLoader;

/** Passive exec/class metadata only: never loads any Product class. */
public final class RootContextCtorOnlyProbeAuditV1 {
  private static final String NAME = "dev/codex/schubert/nk/batch/platform/RootStartupContext";
  private static final String DESC = "(L" + NAME + "$Io;)V";
  private RootContextCtorOnlyProbeAuditV1() {}
  public static void main(String[] args) throws Exception {
    if (args.length != 4 || !args[2].equals("PG17661-ROOT-ENTRY-DENIAL-ORIGINAL4-V2")
        || !Set.of("ORIGINAL", "FORGED_CONTEXT").contains(args[3]))
      throw new IllegalArgumentException("exact session and metadata mode required");
    var loader = new ExecFileLoader();
    loader.load(Path.of(args[0]).toFile());
    var sessions = loader.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals(args[2]))
      throw new IllegalStateException("single exact session required");
    var store = loader.getExecutionDataStore();
    var record = store.getContents().stream().filter(v -> v.getName().equals(NAME))
        .findFirst().orElseThrow();
    if (args[3].equals("FORGED_CONTEXT")) Arrays.fill(record.getProbes(), true);
    var coverage = new CoverageBuilder();
    try (var jar = new JarFile(args[1]);
        var input = jar.getInputStream(jar.getJarEntry(NAME + ".class"))) {
      new Analyzer(store, coverage).analyzeClass(input, NAME + ".class");
    }
    if (coverage.getClasses().size() != 1 || !coverage.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("exact context CRC required");
    var type = coverage.getClasses().iterator().next();
    if (!type.getName().equals(NAME) || type.getId() != record.getId())
      throw new IllegalStateException("exact context identity required");
    int constructor = 0;
    int denied = 0;
    for (var method : type.getMethods()) {
      int covered = method.getInstructionCounter().getCoveredCount();
      if (method.getName().equals("<init>") && method.getDesc().equals(DESC)) {
        if (covered <= 0) throw new IllegalStateException("original injected constructor missing");
        constructor++;
      } else {
        denied++;
        if (covered != 0) throw new IllegalStateException("NON_CONSTRUCTOR_CONTEXT_INSTRUCTION");
      }
    }
    if (constructor != 1 || denied == 0)
      throw new IllegalStateException("complete context method denominator required");
    System.out.println("ROOT_CONTEXT_CTOR_ONLY_RECORDED_SCOPE_OK\t" + denied);
  }
}
