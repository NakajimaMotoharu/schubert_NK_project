import java.util.Map;

/** Original header/layout suites: pure values and two fixed public catalog fixtures only. */
public final class OriginalProtocolHeaderLayoutJunitLauncher {
  private OriginalProtocolHeaderLayoutJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.protocol.header.HeaderModelTest", 7,
            "dev.codex.schubert.nk.protocol.layout.LayoutMetadataTest", 4,
            "dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalogTest", 3));
  }
}
