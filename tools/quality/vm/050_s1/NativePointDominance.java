import java.io.File;
import java.util.Collection;
import org.jacoco.core.data.ExecutionData;
import org.jacoco.core.data.ExecutionDataStore;
import org.jacoco.core.tools.ExecFileLoader;

/** Independent snapshot monotonicity oracle; prints no raw session identifiers or probe arrays. */
public final class NativePointDominance {
  private NativePointDominance() {}

  static void verify(Collection<ExecutionData> early, ExecutionDataStore late) {
    if (early == null || early.isEmpty() || late == null) {
      throw new IllegalArgumentException("complete actual snapshot data required");
    }
    for (ExecutionData a : early) {
      ExecutionData b = late.get(a.getId());
      if (b == null
          || !a.getName().equals(b.getName())
          || a.getProbes().length != b.getProbes().length) {
        throw new IllegalArgumentException("same class identity and probe shape required");
      }
      for (int i = 0; i < a.getProbes().length; i++) {
        if (a.getProbes()[i] && !b.getProbes()[i]) {
          throw new IllegalArgumentException("covered probe rollback refused");
        }
      }
    }
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2) {
      throw new IllegalArgumentException("independent early and closing points required");
    }
    var early = new ExecFileLoader();
    var late = new ExecFileLoader();
    early.load(new File(args[0]));
    late.load(new File(args[1]));
    var a = early.getSessionInfoStore().getInfos();
    var b = late.getSessionInfoStore().getInfos();
    if (a.size() != 1
        || b.size() != 1
        || !a.getFirst().getId().equals(b.getFirst().getId())
        || a.getFirst().getStartTimeStamp() != b.getFirst().getStartTimeStamp()
        || a.getFirst().getDumpTimeStamp() > b.getFirst().getDumpTimeStamp()) {
      throw new IllegalArgumentException("same session and ordered actual points required");
    }
    verify(early.getExecutionDataStore().getContents(), late.getExecutionDataStore());
    System.out.println("sameSessionProbeMonotonic=true;latestClosingOnly=true");
  }
}
