import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.Connection;
import java.util.*;

/** SSC191/DEPLOY008 new completed recovery, never resumed/normalized old interrupted operation.
 * Existing normal DONE is retained; only new INVALID/current/static bootstrap Unit are written.
 */
public final class Pg466CompletedRecovery {
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg466-completed-recovery");
  static String stage="PREFLIGHT";static boolean touched;
  static void require(boolean b){if(!b)throw new IllegalStateException("new completed recovery refused at "+stage);}
  static boolean arguments(String[] args){return args!=null && args.length==1 && "activate".equals(args[0]);}
  static void retain(){System.err.println("PG466_NEW_RECOVERY_UNKNOWN stage="+stage+" newOwnedScopesRetained=true oldCloseNotInferred=true");Pg465CompletedDeployment.retain();}
  static void save(String name,byte[] data)throws Exception{
    require(!name.contains("/"));var p=SAVE.resolve(name);Files.write(p,data,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var f=FileChannel.open(p,StandardOpenOption.READ)){f.force(true);}require(Arrays.equals(data,Files.readAllBytes(p)));Pg387TrustedDeployment.sync(SAVE);
  }
  static void terminal()throws Exception{
    byte[] data=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/python3","-B","/var/lib/pgpt-s1-preservation/pg466-tool-v5/pg466_handoff.py","closed");
    require(new String(data,StandardCharsets.US_ASCII).equals("PG466_CLOSED allNineUnchanged=true oldPhysicalHolderAbsent=true oldCloseUnknown=true\n"));
    Pg387TrustedDeployment.requireNoUndeliveredWork();
  }
  static void preserved(Map<String,String> before,Connection db,Connection schema,Map<String,byte[]> raw)throws Exception{
    require(before.get("rows").equals(Pg407FailedRootRecovery.databaseRows(db).toString()));
    require(Pg464CompletedReadback.businessBefore(before.get("business")).equals(Pg456SignedMigration.business(schema)));
    require(Pg464CompletedReadback.snapshot(before.get("backup")).equals(Pg428ColdBootPreparation.backupSnapshot()));
    require(Pg466MapText.canonical(before.get("original")).equals(Pg466MapText.canonical(Pg428ColdBootPreparation.original().toString())));
    require(Pg466MapText.canonical(before.get("fixture")).equals(Pg466MapText.canonical(Pg428ColdBootPreparation.fixtureSnapshot())));
    require(before.get("history").equals(Pg422SignedMigration.history(schema).toString()));
    var current=Pg465CompletedDeployment.startup();require(current.keySet().equals(raw.keySet()));
    for(var e:raw.entrySet())if(!e.getKey().equals("epoch.current")){
      require(Arrays.equals(e.getValue(),current.get(e.getKey())));
      require(before.get("startup."+e.getKey()).equals(Pg410KnownAuthRecovery.metadata(Pg465CompletedDeployment.STARTUP.resolve(e.getKey()))+":"+Pg410KnownAuthRecovery.hash(e.getValue())));
    }
  }
  interface Action {void run(int step)throws Exception;}
  static void sequence(Action action)throws Exception{for(int step=0;step<6;step++)action.run(step);}
  static void activate(ReleaseApproval next,StartupPermitFiles files,StartupPermitRecords.Epoch before,MaintenanceRunFiles.StartupOriginal original)throws Exception{
    require(Pg465CompletedDeployment.normalDone(original) && original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()))) && before.equals(files.current()));
    var current=Path.of("/etc/schubert-nk/release-approval/current");var link=Path.of("/opt/schubert-nk/current");var installed=Path.of("/etc/systemd/system",Pg465CompletedDeployment.UNIT);
    save("epoch-before.private",Files.readAllBytes(Pg465CompletedDeployment.STARTUP.resolve("epoch.current")));
    save("approval-before.private",Files.readAllBytes(current));save("current-before.private",Files.readSymbolicLink(link).toString().getBytes(StandardCharsets.US_ASCII));
    sequence(step->{stage="ACTIVATE_STEP_"+step;touched=true;
      switch(step){
        case 0->{var invalid=files.invalidate(before.boot(),UUID.randomUUID(),before.activation());require(invalid.equals(files.current()) && invalid.state()==StartupPermitRecords.State.INVALID && !invalid.epoch().equals(before.epoch()) && invalid.activation().equals(before.activation()));}
        case 1->{Files.copy(Pg465CompletedDeployment.NEXT.resolve("systemd").resolve(Pg465CompletedDeployment.UNIT),installed);Files.setPosixFilePermissions(installed,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r--r--"));try(var f=FileChannel.open(installed,StandardOpenOption.READ)){f.force(true);}Pg387TrustedDeployment.sync(installed.getParent());}
        case 2->{var p=new ProcessBuilder("/usr/bin/systemctl","daemon-reload").redirectError(ProcessBuilder.Redirect.DISCARD).start();require(p.waitFor(10,java.util.concurrent.TimeUnit.SECONDS) && p.exitValue()==0);}
        case 3->{var part=current.resolveSibling("pg466.part");Files.write(part,next.encode(),StandardOpenOption.CREATE_NEW);Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));try(var f=FileChannel.open(part,StandardOpenOption.READ)){f.force(true);}Files.move(part,current,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(current.getParent());}
        case 4->{var part=link.resolveSibling("pg466-current.part");Files.createSymbolicLink(part,Pg465CompletedDeployment.NEXT);Files.move(part,link,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(link.getParent());}
        case 5->{require(Arrays.equals(next.encode(),Files.readAllBytes(current)) && Files.readSymbolicLink(link).equals(Pg465CompletedDeployment.NEXT));StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(next);require(Arrays.equals(Files.readAllBytes(installed),Files.readAllBytes(Pg465CompletedDeployment.NEXT.resolve("systemd").resolve(Pg465CompletedDeployment.UNIT))));var state=new String(Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",Pg465CompletedDeployment.UNIT,"--property=UnitFileState,ActiveState,MainPID,ControlPID,Job"),StandardCharsets.US_ASCII);require(Set.of(state.split("\n")).equals(Set.of("UnitFileState=static","ActiveState=inactive","MainPID=0","ControlPID=0","Job=")));}
        default->throw new IllegalStateException("fixed step only");
      }
    });
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(Pg465CompletedDeployment.BOOT) && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()->{
        try{
          terminal();Pg466HandoffReadback.main(new String[]{"verify"});var before=Pg466HandoffReadback.values();
          Pg464CodeOnlyDeployment.configure("PG465",Pg465CompletedDeployment.SOURCE,Pg465CompletedDeployment.NEXT);Pg387TrustedDeployment.freezeCandidate();var next=Pg387TrustedDeployment.verify();require(next.manifestSha256().equals(Pg465CompletedDeployment.DIGEST));Pg465CompletedDeployment.signedFiles();
          try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg465CompletedDeployment.STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
            try{
              db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
              try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && Boolean.TRUE.equals(r.getObject(1,Boolean.class)) && !r.next());}
              var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.boot().toString().equals(Pg465CompletedDeployment.BOOT) && files.readIssued().releaseDigest().equals(Pg464CompletedReadback.DIGEST));
              var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));require(Pg465CompletedDeployment.normalDone(original));var raw=Pg465CompletedDeployment.startup();preserved(before,db,schema,raw);terminal();
              Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));for(var e:before.entrySet())save(e.getKey()+".private",e.getValue().getBytes(StandardCharsets.UTF_8));
              activate(next,files,epoch,original);terminal();preserved(before,db,schema,raw);require(original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()))));
              db.rollback();schema.rollback();stage="NEW_OWNED_SCOPE_CLOSE";
            }catch(Exception|Error e){if(touched || stage.endsWith("SCOPE_CLOSE") || e.getSuppressed().length!=0)retain();throw e;}
          }catch(Exception|Error e){if(touched || stage.endsWith("SCOPE_CLOSE") || e.getSuppressed().length!=0)retain();throw e;}
          return Boolean.TRUE;
        }catch(Exception|Error e){if(touched || stage.endsWith("SCOPE_CLOSE") || e.getSuppressed().length!=0)retain();throw e;}
      })).orElseThrow();}catch(Exception|Error e){if(touched || stage.endsWith("SCOPE_CLOSE") || e.getSuppressed().length!=0)retain();throw e;}
      return Boolean.TRUE;
    })).orElseThrow();
    save("complete.private","newOwnedScopesReturnedNormally=true\noldInterrupted143=true\noldCloseUnknown=true\noriginalDonePreserved=true\nrows331=true\nbackup20=true\nstarts0=true\npermits0=true\nddl0=true\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);
    System.out.println("PG466_COMPLETED_RECOVERY_ACTIVATED newOwnedScopesReturnedNormally=true oldCloseUnknown=true originalDone=true rows331=true backup20=true starts0=true permits0=true ddl0=true formal=false");
  }
}
