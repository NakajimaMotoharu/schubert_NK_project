import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** BOOT007..008: new source initial ADMIN accepted, snapshot before a NEW ordinary Morning.
 * Real new M/A + read-only DB; never issues permit/start or rewrites old DONE/backup/current.
 */
public final class Pg467BeforeNewRun {
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg467-before-new-run");
  static void require(boolean b){if(!b)throw new IllegalStateException("new-run baseline refused");}
  public static void main(String[] args)throws Exception{
    require(args.length==0 && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(Pg465CompletedDeployment.BOOT));
    var values=new TreeMap<String,String>();
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()->{
        Pg466CompletedRecovery.terminal();Pg464CodeOnlyDeployment.configure("PG465",Pg465CompletedDeployment.SOURCE,Pg465CompletedDeployment.NEXT);var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals(Pg465CompletedDeployment.DIGEST) && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))) && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg465CompletedDeployment.NEXT));
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg465CompletedDeployment.STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
          db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();require(epoch.state()==StartupPermitRecords.State.INVALID && epoch.boot().toString().equals(Pg465CompletedDeployment.BOOT));
          require(Pg465CompletedDeployment.normalDone(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()))));
          var raw=Pg465CompletedDeployment.startup();require(raw.size()==33 && raw.keySet().stream().noneMatch(s->s.contains("intent")));
          var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==331);
          values.put("rows",rows.toString());values.put("business",Pg456SignedMigration.business(schema).toString());values.put("backup",Pg428ColdBootPreparation.backupSnapshot().toString());values.put("original",Pg428ColdBootPreparation.original().toString());values.put("fixture",Pg428ColdBootPreparation.fixtureSnapshot());values.put("history",Pg422SignedMigration.history(schema).toString());
          try(var q=schema.createStatement();var r=q.executeQuery("select count(*) from schubert.app_users where role='ADMIN' and status='ACTIVE'")){require(r.next() && r.getLong(1)==1 && !r.next());}
          Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
          for(var e:values.entrySet())write(e.getKey()+".private",e.getValue().getBytes(StandardCharsets.UTF_8));for(var e:raw.entrySet())write(e.getKey(),e.getValue());
          require(rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && raw.keySet().equals(Pg465CompletedDeployment.startup().keySet()));db.rollback();schema.rollback();
        }
        return Boolean.TRUE;
      })).orElseThrow();return Boolean.TRUE;
    })).orElseThrow();
    write("complete.private","newReadOnlyMAAndDbReturnedNormally=true\nrows331=true\nstartup33=true\nadmin1=true\noldOriginalDone=true\nstarts0=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG467_BEFORE_NEW_RUN_ACCEPTED newReadOnlyMAAndDbReturnedNormally=true sourcePG465=true rows331=true startup33=true admin1=true oldDonePreserved=true starts0=true");
  }
  static void write(String name,byte[] data)throws Exception{
    var p=SAVE.resolve(name);Files.write(p,data,StandardOpenOption.CREATE_NEW);Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));try(var f=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){f.force(true);}require(Arrays.equals(data,Files.readAllBytes(p)));Pg387TrustedDeployment.sync(SAVE);
  }
}
