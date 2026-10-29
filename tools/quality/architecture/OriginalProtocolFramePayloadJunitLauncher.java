import java.util.Map;

/** Whole five codec suites; fixed public golden fixtures and own memory threads only. */
public final class OriginalProtocolFramePayloadJunitLauncher {
  private OriginalProtocolFramePayloadJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.protocol.codec.MessageCodecTest", 7,
            "dev.codex.schubert.nk.protocol.codec.PayloadCodecTest", 8,
            "dev.codex.schubert.nk.protocol.codec.PayloadGoldenVectorTest", 3,
            "dev.codex.schubert.nk.protocol.codec.ScenarioRecordEncodingTest", 3,
            "dev.codex.schubert.nk.protocol.codec.AuthenticationErrorProfileTest", 3));
  }
}
