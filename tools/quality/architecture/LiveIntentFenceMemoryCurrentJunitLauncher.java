import java.util.Map;

/** Existing whole tests use memory Child/marker/gates, not actual start or intent retirement. */
public final class LiveIntentFenceMemoryCurrentJunitLauncher {
  private LiveIntentFenceMemoryCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.platform.ServiceIntentReadyRetirementTest", 3,
            "dev.codex.schubert.nk.batch.platform.CaddyAdmissionFenceTest", 3));
  }
}
