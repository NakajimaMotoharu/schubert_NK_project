import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;
/** Literal independent completed-original/order/refusal vectors; tool assertions, PT0. */
public final class Pg471CompletedDeploymentTest {
  static int count;
  static void check(boolean b){count++;if(!b)throw new AssertionError("completed vector "+count);}
  static MaintenanceRunFiles.StartupOriginal original(UUID run,UUID activation,String ended,MaintenanceCompletion.Outcome outcome){
    var a=new MaintenanceActivation(new BatchRun(run,Instant.parse("2026-09-27T15:00:00Z")),activation);
    return new MaintenanceRunFiles.StartupOriginal(a,ended==null?Optional.empty():Optional.of(new MaintenanceCompletion(a,Instant.parse(ended),outcome)));
  }
  public static void main(String[] args)throws Exception{
    for(String v:List.of("verify","activate"))check(Pg471CompletedDeployment.arguments(new String[]{v}));
    check(!Pg471CompletedDeployment.arguments(null));check(!Pg471CompletedDeployment.arguments(new String[]{}));check(!Pg471CompletedDeployment.arguments(new String[]{null}));
    for(String v:List.of("","start","restore","migrate","Activate"," verify"))check(!Pg471CompletedDeployment.arguments(new String[]{v}));
    check(!Pg471CompletedDeployment.arguments(new String[]{"verify","extra"}));
    UUID run=UUID.fromString("31100027-2222-4333-8444-555555555555"),activation=UUID.fromString("5c87de9a-ec69-492b-a6e2-9926b9f7cac7"),foreign=UUID.fromString("22222222-2222-4333-8444-555555555555");
    check(!Pg471CompletedDeployment.normalDone(null));
    check(!Pg471CompletedDeployment.normalDone(original(run,activation,null,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String instant:List.of("2026-10-05T16:34:20Z","2026-10-05T16:55:12.310761Z","2026-10-05T17:04:21Z"))check(Pg471CompletedDeployment.normalDone(original(run,activation,instant,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String instant:List.of("2026-10-05T16:34:19.999999Z","2026-10-05T17:04:21.000001Z"))check(!Pg471CompletedDeployment.normalDone(original(run,activation,instant,MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg471CompletedDeployment.normalDone(original(run,activation,"2026-10-05T16:55:12Z",MaintenanceCompletion.Outcome.WARNING)));
    check(!Pg471CompletedDeployment.normalDone(original(foreign,activation,"2026-10-05T16:55:12Z",MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg471CompletedDeployment.normalDone(original(run,foreign,"2026-10-05T16:55:12Z",MaintenanceCompletion.Outcome.SUCCESS)));
    UUID epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");var history=new HashSet<String>();
    for(int n=1;n<=10;n++)for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))history.add(String.format(java.util.Locale.ROOT,"%08d",n)+"-2222-4333-8444-555555555555"+suffix);
    var full=new HashSet<>(history);full.addAll(Set.of("epoch.current","11111111-2222-4333-8444-555555555555.permit","11111111-2222-4333-8444-555555555555.owner","11111111-2222-4333-8444-555555555555.API.launch","11111111-2222-4333-8444-555555555555.WEB.launch"));
    check(Pg471CompletedDeployment.names(full,history,epoch));check(!Pg471CompletedDeployment.names(null,history,epoch));check(!Pg471CompletedDeployment.names(full,null,epoch));check(!Pg471CompletedDeployment.names(full,history,null));
    for(String name:full){var missing=new HashSet<>(full);missing.remove(name);check(!Pg471CompletedDeployment.names(missing,history,epoch));}
    for(String name:List.of("foreign","publication.current",epoch+".API.start.intent",epoch+".WEB.start.intent",epoch+".publication.intent")){var plus=new HashSet<>(full);plus.add(name);check(!Pg471CompletedDeployment.names(plus,history,epoch));}
    var order=List.of("caddy.service","schubert-nk-web.service","schubert-nk-api.service","schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service","schubert-nk-expiry-cleanup.service","schubert-nk-backup.service","artemis.service");
    var observed=new ArrayList<String>();Pg471CompletedDeployment.stopOwned(observed::add);check(observed.equals(order));
    for(int at=0;at<order.size();at++){
      int index=at;var calls=new ArrayList<String>();var failure=new Exception("fixed stop fault");
      try{Pg471CompletedDeployment.stopOwned(unit->{calls.add(unit);if(calls.size()==index+1)throw failure;});throw new AssertionError("fault missing");}
      catch(Exception actual){check(actual==failure && calls.equals(order.subList(0,index+1)));}
    }
    check(Pg471CompletedDeployment.SOURCE.equals("717d72dd844fff286b4c696b9d08c41b136f0a6c"));check(Pg471CompletedDeployment.DIGEST.equals("47f7a338de848c83e96d2fc8208a9eade43e9d4e5218c79b3834603e27648b18"));
    var live=new HashMap<String,String>(Map.of("LoadState","loaded","Result","success","ControlPID","0","Job","","MainPID","2004047","InvocationID","5382161425dd4edcac8758357f747c0e","ActiveState","active","SubState","running"));
    String peer="2004047:5382161425dd4edcac8758357f747c0e";check(Pg471CompletedDeployment.capturedNormal(live,peer));check(!Pg471CompletedDeployment.capturedNormal(null,peer));
    for(String key:live.keySet()){var missing=new HashMap<>(live);missing.remove(key);check(!Pg471CompletedDeployment.capturedNormal(missing,peer));var changed=new HashMap<>(live);changed.put(key,"unknown");check(!Pg471CompletedDeployment.capturedNormal(changed,peer));}
    check(!Pg471CompletedDeployment.capturedNormal(live,"2004048:5382161425dd4edcac8758357f747c0e"));check(!Pg471CompletedDeployment.capturedNormal(live,"2004047:0382161425dd4edcac8758357f747c0e"));
    var completed=new HashMap<>(live);completed.put("MainPID","0");completed.put("ActiveState","active");completed.put("SubState","exited");completed.put("ExecMainCode","1");completed.put("ExecMainStatus","0");check(Pg471CompletedDeployment.capturedNormal(completed,null));
    for(String key:List.of("ExecMainCode","ExecMainStatus","Result","ControlPID","Job")){var bad=new HashMap<>(completed);bad.put(key,"unknown");check(!Pg471CompletedDeployment.capturedNormal(bad,null));}
    completed.put("ActiveState","inactive");completed.put("SubState","dead");check(Pg471CompletedDeployment.capturedNormal(completed,null));completed.put("Result","timeout");check(!Pg471CompletedDeployment.capturedNormal(completed,null));
    System.out.println("PG471_COMPLETED_TOOL_PASS independentAssertions="+count+" productionPT0=true nativeMutation=false");
  }
}
