import java.util.Map;

/** Two original whole pure form suites; no cancellation/deletion/account change is performed. */
public final class OriginalWebTargetMutationJunitLauncher {
  private OriginalWebTargetMutationJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.web.form.TargetOperationFormTest", 8,
            "dev.codex.schubert.nk.web.form.UserMutationFormTest", 16));
  }
}
