import java.util.Map;

/** Original Field6 and NFC3: pure scalar/byte golden vectors only. */
public final class OriginalProtocolFieldJunitLauncher {
  private OriginalProtocolFieldJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.protocol.codec.FieldCodecTest", 6,
            "dev.codex.schubert.nk.protocol.codec.FieldCodecNfcGoldenTest", 3));
  }
}
