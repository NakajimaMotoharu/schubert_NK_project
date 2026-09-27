import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.time.Instant;
import java.util.UUID;

/** NATIVE027: real root M/LoadCredential/role/session lock/legacy check before durable run start.
 * Leaves genuine pending original for the continuing morning path. No fabricated .done/DB step.
 */
public final class NativeRootMorningRunProbe {
  public static void main(String[] args) throws Exception {
    if(args.length!=0 || LinuxInodeSecurity.create().effectiveUid()!=0 ||
       !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new AssertionError("isolated root VM only");
    Thread.currentThread().setUncaughtExceptionHandler((thread,failure)->System.err.println("PT-OPS-NATIVE-027 REFUSED diagnosticsRedacted=true"));
    var context=RootStartupContext.create();
    var expected=context.capture(RootStartupContext.Service.MORNING);
    var database=new MorningDatabaseSession("jdbc:postgresql://127.0.0.1:5432/schubert_nk",context,expected);
    var run=new BatchRun(UUID.fromString("31100027-2222-4333-8444-555555555555"),Instant.parse("2026-09-27T15:00:00Z"));
    var activation=UUID.fromString("31100027-6666-4777-8888-999999999999");
    var result=MaintenanceFileLock.create().tryExclusive(()->{
      context.recheck(expected);
      Path location=ServiceCredentialLocation.read(System.getenv()).directory();
      if(!location.equals(Path.of("/run/credentials/schubert-nk-morning-controller.service")))throw new AssertionError("fixed root credential namespace required");
      var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),location);
      return ResourceScope.use(root::close,()->database.execute(new RootBatchCredentialReader(root,LinuxInodeSecurity.create()).read(),session->{
        session.requireUnused(run);
        context.recheck(expected);
        var original=MaintenanceRunFiles.create().execute(records->records.start(run,activation));
        if(!original.activation().run().equals(run)||!original.activation().id().equals(activation))throw new AssertionError("original mismatch");
        context.recheck(expected);
        return Boolean.TRUE;
      }));
    });
    if(!result.orElseThrow())throw new AssertionError("M contention");
    context.recheck(expected);
    System.out.println("PT-OPS-NATIVE-027 PASS actualRootMorningContext=true actualM=true actualRootLoadCredential=true fixedDbRole=true sessionAdvisory=true legacyAbsentBeforeOriginal=true durableOriginalPending=true dbBackupBegins=false fullSchemaBomAdmission=false fullParentBackup=false fullBusinessGate=false");
  }
}
