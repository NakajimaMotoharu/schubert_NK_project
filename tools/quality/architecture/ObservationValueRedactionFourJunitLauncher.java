import java.util.Map;

/** Original public-value contracts only; never an enclosing Root/DB/broker operation. */
public final class ObservationValueRedactionFourJunitLauncher {
  private ObservationValueRedactionFourJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.file.ObservationValueRedactionTest", 4));
  }
}
