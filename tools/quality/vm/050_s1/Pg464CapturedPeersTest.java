import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Fixed actual capture is input; independently specified mutation outcomes are the oracle. */
public final class Pg464CapturedPeersTest {
  public static void main(String[] args) throws Exception {
    if(args.length!=1)throw new IllegalArgumentException("private input path required");
    String raw=Files.readString(Path.of(args[0]),StandardCharsets.UTF_8);
    Pg464CapturedPeers.watch(raw.getBytes(StandardCharsets.UTF_8));
    int assertions=1;
    for(var change:List.of(
        new String[]{"eda2df544e7e4b4d9e3f33eb46801c96","1".repeat(32)},
        new String[]{"b6612dc72c6141a7a93cff14991731a8","2".repeat(32)},
        new String[]{"f010f29e17ec4e5e9a38378185041e3e","3".repeat(32)},
        new String[]{"11109164","9155798"},new String[]{"11110271","9156927"},
        new String[]{"11039974","8411501"},new String[]{"1085387","304688"},
        new String[]{"1087473","306805"},new String[]{"944286","162625"},
        new String[]{"0.1.0-SNAPSHOT","0.2.0-SNAPSHOT"},
        new String[]{"11c1feb1c0b51543f98c28e3f54213274648f06f","4".repeat(40)})) {
      String bad=raw.replace(change[0],change[1]);if(bad.equals(raw))throw new AssertionError("fixture has no mutation target");
      try{Pg464CapturedPeers.watch(bad.getBytes(StandardCharsets.UTF_8));throw new AssertionError("drift accepted");}
      catch(IllegalArgumentException|IllegalStateException rejected){assertions++;}
    }
    for(String role:List.of("api","web")) {
      String missing=raw.lines().filter(l->!l.contains("\"ready\": \""+role+"\"")).reduce("",(a,b)->a+b+"\n");
      if(missing.equals(raw))throw new AssertionError("actual readiness fixture absent");
      try{Pg464CapturedPeers.watch(missing.getBytes(StandardCharsets.UTF_8));throw new AssertionError("missing ready accepted");}
      catch(IllegalStateException rejected){assertions++;}
    }
    // Actual transition is NOT ordinary proof; loss of real ordinary records must reject.
    String withoutOrdinary=raw.lines().filter(l->!l.contains("999\\t999\\t999\\t999")).reduce("",(a,b)->a+b+"\n");
    if(withoutOrdinary.equals(raw))throw new AssertionError("ordinary fixture absent");
    try{Pg464CapturedPeers.watch(withoutOrdinary.getBytes(StandardCharsets.UTF_8));throw new AssertionError("transition treated as ordinary");}
    catch(IllegalStateException rejected){assertions++;}
    String transition=raw.lines().filter(l->l.contains("00000000000801c4") && l.contains("api.bootstrap.ApiProcessMain")).findFirst().orElseThrow();
    try{Pg464CapturedPeers.watch((raw+transition+"\n").getBytes(StandardCharsets.UTF_8));throw new AssertionError("Root returned after ordinary");}
    catch(IllegalStateException rejected){assertions++;}
    for(String[] change:List.of(new String[]{"00000000000801c4","00000000000801c5"},new String[]{"0\\t0\\t0\\t0","1\\t1\\t1\\t1"})) {
      String bad=raw.replace(transition,transition.replace(change[0],change[1]));
      if(bad.equals(raw))throw new AssertionError("transition mutation absent");
      try{Pg464CapturedPeers.watch(bad.getBytes(StandardCharsets.UTF_8));throw new AssertionError("transition drift accepted");}
      catch(IllegalStateException rejected){assertions++;}
    }
    System.out.println("PG464_PEERS_TOOL_PASS independentAssertions="+assertions+" productionPt0=true nativeMutation=false");
  }
}
