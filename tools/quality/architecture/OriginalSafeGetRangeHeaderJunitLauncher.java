import java.util.Map;

/** Four entire in-memory value suites; no deployed request or file access. */
public final class OriginalSafeGetRangeHeaderJunitLauncher {
  private OriginalSafeGetRangeHeaderJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.security.SavedRequestTargetTest", 4,
        "dev.codex.schubert.nk.web.media.HttpByteRangeParserTest", 4,
        "dev.codex.schubert.nk.web.media.ContentDispositionFactoryTest", 1,
        "dev.codex.schubert.nk.web.media.ContentDispositionBoundaryTest", 3));
  }
}
