import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.regex.*;

/** STOPCOMP004: fixed completed PG473 readback only; no start/stop/permit/DDL/repair. */
public final class Pg473CompletedReadback {
  static String phase="PREFLIGHT";
  static boolean retainRequired(String at,Throwable failure) {
    return at!=null && failure!=null && (at.endsWith("_SCOPE_CLOSE") || failure instanceof Error || failure.getSuppressed().length!=0);
  }
  static void retain() {
    System.err.println("PG473_COMPLETED_UNKNOWN phase="+phase+" nextOperationIsolated=true remainingScopeOwnershipNotAssumedClosed=true");
    for(;;){try{Thread.sleep(1000);}catch(InterruptedException interrupted){Thread.interrupted();}}
  }
  static final String SOURCE="a5f9e6a54427ff356626245230496d8667082465";
  static final String DIGEST="ffae42347b43d9654d026f66f10cbf81ce9a98baa30bb33510ff19279d90676d";
  static final Path BEFORE=Path.of("/var/lib/pgpt-s1-preservation/pg473-stopped-deploy");
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed completed readback refused");}
  /** Parse only the captured Map<String,String> snapshot envelope, never an auth oracle. */
  static Map<String,String> snapshot(String text) {
    require(text!=null && text.length()<=1048576 && text.startsWith("{") && text.endsWith("}"));
    var result=new HashMap<String,String>();int depth=0,start=1;
    for(int n=1;n<text.length()-1;n++) {
      char c=text.charAt(n);if(c=='{')depth++;if(c=='}')depth--;require(depth>=0 && depth<=4);
      if(c==',' && depth==0){entry(result,text.substring(start,n));require(text.charAt(n+1)==' ');start=n+2;n++;}
    }
    require(depth==0);if(start<text.length()-1)entry(result,text.substring(start,text.length()-1));
    return Map.copyOf(result);
  }
  static void entry(Map<String,String> result,String entry) {
    int at=entry.indexOf('=');require(at>=0 && at<entry.length()-1);
    require(result.putIfAbsent(entry.substring(0,at),entry.substring(at+1))==null);
  }
  static Map<String,Pg456SignedMigration.Data> businessBefore(String text) {
    require(text!=null && text.length()<=1048576 && text.startsWith("{") && text.endsWith("}"));
    var result=new HashMap<String,Pg456SignedMigration.Data>();
    var matcher=Pattern.compile("(schubert(?:_web_session)?\\.[a-z_]+)=Data\\[rows=([0-9]+), digest=([0-9a-f]{64})\\]").matcher(text);
    int end=1;
    while(matcher.find()) {
      require(matcher.start()==end || (end>1 && matcher.start()==end+2 && text.substring(end,end+2).equals(", ")));
      require(result.putIfAbsent(matcher.group(1),new Pg456SignedMigration.Data(Long.parseLong(matcher.group(2)),matcher.group(3)))==null);end=matcher.end();
    }
    require(end==text.length()-1);
    require(result.keySet().equals(Set.copyOf(Pg456SignedMigration.TABLES)));return Map.copyOf(result);
  }
  static Map<String,String> show(String unit) throws Exception {
    require(Set.of("schubert-nk-morning-controller.service","schubert-nk-api.service","schubert-nk-web.service","caddy.service").contains(unit));
    byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",unit,"--property="+String.join(",",Pg410KnownAuthRecovery.FIELDS));
    var result=new HashMap<String,String>();
    for(String line:new String(raw,java.nio.charset.StandardCharsets.US_ASCII).split("\n")) {
      int at=line.indexOf('=');require(at>0 && result.putIfAbsent(line.substring(0,at),line.substring(at+1))==null);
    }
    require(result.keySet().equals(Pg410KnownAuthRecovery.FIELDS) && unit.equals(result.get("Id")));return Map.copyOf(result);
  }
  static void peer(String role,long pid,String invocation) throws Exception {
    var actual=show(role);
    require(actual.get("LoadState").equals("loaded") && actual.get("MainPID").equals(Long.toString(pid))
        && actual.get("InvocationID").equals(invocation) && actual.get("ActiveState").equals("active")
        && actual.get("SubState").equals("running") && actual.get("ControlPID").equals("0") && actual.get("Job").isEmpty());
  }
  static boolean references(Boolean history,Boolean inbox,Boolean log,Boolean consistent) {
    return Boolean.TRUE.equals(history) && inbox!=null && log!=null && Boolean.TRUE.equals(consistent);
  }
  static boolean allowedChanges(Set<String> tables) {
    return tables!=null && Set.of("schubert.batch_runs","schubert.inbox_inspection_progress","schubert.log_cleanup_progress",
        "schubert.app_logs","schubert.request_inbox","schubert.mq_outbox","schubert_web_session.web_log_outbox",
        "schubert_web_session.web_http_sessions").containsAll(tables);
  }
  static boolean authenticatedFixture(Long users,Long contexts,Long invalidSessions) {
    return Long.valueOf(1).equals(users) && Long.valueOf(6).equals(contexts) && Long.valueOf(0).equals(invalidSessions);
  }
  static boolean namespace(Set<String> names) {
    if(names==null || names.size()!=57 || !names.contains("epoch.current") || names.stream().anyMatch(Objects::isNull))return false;
    var groups=new HashMap<String,Set<String>>();
    for(String name:names)if(!name.equals("epoch.current")) {
      if(!name.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\.(permit|owner|API\\.launch|WEB\\.launch)"))return false;
      groups.computeIfAbsent(name.substring(0,36),key->new HashSet<>()).add(name.substring(37));
    }
    return groups.size()==14 && groups.values().stream().allMatch(s->s.equals(Set.of("permit","owner","API.launch","WEB.launch")));
  }
  static boolean field(com.google.gson.JsonObject row,String key,String expected) {
    return row!=null && row.has(key) && row.get(key).isJsonPrimitive() && row.get(key).getAsJsonPrimitive().isString() && expected.equals(row.get(key).getAsString());
  }
  static boolean jobDone(com.google.gson.JsonObject row) {
    for(var e:Map.of("_BOOT_ID","e07aa7061acd4e65b309d7f330f79d54","_PID","1","_UID","0","_COMM","systemd","MESSAGE_ID","39f53479d3a045ac8e11786248231fbf","UNIT","schubert-nk-morning-controller.service","INVOCATION_ID","0f1570d2c1cb4d8886d0bb43c96aa07f","JOB_ID","204144","JOB_TYPE","start","JOB_RESULT","done").entrySet())
      if(!field(row,e.getKey(),e.getValue()))return false;
    if(!row.has("_SOURCE_REALTIME_TIMESTAMP") || !row.get("_SOURCE_REALTIME_TIMESTAMP").isJsonPrimitive() || !row.get("_SOURCE_REALTIME_TIMESTAMP").getAsJsonPrimitive().isString())return false;
    String text=row.get("_SOURCE_REALTIME_TIMESTAMP").getAsString();if(!text.matches("[0-9]{16}"))return false;
    long value=Long.parseLong(text);return value>=1791245996000000L && value<=1791247797000000L;
  }
  static boolean parentAfter(Map<String,String> p) {
    if(p==null || !p.keySet().equals(Pg410KnownAuthRecovery.FIELDS) || p.values().stream().anyMatch(Objects::isNull))return false;
    for(var e:Map.of("Id","schubert-nk-morning-controller.service","LoadState","loaded","MainPID","0","ControlPID","0","Job","","ActiveState","inactive","SubState","dead","Result","success","ExecMainStatus","0").entrySet())if(!e.getValue().equals(p.get(e.getKey())))return false;
    for(var e:Map.of("Type","oneshot","Restart","no","RemainAfterExit","no","KillMode","control-group","SendSIGKILL","no").entrySet())if(!e.getValue().equals(p.get(e.getKey())))return false;
    if(p.get("InvocationID").isEmpty())return p.get("ExecMainCode").equals("0") && p.get("ExecMainStartTimestampMonotonic").equals("0") && p.get("ExecMainExitTimestampMonotonic").equals("0");
    if(!p.get("InvocationID").equals("0f1570d2c1cb4d8886d0bb43c96aa07f") || !p.get("ExecMainCode").equals("1") || !p.get("ExecMainStartTimestampMonotonic").equals("201646455160") || !p.get("ExecMainExitTimestampMonotonic").matches("[0-9]{1,15}"))return false;
    long ended=Long.parseLong(p.get("ExecMainExitTimestampMonotonic"));return ended>201646455160L && ended<=203446455160L;
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->{
      System.err.println("PG473_COMPLETED_REFUSED type="+e.getClass().getName()+" privateDiagnostics=true");
      for(var frame:e.getStackTrace())if(frame.getClassName().equals("Pg473CompletedReadback"))
        System.err.println("PG473_COMPLETED_SOURCE_FRAME "+frame.getMethodName()+":"+frame.getLineNumber());
    });
    require(args.length==0);
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("e07aa706-1acd-4e65-b309-d7f330f79d54"));
    require(Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    try { require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      try { var value=StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        phase="READBACK_BODY";
        Pg387TrustedDeployment.LABEL="PG473";Pg387TrustedDeployment.STEM="pg473";
        Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG473");
        Pg387TrustedDeployment.expectedSchema("027");var approval=Pg387TrustedDeployment.verify();
        require(approval.manifestSha256().equals(DIGEST) && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
        require(Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
        var parent=show("schubert-nk-morning-controller.service");
        require(parentAfter(parent));
        var journal=Path.of("/var/lib/pgpt-s1-preservation/pg473-completed-journal-v1/parent.private.jsonl");
        var journalBytes=Pg410KnownAuthRecovery.material(journal,4194304);int doneJobs=0;
        for(String line:new String(journalBytes,java.nio.charset.StandardCharsets.UTF_8).split("\n")) {
          var row=com.google.gson.JsonParser.parseString(line).getAsJsonObject();
          if(jobDone(row))doneJobs++;
        }require(doneJobs==1);
        Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
        peer("schubert-nk-api.service",2782055,"e93ae37bc6b54a24abd2c62e0e8c431e");
        peer("schubert-nk-web.service",2784401,"4504c595204d47f4a110059e71c13c63");
        peer("caddy.service",2790116,"ad0a34dc0667429bb89ea219a40390b5");
        Pg387TrustedDeployment.requireNoUndeliveredWork();
        try { try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
            var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
          try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
          require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
              && !epoch.activation().id().equals(UUID.fromString("5c87de9a-ec69-492b-a6e2-9926b9f7cac7")));
          var names=new HashSet<String>();try(var entries=Files.list(Path.of("/run/schubert-nk/startup"))){entries.forEach(p->names.add(p.getFileName().toString()));}
          require(namespace(names));
          int old=0;try(var entries=Files.list(BEFORE)) {for(var p:entries.toList())if(p.getFileName().toString().matches("[0-9a-f-]{36}\\.(permit|owner|API\\.launch|WEB\\.launch)")) {
            String name=p.getFileName().toString();require(names.contains(name) && Arrays.equals(Files.readAllBytes(p),Files.readAllBytes(Path.of("/run/schubert-nk/startup",name))));old++;
          }}require(old==52);
          var metadataBefore=snapshot(Files.readString(BEFORE.resolve("metadata-before.private")));
          var metadataNow=Pg471CompletedDeployment.startupMetadata();
          for(String name:metadataBefore.keySet())if(!name.equals("epoch.current"))
            require(snapshot(metadataBefore.get(name)).equals(snapshot(metadataNow.get(name).toString())));
          var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
          var done=original.completed().orElseThrow();require(done.outcome()==MaintenanceCompletion.Outcome.SUCCESS);
          require(!done.endedAt().isBefore(Instant.parse("2026-10-06T00:19:56Z")) && !done.endedAt().isAfter(Instant.parse("2026-10-06T00:49:57Z")));
          var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==391);
          require(rows.subList(0,381).toString().equals(Files.readString(BEFORE.resolve("rows-before.private"))));
          require(rows.subList(381,391).stream().map(r->r.get(3)).collect(java.util.stream.Collectors.toSet()).equals(Set.of(
              "BACKUP_DB","BACKUP_CONFIG","CLEAN_NOTIFICATION","CLEAN_QUESTION","CLEAN_SESSION","CLEAN_INBOX_OUTBOX","CLEAN_LOG","CLEAN_BATCH_RUN","CLEAN_TRANSFER","CLEAN_EXPIRY")));
          for(var row:rows.subList(381,391))require(row.get(7).equals("SKIPPED")
              && row.subList(8,12).stream().allMatch(x->x instanceof Number n && n.longValue()==0));
          var originalBefore=snapshot(Files.readString(BEFORE.resolve("original-before.private")));
          var originalNow=Pg428ColdBootPreparation.original();
          int preservedOriginalFiles=0;
          for(var entry:originalBefore.entrySet())if(entry.getValue().contains("}/") && !entry.getKey().endsWith("/active")) {
            require(entry.getValue().equals(originalNow.get(entry.getKey())));preservedOriginalFiles++;
          }
          require(preservedOriginalFiles>0);
          // A writable-owned repository is not a read-only diagnostic capability. Fixed SQL only.
          try(var q=db.prepareStatement("select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent from schubert.maintenance_read_run_references(?,?)")) {
            q.setQueryTimeout(5);q.setObject(1,epoch.activation().run().id());q.setObject(2,epoch.activation().run().cutoff().atOffset(ZoneOffset.UTC));
            try(var r=q.executeQuery()) {
              require(r.next() && references(r.getObject(1,Boolean.class),r.getObject(2,Boolean.class),r.getObject(3,Boolean.class),r.getObject(4,Boolean.class)) && !r.next());
            }
          }
          require(Pg428ColdBootPreparation.backupSnapshot().equals(snapshot(Files.readString(BEFORE.resolve("backup-before.private")))));
          Pg428ColdBootPreparation.fixtureSnapshot();
          var beforeBusiness=businessBefore(Files.readString(BEFORE.resolve("business-before.private")));var after=Pg456SignedMigration.business(schema);
          // REQUEST readiness/A01 logs and current maintenance progress are authorized changes,
          // not waved away as full Log compatibility; QA051/native L01 remains separate.
          var observed=new TreeSet<String>();var unchanged=new TreeSet<String>();
          for(String table:beforeBusiness.keySet()) {
            if(beforeBusiness.get(table).equals(after.get(table)))unchanged.add(table);else observed.add(table);
          }
          System.out.println("PG473_COMPLETED_DIAGNOSTIC changedFixedTableNamesOnly="+observed+" rowValuesRedacted=true");
          require(allowedChanges(observed));
          // Current saved baseline has six contexts after the PG472 L01 observation.
          // Expired contexts remain records; nonrevoked count is not the concurrent bound.
          try(var q=schema.createStatement()) {
            q.setQueryTimeout(5);
            try(var r=q.executeQuery("select (select count(*) from schubert.app_users),(select count(*) from schubert.auth_sessions),(select count(*) from schubert_web_session.web_http_sessions where session_id_hash !~ '^[0-9a-f]{64}$' or octet_length(attributes_ciphertext)<=28 or created_at>last_accessed_at or last_accessed_at>expires_at or max_inactive_seconds<1 or max_inactive_seconds>28800 or version<0 or version>999999999)")) {
              require(r.next() && authenticatedFixture(r.getObject(1,Long.class),r.getObject(2,Long.class),r.getObject(3,Long.class)) && !r.next());
            }
          }
          try(var q=schema.createStatement();var r=q.executeQuery("select (select count(*) from schubert.app_users where role='ADMIN' and status='ACTIVE' and version=1),(select count(*) from schubert.auth_sessions where revoked),(select count(*) from schubert.auth_sessions where not revoked),(select count(*) from schubert_web_session.web_log_outbox where status<>'SENT'),(select count(*) from schubert.auth_sessions where not revoked and expires_at>current_timestamp)")) {
            require(r.next() && r.getLong(1)==1 && r.getLong(2)>=0 && r.getLong(3)>=0 && r.getLong(2)+r.getLong(3)==6 && r.getLong(4)==0 && r.getLong(5)>=0 && r.getLong(5)<=2 && !r.next());
          }
          for(String credential:List.of("bootstrap-admin-username","bootstrap-admin-password")) {
            require(!Files.exists(Path.of("/etc/schubert-nk/credentials",credential),LinkOption.NOFOLLOW_LINKS));
            var p=Path.of("/var/lib/pgpt-s1-preservation/pg468-bootstrap-retired-v1",credential);
            var a=Files.readAttributes(p,"unix:mode,uid,gid,nlink",LinkOption.NOFOLLOW_LINKS);
            require(Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS) && !Files.isSymbolicLink(p)
                && a.get("mode").equals(0100400) && a.get("uid").equals(0) && a.get("gid").equals(0) && a.get("nlink").equals(1));
          }
          System.out.println("PG473_COMPLETED body=true originalDoneSuccess=true rows391Old381Full14Preserved=true allPreviousBackupPreserved=true fixedAssetTransferValid=true namespace57Intent0=true unchangedBusinessTables="+unchanged.size()+" permittedChangedTableNames="+observed+" outerNotYetReturned=true");
          require(epoch.equals(files.current()));db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE";
        }
        }catch(Exception|Error failure){if(retainRequired(phase,failure))retain();throw failure;}
        phase="A_SCOPE_CLOSE";
        return Boolean.TRUE;
      })).orElseThrow();phase="M_SCOPE_CLOSE";return value;
      }catch(Exception|Error failure){if(retainRequired(phase,failure))retain();throw failure;}
    })).orElseThrow());
    }catch(Exception|Error failure){if(retainRequired(phase,failure))retain();throw failure;}
    System.out.println("PG473_COMPLETED newReadOnlyMAAndDatabaseScopesReturnedNormally=true previousTimeoutNormalized=false productionMutation0=true formal=false");
  }
}
