import dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatchReport;

/** No IO or dispatcher: the unmodified normal artifact must reject this fixed inconsistent sum. */
public final class OutboxReportOverflowWitness {
  private OutboxReportOverflowWitness() {}

  public static void main(String[] args) {
    if (args.length != 0) throw new IllegalArgumentException("no arguments");
    try {
      new OutboxDispatchReport(0, Integer.MAX_VALUE, Integer.MAX_VALUE, 2);
    } catch (IllegalArgumentException expected) {
      System.out.println("inconsistentCountRejected=true");
      return;
    }
    System.out.println("inconsistentCountRejected=false;mathematicalSum=4294967296;claimed=0");
    throw new AssertionError("existing API count invariant accepts wrapped int sum");
  }
}
