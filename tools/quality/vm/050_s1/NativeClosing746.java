import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.*;
import org.jacoco.core.analysis.*;
import org.jacoco.core.data.*;
import org.jacoco.core.tools.ExecFileLoader;

/** SSC234 independent latest-only same-session/probe oracle, never business/OS authority. */
public final class NativeClosing746 {
  static void require(boolean value) {
    if (!value) throw new IllegalStateException("closing native qualification rejected");
  }

  static long validate(List<SessionInfo> first, List<SessionInfo> last,
      Collection<ExecutionData> terminal, Collection<ExecutionData> closing,
      String expected, long lower, long upper) {
    require(first != null && last != null && terminal != null && closing != null
        && expected != null && lower > 0 && upper >= lower);
    require(first.size() == 1 && last.size() == 1);
    var a = first.getFirst(); var b = last.getFirst();
    require(a != null && b != null && expected.equals(a.getId()) && expected.equals(b.getId()));
    require(lower <= a.getStartTimeStamp() && a.getStartTimeStamp() == b.getStartTimeStamp()
        && a.getStartTimeStamp() <= a.getDumpTimeStamp()
        && a.getDumpTimeStamp() <= b.getDumpTimeStamp() && b.getDumpTimeStamp() <= upper);
    var selected = new HashMap<Long, ExecutionData>();
    for (var d : closing) require(d != null && selected.putIfAbsent(d.getId(), d) == null);
    require(!terminal.isEmpty() && !closing.isEmpty());
    var oldIds = new HashSet<Long>();
    long additional = 0;
    for (var d : terminal) {
      require(d != null && oldIds.add(d.getId()));
      var actual = selected.get(d.getId());
      require(actual != null && d.getName().equals(actual.getName())
          && d.getProbes().length == actual.getProbes().length);
      for (int i = 0; i < d.getProbes().length; i++) {
        require(!d.getProbes()[i] || actual.getProbes()[i]);
        if (!d.getProbes()[i] && actual.getProbes()[i]) additional++;
      }
    }
    return additional;
  }

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 12) throw new IllegalArgumentException("fixed role/invocation/window/pair/six jars required");
    require(Set.of("BOOTSTRAP", "INSPECTOR").contains(args[0])
        && args[1].matches("(?!0{32}$)[0-9a-f]{32}"));
    long lower = Long.parseLong(args[2]), upper = Long.parseLong(args[3]);
    Path terminal = Path.of(args[4]), closing = Path.of(args[5]);
    require(!Files.isSameFile(terminal, closing));
    for (var p : List.of(terminal, closing)) require(Files.size(p) >= 5 && Files.size(p) <= 16777216);
    var a = new ExecFileLoader(); a.load(terminal.toFile());
    var b = new ExecFileLoader(); b.load(closing.toFile());
    String expected = args[0] + "-" + args[1] + "-ordinary";
    long gain = validate(a.getSessionInfoStore().getInfos(), b.getSessionInfoStore().getInfos(),
        a.getExecutionDataStore().getContents(), b.getExecutionDataStore().getContents(), expected, lower, upper);
    var frozen = new HashMap<String, Long>();
    for (int i = 6; i < 12; i++) {
      var classes = new CoverageBuilder();
      new Analyzer(new ExecutionDataStore(), classes).analyzeAll(new File(args[i]));
      for (var c : classes.getClasses()) {
        Long old = frozen.putIfAbsent(c.getName(), c.getId());
        require(old == null || old.longValue() == c.getId());
      }
    }
    int[] counts = new int[2]; int index = 0;
    for (var loader : List.of(a, b)) {
      for (var d : loader.getExecutionDataStore().getContents()) {
        if (d.getName().startsWith("dev/codex/schubert/nk/")) {
          Long id = frozen.get(d.getName());
          require(id != null && id.longValue() == d.getId()); counts[index]++;
        }
      }
      require(counts[index] > 0); index++;
    }
    String sessionHash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(expected.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
    System.out.println("{\"latestOnly\":true,\"singleSession\":true,\"monotonicProbes\":true,\"classByteMismatch\":0,\"terminalProductionClasses\":" + counts[0]
        + ",\"closingProductionClasses\":" + counts[1] + ",\"additionalPriorProbes\":" + gain + ",\"sessionIdSha256\":\"" + sessionHash
        + "\",\"startMs\":" + b.getSessionInfoStore().getInfos().getFirst().getStartTimeStamp()
        + ",\"terminalMs\":" + a.getSessionInfoStore().getInfos().getFirst().getDumpTimeStamp()
        + ",\"closingMs\":" + b.getSessionInfoStore().getInfos().getFirst().getDumpTimeStamp() + ",\"formalAccepted\":false}");
  }
}
