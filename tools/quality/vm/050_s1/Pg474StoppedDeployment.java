import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;

/** PG-D378 / SSC190191193194195: code-only after authenticated genuine stopped PG473.
 * No stop/start, DDL, restored /run, reused permit or historical UNKNOWN normalization.
 */
public final class Pg474StoppedDeployment {
  static final String SOURCE="09b448644cfe70c87df9c89aa5c0c1bf6efdeeea";
  static final String DIGEST="3f6b837c12282baca8b2c5fc79c85916421b6940471cca5d544381072120af18";
  static final String OLD_SOURCE="a5f9e6a54427ff356626245230496d8667082465";
  static final String OLD_DIGEST="ffae42347b43d9654d026f66f10cbf81ce9a98baa30bb33510ff19279d90676d";
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG473");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG474");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg474-stopped-deploy");
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg474-stopped-tools-v1");
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static String phase="PREFLIGHT";
  static boolean touched;
  static void require(boolean value){if(!value)throw new IllegalStateException("stopped deployment refused");}
  static boolean arguments(String[] args){return args!=null && args.length==1 && args[0]!=null && Set.of("verify","activate").contains(args[0]);}
  static boolean normalDone(MaintenanceRunFiles.StartupOriginal original){
    return original!=null && original.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
        && !original.activation().id().equals(UUID.fromString("5c87de9a-ec69-492b-a6e2-9926b9f7cac7"))
        && original.completed().isPresent() && original.completed().orElseThrow().outcome()==MaintenanceCompletion.Outcome.SUCCESS
        && !original.completed().orElseThrow().endedAt().isBefore(Instant.parse("2026-10-06T00:19:56Z"))
        && !original.completed().orElseThrow().endedAt().isAfter(Instant.parse("2026-10-06T00:49:57Z"));
  }
  static boolean retainRequired(String stage,boolean changed,Throwable failure){
    return changed || Pg471CompletedReadback.retainRequired(stage,failure);
  }
  static boolean sameMetadata(Map<String,Map<String,Object>> actual,String saved){
    if(actual==null || saved==null)return false;
    var before=Pg471CompletedReadback.snapshot(saved);
    if(!actual.keySet().equals(before.keySet()))return false;
    for(var entry:actual.entrySet())
      if(!Pg471CompletedReadback.snapshot(new TreeMap<>(entry.getValue()).toString())
          .equals(Pg471CompletedReadback.snapshot(before.get(entry.getKey()))))return false;
    return true;
  }
  static void retain(){
    System.err.println("PG474_STOPPED_UNKNOWN phase="+phase+" ownershipRetained=true nextStartIsolated=true historicalUnknownNotNormalized=true");
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static void save(String name,byte[] bytes)throws Exception{
    try(var file=FileChannel.open(SAVE.resolve(name),Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS),
        java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")))){
      var buffer=java.nio.ByteBuffer.wrap(bytes);while(buffer.hasRemaining())file.write(buffer);file.force(true);
    }
    Pg387TrustedDeployment.sync(SAVE);require(Arrays.equals(bytes,Files.readAllBytes(SAVE.resolve(name))));
  }
  static void saveText(String name,Object value)throws Exception{save(name,value.toString().getBytes(StandardCharsets.UTF_8));}
  static void helper(String action,String logName)throws Exception{
    Path log=TOOLS.resolve(logName+".private.log");
    Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
    phase="STOPPED_HELPER_SCOPE_CLOSE";
    var child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg474_stopped_native.py").toString(),action)
        .redirectErrorStream(true).redirectOutput(log.toFile()).start();
    try(var input=child.getOutputStream()){input.flush();}
    if(!child.waitFor(60,java.util.concurrent.TimeUnit.SECONDS))retain();
    phase="STOPPED_HELPER_READBACK";require(child.exitValue()==0);
    require(new String(Pg410KnownAuthRecovery.material(log,4194304),StandardCharsets.US_ASCII)
        .equals("PG474_STOPPED_NATIVE action="+action+" sameSavedCohort=true allNineKernelEmpty=true ordinary143IsStopData=true currentMatched=true starts0=true stops0=true\n"));
  }
  static void signedFiles()throws Exception{
    for(String directory:List.of("db/migration","systemd","config")){
      try(var entries=Files.walk(OLD.resolve(directory))){
        for(Path file:entries.filter(Files::isRegularFile).toList())
          require(Arrays.equals(Files.readAllBytes(file),Files.readAllBytes(NEXT.resolve(OLD.relativize(file)))));
      }
    }
    try(var entries=Files.list(NEXT.resolve("db/migration"))){require(entries.count()==27);}
  }
  static void activate(ReleaseApproval next,StartupPermitFiles files,StartupPermitRecords.Epoch before,
      MaintenanceRunFiles.StartupOriginal original)throws Exception{
    require(normalDone(original) && before.equals(files.current())
        && original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()))));
    save("epoch-before.private",Files.readAllBytes(STARTUP.resolve("epoch.current")));
    var invalid=files.invalidate(before.boot(),UUID.randomUUID(),before.activation());
    require(invalid.equals(files.current()) && invalid.state()==StartupPermitRecords.State.INVALID
        && !invalid.epoch().equals(before.epoch()) && invalid.activation().equals(before.activation()));
    Path approval=Path.of("/etc/schubert-nk/release-approval/current");save("approval-before.private",Files.readAllBytes(approval));
    Path part=approval.resolveSibling("pg474.part");
    try(var file=FileChannel.open(part,Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS),
        java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("r--------")))){
      var buffer=java.nio.ByteBuffer.wrap(next.encode());while(buffer.hasRemaining())file.write(buffer);file.force(true);
    }
    Files.move(part,approval,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(approval.getParent());
    Path current=Path.of("/opt/schubert-nk/current"),link=current.resolveSibling("pg474-current.part");
    saveText("current-before.private",Files.readSymbolicLink(current));Files.createSymbolicLink(link,NEXT);
    Files.move(link,current,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(current.getParent());
    require(Arrays.equals(next.encode(),Files.readAllBytes(approval)) && Files.readSymbolicLink(current).equals(NEXT));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(next);
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    boolean verify=args[0].equals("verify");
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));
    try{require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{var result=StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()->{
        try{
          Pg464CodeOnlyDeployment.configure("PG473",OLD_SOURCE,OLD);var old=Pg387TrustedDeployment.verify();
          require(old.manifestSha256().equals(OLD_DIGEST) && Arrays.equals(old.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
              && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(OLD));
          helper("verify",args[0]+"-before");Pg387TrustedDeployment.requireNoUndeliveredWork();
          Pg464CodeOnlyDeployment.configure("PG474",SOURCE,NEXT);Pg387TrustedDeployment.freezeCandidate();var next=Pg387TrustedDeployment.verify();
          require(next.manifestSha256().equals(DIGEST));signedFiles();
          try{try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);
              var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
            db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
            try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
            var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var before=files.current();
            require(before.state()==StartupPermitRecords.State.ISSUED && before.boot().toString().equals(BOOT) && files.readIssued().releaseDigest().equals(OLD_DIGEST));
            var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()));require(normalDone(original));
            var bytes=Pg471CompletedDeployment.startup();var metadata=Pg471CompletedDeployment.startupMetadata();
            require(Pg473CompletedReadback.namespace(bytes.keySet()));
            var originalBytes=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();require(!backup.isEmpty());
            var fixture=Pg428ColdBootPreparation.fixtureSnapshot();var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==391);
            var business=Pg456SignedMigration.business(schema);var history=Pg422SignedMigration.history(schema);
            require(history.equals(Pg456SignedMigration.expected(NEXT,OLD,27)));
            require(originalBytes.equals(Pg471CompletedReadback.snapshot(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg473-native-stop-v1/original-before.private"))))
                && backup.equals(Pg471CompletedReadback.snapshot(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg473-native-stop-v1/backup-before.private"))))
                && rows.toString().equals(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg473-native-stop-v1/rows-before.private")))
                && business.equals(Pg471CompletedReadback.businessBefore(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg473-native-stop-v1/business-before.private"))))
                && sameMetadata(metadata,Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg473-native-stop-v1/startup-before.private"))));
            if(!verify){
              Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
              for(var entry:bytes.entrySet())save(entry.getKey(),entry.getValue());
              saveText("rows-before.private",rows);saveText("business-before.private",business);saveText("original-before.private",originalBytes);
              saveText("backup-before.private",backup);saveText("fixture-before.private",fixture);saveText("metadata-before.private",metadata);saveText("history-before.private",history);
              touched=true;helper("archive","activate-archive");phase="ACTIVATE_COMPLETED";activate(next,files,before,original);helper("after","activate-after");
              var after=Pg471CompletedDeployment.startup();require(after.keySet().equals(bytes.keySet()));
              for(var entry:bytes.entrySet())if(!entry.getKey().equals("epoch.current"))
                require(Arrays.equals(entry.getValue(),after.get(entry.getKey())) && metadata.get(entry.getKey()).equals(Pg471CompletedDeployment.startupMetadata().get(entry.getKey())));
            }
            require(originalBytes.equals(Pg428ColdBootPreparation.original()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db))
                && business.equals(Pg456SignedMigration.business(schema)) && history.equals(Pg422SignedMigration.history(schema))
                && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot())
                && original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()))));
            db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE";
          }}catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
          phase="A_SCOPE_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
      })).orElseThrow();phase="M_SCOPE_CLOSE";return result;
      }catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
    })).orElseThrow());}catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
    phase="RETURNED";
    if(!verify)saveText("complete.private","allNewScopesReturnedNormally=true\noriginalDonePreserved=true\nrows391=true\nallBackupPreserved=true\nstarts0=true\nstops0=true\npermits0=true\nddl0=true\n");
    System.out.println("PG474_STOPPED_"+(verify?"VERIFIED":"ACTIVATED")+" allNewScopesReturnedNormally=true oldUnknownNormalized=false starts0=true stops0=true permits0=true ddl0=true");
  }
}
