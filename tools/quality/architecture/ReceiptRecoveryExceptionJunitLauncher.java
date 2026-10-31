import java.util.Map;

/** Whole original recovery/exception value contracts; injected memory callbacks, no crypto/DB. */
public final class ReceiptRecoveryExceptionJunitLauncher {
  private ReceiptRecoveryExceptionJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.application.question.QuestionReceiptRecoveryTest", 4,
        "dev.codex.schubert.nk.api.idempotency.ExceptionValueContractTest", 1));
  }
}
