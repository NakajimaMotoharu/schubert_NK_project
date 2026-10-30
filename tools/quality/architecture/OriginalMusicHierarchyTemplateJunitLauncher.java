import java.util.Map;

/** Whole synthetic MVC template test only, no real endpoint or playback. */
public final class OriginalMusicHierarchyTemplateJunitLauncher {
  private OriginalMusicHierarchyTemplateJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.view.MusicHierarchyTemplateTest", 6));
  }
}
