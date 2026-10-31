import java.util.Map;

/** Whole original Scenario reader4 with own public temporary files, no live result store. */
public final class ScenarioRecordReaderFourJunitLauncher {
  private ScenarioRecordReaderFourJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.storage.ScenarioRecordReaderTest", 4));
  }
}
