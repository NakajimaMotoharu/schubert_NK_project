import java.util.Map;

/** Original Scenario stream five on own public temporary files; no actual publication. */
public final class ScenarioRecordStreamFiveJunitLauncher {
  private ScenarioRecordStreamFiveJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.storage.ScenarioRecordStreamTest", 5));
  }
}
