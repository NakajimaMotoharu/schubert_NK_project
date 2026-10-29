import java.util.Map;

/** Entire original animation presentation suite, using its real closed category types. */
public final class OriginalAnimationViewJunitLauncher {
  private OriginalAnimationViewJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.AnimationViewModelTest", 8));
  }
}
