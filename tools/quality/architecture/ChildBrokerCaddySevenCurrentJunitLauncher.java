import java.util.Map;

public final class ChildBrokerCaddySevenCurrentJunitLauncher {
  private ChildBrokerCaddySevenCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of("dev.codex.schubert.nk.bootstrap.ChildBrokerTest", 5, "dev.codex.schubert.nk.bootstrap.ChildCaddyTest", 2));
  }
}
