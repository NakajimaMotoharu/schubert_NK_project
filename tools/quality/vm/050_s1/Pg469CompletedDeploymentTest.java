import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;
/** Literal independent completed-original/order/refusal vectors; tool assertions, PT0. */
public final class Pg469CompletedDeploymentTest {
  static int count;
  static void check(boolean b){count++;if(!b)throw new AssertionError("completed vector "+count);}
  static MaintenanceRunFiles.StartupOriginal original(UUID run,UUID activation,String ended,MaintenanceCompletion.Outcome outcome){
    var a=new MaintenanceActivation(new BatchRun(run,Instant.parse("2026-09-27T15:00:00Z")),activation);
    return new MaintenanceRunFiles.StartupOriginal(a,ended==null?Optional.empty():Optional.of(new MaintenanceCompletion(a,Instant.parse(ended),outcome)));
  }
  public static void main(String[] args)throws Exception{
    for(String v:List.of("verify","activate"))check(Pg469CompletedDeployment.arguments(new String[]{v}));
    check(!Pg469CompletedDeployment.arguments(null));check(!Pg469CompletedDeployment.arguments(new String[]{}));check(!Pg469CompletedDeployment.arguments(new String[]{null}));
    for(String v:List.of("","start","restore","migrate","Activate"," verify"))check(!Pg469CompletedDeployment.arguments(new String[]{v}));
    check(!Pg469CompletedDeployment.arguments(new String[]{"verify","extra"}));
    UUID run=UUID.fromString("31100027-2222-4333-8444-555555555555"),activation=UUID.fromString("1f026aa2-899a-4f22-aca9-32f4918a03c8"),foreign=UUID.fromString("22222222-2222-4333-8444-555555555555");
    check(!Pg469CompletedDeployment.normalDone(null));
    check(!Pg469CompletedDeployment.normalDone(original(run,activation,null,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String instant:List.of("2026-10-05T05:33:53Z","2026-10-05T05:40:38.206452Z","2026-10-05T05:51:12Z"))check(Pg469CompletedDeployment.normalDone(original(run,activation,instant,MaintenanceCompletion.Outcome.SUCCESS)));
    for(String instant:List.of("2026-10-05T05:33:52.999999Z","2026-10-05T05:51:12.000001Z"))check(!Pg469CompletedDeployment.normalDone(original(run,activation,instant,MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg469CompletedDeployment.normalDone(original(run,activation,"2026-10-05T05:40:38Z",MaintenanceCompletion.Outcome.WARNING)));
    check(!Pg469CompletedDeployment.normalDone(original(foreign,activation,"2026-10-05T05:40:38Z",MaintenanceCompletion.Outcome.SUCCESS)));
    check(!Pg469CompletedDeployment.normalDone(original(run,foreign,"2026-10-05T05:40:38Z",MaintenanceCompletion.Outcome.SUCCESS)));
    UUID epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");var history=new HashSet<String>();
    for(int n=1;n<=9;n++)for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))history.add("0000000"+n+"-2222-4333-8444-555555555555"+suffix);
    var full=new HashSet<>(history);full.addAll(Set.of("epoch.current","11111111-2222-4333-8444-555555555555.permit","11111111-2222-4333-8444-555555555555.owner","11111111-2222-4333-8444-555555555555.API.launch","11111111-2222-4333-8444-555555555555.WEB.launch"));
    check(Pg469CompletedDeployment.names(full,history,epoch));check(!Pg469CompletedDeployment.names(null,history,epoch));check(!Pg469CompletedDeployment.names(full,null,epoch));check(!Pg469CompletedDeployment.names(full,history,null));
    for(String name:full){var missing=new HashSet<>(full);missing.remove(name);check(!Pg469CompletedDeployment.names(missing,history,epoch));}
    for(String name:List.of("foreign","publication.current",epoch+".API.start.intent",epoch+".WEB.start.intent",epoch+".publication.intent")){var plus=new HashSet<>(full);plus.add(name);check(!Pg469CompletedDeployment.names(plus,history,epoch));}
    var order=List.of("caddy.service","schubert-nk-web.service","schubert-nk-api.service","schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service","schubert-nk-expiry-cleanup.service","schubert-nk-backup.service","artemis.service");
    var observed=new ArrayList<String>();Pg469CompletedDeployment.stopOwned(observed::add);check(observed.equals(order));
    for(int at=0;at<order.size();at++){
      int index=at;var calls=new ArrayList<String>();var failure=new Exception("fixed stop fault");
      try{Pg469CompletedDeployment.stopOwned(unit->{calls.add(unit);if(calls.size()==index+1)throw failure;});throw new AssertionError("fault missing");}
      catch(Exception actual){check(actual==failure && calls.equals(order.subList(0,index+1)));}
    }
    check(Pg469CompletedDeployment.SOURCE.equals("d3bba6db6eb9fec13e4847a10541cf337f575731"));check(Pg469CompletedDeployment.DIGEST.equals("cc5e4dd7ca70d3a21e1145dd35b9f047856c4ab83bfac6f11722663ba7744462"));
    var live=new HashMap<String,String>(Map.of("LoadState","loaded","Result","success","ControlPID","0","Job","","MainPID","1747577","InvocationID","385f36f479ee4033b76453f01aea13e3","ActiveState","active","SubState","running"));
    String peer="1747577:385f36f479ee4033b76453f01aea13e3";check(Pg469CompletedDeployment.capturedNormal(live,peer));check(!Pg469CompletedDeployment.capturedNormal(null,peer));
    for(String key:live.keySet()){var missing=new HashMap<>(live);missing.remove(key);check(!Pg469CompletedDeployment.capturedNormal(missing,peer));var changed=new HashMap<>(live);changed.put(key,"unknown");check(!Pg469CompletedDeployment.capturedNormal(changed,peer));}
    check(!Pg469CompletedDeployment.capturedNormal(live,"1747578:385f36f479ee4033b76453f01aea13e3"));check(!Pg469CompletedDeployment.capturedNormal(live,"1747577:085f36f479ee4033b76453f01aea13e3"));
    var completed=new HashMap<>(live);completed.put("MainPID","0");completed.put("ActiveState","active");completed.put("SubState","exited");completed.put("ExecMainCode","1");completed.put("ExecMainStatus","0");check(Pg469CompletedDeployment.capturedNormal(completed,null));
    for(String key:List.of("ExecMainCode","ExecMainStatus","Result","ControlPID","Job")){var bad=new HashMap<>(completed);bad.put(key,"unknown");check(!Pg469CompletedDeployment.capturedNormal(bad,null));}
    completed.put("ActiveState","inactive");completed.put("SubState","dead");check(Pg469CompletedDeployment.capturedNormal(completed,null));completed.put("Result","timeout");check(!Pg469CompletedDeployment.capturedNormal(completed,null));
    System.out.println("PG469_COMPLETED_TOOL_PASS independentAssertions="+count+" productionPT0=true nativeMutation=false");
  }
}
