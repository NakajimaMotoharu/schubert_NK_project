import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.IClassCoverage;
import org.jacoco.core.analysis.IMethodCoverage;
import org.jacoco.core.data.ExecutionDataStore;

/** Tool-only byte analysis: target files are data and are never placed on the class path. */
public final class OfficialMeasuredMethods {
  private OfficialMeasuredMethods() {}

  public static void main(String[] paths) throws Exception {
    CoverageBuilder builder = new CoverageBuilder();
    Analyzer analyzer = new Analyzer(new ExecutionDataStore(), builder);
    for (String path : paths) {
      analyzer.analyzeClass(Files.readAllBytes(Path.of(path)), path);
    }
    for (IClassCoverage type : builder.getClasses().stream()
        .sorted(Comparator.comparing(IClassCoverage::getName)).toList()) {
      for (IMethodCoverage method : type.getMethods().stream()
          .sorted(Comparator.comparing(IMethodCoverage::getName)
              .thenComparing(IMethodCoverage::getDesc)).toList()) {
        if (method.getMethodCounter().getCoveredCount() != 0
            || method.getInstructionCounter().getCoveredCount() != 0) {
          throw new AssertionError("empty execution data must never become measured coverage");
        }
        System.out.println(type.getName() + "\t" + method.getName() + "\t" + method.getDesc()
            + "\t" + method.getMethodCounter().getMissedCount()
            + "\t" + method.getInstructionCounter().getMissedCount());
      }
    }
  }
}
