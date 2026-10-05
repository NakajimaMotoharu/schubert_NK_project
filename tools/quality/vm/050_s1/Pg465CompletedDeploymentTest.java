import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;
/** Literal independent completed-original/order/refusal vectors; tool assertions, PT0. */
public final class Pg465CompletedDeploymentTest {
  static int count;
  static void check(boolean b){count++;if(!b)throw new AssertionError("completed vector "+count);}
  static MaintenanceRunFiles.StartupOriginal original(UUID run,UUID activation,String ended,MaintenanceCompletion.Outcome outcome){
    var a=new MaintenanceActivation(new BatchRun(run,Instant.parse("2026-09-27T15:00:00Z")),activation);
    return new MaintenanceRunFiles.StartupOriginal(a,ended==null?Optional.empty():Optional.of(new MaintenanceCompletion(a,Instant.parse(ended),outcome)));
  }
  public static void main(String[] args)throws Exception{
    for(String v:List.of("verify","activate"))check(Pg465CompletedDeployment.arguments(new String[]{v}));
    check(!Pg465CompletedDeployment.arguments(null));check(!Pg465CompletedDeployment.arguments(new String[]{}));check(!Pg465CompletedDeployment.arguments(new String[]{null}));
    for(String v:List.of("","start","restore","migrate","Activate"," verify"))check(!Pg465CompletedDeployment.arguments(new String[]{v}));
    check(!Pg465CompletedDeployment.arguments(new String[]{"verify","extra"}));
    UUID run=UUID.fromString("31100027-2222-4333-8444-555555555555"),activation=UUID.fromString("31100027-6666-4777-8888-999999999999"),foreign=UUID.fromString("22222222-2222-4333-8444-555555555555");
    check(!Pg465CompletedDeployment.normalDone(null));
    check(!Pg465CompletedDeployment.normalDone(original(run,activation,null,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String instant:List.of("2026-10-05T00:35:52Z","2026-10-05T00:42:36.918Z","2026-10-05T00:42:37Z"))check(Pg465CompletedDeployment.normalDone(original(run,activation,instant,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String instant:List.of("2026-10-05T00:35:51.999999Z","2026-10-05T00:42:37.000001Z"))check(!Pg465CompletedDeployment.normalDone(original(run,activation,instant,MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg465CompletedDeployment.normalDone(original(run,activation,"2026-10-05T00:42:36Z",MaintenanceCompletion.Outcome.WARNING)));
    check(!Pg465CompletedDeployment.normalDone(original(foreign,activation,"2026-10-05T00:42:36Z",MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg465CompletedDeployment.normalDone(original(run,foreign,"2026-10-05T00:42:36Z",MaintenanceCompletion.Outcome.SUCCESS)));
    UUID epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");var history=new HashSet<String>();
    for(int n=1;n<=7;n++)for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))history.add("0000000"+n+"-2222-4333-8444-555555555555"+suffix);
    var full=new HashSet<>(history);full.addAll(Set.of("epoch.current","11111111-2222-4333-8444-555555555555.permit","11111111-2222-4333-8444-555555555555.owner","11111111-2222-4333-8444-555555555555.API.launch","11111111-2222-4333-8444-555555555555.WEB.launch"));
    check(Pg465CompletedDeployment.names(full,history,epoch));check(!Pg465CompletedDeployment.names(null,history,epoch));check(!Pg465CompletedDeployment.names(full,null,epoch));check(!Pg465CompletedDeployment.names(full,history,null));
    for(String name:full){var missing=new HashSet<>(full);missing.remove(name);check(!Pg465CompletedDeployment.names(missing,history,epoch));}
    for(String name:List.of("foreign","publication.current",epoch+".API.start.intent",epoch+".WEB.start.intent",epoch+".publication.intent")){var plus=new HashSet<>(full);plus.add(name);check(!Pg465CompletedDeployment.names(plus,history,epoch));}
    var order=List.of("caddy.service","schubert-nk-web.service","schubert-nk-api.service","schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service","schubert-nk-expiry-cleanup.service","schubert-nk-backup.service","artemis.service");
    var observed=new ArrayList<String>();Pg465CompletedDeployment.stopOwned(observed::add);check(observed.equals(order));
    for(int at=0;at<order.size();at++){
      int index=at;var calls=new ArrayList<String>();var failure=new Exception("fixed stop fault");
      try{Pg465CompletedDeployment.stopOwned(unit->{calls.add(unit);if(calls.size()==index+1)throw failure;});throw new AssertionError("fault missing");}
      catch(Exception actual){check(actual==failure && calls.equals(order.subList(0,index+1)));}
    }
    check(Pg465CompletedDeployment.SOURCE.equals("df9a33febf3703f0d18ac2c4ef56fd0225aac2b9"));check(Pg465CompletedDeployment.DIGEST.equals("8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e"));
    var live=new HashMap<String,String>(Map.of("LoadState","loaded","Result","success","ControlPID","0","Job","","MainPID","1338494","InvocationID","9269078370384fdaab05ca9a0fcd50bd","ActiveState","active","SubState","running"));
    String peer="1338494:9269078370384fdaab05ca9a0fcd50bd";check(Pg465CompletedDeployment.capturedNormal(live,peer));check(!Pg465CompletedDeployment.capturedNormal(null,peer));
    for(String key:live.keySet()){var missing=new HashMap<>(live);missing.remove(key);check(!Pg465CompletedDeployment.capturedNormal(missing,peer));var changed=new HashMap<>(live);changed.put(key,"unknown");check(!Pg465CompletedDeployment.capturedNormal(changed,peer));}
    check(!Pg465CompletedDeployment.capturedNormal(live,"1338495:9269078370384fdaab05ca9a0fcd50bd"));check(!Pg465CompletedDeployment.capturedNormal(live,"1338494:0269078370384fdaab05ca9a0fcd50bd"));
    var completed=new HashMap<>(live);completed.put("MainPID","0");completed.put("ActiveState","active");completed.put("SubState","exited");completed.put("ExecMainCode","1");completed.put("ExecMainStatus","0");check(Pg465CompletedDeployment.capturedNormal(completed,null));
    for(String key:List.of("ExecMainCode","ExecMainStatus","Result","ControlPID","Job")){var bad=new HashMap<>(completed);bad.put(key,"unknown");check(!Pg465CompletedDeployment.capturedNormal(bad,null));}
    completed.put("ActiveState","inactive");completed.put("SubState","dead");check(Pg465CompletedDeployment.capturedNormal(completed,null));completed.put("Result","timeout");check(!Pg465CompletedDeployment.capturedNormal(completed,null));
    System.out.println("PG465_COMPLETED_TOOL_PASS independentAssertions="+count+" productionPT0=true nativeMutation=false");
  }
}
