import java.util.Map;

/** Whole original JSON schema/v2 tests using only fixed synthetic in-memory values. */
public final class OriginalSessionJsonV2JunitLauncher {
  private OriginalSessionJsonV2JunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.session.SessionAttributeCodecTest", 7,
        "dev.codex.schubert.nk.web.session.SessionOperationTokenV2Test", 5));
  }
}
