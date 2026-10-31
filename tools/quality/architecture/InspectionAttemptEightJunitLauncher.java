import java.util.Map;

/** Pure fixed count/run reconciliation; no DB observation acquisition or process certificate. */
public final class InspectionAttemptEightJunitLauncher {
  private InspectionAttemptEightJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.cleanup.InspectionAttemptTest", 8));
  }
}
