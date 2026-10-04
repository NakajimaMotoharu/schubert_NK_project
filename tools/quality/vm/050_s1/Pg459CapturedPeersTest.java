import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Fixed actual capture is input; independently specified mutation outcomes are the oracle. */
public final class Pg459CapturedPeersTest {
  public static void main(String[] args) throws Exception {
    if(args.length!=1)throw new IllegalArgumentException("private input path required");
    String raw=Files.readString(Path.of(args[0]),StandardCharsets.UTF_8);
    Pg459CapturedPeers.watch(raw.getBytes(StandardCharsets.UTF_8));
    int assertions=1;
    for(var change:List.of(
        new String[]{"386729898874494ebff10f86647d3e3a","1".repeat(32)},
        new String[]{"5b8cd47d114d465582216725317d6788","2".repeat(32)},
        new String[]{"fb3eaf763a8c4a5e8172d3c42f8fc954","3".repeat(32)},
        new String[]{"8483207","8483208"},new String[]{"8484334","8484335"},
        new String[]{"8411500","8411501"},new String[]{"304687","304688"},
        new String[]{"306804","306805"},new String[]{"162624","162625"},
        new String[]{"0.1.0-SNAPSHOT","0.2.0-SNAPSHOT"},
        new String[]{"ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a","4".repeat(40)})) {
      String bad=raw.replace(change[0],change[1]);if(bad.equals(raw))throw new AssertionError("fixture has no mutation target");
      try{Pg459CapturedPeers.watch(bad.getBytes(StandardCharsets.UTF_8));throw new AssertionError("drift accepted");}
      catch(IllegalArgumentException|IllegalStateException rejected){assertions++;}
    }
    for(String role:List.of("api","web")) {
      String missing=raw.lines().filter(l->!l.contains("\"ready\": \""+role+"\"")).reduce("",(a,b)->a+b+"\n");
      if(missing.equals(raw))throw new AssertionError("actual readiness fixture absent");
      try{Pg459CapturedPeers.watch(missing.getBytes(StandardCharsets.UTF_8));throw new AssertionError("missing ready accepted");}
      catch(IllegalStateException rejected){assertions++;}
    }
    System.out.println("PG459_PEERS_TOOL_PASS independentAssertions="+assertions+" productionPt0=true nativeMutation=false");
  }
}
