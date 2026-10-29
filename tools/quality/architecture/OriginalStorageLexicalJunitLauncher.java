import java.util.Map;

/** Original lexical-only storage suites; no credential bytes, filesystem calls or native methods. */
public final class OriginalStorageLexicalJunitLauncher {
  private OriginalStorageLexicalJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.storage.ServiceCredentialLocationTest", 5,
        "dev.codex.schubert.nk.storage.StorageRootLayoutTest", 2,
        "dev.codex.schubert.nk.storage.ExceptionValueContractTest", 1));
  }
}
