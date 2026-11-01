import java.util.Map;
/** SS343/PG371: original synthetic permit correlation only, no actual Root/permit operation. */
public final class CurrentPermitDataSixCurrentJunitLauncher {
  private CurrentPermitDataSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.file.RootCurrentPermitPreflightTest", 6));
  }
}
