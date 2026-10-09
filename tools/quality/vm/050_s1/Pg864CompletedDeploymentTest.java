import dev.codex.schubert.nk.batch.file.MaintenanceRunFiles;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;

/** Literal data oracle, never generated expected by Production. */
public final class Pg864CompletedDeploymentTest {
  static void require(boolean value){if(!value)throw new AssertionError("independent fixture refused");}
  public static void main(String[] ignored)throws Exception{
    for(String good:List.of("prepare-ro","verify","activate"))require(Pg864CompletedDeployment.arguments(new String[]{good}));
    for(String[] bad:new String[][]{null,{}, {null},{"unknown"},{"verify","activate"}})require(!Pg864CompletedDeployment.arguments(bad));
    var activation=new MaintenanceActivation(new BatchRun(UUID.fromString("9de2d03c-28c7-4647-97d9-c66ace06048c"),Instant.parse("2026-10-09T05:42:22.532331Z")),UUID.fromString("021111b4-6de5-4733-917d-5ac176240ffc"));
    var done=new MaintenanceCompletion(activation,Instant.parse("2026-10-09T15:32:16.513983Z"),MaintenanceCompletion.Outcome.SUCCESS);
    require(Pg864CompletedDeployment.completion(new MaintenanceRunFiles.StartupOriginal(activation,Optional.of(done))));
    require(!Pg864CompletedDeployment.completion(null));require(!Pg864CompletedDeployment.completion(new MaintenanceRunFiles.StartupOriginal(activation,Optional.empty())));
    for(var bad:List.of(new MaintenanceCompletion(activation,Instant.parse("2026-10-09T15:32:16.513984Z"),MaintenanceCompletion.Outcome.SUCCESS),new MaintenanceCompletion(activation,done.endedAt(),MaintenanceCompletion.Outcome.WARNING)))require(!Pg864CompletedDeployment.completion(new MaintenanceRunFiles.StartupOriginal(activation,Optional.of(bad))));
    var foreign=new MaintenanceActivation(activation.run(),UUID.fromString("11111111-2222-4333-8444-555555555555"));require(!Pg864CompletedDeployment.completion(new MaintenanceRunFiles.StartupOriginal(foreign,Optional.of(new MaintenanceCompletion(foreign,done.endedAt(),done.outcome())))));
    var events=new ArrayList<String>();Pg864CompletedDeployment.publications(step->events.add(step.name()));require(events.equals(List.of("EPOCH","APPROVAL","CURRENT")));
    for(String failure:List.of("EPOCH","APPROVAL","CURRENT"))for(int kind=0;kind<3;kind++){
      events.clear();int type=kind;
      boolean caught=false;
      try{Pg864CompletedDeployment.publications(step->{events.add(step.name());if(step.name().equals(failure)){switch(type){case 0->throw new java.io.IOException("literal IO");case 1->throw new IllegalStateException("literal state");default->throw new AssertionError("literal error");}}});}
      catch(java.io.IOException|IllegalStateException|AssertionError expected){caught=true;require(type==0?expected instanceof java.io.IOException:type==1?expected instanceof IllegalStateException:expected instanceof AssertionError);}
      require(caught);require(events.getLast().equals(failure));require(events.size()==List.of("EPOCH","APPROVAL","CURRENT").indexOf(failure)+1);
    }
    // MOUNT_ORACLE
    System.out.println("PG864_LITERAL_DATA_ORACLE PASS mutation0=true");
  }
}
