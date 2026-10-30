import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import org.jacoco.core.tools.ExecFileLoader;

/** Reads an already-finished own exec only; never loads or invokes Product classes. */
public final class ReviewedProjectionHeldProbeAudit {
  private static final Set<String> HELD = Set.of(
      "dev/codex/schubert/nk/api/error/TemporaryInfrastructureException",
      "dev/codex/schubert/nk/web/bootstrap/WebStartupException",
      "dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing",
      "dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec");

  private ReviewedProjectionHeldProbeAudit() {}

  static int hits(Map<String, boolean[]> data) {
    int hits = 0;
    for (var entry : data.entrySet()) {
      if (HELD.contains(entry.getKey())) {
        for (boolean value : entry.getValue()) if (value) hits++;
      }
    }
    return hits;
  }

  public static void main(String[] args) throws Exception {
    if (args.length == 1 && args[0].equals("--self-test")) {
      if (hits(Map.of()) != 0 || hits(Map.of("unrelated", new boolean[] {true})) != 0)
        throw new IllegalStateException("unrelated/empty metadata");
      for (String name : HELD) {
        if (hits(Map.of(name, new boolean[] {false, true, false})) != 1)
          throw new IllegalStateException("held positive metadata must not be ignored");
        if (hits(Map.of(name, new boolean[] {false, false})) != 0)
          throw new IllegalStateException("zero metadata must not be invented");
      }
      System.out.println("TOOL_METADATA_CHECKS=10");
      return;
    }
    if (args.length != 2) throw new IllegalArgumentException("own exec and exact session");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals(args[1]))
      throw new IllegalStateException("one exact original session");
    var values = new HashMap<String, boolean[]>();
    for (var value : exec.getExecutionDataStore().getContents()) {
      if (values.put(value.getName(), value.getProbes()) != null)
        throw new IllegalStateException("duplicate original class identity");
    }
    int count = hits(values);
    if (count != 0) throw new IllegalStateException("held Product probes nonzero: " + count);
    System.out.println("FORBIDDEN_PROBE_HITS=0");
  }
}
