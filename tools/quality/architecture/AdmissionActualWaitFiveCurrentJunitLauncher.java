import java.util.Map;
/** Full original admission3 and real-wait quality2; no native/Root production start. */
public final class AdmissionActualWaitFiveCurrentJunitLauncher {
  private AdmissionActualWaitFiveCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.web.bootstrap.WebHttpAdmissionTest", 3,
        "dev.codex.schubert.nk.web.bootstrap.WebHttpAdmissionWaitingContractTest", 2));
  }
}
