import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.regex.*;

/** STOPCOMP004: fixed completed PG464 readback only; no start/stop/permit/DDL/repair. */
public final class Pg464CompletedReadback {
  static final String SOURCE="e4c7f0b84b02a2124a0aba2a7b682ad482d5cd45";
  static final String DIGEST="b080dfa29bbed038d9a1f0f25196de34e8b75b5c1ee28f7035164a622ea15e7e";
  static final Path BEFORE=Path.of("/var/lib/pgpt-s1-preservation/pg464-code-only");
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
  static boolean anonymousFixture(Long users,Long contexts,Long invalidSessions) {
    return Long.valueOf(0).equals(users) && Long.valueOf(0).equals(contexts) && Long.valueOf(0).equals(invalidSessions);
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->{
      System.err.println("PG464_COMPLETED_REFUSED type="+e.getClass().getName()+" privateDiagnostics=true");
      for(var frame:e.getStackTrace())if(frame.getClassName().equals("Pg464CompletedReadback"))
        System.err.println("PG464_COMPLETED_SOURCE_FRAME "+frame.getMethodName()+":"+frame.getLineNumber());
    });
    require(args.length==0);
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("e07aa706-1acd-4e65-b309-d7f330f79d54"));
    require(Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->
      StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        Pg387TrustedDeployment.LABEL="PG464";Pg387TrustedDeployment.STEM="pg464";
        Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG464");
        Pg387TrustedDeployment.expectedSchema("027");var approval=Pg387TrustedDeployment.verify();
        require(approval.manifestSha256().equals(DIGEST) && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
        require(Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
        var parent=show("schubert-nk-morning-controller.service");
        require(parent.get("LoadState").equals("loaded") && parent.get("MainPID").equals("0") && parent.get("ControlPID").equals("0")
            && parent.get("Job").isEmpty() && parent.get("ActiveState").equals("inactive") && parent.get("SubState").equals("dead")
            && parent.get("Result").equals("success"));
        Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
        peer("schubert-nk-api.service",1338494,"9269078370384fdaab05ca9a0fcd50bd");
        peer("schubert-nk-web.service",1340568,"716bd4789cde40af97775e48641159fe");
        peer("caddy.service",1345626,"5fab43f2da6d40c9a2bb3987e7d63088");
        Pg387TrustedDeployment.requireNoUndeliveredWork();
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
            var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
          try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
          require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
              && epoch.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION));
          var names=new HashSet<String>();try(var entries=Files.list(Path.of("/run/schubert-nk/startup"))){entries.forEach(p->names.add(p.getFileName().toString()));}
          require(names.size()==33 && names.stream().noneMatch(n->n.contains("intent") || n.equals("publication.current")));
          int old=0;try(var entries=Files.list(BEFORE)) {for(var p:entries.toList())if(p.getFileName().toString().matches("[0-9a-f-]{36}\\.(permit|owner|API\\.launch|WEB\\.launch)")) {
            String name=p.getFileName().toString();require(names.contains(name) && Arrays.equals(Files.readAllBytes(p),Files.readAllBytes(Path.of("/run/schubert-nk/startup",name))));old++;
          }}require(old==28);
          var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
          var done=original.completed().orElseThrow();require(done.outcome()==MaintenanceCompletion.Outcome.SUCCESS);
          require(!done.endedAt().isBefore(Instant.parse("2026-10-05T00:35:52Z")) && !done.endedAt().isAfter(Instant.parse("2026-10-05T00:42:37Z")));
          var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==331);
          require(rows.subList(0,321).toString().equals(Files.readString(BEFORE.resolve("rows-before.private"))));
          require(rows.subList(321,331).stream().map(r->r.get(3)).collect(java.util.stream.Collectors.toSet()).equals(Set.of(
              "BACKUP_DB","BACKUP_CONFIG","CLEAN_NOTIFICATION","CLEAN_QUESTION","CLEAN_SESSION","CLEAN_INBOX_OUTBOX","CLEAN_LOG","CLEAN_BATCH_RUN","CLEAN_TRANSFER","CLEAN_EXPIRY")));
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
          System.out.println("PG464_COMPLETED_DIAGNOSTIC changedFixedTableNamesOnly="+observed+" rowValuesRedacted=true");
          require(allowedChanges(observed));
          // UI222/SS314 login CSRF creates encrypted anonymous HTTP sessions; no auth succeeds.
          try(var q=schema.createStatement()) {
            q.setQueryTimeout(5);
            try(var r=q.executeQuery("select (select count(*) from schubert.app_users),(select count(*) from schubert.auth_sessions),(select count(*) from schubert_web_session.web_http_sessions where session_id_hash !~ '^[0-9a-f]{64}$' or octet_length(attributes_ciphertext)<=28 or created_at>last_accessed_at or last_accessed_at>expires_at or max_inactive_seconds<1 or max_inactive_seconds>28800 or version<0 or version>999999999)")) {
              require(r.next() && anonymousFixture(r.getObject(1,Long.class),r.getObject(2,Long.class),r.getObject(3,Long.class)) && !r.next());
            }
          }
          System.out.println("PG464_COMPLETED body=true originalDoneSuccess=true rows331Old321Full14Preserved=true backup20Preserved=true fixedAssetTransferValid=true namespace33Intent0=true unchangedBusinessTables="+unchanged.size()+" permittedChangedTableNames="+observed+" outerNotYetReturned=true");
          require(epoch.equals(files.current()));db.rollback();schema.rollback();
        }
        return Boolean.TRUE;
      })).orElseThrow())).orElseThrow());
    System.out.println("PG464_COMPLETED newReadOnlyMAAndDatabaseScopesReturnedNormally=true previousTimeoutNormalized=false productionMutation0=true formal=false");
  }
}
