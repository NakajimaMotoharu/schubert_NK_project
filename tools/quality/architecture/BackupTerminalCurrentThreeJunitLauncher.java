import java.util.Map;

/** Whole terminal-value tests with hand-written rows and memory-only ResultSet proxies. */
public final class BackupTerminalCurrentThreeJunitLauncher {
  private BackupTerminalCurrentThreeJunitLauncher() {}

  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.repository.BackupTerminalObservationTest", 3));
  }
}
