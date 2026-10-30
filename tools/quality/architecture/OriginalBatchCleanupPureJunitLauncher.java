import java.util.Map;

/** Entire original pure cleanup value and diagnostic contracts; never runs cleanup. */
public final class OriginalBatchCleanupPureJunitLauncher {
  private OriginalBatchCleanupPureJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.cleanup.LogCleanupValueContractTest", 4,
        "dev.codex.schubert.nk.batch.cleanup.ExceptionValueContractTest", 1));
  }
}
