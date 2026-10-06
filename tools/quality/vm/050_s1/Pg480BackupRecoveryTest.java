import dev.codex.schubert.nk.batch.file.StartupPermitRecords;
import dev.codex.schubert.nk.batch.repository.*;
import java.time.Instant;
import java.util.*;
/** BREC198009 independent fixed public records, not VM authority. */
public final class Pg480BackupRecoveryTest {
  static int n;
  static void check(boolean value){if(!value)throw new AssertionError("fixed recovery oracle");n++;}
  public static void main(String[] args){
    check(!Pg480BackupRecovery.arguments(null));check(!Pg480BackupRecovery.arguments(new String[0]));
    check(!Pg480BackupRecovery.arguments(new String[]{null}));check(!Pg480BackupRecovery.arguments(new String[]{"activate"}));
    check(!Pg480BackupRecovery.arguments(new String[]{"retire","extra"}));
    check(Pg480BackupRecovery.arguments(new String[]{"retire"}));check(Pg480BackupRecovery.arguments(new String[]{"verify"}));
    UUID boot=UUID.fromString("e07aa706-1acd-4e65-b309-d7f330f79d54"),epoch=UUID.fromString("11111111-2222-4333-8444-555555555555");
    var activation=new MaintenanceActivation(new BatchRun(UUID.fromString("49437eda-1681-43a9-883a-424eb55a6166"),Instant.parse("2026-10-06T06:28:43.734078Z")),UUID.fromString("21111111-2222-4333-8444-555555555555"));
    check(!Pg480BackupRecovery.pending(null));
    check(Pg480BackupRecovery.pending(new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,boot,epoch,activation,Optional.empty())));
    check(!Pg480BackupRecovery.pending(new StartupPermitRecords.Epoch(StartupPermitRecords.State.ISSUED,boot,epoch,activation,Optional.of("a".repeat(64)))));
    check(!Pg480BackupRecovery.pending(new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,epoch,epoch,activation,Optional.empty())));
    check(!Pg480BackupRecovery.pending(new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,boot,epoch,new MaintenanceActivation(new BatchRun(epoch,activation.run().cutoff()),activation.id()),Optional.empty())));
    for(long delta:new long[]{-1000,1000})check(!Pg480BackupRecovery.pending(new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,boot,epoch,new MaintenanceActivation(new BatchRun(activation.run().id(),activation.run().cutoff().plusNanos(delta)),activation.id()),Optional.empty())));
    System.out.println("PG480_RECOVERY_ORACLE assertions="+n+" actual0=true vmAuthority0=true");
  }
}
