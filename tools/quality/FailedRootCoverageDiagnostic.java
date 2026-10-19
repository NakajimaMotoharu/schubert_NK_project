import java.io.File;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.tools.ExecFileLoader;

/** Failed-run diagnosis only. Never reports a successful run, session qualification or coverage gate. */
public final class FailedRootCoverageDiagnostic {
  public static void main(String[] args) throws Exception {
    if (args.length != 7 && (args.length != 8 || !args[7].equals("ALL_SOURCE")))
      throw new IllegalArgumentException("failed exec/six current Main roots/optional ALL_SOURCE");
    var data = new ExecFileLoader();
    data.load(new File(args[0]));
    var builder = new CoverageBuilder();
    var analyzer = new Analyzer(data.getExecutionDataStore(), builder);
    for (int i = 1; i <= 6; i++) analyzer.analyzeAll(new File(args[i]));
    Set<String> focus = Set.of("RootStartupContext", "MorningServiceReadiness", "MorningStartupLaunchOwner",
        "MorningParentBudget", "MorningProcessMain", "ResourceScope", "ServiceStartupAdmission");
    int mismatches = 0;
    for (var cls : builder.getClasses()) {
      if (cls.isNoMatch()) mismatches++;
      String simple = cls.getName().substring(cls.getName().lastIndexOf('/') + 1).split("\\$", 2)[0];
      if (args.length == 7 && !focus.contains(simple)) continue;
      for (var method : cls.getMethods()) {
        System.out.println("METHOD\t" + cls.getName() + "\t" + method.getName() + "\t"
            + method.getDesc() + "\t" + method.getInstructionCounter().getCoveredCount() + "\t"
            + method.getInstructionCounter().getMissedCount());
      }
      for (int line = cls.getFirstLine(); line <= cls.getLastLine(); line++) {
        var value = cls.getLine(line);
        if (value.getInstructionCounter().getTotalCount() == 0) continue;
        System.out.println("LINE\t" + cls.getName() + "\t" + line + "\t"
            + value.getInstructionCounter().getCoveredCount() + "\t"
            + value.getInstructionCounter().getMissedCount() + "\t"
            + value.getBranchCounter().getCoveredCount() + "\t" + value.getBranchCounter().getMissedCount());
      }
    }
    if (mismatches != 0) throw new IllegalStateException("actual current class-byte mismatch");
    System.out.println("DIAGNOSTIC_FAILED_RUN_ONLY\tclassByteMismatch=0\tformalAccepted=false");
  }
}
