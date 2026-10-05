import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;

/** Literal source/DONE/metadata-order/UNKNOWN vectors. Tool assertions only, Production PT0. */
public final class Pg472StoppedDeploymentTest {
  static int checks;
  static void check(boolean value){checks++;if(!value)throw new AssertionError("stopped vector "+checks);}
  static MaintenanceRunFiles.StartupOriginal original(UUID run,UUID activation,String ended,MaintenanceCompletion.Outcome outcome){
    var value=new MaintenanceActivation(new BatchRun(run,Instant.parse("2026-09-27T15:00:00Z")),activation);
    return new MaintenanceRunFiles.StartupOriginal(value,ended==null?Optional.empty():Optional.of(new MaintenanceCompletion(value,Instant.parse(ended),outcome)));
  }
  public static void main(String[] args){
    check(Pg472StoppedDeployment.SOURCE.equals("c8ad413437be409f70ec37bdba33c5e3cd21790b"));
    check(Pg472StoppedDeployment.DIGEST.equals("8e6bc3c26c1d707b5873dd14c229d41fa129bf7e5547dacc2bbc3780a90df3f1"));
    check(Pg472StoppedDeployment.OLD_SOURCE.equals("717d72dd844fff286b4c696b9d08c41b136f0a6c"));
    for(String action:List.of("verify","activate"))check(Pg472StoppedDeployment.arguments(new String[]{action}));
    check(!Pg472StoppedDeployment.arguments(null));check(!Pg472StoppedDeployment.arguments(new String[0]));
    check(!Pg472StoppedDeployment.arguments(new String[]{null}));check(!Pg472StoppedDeployment.arguments(new String[]{"verify","extra"}));
    for(String action:List.of("","stop","start","restore","migrate","Activate"," verify"))check(!Pg472StoppedDeployment.arguments(new String[]{action}));
    UUID run=UUID.fromString("31100027-2222-4333-8444-555555555555"),activation=UUID.fromString("33333333-2222-4333-8444-555555555555"),foreign=UUID.fromString("44444444-2222-4333-8444-555555555555");
    check(!Pg472StoppedDeployment.normalDone(null));
    check(!Pg472StoppedDeployment.normalDone(original(run,activation,null,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String ended:List.of("2026-10-05T20:24:33Z","2026-10-05T20:46:56Z","2026-10-05T20:54:34Z"))check(Pg472StoppedDeployment.normalDone(original(run,activation,ended,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String ended:List.of("2026-10-05T20:24:32.999999Z","2026-10-05T20:54:34.000001Z"))check(!Pg472StoppedDeployment.normalDone(original(run,activation,ended,MaintenanceCompletion.Outcome.SUCCESS)));
    for(var outcome:MaintenanceCompletion.Outcome.values())check(Pg472StoppedDeployment.normalDone(original(run,activation,"2026-10-05T20:46:56Z",outcome))==(outcome==MaintenanceCompletion.Outcome.SUCCESS));
    check(!Pg472StoppedDeployment.normalDone(original(foreign,activation,"2026-10-05T20:46:56Z",MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg472StoppedDeployment.normalDone(original(run,UUID.fromString("5c87de9a-ec69-492b-a6e2-9926b9f7cac7"),"2026-10-05T20:46:56Z",MaintenanceCompletion.Outcome.SUCCESS)));
    var actual=Map.<String,Map<String,Object>>of("epoch.current",Map.of("uid",0,"mode",33152,"ino",42L),"literal.permit",Map.of("size",123L,"gid",0));
    String first="{epoch.current={uid=0, mode=33152, ino=42}, literal.permit={size=123, gid=0}}";
    String reordered="{literal.permit={gid=0, size=123}, epoch.current={ino=42, mode=33152, uid=0}}";
    check(Pg472StoppedDeployment.sameMetadata(actual,first));check(Pg472StoppedDeployment.sameMetadata(actual,reordered));
    check(!Pg472StoppedDeployment.sameMetadata(null,first));check(!Pg472StoppedDeployment.sameMetadata(actual,null));
    check(!Pg472StoppedDeployment.sameMetadata(actual,"{}"));
    check(!Pg472StoppedDeployment.sameMetadata(actual,first.replace("ino=42","ino=43")));
    check(!Pg472StoppedDeployment.sameMetadata(actual,first.replace("mode=33152","mode=33153")));
    check(!Pg472StoppedDeployment.sameMetadata(actual,first.replace("literal.permit","foreign.permit")));
    for(String stage:new String[]{null,"PREFLIGHT","BODY","DATABASE_SCOPE_CLOSE","A_SCOPE_CLOSE","M_SCOPE_CLOSE"}){
      var ordinary=new IllegalStateException("synthetic");var secondary=new IllegalStateException("synthetic");secondary.addSuppressed(new java.io.IOException("synthetic"));
      for(boolean changed:new boolean[]{false,true})for(Throwable failure:new Throwable[]{ordinary,secondary,new AssertionError("synthetic")})
        check(Pg472StoppedDeployment.retainRequired(stage,changed,failure)==(changed || (stage!=null && (stage.endsWith("_SCOPE_CLOSE") || failure instanceof Error || failure.getSuppressed().length>0))));
    }
    System.out.println("PG472_STOPPED_TEST independentAssertions="+checks+" mutation0=true productionPT0=true");
  }
}
