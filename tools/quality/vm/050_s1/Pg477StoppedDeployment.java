import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;

/** PG-D380 / SSC190191193194195: code-only after authenticated genuine stopped PG474.
 * No stop/start, DDL, restored /run, reused permit or historical UNKNOWN normalization.
 */
public final class Pg477StoppedDeployment {
  static final String SOURCE="cce61f63900b1479f9f8dbdc338e222b1c8c38a3";
  static final String DIGEST="613b71a06c2b215887219cd3502d3db34542fea957e0d88dbb9c54c8bab18667";
  static final String OLD_SOURCE="979c5ac3e9c28ae76363adacdf9f0736f5a59df1";
  static final String OLD_DIGEST="9183662292299cc86412c31a551bf140c8b32ccd9b2d6dcdd414b14e4bcd4806";
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG475");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG477");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg477-stopped-deploy");
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg477-stopped-tools-v3");
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static String phase="PREFLIGHT";
  static boolean touched;
  static void require(boolean value){if(!value)throw new IllegalStateException("stopped deployment refused");}
  static boolean arguments(String[] args){return args!=null && args.length==1 && args[0]!=null && Set.of("verify","activate").contains(args[0]);}
  static boolean normalDone(MaintenanceRunFiles.StartupOriginal original){
    return original!=null && original.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
        && !original.activation().id().equals(UUID.fromString("5c87de9a-ec69-492b-a6e2-9926b9f7cac7"))
        && original.completed().isPresent() && original.completed().orElseThrow().outcome()==MaintenanceCompletion.Outcome.SUCCESS
        && !original.completed().orElseThrow().endedAt().isBefore(Instant.parse("2026-10-06T03:26:09Z"))
        && !original.completed().orElseThrow().endedAt().isAfter(Instant.parse("2026-10-06T03:56:10Z"));
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
    System.err.println("PG477_STOPPED_UNKNOWN phase="+phase+" ownershipRetained=true nextStartIsolated=true historicalUnknownNotNormalized=true");
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
    var child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg477_stopped_native.py").toString(),action)
        .redirectErrorStream(true).redirectOutput(log.toFile()).start();
    try(var input=child.getOutputStream()){input.flush();}
    if(!child.waitFor(60,java.util.concurrent.TimeUnit.SECONDS))retain();
    phase="STOPPED_HELPER_READBACK";require(child.exitValue()==0);
    require(new String(Pg410KnownAuthRecovery.material(log,4194304),StandardCharsets.US_ASCII)
        .equals("PG477_STOPPED_NATIVE action="+action+" sameSavedCohort=true allNineKernelEmpty=true ordinary143IsStopData=true currentMatched=true starts0=true stops0=true\n"));
  }
  static boolean allowedUnitDelta(String name,byte[] before,byte[] after) {
    if(name==null || before==null || after==null || before.length==0 || before.length>65536 || after.length>65536)return false;
    if(!Set.of("systemd/schubert-nk-inbox-inspector.service","systemd/schubert-nk-bootstrap-admin.service").contains(name))return Arrays.equals(before,after);
    for(byte value:before)if(value!=10 && value!=9 && ((value>=0 && value<32) || value==127))return false;
    String old=new String(before,StandardCharsets.UTF_8);
    if(!Arrays.equals(before,old.getBytes(StandardCharsets.UTF_8)) || old.contains("ReadWritePaths=") || !old.endsWith("\n"))return false;
    String expected;
    if(name.equals("systemd/schubert-nk-bootstrap-admin.service")) {
      String prefix="ExecStart=/usr/bin/java --enable-native-access=ALL-UNNAMED";
      if(old.split(java.util.regex.Pattern.quote(prefix),-1).length!=2)return false;
      expected=old.replace(prefix,prefix+" -javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=BOOTSTRAP-${INVOCATION_ID}-ordinary")+"\nReadWritePaths=/run/schubert-nk/pt-coverage/ordinary-bootstrap196\n";
    }else expected=old+"\nReadWritePaths=/run/schubert-nk/pt-coverage/ordinary-inspector196\n";
    return Arrays.equals(expected.getBytes(StandardCharsets.UTF_8),after);
  }
  static void signedFiles()throws Exception{
    for(String directory:List.of("db/migration","systemd","config")){
      try(var entries=Files.walk(OLD.resolve(directory))){
        for(Path file:entries.filter(Files::isRegularFile).toList())
          require(allowedUnitDelta(OLD.relativize(file).toString(),Files.readAllBytes(file),Files.readAllBytes(NEXT.resolve(OLD.relativize(file)))));
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
    Path part=approval.resolveSibling("pg477.part");
    try(var file=FileChannel.open(part,Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS),
        java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("r--------")))){
      var buffer=java.nio.ByteBuffer.wrap(next.encode());while(buffer.hasRemaining())file.write(buffer);file.force(true);
    }
    Files.move(part,approval,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(approval.getParent());
    Path current=Path.of("/opt/schubert-nk/current"),link=current.resolveSibling("pg477-current.part");
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
          phase="REFERENCE_SCOPE_CLOSE";var refs=new Pg477UnitReferences(TOOLS,args[0]);
          try {
          phase="SIGNED_OLD";Pg464CodeOnlyDeployment.configure("PG475",OLD_SOURCE,OLD);var old=Pg387TrustedDeployment.verify();
          require(old.manifestSha256().equals(OLD_DIGEST) && Arrays.equals(old.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
              && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(OLD));
          helper("verify",args[0]+"-before");Pg387TrustedDeployment.requireNoUndeliveredWork();
          Pg464CodeOnlyDeployment.configure("PG477",SOURCE,NEXT);Pg387TrustedDeployment.freezeCandidate();var next=Pg387TrustedDeployment.verify();
          require(next.manifestSha256().equals(DIGEST));signedFiles();
          try{try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);
              var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
            db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
            try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
            var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var before=files.current();
            require(before.state()==StartupPermitRecords.State.ISSUED && before.boot().toString().equals(BOOT) && files.readIssued().releaseDigest().equals(OLD_DIGEST));
            var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()));require(normalDone(original));
            var bytes=Pg471CompletedDeployment.startup();var metadata=Pg471CompletedDeployment.startupMetadata();
            require(Pg475CompletedReadback.namespace(bytes.keySet()));
            var originalBytes=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();require(!backup.isEmpty());
            var fixture=Pg428ColdBootPreparation.fixtureSnapshot();var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==411);
            var business=Pg456SignedMigration.business(schema);var history=Pg422SignedMigration.history(schema);
            require(history.equals(Pg456SignedMigration.expected(NEXT,OLD,27)));
            require(originalBytes.equals(Pg471CompletedReadback.snapshot(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg475-native-stop-v1/original-before.private"))))
                && backup.equals(Pg471CompletedReadback.snapshot(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg475-native-stop-v1/backup-before.private"))))
                && rows.toString().equals(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg475-native-stop-v1/rows-before.private")))
                && business.equals(Pg471CompletedReadback.businessBefore(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg475-native-stop-v1/business-before.private"))))
                && sameMetadata(metadata,Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg475-native-stop-v1/startup-before.private"))));
            if(!verify){
              Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
              for(var entry:bytes.entrySet())save(entry.getKey(),entry.getValue());
              saveText("rows-before.private",rows);saveText("business-before.private",business);saveText("original-before.private",originalBytes);
              saveText("backup-before.private",backup);saveText("fixture-before.private",fixture);saveText("metadata-before.private",metadata);saveText("history-before.private",history);
              touched=true;helper("archive","activate-archive");phase="ACTIVATE_COMPLETED";activate(next,files,before,original);phase="UNIT_CONFIGURE";refs.configure();helper("after","activate-after");
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
          phase="REFERENCE_SCOPE_CLOSE";refs.check();refs.release();
          } catch(Exception|Error failure){
            if(retainRequired(phase,touched,failure))retain();
            String failedStage=phase;phase="REFERENCE_SCOPE_CLOSE";refs.release();phase=failedStage;throw failure;
          }
          phase="A_SCOPE_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
      })).orElseThrow();phase="M_SCOPE_CLOSE";return result;
      }catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
    })).orElseThrow());}catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain();throw failure;}
    phase="RETURNED";
    if(!verify)saveText("complete.private","allNewScopesReturnedNormally=true\noriginalDonePreserved=true\nrows411=true\nallBackupPreserved=true\nstarts0=true\nstops0=true\npermits0=true\nddl0=true\n");
    System.out.println("PG477_STOPPED_"+(verify?"VERIFIED":"ACTIVATED")+" allNewScopesReturnedNormally=true oldUnknownNormalized=false starts0=true stops0=true permits0=true ddl0=true");
  }
}
