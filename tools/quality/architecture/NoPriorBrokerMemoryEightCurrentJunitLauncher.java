import java.util.Map;

public final class NoPriorBrokerMemoryEightCurrentJunitLauncher {
  private NoPriorBrokerMemoryEightCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of("dev.codex.schubert.nk.batch.platform.MorningNoPriorBrokerTest",8));
  }
}
