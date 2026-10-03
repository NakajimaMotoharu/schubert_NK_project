import java.util.*;
/** Independent literal new-boot policy; operator PT outside Production numerator. */
public final class Pg428ColdBootPreparationTest {
  static int count;
  static void check(boolean expected,Map<String,String> input) {
    if(Pg428ColdBootPreparation.cold(input)!=expected)throw new AssertionError("cold predicate");count++;
  }
  public static void main(String[] args) throws Exception {
    var base=new HashMap<String,String>();
    for(String line:("Id=schubert-nk-morning-controller.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID=\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=0\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=no\nKillMode=control-group\nSendSIGKILL=no").split("\n")) {
      int at=line.indexOf('=');base.put(line.substring(0,at),line.substring(at+1));
    }
    check(true,base);check(false,null);check(false,Map.of());
    for(String key:base.keySet()) {var x=new HashMap<>(base);x.remove(key);check(false,x);}
    var extra=new HashMap<>(base);extra.put("unknown","value");check(false,extra);
    // BUG595: full18 keys alone must not accept an old failure/time as new cold state.
    for(String key:base.keySet())
      for(String value:Arrays.asList(null,"unknown","1234")) {var x=new HashMap<>(base);x.put(key,value);check(false,x);}
    if(!Pg428ColdBootPreparation.newBoot("58006280-5301-4a1b-a0c2-66bce4a8a38e"))throw new AssertionError("actual new boot");count++;
    for(String boot:Arrays.asList(null,"9024b59c-41d0-4dbd-8a3e-96bfad1467c0","58006280-5301-4a1b-a0c2-66bce4a8a38f","")) {
      if(Pg428ColdBootPreparation.newBoot(boot))throw new AssertionError("other boot");count++;
    }
    String[] ids={"caddy.service","artemis.service","schubert-nk-api.service","schubert-nk-web.service",
        "schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service","schubert-nk-expiry-cleanup.service","schubert-nk-backup.service"};
    for(int i=0;i<ids.length;i++) {
      var unit=new HashMap<>(base);unit.put("Id",ids[i]);unit.put("Type",i==0?"notify":i<=3?"simple":"oneshot");
      unit.put("Restart",i>0 && i<=3?"on-failure":"no");unit.put("RemainAfterExit",i>=4?"yes":"no");check(true,unit);
      for(String k:base.keySet())for(String value:Arrays.asList(null,"unknown")) {
        var bad=new HashMap<>(unit);bad.put(k,value);check(false,bad);
      }
    }
    for(String value:List.of("00","+0","-0","1","50"))for(String k:List.of("MainPID","ControlPID","ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic")) {
      var bad=new HashMap<>(base);bad.put(k,value);check(false,bad);
    }
    for(String[] bad:Arrays.asList(null,new String[]{null},new String[]{"unknown"},new String[]{"PG444","extra"})) {
      try {Pg428ColdBootPreparation.profile(bad);throw new AssertionError("bad profile accepted");}
      catch(IllegalArgumentException expected){count++;}
    }
    Pg428ColdBootPreparation.profile(new String[]{"PG444"});
    if(!Pg428ColdBootPreparation.newBoot("e07aa706-1acd-4e65-b309-d7f330f79d54")
        || Pg428ColdBootPreparation.newBoot("58006280-5301-4a1b-a0c2-66bce4a8a38e")
        || Pg428ColdBootPreparation.activeRows!=251 || !Pg428ColdBootPreparation.activeLabel.equals("PG430"))throw new AssertionError("independent resumed profile");count++;
    System.out.println("PG428_COLD_BOOT_TOOL independentAssertions="+count+" success=true productionTestCount=0");
  }
}
