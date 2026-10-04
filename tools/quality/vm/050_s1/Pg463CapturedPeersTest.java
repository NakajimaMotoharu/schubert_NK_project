import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Fixed actual capture is input; independently specified mutation outcomes are the oracle. */
public final class Pg463CapturedPeersTest {
  public static void main(String[] args) throws Exception {
    if(args.length!=1)throw new IllegalArgumentException("private input path required");
    String raw=Files.readString(Path.of(args[0]),StandardCharsets.UTF_8);
    Pg463CapturedPeers.watch(raw.getBytes(StandardCharsets.UTF_8));
    int assertions=1;
    for(var change:List.of(
        new String[]{"2dcf55ab91a74041be1b997d6e5de258","1".repeat(32)},
        new String[]{"e5b1b0bc62a54593a7f9b3f5d23b82ae","2".repeat(32)},
        new String[]{"4105e7a77d3449b1aeff0dcea2f0d5ca","3".repeat(32)},
        new String[]{"10659726","9155798"},new String[]{"10661011","9156927"},
        new String[]{"10587260","8411501"},new String[]{"925161","304688"},
        new String[]{"927354","306805"},new String[]{"782118","162625"},
        new String[]{"0.1.0-SNAPSHOT","0.2.0-SNAPSHOT"},
        new String[]{"ca33239da3019dad50b6ebad22318130283d6756","4".repeat(40)})) {
      String bad=raw.replace(change[0],change[1]);if(bad.equals(raw))throw new AssertionError("fixture has no mutation target");
      try{Pg463CapturedPeers.watch(bad.getBytes(StandardCharsets.UTF_8));throw new AssertionError("drift accepted");}
      catch(IllegalArgumentException|IllegalStateException rejected){assertions++;}
    }
    for(String role:List.of("api","web")) {
      String missing=raw.lines().filter(l->!l.contains("\"ready\": \""+role+"\"")).reduce("",(a,b)->a+b+"\n");
      if(missing.equals(raw))throw new AssertionError("actual readiness fixture absent");
      try{Pg463CapturedPeers.watch(missing.getBytes(StandardCharsets.UTF_8));throw new AssertionError("missing ready accepted");}
      catch(IllegalStateException rejected){assertions++;}
    }
    System.out.println("PG463_PEERS_TOOL_PASS independentAssertions="+assertions+" productionPt0=true nativeMutation=false");
  }
}
