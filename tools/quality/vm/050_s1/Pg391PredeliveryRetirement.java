import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;

/** SSC123 fixed isolated recovery of actual BUG368; not UNKNOWN/intent cleanup or a startup issuer. */
public final class Pg391PredeliveryRetirement {
  static final String OLD="6b41c7f23f124530b65a1a82976f8b85";
  static final String PARENT="8b1de6b715544579bee5524c214b1653";
  static final Path REQUEST=Path.of("/run/schubert-nk/cleanup-request");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg391-predelivery");
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println(
        "PG391_PREDELIVERY_REFUSED diagnosticsRedacted=true type="+e.getClass().getName()));
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new IllegalStateException("isolated VM only");
    Pg387TrustedDeployment.LABEL="PG391"; Pg387TrustedDeployment.STEM="pg391";
    Pg387TrustedDeployment.SOURCE="6ce5bb93ce7497de4ab0f5a5e495782e28e08858";
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG391");
    MaintenanceFileLock.create().tryExclusive(()->StartupAdmissionFile.create().tryExclusive(a->
        Pg387TrustedDeployment.checked(()->{
          checkUnits();
          var approval=Pg387TrustedDeployment.verify();
          var parsed=ReleaseApproval.parse(Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")));
          if(!parsed.version().equals(approval.version())
              || !parsed.manifestSha256().equals(approval.manifestSha256()))throw new IllegalStateException("current approval differs");
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(parsed);
          try(var startup=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
              var directory=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),REQUEST)) {
            var epoch=new StartupPermitFiles(startup,LinuxInodeSecurity.create()).current();
            if(epoch.state()!=StartupPermitRecords.State.INVALID || epoch.permitDigest().isPresent())throw new IllegalStateException("INVALID required");
            var original=MaintenanceRunFiles.create().execute(s->s.observe(epoch.activation()));
            if(!original.equals(epoch.activation()))throw new IllegalStateException("original mismatch");
            var requests=new CleanupWorkerRequestFiles(directory,LinuxInodeSecurity.create());
            var owners=CleanupWorkerRequestFiles.forOwner(directory,LinuxInodeSecurity.create(),CleanupWorkerRequestFiles.OwnerSource.PARENT);
            var request=requests.read(); var owner=owners.readOwner();
            if(!owner.morning().invocation().equals(PARENT) || owner.cleanup().isPresent()
                || Files.exists(Path.of("/proc",Long.toString(owner.morning().pid())))
                || !owner.boot().equals(epoch.boot()) || !owner.epoch().equals(epoch.epoch())
                || !owner.run().equals(original.run().id()) || !owner.activation().equals(original.id())
                || !owner.cutoff().equals(original.run().cutoff())
                || !request.run().equals(owner.run()) || !request.activation().equals(owner.activation())
                || !request.cutoff().equals(owner.cutoff()))throw new IllegalStateException("orphan binding mismatch");
            try(var names=Files.list(REQUEST)) {
              if(!new TreeSet<>(names.map(p->p.getFileName().toString()).toList())
                  .equals(new TreeSet<>(List.of("cleanup-request","maintenance-owner"))))throw new IllegalStateException("intent/extra namespace");
            }
            try(var maintenance=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/maintenance"))) {
              new InspectorEnvironmentPublisher(maintenance,LinuxInodeSecurity.create()).requireFresh();
            }
            if(Files.exists(SAVED,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("preserve previous recovery");
            Files.createDirectory(SAVED,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
            save("cleanup-request",request.encode()); save("maintenance-owner",owner.encode());
            checkUnits();
            if(!new StartupPermitFiles(startup,LinuxInodeSecurity.create()).current().equals(epoch))throw new IllegalStateException("Epoch changed");
            requests.retire(request); owners.retireOwner(owner); requests.requireClear();
            checkUnits(); Pg387TrustedDeployment.sync(SAVED);
            System.out.println("PG391_PREDELIVERY_RETIRED M_A=true oldCleanupUnchanged=true originalInvalidUnchanged=true rawPrivatelySaved=true permitsIssued=0");
          }
          return true;
        })).orElseThrow()).orElseThrow();
  }
  static void save(String name,byte[] bytes)throws Exception {
    var p=SAVED.resolve(name);
    Files.write(p,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,PosixFilePermissions.fromString("rw-------"));
    try(var file=FileChannel.open(p,StandardOpenOption.READ)){file.force(true);}
  }
  static void checkUnits()throws Exception {
    Pg387TrustedDeployment.terminalAll();
    var process=new ProcessBuilder("/usr/bin/systemctl","show","schubert-nk-cleanup.service",
        "-p","InvocationID","-p","ExecMainStatus","-p","ExecMainCode","-p","Result").start();
    String text=new String(process.getInputStream().readAllBytes(),StandardCharsets.US_ASCII);
    if(process.waitFor()!=0 || !Set.of(text.split("\n")).equals(Set.of("InvocationID="+OLD,
        "ExecMainStatus=30","ExecMainCode=1","Result=exit-code")))throw new IllegalStateException("old Cleanup changed");
  }
}
