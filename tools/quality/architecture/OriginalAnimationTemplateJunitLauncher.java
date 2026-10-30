import java.util.Map;

/** Whole synthetic Animation DOM tests, never a player or real endpoint. */
public final class OriginalAnimationTemplateJunitLauncher {
  private OriginalAnimationTemplateJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.AnimationTemplateTest", 8));
  }
}
