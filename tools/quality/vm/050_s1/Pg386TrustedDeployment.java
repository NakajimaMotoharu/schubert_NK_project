import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Isolated PG/PT VM trusted operator, NOT a Morning/worker probe or runtime authority fallback.
 * SS343 initial provisioning exception/SSC096/110. Fixed separately provisioned pin, genuine
 * original-byte signature/full Production BOM before any approval. Private input never printed.
 * Actual application source must already be built/tested/committed. No clean/repair/baseline.
 */
public final class Pg386TrustedDeployment {
  static final Path RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG386");
  static final Path PRESERVE=Path.of("/var/lib/pgpt-s1-preservation");
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e) -> {
      System.err.println("PG386 DEPLOYMENT_REFUSED diagnosticsRedacted=true type="+e.getClass().getName());
      for(var frame:e.getStackTrace()) {
        if(frame.getClassName().equals("Pg386TrustedDeployment"))
          System.err.println("PG386 FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
      }
    });
    if(args.length!=1 || !Set.of("verify","activate").contains(args[0])) throw new IllegalArgumentException("fixed mode");
    if(!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01")) throw new IllegalStateException("isolated VM only");
    var result=MaintenanceFileLock.create().tryExclusive(() -> {
      System.out.println("PG386 STAGE M_ACQUIRED");
      checked(() -> { stopAll(); return Boolean.TRUE; });
      System.out.println("PG386 STAGE ALL_STOPPED");
      return StartupAdmissionFile.create().tryExclusive(admission -> {
        System.out.println("PG386 STAGE A_ACQUIRED");
        return checked(() -> {
          terminalAll();
          freezeCandidate();
          var approval=verify();
          if(args[0].equals("activate")) activate(approval);
          terminalAll();
          return Boolean.TRUE;
        });
      }).orElseThrow();
    }).orElseThrow();
    if(!result) throw new IllegalStateException("deployment result");
    System.out.println("PG386 DEPLOYMENT "+args[0]+" completed=true signatureAndBom=true runtimePermitIssued=false");
  }
  interface Checked<T> { T execute() throws Exception; }
  static <T> T checked(Checked<T> work) throws java.io.IOException {
    try { return work.execute(); }
    catch (RuntimeException programming) { throw programming; }
    catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); throw new java.io.IOException("deployment interrupted"); }
    catch (Exception known) { throw new java.io.IOException("deployment failed"); }
  }
  static ReleaseApproval verify() throws Exception {
    byte[] pin=material(Path.of("/etc/schubert-nk/deployment-key/pin.der"),44);
    byte[] signature=material(PRESERVE.resolve("pg386-manifest.sig"),64);
    byte[] original=Files.readAllBytes(RELEASE.resolve("RELEASE-MANIFEST.json"));
    if(original.length==0 || original.length>1048576) throw new IllegalStateException("manifest bounds");
    new ReleaseSignatureVerifier(pin).verify(original,signature);
    System.out.println("PG386 STAGE PINNED_SIGNATURE_VERIFIED");
    var approval=new ReleaseApproval("0.1.0-PG386",HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(original)));
    var inspected=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verifyCandidate(approval);
    System.out.println("PG386 STAGE FULL_CANDIDATE_BOM_VERIFIED");
    if(!inspected.version().equals(approval.version()) || inspected.migrations().size()!=24) throw new IllegalStateException("BOM mismatch");
    return approval;
  }
  static void freezeCandidate() throws Exception {
    // BUG342: host immutable payload, not merely ProtectSystem's private RO view.
    // Fixed isolated candidate only; M/A and terminal stop set are held by caller.
    var mounted=new ProcessBuilder("/usr/bin/mountpoint","-q",RELEASE.toString()).start();
    int status=mounted.waitFor();
    if(status==1 || status==32) {
      var bind=new ProcessBuilder("/usr/bin/mount","--bind",RELEASE.toString(),RELEASE.toString()).inheritIO().start();
      if(bind.waitFor()!=0) throw new IllegalStateException("candidate bind failed");
    } else if(status!=0) throw new IllegalStateException("candidate mount query failed");
    var freeze=new ProcessBuilder("/usr/bin/mount","-o","remount,bind,ro",RELEASE.toString()).inheritIO().start();
    if(freeze.waitFor()!=0) throw new IllegalStateException("candidate immutable mount failed");
    System.out.println("PG386 STAGE FIXED_CANDIDATE_HOST_RO");
  }
  static void activate(ReleaseApproval approval) throws Exception {
    invalidatePreservedRun();
    Path dir=Path.of("/etc/schubert-nk/release-approval");
    if(!Files.isDirectory(dir,LinkOption.NOFOLLOW_LINKS)
       || !Integer.valueOf(0).equals(Files.getAttribute(dir,"unix:uid",LinkOption.NOFOLLOW_LINKS))
       || !Integer.valueOf(0040700).equals(Files.getAttribute(dir,"unix:mode",LinkOption.NOFOLLOW_LINKS)))
      throw new IllegalStateException("existing approval namespace");
    long size=Files.size(dir.resolve("current"));
    if(size<1 || size>1024)throw new IllegalStateException("existing approval bounds");
    byte[] previous=material(dir.resolve("current"),(int)size);
    var old=ReleaseApproval.parse(previous);
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(old);
    Files.write(PRESERVE.resolve("pg386-previous-approval"),previous,StandardOpenOption.CREATE_NEW);
    Path part=dir.resolve("pg386.part");
    Files.write(part,approval.encode(),StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var f=FileChannel.open(part,StandardOpenOption.READ)){f.force(true);}
    Files.move(part,dir.resolve("current"),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
    sync(dir);
    Path current=Path.of("/opt/schubert-nk/current"), next=current.resolveSibling("pg386-current.part");
    Path previousLink=Files.readSymbolicLink(current);
    Files.writeString(PRESERVE.resolve("pg386-previous-current.txt"),previousLink+"\n",StandardOpenOption.CREATE_NEW);
    Files.createSymbolicLink(next,RELEASE);
    Files.move(next,current,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
    sync(current.getParent());
    var result=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(ReleaseApproval.parse(Files.readAllBytes(dir.resolve("current"))));
    if(!result.version().equals("0.1.0-PG386")) throw new IllegalStateException("activation readback");
  }
  static void invalidatePreservedRun() throws Exception {
    if(Files.exists(Path.of("/run/schubert-nk/backup-request/backup-start.intent"),LinkOption.NOFOLLOW_LINKS))
      throw new IllegalStateException("unresolved start isolated");
    try(var root=dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
        dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))) {
      var files=new StartupPermitFiles(root,dev.codex.schubert.nk.storage.LinuxInodeSecurity.create());
      var old=files.current();
      UUID boot=UUID.fromString(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim());
      if(old.state()!=StartupPermitRecords.State.INVALID || old.permitDigest().isPresent()
          || !old.boot().equals(boot)
          || !old.activation().run().id().equals(UUID.fromString("31100027-2222-4333-8444-555555555555")))
        throw new IllegalStateException("preserved INVALID only");
      var original=MaintenanceRunFiles.create().execute(session -> session.observe(old.activation()));
      if(!original.equals(old.activation()))throw new IllegalStateException("original mismatch");
      Files.write(PRESERVE.resolve("pg386-previous-epoch"),StartupPermitRecords.epoch(old),StandardOpenOption.CREATE_NEW);
      var next=files.invalidate(boot,UUID.randomUUID(),old.activation());
      if(!next.equals(files.current()) || next.state()!=StartupPermitRecords.State.INVALID
          || !next.activation().equals(old.activation()) || next.epoch().equals(old.epoch()))
        throw new IllegalStateException("INVALID readback");
      System.out.println("PG386 STAGE FRESH_INVALID_PRESERVED_ORIGINAL");
    }
  }
  static void stopAll() throws Exception {
    for(var unit:MaintenanceUnit.values()) {
      var p=new ProcessBuilder("/usr/bin/systemctl","stop",unit.serviceName()).inheritIO().start();
      if(p.waitFor()!=0)throw new IllegalStateException("stop failed");
    }
    terminalAll();
  }
  static void terminalAll() throws Exception {
    for(var unit:MaintenanceUnit.values()) {
      var p=new ProcessBuilder("/usr/bin/systemctl","show",unit.serviceName(),"--property=LoadState,ActiveState,MainPID,ControlPID,ControlGroup,Job").start();
      String raw=new String(p.getInputStream().readAllBytes(),StandardCharsets.US_ASCII);
      if(p.waitFor()!=0)throw new IllegalStateException("unit observation failed");
      var fields=new HashMap<String,String>();
      for(String line:raw.split("\n")){int split=line.indexOf('=');if(split<1 || fields.put(line.substring(0,split),line.substring(split+1))!=null)throw new IllegalStateException("unit profile");}
      if(!fields.keySet().equals(Set.of("LoadState","ActiveState","MainPID","ControlPID","ControlGroup","Job"))
          || !"loaded".equals(fields.get("LoadState")) || !Set.of("inactive","failed").contains(fields.get("ActiveState"))
          || !"0".equals(fields.get("MainPID")) || !"0".equals(fields.get("ControlPID")) || !"".equals(fields.get("Job")))throw new IllegalStateException("unit not terminal");
      Path cgroup=Path.of("/sys/fs/cgroup/system.slice",unit.serviceName());
      if(Files.exists(cgroup)) {
        if(!Files.readString(cgroup.resolve("cgroup.procs")).isBlank() || !Files.readString(cgroup.resolve("cgroup.events")).contains("populated 0\n"))throw new IllegalStateException("unit processes remain");
      }
    }
  }
  static byte[] material(Path p,int size) throws Exception {
    var before=Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS);
    if(!Integer.valueOf(0).equals(before.get("uid")) || !Integer.valueOf(0).equals(before.get("gid")) || !Integer.valueOf(0100400).equals(before.get("mode"))
       || !Integer.valueOf(1).equals(before.get("nlink")) || !Long.valueOf(size).equals(before.get("size")))throw new IllegalStateException("fixed public material metadata");
    byte[] value=Files.readAllBytes(p);
    if(value.length!=size || !before.equals(Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS)))throw new IllegalStateException("public material changed");
    return value;
  }
  static void sync(Path dir) throws Exception {try(var f=FileChannel.open(dir,StandardOpenOption.READ)){f.force(true);}}
}
