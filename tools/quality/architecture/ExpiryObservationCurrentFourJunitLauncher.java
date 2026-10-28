import java.util.Map;

/** Existing whole four data-only record tests; no real database, Unit or receipt authority. */
public final class ExpiryObservationCurrentFourJunitLauncher {
  private ExpiryObservationCurrentFourJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.repository.MorningExpiryObservationInvariantTest", 4));
  }
}
