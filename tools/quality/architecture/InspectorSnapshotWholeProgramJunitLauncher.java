import java.util.Map;

/** Pure state contracts; one fixed public unit-file fixture, no real service operations. */
public final class InspectorSnapshotWholeProgramJunitLauncher {
  private InspectorSnapshotWholeProgramJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    if (System.getProperty("nk.pt.repository") != null) {
      throw new IllegalStateException("unexpected fixture root override");
    }
    System.setProperty(
        "nk.pt.repository",
        "/home/mini/codex/project1/work/pgpt-runs/PG379/pg13812-snapshot-program-six-compile-v1/snapshot");
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest", 10,
            "dev.codex.schubert.nk.batch.platform.InspectorHeldStateContractTest", 9,
            "dev.codex.schubert.nk.batch.platform.ArtemisUnitSnapshotTest", 4));
  }
}
