import java.util.Map;

/** Original semantic tests and fixed public named-field oracle only; no business or external I/O. */
public final class OriginalProtocolSemanticJunitLauncher {
  private OriginalProtocolSemanticJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.protocol.layout.SemanticFieldValueTest", 4,
            "dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidatorTest", 8,
            "dev.codex.schubert.nk.protocol.layout.SemanticDirectBoundaryTest", 3,
            "dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalogTest", 6,
            "dev.codex.schubert.nk.protocol.layout.PayloadPaginationBoundaryTest", 3,
            "dev.codex.schubert.nk.protocol.layout.semantic.ProtocolSemanticTypeTest", 5,
            "dev.codex.schubert.nk.protocol.layout.semantic.EnumWireCompatibilityTest", 2));
  }
}
