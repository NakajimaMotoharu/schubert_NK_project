import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import com.google.gson.*;

/** PT-OPS-PG487004: independent literal same-day contract, read-only, new scopes. */
public final class Pg487CompletedReadback {
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg487-completed-readback");
  static final String RUN="91a748b4-1abe-484c-9682-44f46429b324";
  static final Instant START=Instant.parse("2026-10-06T12:06:12Z"), END=Instant.parse("2026-10-06T12:36:13Z");
  static String phase="PREFLIGHT";
  static void require(boolean v){if(!v)throw new IllegalStateException("fixed new completed readback refused");}
  static void retain(Throwable failure){
    System.err.println("PG487_COMPLETED_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" scopesNotAssumedClosed=true");
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException interrupted){Thread.interrupted();}
  }
  static void validateRows(JsonObject before,JsonObject after){
    require(before!=null && after!=null && before.keySet().equals(after.keySet()));
    for(String table:before.keySet())if(!table.equals("schubert.batch_runs"))require(before.get(table).equals(after.get(table)));
    var old=before.getAsJsonArray("schubert.batch_runs");require(old.size()==423);
    var expected=new HashMap<Long,JsonElement>();for(var value:old)require(expected.put(value.getAsJsonObject().get("id").getAsLong(),value)==null);
    var newest=new HashMap<String,JsonObject>();int preserved=0;
    for(var element:after.getAsJsonArray("schubert.batch_runs")){
      var row=element.getAsJsonObject();long id=row.get("id").getAsLong();
      if(expected.containsKey(id)){require(expected.get(id).equals(row));preserved++;continue;}
      require(row.get("run_id").getAsString().equals(RUN));String step=row.get("step").getAsString();require(newest.put(step,row)==null);
      boolean backup=Set.of("BACKUP_DB","BACKUP_CONFIG").contains(step);
      require(row.get("status").getAsString().equals(backup?"SUCCESS":"SKIPPED"));
      long count=step.equals("BACKUP_DB")?1:step.equals("BACKUP_CONFIG")?2:0;
      require(row.get("target_count").getAsLong()==count && row.get("success_count").getAsLong()==count && row.get("failure_count").getAsLong()==0);
      require(backup?row.get("error_code").isJsonNull():row.get("error_code").getAsString().equals("ALREADY_SUCCESSFUL"));
      require(backup?row.get("error_summary").isJsonNull():row.get("error_summary").getAsString().equals("step already successful for business date"));
      require(row.get("attempt").getAsInt()==(backup?1:2) && !row.get("ended_at").isJsonNull());
      var started=Instant.parse(row.get("started_at").getAsString());var ended=Instant.parse(row.get("ended_at").getAsString());
      require(!started.isBefore(START) && !ended.isBefore(started) && !ended.isAfter(END));
    }
    require(preserved==423 && newest.keySet().equals(Set.of("BACKUP_DB","BACKUP_CONFIG","CLEAN_NOTIFICATION","CLEAN_QUESTION","CLEAN_SESSION","CLEAN_INBOX_OUTBOX","CLEAN_LOG","CLEAN_BATCH_RUN","CLEAN_TRANSFER","CLEAN_EXPIRY")));
  }
  static void body()throws Exception{
    Pg464CodeOnlyDeployment.configure("PG486","2e017b4063960bfb5f2483f10510d1a6a3391a9f",Path.of("/opt/schubert-nk/releases/0.1.0-PG486"));
    var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals("230c6174931a8d98a34e4369086619c54cb0668e0793baf2f1efce3e0993bd1d") && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
    phase="ORIGINAL_AND_DB_SCOPE";
    var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
    try{
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
      require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.boot().toString().equals("e07aa706-1acd-4e65-b309-d7f330f79d54") && epoch.activation().run().id().toString().equals(RUN) && epoch.activation().run().cutoff().equals(Instant.parse("2026-10-06T12:06:14.564793Z")));
      var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));var done=original.completed().orElseThrow();
      require(done.outcome()==MaintenanceCompletion.Outcome.SUCCESS && !done.endedAt().isBefore(START) && !done.endedAt().isAfter(END));
      byte[] saved=Files.readAllBytes(Path.of("/var/lib/pgpt-s1-preservation/pg486-completed-codeonly/after.private.json"));
      require(HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(saved)).equals("a189a4b029d9a2d66b6767aa86bd85c63879438d84b99b5a86b36ac3093d4ba5"));
      var before=JsonParser.parseString(new String(saved,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonObject("rows");require(before.size()==24);
      var db=Pg407FailedRootRecovery.openDatabase();
      try{
        db.setReadOnly(true);db.setAutoCommit(false);
        try(var q=db.createStatement();var r=q.executeQuery("select pg_backend_pid(),set_config('application_name','PG487-completed-readback',false),pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(3) && !r.next());}
        var after=new JsonObject();
        for(String table:before.keySet()){
          var rows=new JsonArray();try(var q=db.createStatement();var r=q.executeQuery("select to_jsonb(t)::text from "+table+" t order by to_jsonb(t)::text")){while(r.next())rows.add(JsonParser.parseString(r.getString(1)));}
          after.add(table,rows);
        }
        validateRows(before,after);
        for(String name:List.of("backup-request","cleanup-request","expiry-request"))try(var entries=Files.list(Path.of("/run/schubert-nk",name))){require(entries.findAny().isEmpty());}
        require(epoch.equals(files.current()) && done.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().orElseThrow()));
        Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
        Pg481PendingDeployment.privateWrite(SAVE.resolve("after-rows.private.json"),after.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
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
    Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"originalDoneSuccess=true\nold423All17ColumnsPreserved=true\nother23TablesPreserved=true\nnewBackupSuccess=true\neightSameDaySkips=true\nrequestsEmpty=true\nallNewScopesReturnedNormally=true\nproductionMutation0=true\n".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
    System.out.println("PG487_COMPLETED originalDoneSuccess=true oldAllColumnsPreserved=true newBackupSuccess=true eightSameDaySkips=true allNewScopesReturnedNormally=true");
  }
}
