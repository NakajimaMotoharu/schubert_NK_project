import java.util.Map;

/** Whole fixed-text snapshot tests, not actual Unit ownership or Root recovery. */
public final class InspectorSnapshotCurrentNineJunitLauncher {
  private InspectorSnapshotCurrentNineJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshotTest", 9));
  }
}
