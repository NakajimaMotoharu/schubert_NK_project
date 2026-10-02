import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
/** REC50 independent literal/hash oracle; tool only, Production PT count zero. */
public final class Pg422KnownIncompleteRecoveryTest {
  static int assertions;
  static void expect(boolean expected,Map<String,String> m,Map<String,String> a) {
    if(Pg422KnownIncompleteRecovery.known(m,a)!=expected)throw new AssertionError("closed known generation");assertions++;
  }
  static Map<String,String> receipt(boolean morning) {
    var v=new HashMap<String,String>();
    v.put("Id",morning?"schubert-nk-morning-controller.service":"schubert-nk-api.service");
    v.put("LoadState","loaded");v.put("ActiveState",morning?"failed":"inactive");v.put("SubState",morning?"failed":"dead");
    v.put("Job","");v.put("InvocationID",morning?"0d39056c1d374f9dbe4938683e4ae20b":"05b8d33d64294727bcff84543e968256");
    v.put("Type",morning?"oneshot":"simple");v.put("Restart",morning?"no":"on-failure");v.put("RemainAfterExit","no");
    v.put("MainPID","0");v.put("ControlPID","0");v.put("Result","exit-code");v.put("ExecMainCode","1");v.put("ExecMainStatus",morning?"30":"50");
    v.put("ExecMainStartTimestampMonotonic","100");v.put("ExecMainExitTimestampMonotonic","200");v.put("KillMode","control-group");v.put("SendSIGKILL","no");return v;
  }
  public static void main(String[] args) throws Exception {
    var m=receipt(true);var a=receipt(false);expect(true,m,a);expect(false,null,a);expect(false,m,null);
    for(boolean morning:List.of(false,true)) {
      var base=morning?m:a;
      for(String field:base.keySet()) {
        var missing=new HashMap<>(base);missing.remove(field);expect(false,morning?missing:m,morning?a:missing);
      }
      for(String field:List.of("Id","InvocationID","ExecMainCode","ExecMainStatus","Result","Job","MainPID","ControlPID")) {
        var changed=new HashMap<>(base);changed.put(field,"different");expect(false,morning?changed:m,morning?a:changed);
        changed.put(field,null);expect(false,morning?changed:m,morning?a:changed);
      }
    }
    if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Pg422KnownIncompleteRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII)))
        .equals("7d7acfaff4787c3651386cd9a155eba1db2038955544b4e2b0332504096273c6"))throw new AssertionError("independent SQL whole bytes");assertions++;
    if(Pg422KnownIncompleteRecovery.NAMES.size()!=16 || !Pg422KnownIncompleteRecovery.NAMES.contains("adc7cb94-b23d-45ea-824a-3ae6c293b09d.API.start.intent")
        || Pg422KnownIncompleteRecovery.NAMES.contains("5689f481-b4e3-4d8f-b450-74b980f5c15c.API.start.intent"))throw new AssertionError("independent fixed namespace");assertions++;
    System.out.println("PG422_RECOVERY_TOOL independentAssertions="+assertions+" success=true productionTestCount=0");
  }
}
