import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.Connection;
import java.util.*;

/** SS343 isolated code-only provisioning after SSC179 recovery. Never repeats DDL,
 * restores /run, edits original/Backup/DB, starts a Unit or issues a permit.
 * This exact boot/old signed027/new signed027 is the only accepted transition.
 */
public final class Pg468CodeOnlyDeployment {
  static final String OLD_SOURCE="df9a33febf3703f0d18ac2c4ef56fd0225aac2b9";
  static final String OLD_DIGEST="8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e";
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG465");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG468");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg468-code-only");
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static String stage="ARGUMENTS";
  static void require(boolean valid){if(!valid)throw new IllegalStateException("fixed code-only proof differs");}
  static boolean arguments(String[] args){return args!=null && args.length==3 && args[0]!=null && args[1]!=null && args[2]!=null
      && args[0].matches("[0-9a-f]{40}") && args[1].matches("[0-9a-f]{64}") && Set.of("verify","activate").contains(args[2]);}
  static boolean names(Set<String> names,UUID epoch){
    if(names==null || epoch==null)return false;
    return names.equals(Set.of("epoch.current",epoch+".permit",epoch+".owner",epoch+".API.launch",epoch+".WEB.launch", "1eecb7b9-1e98-478f-9084-201422b31bff.permit", "1eecb7b9-1e98-478f-9084-201422b31bff.owner", "1eecb7b9-1e98-478f-9084-201422b31bff.API.launch", "1eecb7b9-1e98-478f-9084-201422b31bff.WEB.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.permit","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.owner","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.API.launch","d536cf5a-f5a8-4dd9-8679-3488fab17fdf.WEB.launch","25020aa0-7b69-4554-be47-ea69588da569.permit","25020aa0-7b69-4554-be47-ea69588da569.owner","25020aa0-7b69-4554-be47-ea69588da569.API.launch","25020aa0-7b69-4554-be47-ea69588da569.WEB.launch","e8cce97a-163b-4814-b435-8fc26466e550.permit","e8cce97a-163b-4814-b435-8fc26466e550.owner","e8cce97a-163b-4814-b435-8fc26466e550.API.launch","e8cce97a-163b-4814-b435-8fc26466e550.WEB.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.permit","15e4559b-13ab-46d7-a7a8-c15f1de4a245.owner","15e4559b-13ab-46d7-a7a8-c15f1de4a245.API.launch","15e4559b-13ab-46d7-a7a8-c15f1de4a245.WEB.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.permit","bcd85e18-8926-4a3c-9e9c-78da9dba2670.owner","bcd85e18-8926-4a3c-9e9c-78da9dba2670.API.launch","bcd85e18-8926-4a3c-9e9c-78da9dba2670.WEB.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.permit","1ba8ece5-5297-47c3-9933-95b2330beeb0.owner","1ba8ece5-5297-47c3-9933-95b2330beeb0.API.launch","1ba8ece5-5297-47c3-9933-95b2330beeb0.WEB.launch","42efb43b-658e-4771-8ad4-b01d658a677b.permit","42efb43b-658e-4771-8ad4-b01d658a677b.owner","42efb43b-658e-4771-8ad4-b01d658a677b.API.launch","42efb43b-658e-4771-8ad4-b01d658a677b.WEB.launch"));
  }
  static Set<String> actualNames() throws Exception {try(var files=Files.list(STARTUP)){return new HashSet<>(files.map(p->p.getFileName().toString()).toList());}}
  static void terminal() throws Exception {
    Pg387TrustedDeployment.requireNoUndeliveredWork();Pg387TrustedDeployment.terminalAll();
    require(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).snapshot().quiescent());
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
  }
  static void configure(String label,String source,Path release){
    Pg387TrustedDeployment.LABEL=label;Pg387TrustedDeployment.STEM=label.toLowerCase(Locale.ROOT);
    Pg387TrustedDeployment.SOURCE=source;Pg387TrustedDeployment.RELEASE=release;Pg387TrustedDeployment.expectedSchema("027");
  }
  static void unchangedSignedFiles() throws Exception {
    try(var walk=Files.walk(OLD.resolve("db/migration"))){
      var sql=walk.filter(Files::isRegularFile).sorted().toList();require(sql.size()==27);
      for(var p:sql)require(Arrays.equals(Files.readAllBytes(p),Files.readAllBytes(NEXT.resolve("db/migration").resolve(p.getFileName()))));
    }
    for(String path:List.of("config/effective/backup-profile.json","config/effective/backup-age-recipient",
        "config/caddy/Caddyfile.template","systemd/caddy.service.d/schubert-nk-startup-policy.conf"))
      require(Arrays.equals(Files.readAllBytes(OLD.resolve(path)),Files.readAllBytes(NEXT.resolve(path))));
    for(var unit:dev.codex.schubert.nk.batch.platform.MaintenanceUnit.values()) {
      if(unit==dev.codex.schubert.nk.batch.platform.MaintenanceUnit.CADDY)continue;
      String name=unit.serviceName();require(Arrays.equals(Files.readAllBytes(OLD.resolve("systemd").resolve(name)),Files.readAllBytes(NEXT.resolve("systemd").resolve(name))));
      require(Arrays.equals(Files.readAllBytes(OLD.resolve("systemd").resolve(name)),Files.readAllBytes(Path.of("/etc/systemd/system",name))));
    }
    String bootstrap="schubert-nk-bootstrap-admin.service";
    require(Arrays.equals(Files.readAllBytes(OLD.resolve("systemd").resolve(bootstrap)),Files.readAllBytes(NEXT.resolve("systemd").resolve(bootstrap))));
    require(Arrays.equals(Files.readAllBytes(OLD.resolve("systemd").resolve(bootstrap)),Files.readAllBytes(Path.of("/etc/systemd/system",bootstrap))));
    String morning="schubert-nk-morning-controller.service";
    require(Arrays.equals(Files.readAllBytes(OLD.resolve("systemd").resolve(morning)),Files.readAllBytes(NEXT.resolve("systemd").resolve(morning))));
    require(Arrays.equals(Files.readAllBytes(NEXT.resolve("systemd").resolve(morning)),Files.readAllBytes(Path.of("/etc/systemd/system",morning))));
    require(Arrays.equals(Files.readAllBytes(Pg456SignedMigration.PROFILE),Files.readAllBytes(NEXT.resolve("config/effective/backup-profile.json"))));
    require(Arrays.equals(Files.readAllBytes(Path.of("/etc/caddy/Caddyfile")),Pg456SignedMigration.render(Files.readAllBytes(NEXT.resolve("config/caddy/Caddyfile.template")))));
    require(Arrays.equals(Files.readAllBytes(Path.of("/etc/systemd/system/caddy.service.d/schubert-nk-startup-policy.conf")),Files.readAllBytes(NEXT.resolve("systemd/caddy.service.d/schubert-nk-startup-policy.conf"))));
  }
  static void save(String name,byte[] bytes) throws Exception {
    Path p=SAVE.resolve(name);Files.write(p,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var channel=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){channel.force(true);}
  }
  static void retain(){System.err.println("PG468_CODE_ONLY_UNKNOWN stage="+stage+" isolated=true automaticResume=false diagnosticsRedacted=true");
    boolean interrupted=false;for(;;){try{Thread.sleep(1000);}catch(InterruptedException signal){interrupted=true;}if(interrupted)Thread.interrupted();}}
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println("PG468_CODE_ONLY_REFUSED stage="+stage+" type="+e.getClass().getName()+" diagnosticsRedacted=true"));
    require(arguments(args));boolean verifyOnly=args[2].equals("verify");
    require(Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));
    boolean[] mutating={false};
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      stage="M_TERMINAL";terminal();
      try {
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        stage="A_SIGNED_OLD";terminal();configure("PG465",OLD_SOURCE,OLD);var prior=Pg387TrustedDeployment.verify();
        require(prior.manifestSha256().equals(OLD_DIGEST) && Arrays.equals(prior.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
            && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(OLD));
        stage="NEW_SIGNED_027";configure("PG468",args[0],NEXT);Pg387TrustedDeployment.freezeCandidate();var next=Pg387TrustedDeployment.verify();require(next.manifestSha256().equals(args[1]));
        require(com.google.gson.JsonParser.parseString(Files.readString(NEXT.resolve("RELEASE-MANIFEST.json"))).getAsJsonObject().getAsJsonObject("source").get("commit").getAsString().equals(args[0]));
        unchangedSignedFiles();
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          stage="DB_ORIGINAL";db.setAutoCommit(false);
          try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var before=files.current();
          require(before.state()==StartupPermitRecords.State.INVALID && before.epoch().toString().equals("37599b0d-d64a-41e9-92b5-bfeec4e5e6b6") && before.boot().toString().equals(BOOT) && before.activation().run().id().equals(Pg407FailedRootRecovery.RUN) && before.activation().id().equals(UUID.fromString("1f026aa2-899a-4f22-aca9-32f4918a03c8")) && names(actualNames(),before.epoch()));
          var original=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();var fixture=Pg428ColdBootPreparation.fixtureSnapshot();
          var rows=Pg407FailedRootRecovery.databaseRows(db);var business=Pg456SignedMigration.business(schema);var history=Pg422SignedMigration.history(schema);
          require(rows.size()==341 && history.equals(Pg456SignedMigration.expected(NEXT,OLD,27)));
          // Current complete original and both schema/business/fixture snapshots are bound here;
          // historical cold-pre-migration/old-activation helpers are not this cohort's oracle.
          Pg456SignedMigration.postconditions(schema);
          require(new RunReferenceRepository(db).read(before.activation().run()).identityConsistent() && MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation())).completed().isEmpty());
          var bytes=new TreeMap<String,byte[]>();var metadata=new TreeMap<String,Map<String,Object>>();
          for(String n:actualNames()){bytes.put(n,Pg410KnownAuthRecovery.material(STARTUP.resolve(n),4096));metadata.put(n,Pg410KnownAuthRecovery.metadata(STARTUP.resolve(n)));}
          stage="BEFORE_MUTATION";terminal();unchangedSignedFiles();require(before.equals(files.current()));
          for(var e:bytes.entrySet())require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(e.getKey()),4096)) && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(STARTUP.resolve(e.getKey()))));
          require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)) && history.equals(Pg422SignedMigration.history(schema)));
          require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
          if(verifyOnly){db.rollback();stage="VERIFY_OWNED_CLOSE";return Boolean.TRUE;}
          Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
          for(var e:bytes.entrySet())save(e.getKey(),e.getValue());
          save("original-before.private",original.toString().getBytes(StandardCharsets.UTF_8));save("backup-before.private",backup.toString().getBytes(StandardCharsets.UTF_8));
          save("rows-before.private",rows.toString().getBytes(StandardCharsets.UTF_8));save("business-before.private",business.toString().getBytes(StandardCharsets.UTF_8));
          Pg387TrustedDeployment.sync(SAVE);Pg387TrustedDeployment.sync(SAVE.getParent());
          stage="SAVE_PRESERVATION";terminal();unchangedSignedFiles();require(before.equals(files.current()));
          for(var e:bytes.entrySet())require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(e.getKey()),4096)) && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(STARTUP.resolve(e.getKey()))));
          require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)) && history.equals(Pg422SignedMigration.history(schema)));
          try {
            mutating[0]=true;stage="ACTIVATE_CODE_ONLY";Pg387TrustedDeployment.activate(next);
            stage="POST_PRESERVATION";terminal();unchangedSignedFiles();var after=files.current();
            require(after.state()==StartupPermitRecords.State.INVALID && after.boot().equals(before.boot()) && after.activation().equals(before.activation()) && !after.epoch().equals(before.epoch()));
            // New INVALID is the only namespace mutation; old signed four records are retained.
            require(names(actualNames(),before.epoch()));
            for(var e:bytes.entrySet())if(!e.getKey().equals("epoch.current"))require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(e.getKey()),4096)) && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(STARTUP.resolve(e.getKey()))));
            require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)) && history.equals(Pg422SignedMigration.history(schema)));
            require(Arrays.equals(next.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))) && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(NEXT));
            save("activation-body.private","codeOnly=true\nschema027=true\noriginalPending=true\nall341Preserved=true\npermitsIssued=0\nunitsStarted=0\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);db.rollback();
          }catch(Exception|Error unknown){retain();}
        }catch(Exception|Error ownedUnknown){if(mutating[0] || stage.equals("VERIFY_OWNED_CLOSE") || ownedUnknown.getSuppressed().length!=0)retain();throw ownedUnknown;}
        return Boolean.TRUE;
      })).orElseThrow();
      } catch(Exception|Error admissionUnknown) {
        if(mutating[0] || stage.equals("VERIFY_OWNED_CLOSE") || admissionUnknown.getSuppressed().length!=0) {
          System.err.println("PG468_CODE_ONLY_POST_ADMISSION_UNKNOWN M_RETAINED=true A_OWNERSHIP_NOT_INFERRED=true nextStartIsolated=true");retain();
        }
        throw admissionUnknown;
      }
    })).orElseThrow());
    if(!verifyOnly){save("complete.private","codeOnly=true\nschema027=true\nallOwnedScopesReturnedNormally=true\nall341Preserved=true\noldThirtySixRecordsPreserved=true\nunitsStarted=0\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);}
    System.out.println("PG468_CODE_ONLY_"+(verifyOnly?"VERIFIED":"ACTIVATED")+" signed027=true all341Full14AndBusinessOriginalBackupTransferPreserved=true all9KernelEmpty=true ddl0=true permits0=true starts0=true ownedClosed=true");
  }
}
