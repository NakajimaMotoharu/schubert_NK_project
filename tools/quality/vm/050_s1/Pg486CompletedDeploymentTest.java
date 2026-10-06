import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;

/** DONE485001/003: independent literal completed values; no host/VM authority. */
public final class Pg486CompletedDeploymentTest {
  static int checks;
  static void check(boolean v){checks++;if(!v)throw new AssertionError("completed vector "+checks);}
  static MaintenanceRunFiles.StartupOriginal original(String run,String cutoff,String ended,MaintenanceCompletion.Outcome outcome){
    var activation=new MaintenanceActivation(new BatchRun(UUID.fromString(run),Instant.parse(cutoff)),UUID.fromString("33333333-2222-4333-8444-555555555555"));
    return new MaintenanceRunFiles.StartupOriginal(activation,ended==null?Optional.empty():Optional.of(new MaintenanceCompletion(activation,Instant.parse(ended),outcome)));
  }
  public static void main(String[] args){
    String source="1".repeat(40),digest="2".repeat(64),run="49437eda-1681-43a9-883a-424eb55a6166",cutoff="2026-10-06T06:28:43.734078Z";
    check(Pg486CompletedDeployment.arguments(new String[]{"activate",source,digest}));
    for(String[] bad:new String[][]{null,{}, {null,source,digest},{"activate",null,digest},{"activate",source,null},{"verify",source,digest},{"restore",source,digest},{"activate",source+"a",digest},{"activate",source,digest+"a"},{"activate","z".repeat(40),digest},{"activate",source,"Z".repeat(64)},{"activate",source,digest,"extra"}})check(!Pg486CompletedDeployment.arguments(bad));
    check(!Pg486CompletedDeployment.normalDone(null));
    check(!Pg486CompletedDeployment.normalDone(original(run,cutoff,null,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String ended:List.of("2026-10-06T08:22:25Z","2026-10-06T08:47:59Z","2026-10-06T08:52:26Z"))check(Pg486CompletedDeployment.normalDone(original(run,cutoff,ended,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String ended:List.of("2026-10-06T08:22:24.999999Z","2026-10-06T08:52:26.000001Z"))check(!Pg486CompletedDeployment.normalDone(original(run,cutoff,ended,MaintenanceCompletion.Outcome.SUCCESS)));
    for(var outcome:MaintenanceCompletion.Outcome.values())check(Pg486CompletedDeployment.normalDone(original(run,cutoff,"2026-10-06T08:47:59Z",outcome))==(outcome==MaintenanceCompletion.Outcome.SUCCESS));
    check(!Pg486CompletedDeployment.normalDone(original("44444444-2222-4333-8444-555555555555",cutoff,"2026-10-06T08:47:59Z",MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg486CompletedDeployment.normalDone(original(run,"2026-10-06T06:28:43.734079Z","2026-10-06T08:47:59Z",MaintenanceCompletion.Outcome.SUCCESS)));
    check(Pg486CompletedDeployment.NEXT.toString().equals("/opt/schubert-nk/releases/0.1.0-PG486"));
    System.out.println("PG486_COMPLETED_VALUES assertions="+checks+" actual0=true authority0=true productionPT0=true");
  }
}
