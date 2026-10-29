import java.util.Map;

/** Original supplied media byte counting only; no media stream or HTTP delivery. */
public final class OriginalMediaBytesJunitLauncher {
  private OriginalMediaBytesJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.monitoring.MediaBytesMetricRecorderTest", 8));
  }
}
