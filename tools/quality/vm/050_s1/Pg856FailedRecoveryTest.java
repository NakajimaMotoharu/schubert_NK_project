import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;

/** SSC241/REC856001: independent actual generation/namespace/completion refusal oracle. */
public final class Pg856FailedRecoveryTest {
  static int count;
  static void check(boolean value){count++;if(!value)throw new AssertionError("REC856001");}
  public static void main(String[]args)throws Exception{
    var expected=new HashSet<String>();expected.add("epoch.current");
    for(var epoch:List.of("3c5cdcc5-204c-40fd-a731-996c6cd859e8","41691d5c-68c5-40c9-9bcc-899ce341df6b","538fe967-f9cb-4770-a03c-9bab715d0fdc","a3fd90d9-7470-4695-9ee8-c818fe19e42d","a46f1379-6025-4850-9930-658a72b0fa70","c84f3015-5f29-4844-868b-57de02b1b3fc","e45cbbc0-3eea-4b3b-bd00-2bb39e3ecc19","f5a2d1aa-3879-4f21-8e48-cfb40e48b677","e9f11f1c-f087-458a-aad0-8c1e4e140571","0eece14c-f832-47c2-b7dd-14125682e7ea","8b153538-1523-4987-a456-6cbea0d345ee"))
      for(var suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))expected.add(epoch+suffix);
    expected.add("0a87a07d-09cf-478d-b276-180df3977e6f.owner");expected.add("0a87a07d-09cf-478d-b276-180df3977e6f.permit");
    check(expected.size()==47);check(expected.equals(Pg856FailedRecovery.names()));check(expected.equals(Pg856FailedRecovery.retiredNames()));
    var activation=new MaintenanceActivation(new BatchRun(UUID.fromString("9de2d03c-28c7-4647-97d9-c66ace06048c"),Instant.parse("2026-10-09T05:42:22.532331Z")),UUID.fromString("021111b4-6de5-4733-917d-5ac176240ffc"));
    for(var outcome:MaintenanceCompletion.Outcome.values()){
      var completion=new MaintenanceCompletion(activation,Instant.parse("2026-10-09T15:32:00Z"),outcome);
      check(Pg856FailedRecovery.completedValue(new MaintenanceRunFiles.StartupOriginal(activation,Optional.of(completion)),activation));
    }
    check(!Pg856FailedRecovery.completedValue(new MaintenanceRunFiles.StartupOriginal(activation,Optional.empty()),activation));
    check(!Pg856FailedRecovery.completedValue(null,activation));check(!Pg856FailedRecovery.completedValue(new MaintenanceRunFiles.StartupOriginal(activation,Optional.empty()),null));
    var other=new MaintenanceActivation(activation.run(),UUID.fromString("00000000-0000-0000-0000-000000000001"));
    check(!Pg856FailedRecovery.completedValue(new MaintenanceRunFiles.StartupOriginal(activation,Optional.empty()),other));
    check(!Pg856FailedRecovery.parentValue(null));
    var parent=new HashMap<String,String>();for(var field:Pg410KnownAuthRecovery.FIELDS)parent.put(field,"");
    parent.put("InvocationID","9c08566fff9945a492eaae25559c3084");parent.put("Result","timeout");parent.put("ExecMainCode","1");parent.put("ExecMainStatus","143");parent.put("ActiveState","failed");parent.put("SubState","failed");parent.put("MainPID","0");parent.put("ControlPID","0");
    check(Pg856FailedRecovery.parentValue(parent));
    for(var entry:Map.of("InvocationID","7ea672e8a76c4a4a8a7994652366a4cc","Result","success","ExecMainCode","0","ExecMainStatus","0","MainPID","3417355","ControlPID","1","Job","1").entrySet()){
      var changed=new HashMap<>(parent);changed.put(entry.getKey(),entry.getValue());check(!Pg856FailedRecovery.parentValue(changed));
    }
    var missing=new HashMap<>(parent);missing.remove("Job");check(!Pg856FailedRecovery.parentValue(missing));
    var unknown=new HashMap<>(parent);unknown.put("extra","");check(!Pg856FailedRecovery.parentValue(unknown));
    System.out.println("REC856001 assertions="+count+" old143NotNormalized=true noIntentOperations=true");
  }
}
