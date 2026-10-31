import java.util.Map;

/** Original whole data/policy tests only; supplied fake Process, no service authority. */
public final class LegacyPolicyEightJunitLauncher {
  private LegacyPolicyEightJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.LegacyReceiptValueTest", 1,
        "dev.codex.schubert.nk.batch.platform.MaintenanceUnitStopPolicyTest", 7));
  }
}
