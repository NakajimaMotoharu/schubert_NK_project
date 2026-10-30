import java.util.Map;

/** Whole original one required-null/value test, no JDBC or real data source. */
public final class OriginalRequiredColumnJunitLauncher {
  private OriginalRequiredColumnJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.database.RequiredColumnTest", 1));
  }
}
