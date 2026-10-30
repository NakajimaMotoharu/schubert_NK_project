import java.util.Map;

/** Whole original in-memory checksum and capacity suites; no services or credentials. */
public final class ChecksumCapacityCurrentJunitLauncher {
  private ChecksumCapacityCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.api.file.AssetChecksumManifestTest", 4,
            "dev.codex.schubert.nk.api.storage.TransferCapacityTest", 5));
  }
}
