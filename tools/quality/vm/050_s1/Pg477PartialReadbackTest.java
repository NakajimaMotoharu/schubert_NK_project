import dev.codex.schubert.nk.batch.file.StartupPermitRecords;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;
/** Fixed independent INVALID transition vectors; no file/DB/M-A/native actions. */
public final class Pg477PartialReadbackTest {
  static int count;
  static void check(boolean value){count++;if(!value)throw new AssertionError("partial epoch oracle");}
  public static void main(String[] args){
    var boot=UUID.fromString("e07aa706-1acd-4e65-b309-d7f330f79d54");
    var oldId=UUID.fromString("11111111-2222-4333-8444-555555555555");
    var nextId=UUID.fromString("22222222-2222-4333-8444-555555555555");
    var activation=new MaintenanceActivation(new BatchRun(UUID.fromString("31100027-2222-4333-8444-555555555555"),Instant.parse("2026-09-27T15:00:00Z")),UUID.fromString("33333333-2222-4333-8444-555555555555"));
    var before=new StartupPermitRecords.Epoch(StartupPermitRecords.State.ISSUED,boot,oldId,activation,Optional.of("0".repeat(64)));
    var after=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,boot,nextId,activation,Optional.empty());
    check(Pg477PartialReadback.partialEpoch(before,after));
    check(!Pg477PartialReadback.partialEpoch(null,after));check(!Pg477PartialReadback.partialEpoch(before,null));
    check(!Pg477PartialReadback.partialEpoch(before,before));check(!Pg477PartialReadback.partialEpoch(after,after));
    check(!Pg477PartialReadback.partialEpoch(before,new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,boot,oldId,activation,Optional.empty())));
    check(!Pg477PartialReadback.partialEpoch(before,new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,nextId,nextId,activation,Optional.empty())));
    var other=new MaintenanceActivation(activation.run(),nextId);
    check(!Pg477PartialReadback.partialEpoch(before,new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,boot,nextId,other,Optional.empty())));
    for(String mode:List.of("verify","snapshot"))check(Pg477PartialReadback.arguments(new String[]{mode}));
    check(!Pg477PartialReadback.arguments(null));check(!Pg477PartialReadback.arguments(new String[0]));check(!Pg477PartialReadback.arguments(new String[]{null}));
    for(String mode:List.of("restore","activate","start","stop","Verify",""))check(!Pg477PartialReadback.arguments(new String[]{mode}));
    check(!Pg477PartialReadback.arguments(new String[]{"verify","extra"}));
    System.out.println("PG477_PARTIAL_READBACK_TEST independentAssertions="+count+" productionPT0=true mutation0=true");
  }
}
