import java.util.Map;

/** Whole original public-synthetic PasswordHasher three; no real credential values. */
public final class PasswordHasherCurrentJunitLauncher {
  private PasswordHasherCurrentJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.api.security.PasswordHasherTest", 3));
  }
}
