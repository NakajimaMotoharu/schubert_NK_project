import java.util.Map;

/** Original whole UserCreateFormTest8; fixed in-memory data, no account creation. */
public final class OriginalWebUserCreateJunitLauncher {
  private OriginalWebUserCreateJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of("dev.codex.schubert.nk.web.form.UserCreateFormTest", 8));
  }
}
