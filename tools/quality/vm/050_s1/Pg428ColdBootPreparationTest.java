import java.util.*;
/** Independent literal new-boot policy; operator PT outside Production numerator. */
public final class Pg428ColdBootPreparationTest {
  static int count;
  static void check(boolean expected,Map<String,String> input) {
    if(Pg428ColdBootPreparation.cold(input)!=expected)throw new AssertionError("cold predicate");count++;
  }
  public static void main(String[] args) {
    var base=new HashMap<String,String>();
    for(String line:("Id=schubert-nk-morning-controller.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID=\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=0\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=no\nKillMode=control-group\nSendSIGKILL=yes").split("\n")) {
      int at=line.indexOf('=');base.put(line.substring(0,at),line.substring(at+1));
    }
    check(true,base);check(false,null);check(false,Map.of());
    for(String key:base.keySet()) {var x=new HashMap<>(base);x.remove(key);check(false,x);}
    var extra=new HashMap<>(base);extra.put("unknown","value");check(false,extra);
    for(String key:List.of("LoadState","ActiveState","SubState","Job","MainPID","ControlPID","InvocationID"))
      for(String value:Arrays.asList(null,"unknown","1234")) {var x=new HashMap<>(base);x.put(key,value);check(false,x);}
    if(!Pg428ColdBootPreparation.newBoot("58006280-5301-4a1b-a0c2-66bce4a8a38e"))throw new AssertionError("actual new boot");count++;
    for(String boot:Arrays.asList(null,"9024b59c-41d0-4dbd-8a3e-96bfad1467c0","58006280-5301-4a1b-a0c2-66bce4a8a38f","")) {
      if(Pg428ColdBootPreparation.newBoot(boot))throw new AssertionError("other boot");count++;
    }
    System.out.println("PG428_COLD_BOOT_TOOL independentAssertions="+count+" success=true productionTestCount=0");
  }
}
