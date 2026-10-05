import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** SSC191/DEPLOY006: read-only admin diagnostic under identified old holder, never authority.
 * snapshot is new-only and private; verify compares every original/DB/Backup/Transfer value.
 * No M/A acquisition is claimed here, nor old close success. New ownership is a separate step.
 */
public final class Pg466HandoffReadback {
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg466-before-handoff");
  static void require(boolean b){if(!b)throw new IllegalStateException("fixed handoff readback differs");}
  static Map<String,String> values()throws Exception{
    var result=new TreeMap<String,String>();
    Pg464CodeOnlyDeployment.configure("PG464",Pg464CompletedReadback.SOURCE,Pg465CompletedDeployment.OLD);
    var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals(Pg464CompletedReadback.DIGEST));
    require(Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))) && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg465CompletedDeployment.OLD));
    Pg387TrustedDeployment.requireNoUndeliveredWork();
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg465CompletedDeployment.STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
      db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var current=files.current();
      require(current.state()==StartupPermitRecords.State.ISSUED && current.boot().toString().equals(Pg465CompletedDeployment.BOOT) && files.readIssued().releaseDigest().equals(Pg464CompletedReadback.DIGEST));
      var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(current.activation()));require(Pg465CompletedDeployment.normalDone(original));
      var bytes=Pg465CompletedDeployment.startup();require(bytes.size()==33);
      for(var e:bytes.entrySet()){
        require(Arrays.equals(e.getValue(),Files.readAllBytes(Pg465CompletedDeployment.SAVE.resolve(e.getKey()))));
        result.put("startup."+e.getKey(),Pg410KnownAuthRecovery.metadata(Pg465CompletedDeployment.STARTUP.resolve(e.getKey()))+":"+Pg410KnownAuthRecovery.hash(e.getValue()));
      }
      var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==331 && rows.toString().equals(Files.readString(Pg465CompletedDeployment.SAVE.resolve("rows-before.private"))));
      var business=Pg456SignedMigration.business(schema);require(business.equals(Pg464CompletedReadback.businessBefore(Files.readString(Pg465CompletedDeployment.SAVE.resolve("business-before.private")))));
      var backup=Pg428ColdBootPreparation.backupSnapshot();require(backup.size()==20 && backup.equals(Pg464CompletedReadback.snapshot(Files.readString(Pg465CompletedDeployment.SAVE.resolve("backup-before.private")))));
      result.put("rows",rows.toString());result.put("business",business.toString());result.put("backup",backup.toString());
      result.put("original",Pg428ColdBootPreparation.original().toString());result.put("fixture",Pg428ColdBootPreparation.fixtureSnapshot().toString());
      result.put("history",Pg422SignedMigration.history(schema).toString());
      require(Pg422SignedMigration.history(schema).equals(Pg456SignedMigration.expected(Pg465CompletedDeployment.NEXT,Pg465CompletedDeployment.OLD,27)));
      require(original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(current.activation()))) && current.equals(files.current()));
      db.rollback();schema.rollback();
    }
    return Map.copyOf(result);
  }
  public static void main(String[] args)throws Exception{
    require(args.length==1 && Set.of("snapshot","verify").contains(args[0]));boolean snapshot=args[0].equals("snapshot");
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(Pg465CompletedDeployment.BOOT));
    var before=values();
    if(snapshot){
      require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
      for(var e:before.entrySet()){
        var p=SAVE.resolve(e.getKey()+".private");Files.writeString(p,e.getValue(),StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW);
        Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
        try(var f=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){f.force(true);}
      }Pg387TrustedDeployment.sync(SAVE);Pg387TrustedDeployment.sync(SAVE.getParent());
    }
    try(var entries=Files.list(SAVE)){require(entries.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet()).equals(before.keySet().stream().map(k->k+".private").collect(java.util.stream.Collectors.toSet())));}
    for(var e:before.entrySet()){
      String saved=Files.readString(SAVE.resolve(e.getKey()+".private"));
      if(Set.of("business","backup","original","fixture").contains(e.getKey()))require(Pg466MapText.canonical(e.getValue()).equals(Pg466MapText.canonical(saved)));
      else require(e.getValue().equals(saved));
    }
    require(before.equals(values()));
    System.out.println("PG466_HANDOFF_READBACK allReadOnlyScopesReturnedNormally=true actualNewObservation=true oldToolCloseNotInferred=true full331=true backup20=true originalDone=true startup33=true mutation0=true");
  }
}
