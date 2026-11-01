import java.util.Map;
/** Original public journal7 and in-memory borrowed deadline2, no broker/native operation. */
public final class PublicJournalDeadlineNineCurrentJunitLauncher {
  private PublicJournalDeadlineNineCurrentJunitLauncher() {}
  public static void main(String[] args) throws Exception {
    SharedSelectedJunitReporterV1.run(args, Map.of(
        "dev.codex.schubert.nk.batch.platform.BrokerJournalEvidenceTest", 7,
        "dev.codex.schubert.nk.batch.mq.ArtemisParentDeadlineTest", 2));
  }
}
