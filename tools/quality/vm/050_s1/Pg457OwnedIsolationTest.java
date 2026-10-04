import java.nio.charset.StandardCharsets;
import java.util.*;

/** Independent authority-field retention vectors. Tool-only; no actual stop/permit authority. */
public final class Pg457OwnedIsolationTest {
  static byte[] bytes(String s){return s.getBytes(StandardCharsets.US_ASCII);}
  public static void main(String[] args) {
    if(args.length!=0)throw new IllegalArgumentException("literal vectors only");int count=0;
    String literal="Uid: 200 200 200 200\nGid: 201 201 201 201\nGroups: 201 202\nNoNewPrivs: 1\nCapInh: 0000000000000000\nCapPrm: 0000000000000000\nCapEff: 0000000000000000\nCapBnd: 0000000000000000\nCapAmb: 0000000000000000\nvoluntary_ctxt_switches: 5\n";
    var expected=Map.of("Uid","200 200 200 200","Gid","201 201 201 201","Groups","201 202","NoNewPrivs","1","CapInh","0000000000000000","CapPrm","0000000000000000","CapEff","0000000000000000","CapBnd","0000000000000000","CapAmb","0000000000000000");
    if(!expected.equals(Pg457OwnedIsolation.identity(bytes(literal))))throw new AssertionError("all authority fields");count++;
    if(!expected.equals(Pg457OwnedIsolation.identity(bytes(literal.replace("switches: 5","switches: 6")))))throw new AssertionError("unrelated process counter");count++;
    for(String key:expected.keySet()) {
      String changed=literal.replace(key+": "+expected.get(key),key+": different");
      if(expected.equals(Pg457OwnedIsolation.identity(bytes(changed))))throw new AssertionError("authority field erased");count++;
    }
    try{Pg457OwnedIsolation.status(bytes("Uid: 1\nUid: 2\n"));throw new AssertionError("duplicate accepted");}
    catch(IllegalStateException valid){count++;}
    System.out.println("PG457_ISOLATION_TOOL_PASS independentAssertions="+count+" productionPt0=true stopExecuted=false");
  }
}
