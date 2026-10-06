import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;

/** BREC198010-V01: fresh fixed DONE readback; no recovery, permit or start. */
public final class Pg481CompletedReadback {
  static String phase="PREFLIGHT";
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg481-completed-readback");
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed PG481 completed readback refused");}
  static void retain(Throwable failure){
    System.err.println("PG481_COMPLETED_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" scopesNotAssumedClosed=true");
    for(var f:failure.getStackTrace())if(f.getClassName().equals("Pg481CompletedReadback"))System.err.println("PG481_COMPLETED_FRAME method="+f.getMethodName()+" line="+f.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException interrupted){Thread.interrupted();}
  }
  static void body()throws Exception{
    Pg464CodeOnlyDeployment.configure("PG479","bab704707b8fd7e0dc7581c4489f0892236efe73",Path.of("/opt/schubert-nk/releases/0.1.0-PG479"));
    var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals("a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286") && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
    phase="ORIGINAL_AND_DB_SCOPE";
    var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
    try{
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
      require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.boot().toString().equals("e07aa706-1acd-4e65-b309-d7f330f79d54") && epoch.activation().run().id().toString().equals("49437eda-1681-43a9-883a-424eb55a6166") && epoch.activation().run().cutoff().equals(Instant.parse("2026-10-06T06:28:43.734078Z")));
      var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));var done=original.completed().orElseThrow();
      require(done.outcome()==MaintenanceCompletion.Outcome.SUCCESS && !done.endedAt().isBefore(Instant.parse("2026-10-06T08:22:25Z")) && !done.endedAt().isAfter(Instant.parse("2026-10-06T08:52:26Z")));
      var db=Pg407FailedRootRecovery.openDatabase();
      try{
        db.setReadOnly(true);db.setAutoCommit(false);
        try(var q=db.createStatement();var r=q.executeQuery("select pg_backend_pid(),set_config('application_name','PG481-completed-readback',false),pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(3) && !r.next());}
        var before=com.google.gson.JsonParser.parseString(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg478-newrun-preflight-v2/before.private.json"))).getAsJsonObject().getAsJsonObject("rows").getAsJsonArray("schubert.batch_runs");
        var expected=new HashMap<Long,com.google.gson.JsonElement>();for(var value:before)require(expected.put(value.getAsJsonObject().get("id").getAsLong(),value)==null);require(expected.size()==411);
        var newest=new HashMap<String,com.google.gson.JsonObject>();int preserved=0,abandoned=0;
        try(var q=db.createStatement();var r=q.executeQuery("select to_jsonb(t)::text from schubert.batch_runs t order by id")){
          while(r.next()){
            var value=com.google.gson.JsonParser.parseString(r.getString(1)).getAsJsonObject();long id=value.get("id").getAsLong();
            if(expected.containsKey(id)){require(expected.get(id).equals(value));preserved++;continue;}
            require(value.get("run_id").getAsString().equals("49437eda-1681-43a9-883a-424eb55a6166"));String step=value.get("step").getAsString();
            if(value.get("status").getAsString().equals("FAILED")){require(Set.of("BACKUP_DB","BACKUP_CONFIG").contains(step) && value.get("error_code").getAsString().equals("ABANDONED") && value.get("attempt").getAsInt()==1);abandoned++;}
            else require(newest.put(step,value)==null && value.get("status").getAsString().equals("SUCCESS"));
          }
        }
        require(preserved==411 && abandoned==2 && newest.keySet().equals(Set.of("BACKUP_DB","BACKUP_CONFIG","CLEAN_NOTIFICATION","CLEAN_QUESTION","CLEAN_SESSION","CLEAN_INBOX_OUTBOX","CLEAN_LOG","CLEAN_BATCH_RUN","CLEAN_TRANSFER","CLEAN_EXPIRY")));
        for(var entry:newest.entrySet()){
          long expectedCount=switch(entry.getKey()){case "BACKUP_DB"->1;case "BACKUP_CONFIG"->2;case "CLEAN_SESSION"->1382;case "CLEAN_INBOX_OUTBOX"->7;default->0;};
          var row=entry.getValue();require(row.get("target_count").getAsLong()==expectedCount && row.get("success_count").getAsLong()==expectedCount && row.get("failure_count").getAsLong()==0 && row.get("error_code").isJsonNull() && row.get("error_summary").isJsonNull() && !row.get("ended_at").isJsonNull());
        }
        for(String name:List.of("backup-request","cleanup-request","expiry-request"))try(var entries=Files.list(Path.of("/run/schubert-nk",name))){require(entries.findAny().isEmpty());}
        require(epoch.equals(files.current()) && done.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().orElseThrow()));
        phase="DB_SCOPE_CLOSE";db.rollback();db.close();
      }catch(Exception|Error failure){retain(failure);throw failure;}
      phase="ROOT_SCOPE_CLOSE";root.close();
    }catch(Exception|Error failure){retain(failure);throw failure;}
  }
  public static void main(String[] args)throws Exception{
    require(args.length==0 && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{try{body();phase="A_SCOPE_CLOSE";return Boolean.TRUE;}catch(Exception|Error failure){retain(failure);throw failure;}})).orElseThrow();}
      catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
    Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"originalDoneSuccess=true\nold411All17ColumnsPreserved=true\nnewTenStepsSuccess=true\noldTwoAbandonedPreserved=true\nrequestsEmpty=true\nallNewScopesReturnedNormally=true\nproductionMutation0=true\n".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
    System.out.println("PG481_COMPLETED originalDoneSuccess=true old411All17ColumnsPreserved=true newTenStepsSuccess=true allNewScopesReturnedNormally=true productionMutation0=true");
  }
}
