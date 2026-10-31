import java.util.Map;

/** Literal public IP/inode values only; no Root, certificate, native or filesystem operations. */
public final class CaddyPublicValueJunitLauncher {
  private CaddyPublicValueJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.file.CaddyAddressBoundaryTest", 2,
        "dev.codex.schubert.nk.batch.file.CaddyPublicCaMetadataTest", 3,
        "dev.codex.schubert.nk.batch.file.CaddyPublicMetadataTest", 4));
  }
}
