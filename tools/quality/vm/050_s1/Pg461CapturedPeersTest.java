import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Fixed actual capture is input; independently specified mutation outcomes are the oracle. */
public final class Pg461CapturedPeersTest {
  public static void main(String[] args) throws Exception {
    if(args.length!=1)throw new IllegalArgumentException("private input path required");
    String raw=Files.readString(Path.of(args[0]),StandardCharsets.UTF_8);
    Pg461CapturedPeers.watch(raw.getBytes(StandardCharsets.UTF_8));
    int assertions=1;
    for(var change:List.of(
        new String[]{"97f343d29ea24b6d931becd283f947a4","1".repeat(32)},
        new String[]{"e190b88e422c459f91c635b7255248cd","2".repeat(32)},
        new String[]{"271136af03ae47e3ba9f398e2e2a24b0","3".repeat(32)},
        new String[]{"9437302","9155798"},new String[]{"9438438","9156927"},
        new String[]{"9365225","8411501"},new String[]{"613477","304688"},
        new String[]{"615605","306805"},new String[]{"471458","162625"},
        new String[]{"0.1.0-SNAPSHOT","0.2.0-SNAPSHOT"},
        new String[]{"8e97eb9138828010926cd47fd10868d8a2d54f11","4".repeat(40)})) {
      String bad=raw.replace(change[0],change[1]);if(bad.equals(raw))throw new AssertionError("fixture has no mutation target");
      try{Pg461CapturedPeers.watch(bad.getBytes(StandardCharsets.UTF_8));throw new AssertionError("drift accepted");}
      catch(IllegalArgumentException|IllegalStateException rejected){assertions++;}
    }
    for(String role:List.of("api","web")) {
      String missing=raw.lines().filter(l->!l.contains("\"ready\": \""+role+"\"")).reduce("",(a,b)->a+b+"\n");
      if(missing.equals(raw))throw new AssertionError("actual readiness fixture absent");
      try{Pg461CapturedPeers.watch(missing.getBytes(StandardCharsets.UTF_8));throw new AssertionError("missing ready accepted");}
      catch(IllegalStateException rejected){assertions++;}
    }
    System.out.println("PG461_PEERS_TOOL_PASS independentAssertions="+assertions+" productionPt0=true nativeMutation=false");
  }
}
