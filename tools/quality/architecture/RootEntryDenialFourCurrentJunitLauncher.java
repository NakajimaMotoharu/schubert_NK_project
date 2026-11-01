import java.util.Map;
/** Original role/null denial and fake descriptor ownership only; no native Root entry. */
public final class RootEntryDenialFourCurrentJunitLauncher {
  private RootEntryDenialFourCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.file.RootEntryRejectionTest", 4));
  }
}
