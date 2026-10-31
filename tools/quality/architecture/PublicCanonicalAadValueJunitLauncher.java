import java.util.Map;

/** Explicit public value fixture only; no held suite discovery. */
public final class PublicCanonicalAadValueJunitLauncher {
  private PublicCanonicalAadValueJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.idempotency.PublicCanonicalAadValueTest", 8));
  }
}
