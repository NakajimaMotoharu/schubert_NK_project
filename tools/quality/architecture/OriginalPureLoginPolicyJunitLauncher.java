import java.util.Map;

/** Whole original policy15, synthetic strings/char arrays/fixed time; no login, DB or credential IO. */
public final class OriginalPureLoginPolicyJunitLauncher {
  private OriginalPureLoginPolicyJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.api.security.LoginUsernameTest", 3,
        "dev.codex.schubert.nk.api.security.PasswordPolicyTest", 3,
        "dev.codex.schubert.nk.api.security.LoginAttemptStateTest", 5,
        "dev.codex.schubert.nk.api.security.LoginAttemptSequenceTest", 4));
  }
}
