import java.util.Map;

/** Original file/time/topology suites; memory streams, scalar metadata and no external I/O. */
public final class OriginalProtocolFileTimeTopologyJunitLauncher {
  private OriginalProtocolFileTimeTopologyJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.protocol.file.MediaDescriptorValidatorTest", 7,
            "dev.codex.schubert.nk.protocol.file.LargeResultRecordCodecTest", 7,
            "dev.codex.schubert.nk.protocol.time.JstWireTimestampTest", 4,
            "dev.codex.schubert.nk.protocol.transport.BrokerTopologyTest", 2));
  }
}
