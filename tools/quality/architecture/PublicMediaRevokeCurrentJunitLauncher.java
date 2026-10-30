import java.util.Map;

/** Whole original media4/revocation7; public synthetic inputs, child-local JCA state only. */
public final class PublicMediaRevokeCurrentJunitLauncher {
  private PublicMediaRevokeCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.web.media.MediaResponseDecoderTest", 4,
            "dev.codex.schubert.nk.web.revocation.RevocationPayloadCodecTest", 7));
  }
}
