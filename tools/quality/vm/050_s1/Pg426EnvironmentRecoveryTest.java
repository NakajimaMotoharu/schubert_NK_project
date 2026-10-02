import java.util.*;
/** ENV222 independent fixed receipt/negative oracle; no Production quality numerator. */
public final class Pg426EnvironmentRecoveryTest {
  static int assertions;
  static void expect(boolean wanted,Map<String,String> m,Map<String,String> e) {
    if(Pg426EnvironmentRecovery.known(m,e)!=wanted)throw new AssertionError("fixed captured case");assertions++;
  }
  public static void main(String[] args) throws Exception {
    if(args.length!=1)throw new IllegalArgumentException("captured private full18 only");
    byte[] raw=java.nio.file.Files.readAllBytes(java.nio.file.Path.of(args[0]));
    String sha=HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(raw));
    if(!sha.equals("4e9e3835b34c4afccd9100b4e0f7afd5b18770e5f3f1445e0fd35f06e767caf2"))throw new AssertionError("independent capture hash");assertions++;
    var b=new String(raw,java.nio.charset.StandardCharsets.US_ASCII).stripTrailing().split("\n\n");
    var m=fields(b[0]);var e=fields(b[1]);expect(true,m,e);expect(false,null,e);expect(false,m,null);
    for(boolean morning:List.of(true,false)) {
      var base=morning?m:e;
      for(String k:base.keySet()) {
        var v=new HashMap<>(base);v.remove(k);expect(false,morning?v:m,morning?e:v);
      }
      var keys=new ArrayList<>(List.of("Id","InvocationID","MainPID","ControlPID","Job","ActiveState","SubState","Result","ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic"));
      if(!morning)keys.add("ExecMainExitTimestampMonotonic");
      for(String k:keys)for(String changed:Arrays.asList(null,"unknown")) {
        var v=new HashMap<>(base);v.put(k,changed);expect(false,morning?v:m,morning?e:v);
      }
    }
    var newer=new HashMap<>(e);newer.put("ExecMainStartTimestampMonotonic","204730222080");expect(false,m,newer);
    System.out.println("PG426_ENVIRONMENT_TOOL independentAssertions="+assertions+" success=true productionTestCount=0");
  }
  static Map<String,String> fields(String raw) {
    var result=new HashMap<String,String>();
    for(String line:raw.split("\n")) {
      int at=line.indexOf('=');if(at<1 || result.put(line.substring(0,at),line.substring(at+1))!=null)throw new AssertionError("exact properties");
    }
    return result;
  }
}
