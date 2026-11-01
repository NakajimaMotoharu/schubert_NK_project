import java.util.Map;
/** Original six public ELF and fake inode metadata tests, without native or real Root authority. */
public final class RootElfMetadataSixCurrentJunitLauncher {
  private RootElfMetadataSixCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.file.RootServiceExecutableAdmissionTest", 6));
  }
}
