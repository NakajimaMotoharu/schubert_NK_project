import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.ByteBuffer;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;

/** Fixed isolated negative fixture, not runtime/permit fallback. SSC115/PT-BFAILED-VM001.
 * Root M/A + stop-all + pinned BOM + preserved INVALID original; no DB/schema/clock edits.
 * Values/credential hash never emitted. The original remains private until safe restoration.
 */
public final class BackupFailureFixture {
  static final Path DIR=Path.of("/etc/schubert-nk/credentials");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg386-original-backup-pgpass");
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->{
      System.err.println("FIXTURE_REFUSED diagnosticRedacted=true type="+e.getClass().getName());
      for(var f:e.getStackTrace())if(f.getClassName().equals("BackupFailureFixture"))System.err.println("FIXTURE_FRAME "+f.getMethodName()+":"+f.getLineNumber());
    });
    if(args.length!=1 || !Set.of("fail","restore").contains(args[0]))throw new IllegalArgumentException("fixed mode");
    if(!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new IllegalStateException("isolated VM only");
    MaintenanceFileLock.create().tryExclusive(()->{
      Pg386TrustedDeployment.checked(()->{Pg386TrustedDeployment.stopAll();return true;});
      return StartupAdmissionFile.create().tryExclusive(a->Pg386TrustedDeployment.checked(()->{
        Pg386TrustedDeployment.terminalAll();
        var release=Pg386TrustedDeployment.verify();
        Path approvalPath=Path.of("/etc/schubert-nk/release-approval/current");
        long size=Files.size(approvalPath);
        if(size<1||size>dev.codex.schubert.nk.bootstrap.ReleaseApproval.MAX_BYTES)throw new IllegalStateException("approval bounds");
        byte[] approval=Pg386TrustedDeployment.material(approvalPath,(int)size);
        var parsed=dev.codex.schubert.nk.bootstrap.ReleaseApproval.parse(approval);
        if(!parsed.version().equals(release.version())||!parsed.manifestSha256().equals(release.manifestSha256()))throw new IllegalStateException("current release differs");
        dev.codex.schubert.nk.bootstrap.StartupReleaseManifest.createHost(new dev.codex.schubert.nk.bootstrap.FixedServiceIdentity().configurationGroup()).verify(parsed);
        requireAbsent(Path.of("/run/schubert-nk/backup-request/backup-start.intent"));
        try(var startup=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))){
          var epoch=new StartupPermitFiles(startup,LinuxInodeSecurity.create()).current();
          if(epoch.state()!=StartupPermitRecords.State.INVALID || epoch.permitDigest().isPresent())throw new IllegalStateException("INVALID required");
          var observed=MaintenanceRunFiles.create().execute(s->s.observe(epoch.activation()));
          if(!observed.equals(epoch.activation()))throw new IllegalStateException("original differs");
        }
        var dir=Files.readAttributes(DIR,"unix:uid,gid,mode",LinkOption.NOFOLLOW_LINKS);
        if(!dir.equals(Map.of("uid",0,"gid",0,"mode",0040700)))throw new IllegalStateException("credential namespace");
        Path current=DIR.resolve("backup-pgpass"),part=DIR.resolve("pg386-pgpass.part");
        requireMaterial(current);
        requireAbsent(part);
        if(args[0].equals("fail")){
          requireAbsent(SAVED);
          Files.copy(current,SAVED,StandardCopyOption.COPY_ATTRIBUTES);
          requireMaterial(SAVED);
          try(var held=FileChannel.open(SAVED,StandardOpenOption.READ)){held.force(true);}
          Pg386TrustedDeployment.sync(SAVED.getParent());
          Files.createFile(part,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
          byte[] invalid=("127.0.0.1:5432:schubert_nk:schubert_backup:"+UUID.randomUUID()+"\n").getBytes(java.nio.charset.StandardCharsets.US_ASCII);
          try(var output=FileChannel.open(part,StandardOpenOption.WRITE)){
            var bytes=ByteBuffer.wrap(invalid);while(bytes.hasRemaining())if(output.write(bytes)<=0)throw new IllegalStateException("fixture write");output.force(true);
          }finally{Arrays.fill(invalid,(byte)0);}
        }else{
          requireMaterial(SAVED);
          Path failed=SAVED.resolveSibling("pg386-failed-backup-pgpass");
          requireAbsent(failed);
          Files.copy(current,failed,StandardCopyOption.COPY_ATTRIBUTES);
          try(var held=FileChannel.open(failed,StandardOpenOption.READ)){held.force(true);}
          Pg386TrustedDeployment.sync(failed.getParent());
          Files.copy(SAVED,part,StandardCopyOption.COPY_ATTRIBUTES);
        }
        requireMaterial(part);
        try(var held=FileChannel.open(part,StandardOpenOption.READ)){held.force(true);}
        Files.move(part,current,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        Pg386TrustedDeployment.sync(DIR);
        requireMaterial(current);
        if(args[0].equals("restore") && Files.mismatch(SAVED,current)!=-1)throw new IllegalStateException("restoration differs");
        Pg386TrustedDeployment.terminalAll();
        System.out.println("PG386 BACKUP_FIXTURE "+args[0]+" completed=true originalPrivatelyPreserved=true inputValuesNotEmitted=true permitsIssued=0");
        return true;
      })).orElseThrow();
    }).orElseThrow();
  }
  static void requireAbsent(Path path)throws Exception{
    try{Files.readAttributes(path,"unix:mode",LinkOption.NOFOLLOW_LINKS);throw new IllegalStateException("unexpected existing entry");}
    catch(NoSuchFileException missing){/* Only exact no-entry, never general IO. */}
  }
  static void requireMaterial(Path path)throws Exception{
    var a=Files.readAttributes(path,"unix:uid,gid,mode,nlink,size",LinkOption.NOFOLLOW_LINKS);
    if(!a.get("uid").equals(0)||!a.get("gid").equals(0)||!a.get("mode").equals(0100600)||!a.get("nlink").equals(1)||(Long)a.get("size")<1||(Long)a.get("size")>1024)throw new IllegalStateException("credential material metadata");
  }
}
