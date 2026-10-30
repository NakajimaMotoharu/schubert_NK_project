import java.util.Map;

/** Whole originals: null/authorization/oversize rejected before every JDBC Proxy invocation. */
public final class PreSqlBoundaryCurrentJunitLauncher {
  private PreSqlBoundaryCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.api.persistence.LogQueryPreSqlBoundaryTest", 3,
            "dev.codex.schubert.nk.api.persistence.QuestionQueryPreSqlBoundaryTest", 6,
            "dev.codex.schubert.nk.api.persistence.UserQueryPreSqlBoundaryTest", 4));
  }
}
