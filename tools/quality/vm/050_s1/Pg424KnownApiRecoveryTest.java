import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
/** REC50 independent literal/hash oracle; tool only, Production PT count zero. */
public final class Pg424KnownApiRecoveryTest {
  static int assertions;
  static void expect(boolean expected,Map<String,String> m,Map<String,String> a) {
    if(Pg424KnownApiRecovery.known(m,a)!=expected)throw new AssertionError("closed known generation");assertions++;
  }
  static Map<String,String> receipt(boolean morning) {
    var v=new HashMap<String,String>();
    v.put("Id",morning?"schubert-nk-morning-controller.service":"schubert-nk-api.service");
    v.put("LoadState","loaded");v.put("ActiveState",morning?"failed":"inactive");v.put("SubState",morning?"failed":"dead");
    v.put("Job","");v.put("InvocationID",morning?"8c042ad21cac45df9e098240543644d4":"ab8b4e5b1de445f3b96bb1c6cc78fe14");
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
    if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Pg424KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII)))
        .equals("7d7acfaff4787c3651386cd9a155eba1db2038955544b4e2b0332504096273c6"))throw new AssertionError("independent SQL whole bytes");assertions++;
    if(Pg424KnownApiRecovery.NAMES.size()!=22 || !Pg424KnownApiRecovery.NAMES.contains("2f72c433-cd48-4ab8-b897-f667f9ad4a70.API.start.intent")
        || Pg424KnownApiRecovery.NAMES.contains("5689f481-b4e3-4d8f-b450-74b980f5c15c.API.start.intent"))throw new AssertionError("independent fixed namespace");assertions++;
    if(args.length==1) {
      byte[] actual=java.nio.file.Files.readAllBytes(java.nio.file.Path.of(args[0]));
      if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual)).equals("6cb855d08d42d58813c6ca5c21daa5d2803ec2991477bf743f216c369e987230"))throw new AssertionError("independent captured watch SHA");
      Pg424KnownApiRecovery.watch(actual);assertions++;
      String raw=new String(actual,StandardCharsets.UTF_8);
      for(String invalid:List.of(raw.substring(raw.indexOf('\n')+1),"unknown\n"+raw,raw+"unknown\n")) {
        try {Pg424KnownApiRecovery.watch(invalid.getBytes(StandardCharsets.UTF_8));throw new AssertionError("unknown diagnostic rejected");}
        catch(IllegalStateException | com.google.gson.JsonParseException expected) {assertions++;}
      }
    }
    for(String valid:List.of("999 999 999 999","999\t999\t999\t999"," 999   999\t999 999 ")) {
      if(!Pg424KnownApiRecovery.fourIds(valid,"999"))throw new AssertionError("actual four numeric ID token form");assertions++;
    }
    for(String invalid:Arrays.asList(null,"","999 999 999","999 999 999 999 999","0 999 999 999","999x 999 999 999")) {
      if(Pg424KnownApiRecovery.fourIds(invalid,"999"))throw new AssertionError("closed four numeric ID token form");assertions++;
    }
    System.out.println("PG424_RECOVERY_TOOL independentAssertions="+assertions+" success=true productionTestCount=0");
  }
}
