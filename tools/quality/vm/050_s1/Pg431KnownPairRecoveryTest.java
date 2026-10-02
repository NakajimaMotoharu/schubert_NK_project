import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Independent public manager literals and private captured observation mutations; tool PT only. */
public final class Pg431KnownPairRecoveryTest {
  static int assertions;
  static List<Pg410KnownAuthRecovery.Receipt> receipts() {
    var result=new ArrayList<Pg410KnownAuthRecovery.Receipt>();
    String[] names={"morning-controller","api","web"}, invocations={"334c1680493c41719f556f6eea92fadc","61b650cebb7d42ab95cf96a12ee58a67","a3437b2c9efb40c88bae8949dd6ae46a"}, exits={"30","143","50"};
    var targets=List.of(dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot.Target.MORNING,
        dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot.Target.API,dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot.Target.WEB);
    for(int i=0;i<3;i++) {
      String literal="Id=schubert-nk-"+names[i]+".service\nLoadState=loaded\nActiveState=failed\nSubState=failed\nJob=\nInvocationID="+invocations[i]
          +"\nType="+(i==0?"oneshot":"simple")+"\nRestart="+(i==0?"no":"on-failure")
          +"\nRemainAfterExit=no\nMainPID=0\nControlPID=0\nResult=exit-code\nExecMainStartTimestampMonotonic=100\nExecMainExitTimestampMonotonic=200\nExecMainCode=1\nExecMainStatus="+exits[i]+"\nKillMode=control-group\nSendSIGKILL=no\n";
      result.add(Pg410KnownAuthRecovery.parsed(literal.getBytes(StandardCharsets.US_ASCII),targets.get(i)));
    }return result;
  }
  static void expect(boolean wanted,List<Pg410KnownAuthRecovery.Receipt> value) {
    if(Pg431KnownPairRecovery.known(value)!=wanted)throw new AssertionError("independent manager result");assertions++;
  }
  public static void main(String[] args) throws Exception {
    var good=receipts();expect(true,good);expect(false,null);expect(false,List.of());expect(false,good.subList(0,2));
    for(int index=0;index<3;index++) {
      var base=good.get(index);
      for(String field:base.values().keySet()) {
        var values=new HashMap<>(base.values());values.remove(field);var changed=new ArrayList<>(good);
        changed.set(index,new Pg410KnownAuthRecovery.Receipt(base.raw(),values,base.snapshot()));expect(false,changed);
      }
      for(String field:List.of("Id","InvocationID","ExecMainCode","ExecMainStatus","Result","LoadState","MainPID","ControlPID","Job")) {
        var values=new HashMap<>(base.values());values.put(field,"unknown");var changed=new ArrayList<>(good);
        changed.set(index,new Pg410KnownAuthRecovery.Receipt(base.raw(),values,base.snapshot()));expect(false,changed);
      }
    }
    if(args.length==1) {
      byte[] actual=Files.readAllBytes(Path.of(args[0]));
      if(!Pg410KnownAuthRecovery.hash(actual).equals("af8a802001783fd5a3c3e8766b52fc943e81f4a9b6fb2b4f2cd40d694185fee0"))throw new AssertionError("fixed captured SHA");
      Pg431KnownPairRecovery.watch(actual);assertions++;
      for(String bad:List.of("RootServiceLauncher","ApiProcessMain","WebProcessMain","NoNewPrivs","Groups","schema","848428","849540")) {
        String changed=new String(actual,StandardCharsets.UTF_8).replace(bad,"unknown");
        try {Pg431KnownPairRecovery.watch(changed.getBytes(StandardCharsets.UTF_8));throw new AssertionError("changed observation accepted "+bad);}
        catch(IllegalStateException | IllegalArgumentException | com.google.gson.JsonParseException expected){assertions++;}
      }
    }else throw new AssertionError("captured private proof input required");
    System.out.println("PG431_PAIR_TOOL success=true independentAssertions="+assertions+" productionTestCount=0 nativeAuthorityClaimed=false");
  }
}
