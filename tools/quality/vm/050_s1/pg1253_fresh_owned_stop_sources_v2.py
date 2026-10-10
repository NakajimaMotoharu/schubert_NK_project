"""BUG1068 full original tuple/UTC oracle called by actual verifyOriginal."""
from pg1247_fresh_owned_stop_sources import sources as previous,SOURCE,BEFORE,W,GUEST_BEFORE,OWNED

def sources():
    values={n.replace('1247','1253'):s.replace('Pg1247','Pg1253').replace('PG1247','PG1253').replace('pg1247','pg1253')for n,s in previous().items()}
    java=values['Pg1253NativeStop.java'];a=java.index('      require(epoch.state()==');b=java.index('      try(var entries=Files.list(',a)
    old=java[a:b]
    if '2026-10-10T17:37:58.505406Z'not in old:raise ValueError('fixed failed UTC boundary required')
    java=java[:a]+'      var done=MaintenanceRunFiles.create().execute(x->x.observeStartup(epoch.activation())).completed().orElseThrow();\n      verifyOriginalValues(epoch,done);\n'+java[b:]
    marker='  static void verifyOriginal()throws Exception{'
    if java.count(marker)!=1:raise ValueError('actual original verification call boundary required')
    java=java.replace(marker,VALUES+'\n'+marker)
    values['Pg1253NativeStop.java']=java;values['Pg1253OriginalTupleTest.java']=TEST
    for name,raw in values.items():
        if name.endswith('.py'):compile(raw,'<actual new UTC closure>','exec')
    return values

VALUES=r'''
  static void verifyOriginalValues(StartupPermitRecords.Epoch epoch,MaintenanceCompletion done){
    require(epoch!=null && done!=null);
    require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.boot().toString().equals("cbca8738-3b24-4090-b77c-bf029677cdd6")
      && epoch.activation().run().id().toString().equals("9f651096-aef9-4fba-90b0-a653e99f035a")
      && epoch.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-10T20:03:22.718197Z"))
      && epoch.activation().id().toString().equals("27accac0-c118-4c98-9244-02625a2d88a7")
      && done.activation().equals(epoch.activation()) && done.outcome()==MaintenanceCompletion.Outcome.SUCCESS
      && done.endedAt().equals(java.time.Instant.parse("2026-10-10T20:22:34.439375Z")));
  }
'''

TEST=r'''
import dev.codex.schubert.nk.batch.file.StartupPermitRecords;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;
public final class Pg1253OriginalTupleTest{
  private Pg1253OriginalTupleTest(){}
  static int checks;
  static final UUID BOOT=UUID.fromString("cbca8738-3b24-4090-b77c-bf029677cdd6");
  static final UUID RUN=UUID.fromString("9f651096-aef9-4fba-90b0-a653e99f035a");
  static final UUID ACT=UUID.fromString("27accac0-c118-4c98-9244-02625a2d88a7");
  static final UUID OTHER=UUID.fromString("ada3f7ff-8287-48d7-9ba9-5cce71f61bd3");
  static final Instant CUT=Instant.parse("2026-10-10T20:03:22.718197Z"),END=Instant.parse("2026-10-10T20:22:34.439375Z");
  static MaintenanceActivation act(UUID run,Instant cut,UUID id){return new MaintenanceActivation(new BatchRun(run,cut),id);}
  static StartupPermitRecords.Epoch epoch(StartupPermitRecords.State state,UUID boot,MaintenanceActivation a){return new StartupPermitRecords.Epoch(state,boot,OTHER,a,state==StartupPermitRecords.State.ISSUED?Optional.of("a".repeat(64)):Optional.empty());}
  static void rejected(StartupPermitRecords.Epoch e,MaintenanceCompletion d){try{Pg1253NativeStop.verifyOriginalValues(e,d);throw new AssertionError("foreign original tuple accepted");}catch(IllegalStateException wanted){checks++;}}
  public static void main(String[] ignored){
    var activation=act(RUN,CUT,ACT);var e=epoch(StartupPermitRecords.State.ISSUED,BOOT,activation);var d=new MaintenanceCompletion(activation,END,MaintenanceCompletion.Outcome.SUCCESS);
    Pg1253NativeStop.verifyOriginalValues(e,d);checks++;
    rejected(null,d);rejected(e,null);
    rejected(epoch(StartupPermitRecords.State.INVALID,BOOT,activation),d);rejected(epoch(StartupPermitRecords.State.ISSUED,OTHER,activation),d);
    for(var a:List.of(act(OTHER,CUT,ACT),act(RUN,CUT.minusNanos(1000),ACT),act(RUN,CUT.plusNanos(1000),ACT),act(RUN,CUT,OTHER))){rejected(epoch(StartupPermitRecords.State.ISSUED,BOOT,a),new MaintenanceCompletion(a,END,MaintenanceCompletion.Outcome.SUCCESS));rejected(e,new MaintenanceCompletion(a,END,MaintenanceCompletion.Outcome.SUCCESS));}
    for(var t:List.of(END.minusNanos(1000),END.plusNanos(1000),CUT)){rejected(e,new MaintenanceCompletion(activation,t,MaintenanceCompletion.Outcome.SUCCESS));}
    var old=act(OTHER,Instant.parse("2026-10-10T12:40:27.396847Z"),OTHER);rejected(e,new MaintenanceCompletion(old,Instant.parse("2026-10-10T17:37:58.505406Z"),MaintenanceCompletion.Outcome.SUCCESS));
    rejected(e,new MaintenanceCompletion(activation,END,MaintenanceCompletion.Outcome.WARNING));
    if(checks!=18)throw new AssertionError("independent tuple case count");
    System.out.println("PG1253_ORIGINAL_TUPLE independentChecks="+checks+" actualMethod=true io0=true");
  }
}
'''
