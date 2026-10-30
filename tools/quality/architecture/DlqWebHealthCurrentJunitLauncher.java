import java.util.Map;

/** Whole originals: synthetic JMS and unstarted Tomcat value objects; no service startup. */
public final class DlqWebHealthCurrentJunitLauncher {
  private DlqWebHealthCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(
        args, Map.of(
            "dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMessageWriterTest", 3,
            "dev.codex.schubert.nk.web.bootstrap.WebRuntimeHealthTest", 4,
            "dev.codex.schubert.nk.web.bootstrap.WebHttpAdmissionValveTest", 2));
  }
}
