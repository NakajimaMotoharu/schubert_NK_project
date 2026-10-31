import java.util.Map;

/** Primitive-only value contract fixture; no repository, DB, lookup or business completion. */
public final class RunReferencesTruthTableJunitLauncher {
  private RunReferencesTruthTableJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.repository.RunReferencesTruthTableTest", 3));
  }
}
