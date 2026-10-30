import java.security.Security;
import java.util.Arrays;
import java.util.Map;

/** Four whole originals, public synthetic values; observe own child JCA order only. */
public final class PublicInboxValuesCurrentJunitLauncher {
  private PublicInboxValuesCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    var providers = Security.getProviders();
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.api.idempotency.InboxModelTest", 5,
            "dev.codex.schubert.nk.api.idempotency.OperationFingerprintTest", 5,
            "dev.codex.schubert.nk.api.idempotency.SecretBufferTest", 3,
            "dev.codex.schubert.nk.api.idempotency.QuestionQueryScopeFrameTest", 2));
    if (!Arrays.equals(providers, Security.getProviders())) {
      throw new IllegalStateException("owned JCA provider order changed");
    }
    System.out.println("OWNED_JCA_PROVIDER_ORDER_RESTORED=true");
  }
}
