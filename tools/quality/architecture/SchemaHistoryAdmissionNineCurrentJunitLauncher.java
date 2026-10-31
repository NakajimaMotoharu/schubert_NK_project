import java.util.Map;

/** Original whole hand-JDBC schema projection tests, never a real database connection. */
public final class SchemaHistoryAdmissionNineCurrentJunitLauncher {
  private SchemaHistoryAdmissionNineCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.maintenance.SchemaHistoryAdmissionTest", 9));
  }
}
