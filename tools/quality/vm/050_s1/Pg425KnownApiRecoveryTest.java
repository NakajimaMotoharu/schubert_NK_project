import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
/** REC50 independent literal/hash oracle; tool only, Production PT count zero. */
public final class Pg425KnownApiRecoveryTest {
  static int assertions;
  static void expect(boolean expected,Map<String,String> m,Map<String,String> a) {
    if(Pg425KnownApiRecovery.known(m,a)!=expected)throw new AssertionError("closed known generation");assertions++;
  }
  static Map<String,String> receipt(boolean morning) {
    var v=new HashMap<String,String>();
    v.put("Id",morning?"schubert-nk-morning-controller.service":"schubert-nk-api.service");
    v.put("LoadState","loaded");v.put("ActiveState",morning?"failed":"inactive");v.put("SubState",morning?"failed":"dead");
    v.put("Job","");v.put("InvocationID",morning?"45b7821354e04a3baeaf283b2bbd8b14":"cf7dbd52fe094a84ac4513292ae9fce6");
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
    if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII)))
        .equals("7d7acfaff4787c3651386cd9a155eba1db2038955544b4e2b0332504096273c6"))throw new AssertionError("independent SQL whole bytes");assertions++;
    if(Pg425KnownApiRecovery.NAMES.size()!=25 || !Pg425KnownApiRecovery.NAMES.contains("8fbd510e-5485-4260-8699-490acffbd528.API.start.intent")
        || Pg425KnownApiRecovery.NAMES.contains("2f72c433-cd48-4ab8-b897-f667f9ad4a70.API.start.intent"))throw new AssertionError("independent fixed namespace");assertions++;
    if(args.length==1) {
      byte[] actual=java.nio.file.Files.readAllBytes(java.nio.file.Path.of(args[0]));
      if(!HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual)).equals("b30491cc79698e4bb380fb7b70aec83fbe824d1850f06352d4ecdd62e86fe2f0"))throw new AssertionError("independent captured watch SHA");
      Pg425KnownApiRecovery.watch(actual);assertions++;
      String raw=new String(actual,StandardCharsets.UTF_8);
      for(String invalid:List.of("unknown\n"+raw,raw+"unknown\n")) {
        try {Pg425KnownApiRecovery.watch(invalid.getBytes(StandardCharsets.UTF_8));throw new AssertionError("unknown diagnostic rejected");}
        catch(IllegalStateException | com.google.gson.JsonParseException expected) {assertions++;}
      }
    }
    for(String valid:List.of("999 999 999 999","999\t999\t999\t999"," 999   999\t999 999 ")) {
      if(!Pg425KnownApiRecovery.fourIds(valid,"999"))throw new AssertionError("actual four numeric ID token form");assertions++;
    }
    for(String invalid:Arrays.asList(null,"","999 999 999","999 999 999 999 999","0 999 999 999","999x 999 999 999")) {
      if(Pg425KnownApiRecovery.fourIds(invalid,"999"))throw new AssertionError("closed four numeric ID token form");assertions++;
    }
    System.out.println("PG425_RECOVERY_TOOL independentAssertions="+assertions+" success=true productionTestCount=0");
  }
}
