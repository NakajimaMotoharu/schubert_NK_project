import java.util.Map;

/** Whole fixed exception values only; never sends or receives JMS. */
public final class OriginalWebMessagingExceptionJunitLauncher {
  private OriginalWebMessagingExceptionJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.messaging.ExceptionValueContractTest", 3));
  }
}
