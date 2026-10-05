import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Fixed actual capture is input; independently specified mutation outcomes are the oracle. */
public final class Pg468CapturedPeersTest {
  public static void main(String[] args) throws Exception {
    if(args.length!=1)throw new IllegalArgumentException("private input path required");
    String raw=Files.readString(Path.of(args[0]),StandardCharsets.UTF_8);
    Pg468CapturedPeers.watch(raw.getBytes(StandardCharsets.UTF_8));
    int assertions=1;
    for(var change:List.of(
        new String[]{"28efa4cf44ef4302b4fc9c67d3bb7432","1".repeat(32)},
        new String[]{"960e8045cf1f4c4b88d7ca0da2fc6f8e","2".repeat(32)},
        new String[]{"86fd86f54b464bd29f73a844ee4f1bd3","3".repeat(32)},
        new String[]{"12913800","9155798"},new String[]{"12914892","9156927"},
        new String[]{"12840676","8411501"},new String[]{"1587773","304688"},
        new String[]{"1589852","306805"},new String[]{"1443550","162625"},
        new String[]{"0.1.0-SNAPSHOT","0.2.0-SNAPSHOT"},
        new String[]{"df9a33febf3703f0d18ac2c4ef56fd0225aac2b9","4".repeat(40)})) {
      String bad=raw.replace(change[0],change[1]);if(bad.equals(raw))throw new AssertionError("fixture has no mutation target");
      try{Pg468CapturedPeers.watch(bad.getBytes(StandardCharsets.UTF_8));throw new AssertionError("drift accepted");}
      catch(IllegalArgumentException|IllegalStateException rejected){assertions++;}
    }
    for(String role:List.of("api","web")) {
      String missing=raw.lines().filter(l->!l.contains("\"ready\": \""+role+"\"")).reduce("",(a,b)->a+b+"\n");
      if(missing.equals(raw))throw new AssertionError("actual readiness fixture absent");
      try{Pg468CapturedPeers.watch(missing.getBytes(StandardCharsets.UTF_8));throw new AssertionError("missing ready accepted");}
      catch(IllegalStateException rejected){assertions++;}
    }
    System.out.println("PG468_PEERS_TOOL_PASS independentAssertions="+assertions+" productionPt0=true nativeMutation=false");
  }
}
