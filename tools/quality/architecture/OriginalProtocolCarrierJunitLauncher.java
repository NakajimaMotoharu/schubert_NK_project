import java.util.Map;

/** Exactly eight original scalar carrier cases, no graph classifier or external resources. */
public final class OriginalProtocolCarrierJunitLauncher {
  private OriginalProtocolCarrierJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args,
        Map.of(
            "dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationExceptionTest", 4,
            "dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackExceptionTest", 4));
  }
}
