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
public final class Pg387TrustedDeployment {
  static Path RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG387");
  static String LABEL="PG387", STEM="pg387", SOURCE="7ba352d6f";
  static UUID ORIGINAL_RUN=UUID.fromString("31100027-2222-4333-8444-555555555555");
  static final Path PRESERVE=Path.of("/var/lib/pgpt-s1-preservation");
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e) -> {
      System.err.println(LABEL+" DEPLOYMENT_REFUSED diagnosticsRedacted=true type="+e.getClass().getName());
      for(var frame:e.getStackTrace()) {
        if(frame.getClassName().equals("Pg387TrustedDeployment"))
          System.err.println(LABEL+" FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
      }
    });
    if((args.length!=1 && args.length!=3 && args.length!=4) || !Set.of("verify","activate").contains(args[0])) throw new IllegalArgumentException("fixed mode");
    if(args.length>=3) {
      if(!args[1].matches("0\\.1\\.0-PG[0-9]{3}") || !args[2].matches("[0-9a-f]{40}"))
        throw new IllegalArgumentException("isolated candidate/source");
      LABEL=args[1].substring(6); STEM=LABEL.toLowerCase(Locale.ROOT); SOURCE=args[2];
      RELEASE=Path.of("/opt/schubert-nk/releases",args[1]);
      if(args.length==4) {
        ORIGINAL_RUN=UUID.fromString(args[3]);
        if(!ORIGINAL_RUN.toString().equals(args[3]) || ORIGINAL_RUN.equals(new UUID(0,0)))throw new IllegalArgumentException("explicit preserved original");
      }
    }
    if(!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01")) throw new IllegalStateException("isolated VM only");
    var result=MaintenanceFileLock.create().tryExclusive(() -> {
      System.out.println(LABEL+" STAGE M_ACQUIRED");
      var failedRoot=checked(() -> {
        var recovery=Pg407FailedRootRecovery.captureIfPresent();
        if(recovery==null)requireNoUndeliveredWork();
        return java.util.Optional.ofNullable(recovery);
      });
      checked(() -> { stopAll(); return Boolean.TRUE; });
      System.out.println(LABEL+" STAGE ALL_STOPPED");
      return StartupAdmissionFile.create().tryExclusive(admission -> {
        System.out.println(LABEL+" STAGE A_ACQUIRED");
        return checked(() -> {
          terminalAll();
          freezeCandidate();
          var approval=verify();
          if(args[0].equals("activate")) {
            if(failedRoot.isPresent()) failedRoot.orElseThrow().retire();
            requireNoUndeliveredWork();
            activate(approval);
          }
          terminalAll();
          return Boolean.TRUE;
        });
      }).orElseThrow();
    }).orElseThrow();
    if(!result) throw new IllegalStateException("deployment result");
    System.out.println(LABEL+" DEPLOYMENT "+args[0]+" source="+SOURCE+" completed=true signatureAndBom=true runtimePermitIssued=false");
  }
  interface Checked<T> { T execute() throws Exception; }
  static void requireNoUndeliveredWork() throws Exception {
    for(String name:List.of("backup-request","cleanup-request","expiry-request")) {
      Path directory=Path.of("/run/schubert-nk",name);
      if(!Files.isDirectory(directory,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("fixed request namespace");
      try(var entries=Files.list(directory)) {
        if(entries.findAny().isPresent())throw new IllegalStateException("unresolved work isolated");
      }
    }
    if(Files.exists(Path.of("/run/schubert-nk/startup/broker-start.intent"),LinkOption.NOFOLLOW_LINKS))
      throw new IllegalStateException("unresolved Broker start isolated");
    try(var entries=Files.list(Path.of("/run/schubert-nk/startup"))) {
      for(var entry:entries.toList()) {
        String name=entry.getFileName().toString();
        if(!name.equals("epoch.current") && !name.matches("(?!00000000-0000-0000-0000-000000000000\\.)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\.(permit|owner|API\\.launch|WEB\\.launch)"))
          throw new IllegalStateException("unresolved startup namespace isolated");
      }
    }
  }
  static <T> T checked(Checked<T> work) throws java.io.IOException {
    try { return work.execute(); }
    catch (RuntimeException programming) { throw programming; }
    catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); throw new java.io.IOException("deployment interrupted"); }
    catch (Exception known) { throw new java.io.IOException("deployment failed"); }
  }
  static ReleaseApproval verify() throws Exception {
    byte[] pin=material(Path.of("/etc/schubert-nk/deployment-key/pin.der"),44);
    byte[] signature=material(PRESERVE.resolve(STEM+"-manifest.sig"),64);
    byte[] original=Files.readAllBytes(RELEASE.resolve("RELEASE-MANIFEST.json"));
    if(original.length==0 || original.length>1048576) throw new IllegalStateException("manifest bounds");
    new ReleaseSignatureVerifier(pin).verify(original,signature);
    System.out.println(LABEL+" STAGE PINNED_SIGNATURE_VERIFIED");
    String observedSource=com.google.gson.JsonParser.parseString(new String(original,StandardCharsets.UTF_8))
        .getAsJsonObject().getAsJsonObject("source").get("commit").getAsString();
    if(!observedSource.startsWith(SOURCE))throw new IllegalStateException("signed source mismatch");
    var approval=new ReleaseApproval("0.1.0-"+LABEL,HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(original)));
    var inspected=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verifyCandidate(approval);
    System.out.println(LABEL+" STAGE FULL_CANDIDATE_BOM_VERIFIED");
    if(!inspected.version().equals(approval.version()) || inspected.migrations().size()!=expectedHistoryCount()) throw new IllegalStateException("BOM mismatch");
    return approval;
  }
  static int expectedHistoryCount() {
    // The one still-installed preservation source has V001..023. Never derive expectations
    // from observed DB/manifest counts; new candidates require the approved V001..025.
    return LABEL.equals("PG408") && SOURCE.equals("32c6a7b1e79abf114901003c4a8f1300b33bf0c0") ? 24 : 26;
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
    System.out.println(LABEL+" STAGE FIXED_CANDIDATE_HOST_RO");
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
    installOwnedUnitDelta(old);
    Files.write(PRESERVE.resolve(STEM+"-previous-approval"),previous,StandardOpenOption.CREATE_NEW);
    Path part=dir.resolve(STEM+".part");
    Files.write(part,approval.encode(),StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var f=FileChannel.open(part,StandardOpenOption.READ)){f.force(true);}
    Files.move(part,dir.resolve("current"),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
    sync(dir);
    Path current=Path.of("/opt/schubert-nk/current"), next=current.resolveSibling(STEM+"-current.part");
    Path previousLink=Files.readSymbolicLink(current);
    Files.writeString(PRESERVE.resolve(STEM+"-previous-current.txt"),previousLink+"\n",StandardOpenOption.CREATE_NEW);
    Files.createSymbolicLink(next,RELEASE);
    Files.move(next,current,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
    sync(current.getParent());
    var result=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(ReleaseApproval.parse(Files.readAllBytes(dir.resolve("current"))));
    if(!result.version().equals("0.1.0-"+LABEL)) throw new IllegalStateException("activation readback");
  }
  static void invalidatePreservedRun() throws Exception {
    if(Files.exists(Path.of("/run/schubert-nk/backup-request/backup-start.intent"),LinkOption.NOFOLLOW_LINKS))
      throw new IllegalStateException("unresolved start isolated");
    try(var root=dev.codex.schubert.nk.storage.OwnedTransferDirectory.open(
        dev.codex.schubert.nk.storage.LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))) {
      var files=new StartupPermitFiles(root,dev.codex.schubert.nk.storage.LinuxInodeSecurity.create());
      var old=files.current();
      UUID boot=UUID.fromString(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim());
      if(!old.boot().equals(boot)
          || !old.activation().run().id().equals(ORIGINAL_RUN))
        throw new IllegalStateException("preserved startup binding");
      if(old.state()==StartupPermitRecords.State.ISSUED) {
        var permit=files.readIssued();
        var prior=ReleaseApproval.parse(Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")));
        var oldRelease=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(prior);
        if(!permit.releaseDigest().equals(oldRelease.sha256())) throw new IllegalStateException("prior issued release binding");
      }
      var original=MaintenanceRunFiles.create().execute(session -> session.observe(old.activation()));
      if(!original.equals(old.activation()))throw new IllegalStateException("original mismatch");
      byte[] actual=Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current"));
      if(!old.equals(StartupPermitRecords.readEpoch(actual)) || !old.equals(files.current()))
        throw new IllegalStateException("prior raw epoch drift");
      Files.write(PRESERVE.resolve(STEM+"-previous-epoch"),actual,StandardOpenOption.CREATE_NEW);
      Files.setPosixFilePermissions(PRESERVE.resolve(STEM+"-previous-epoch"),java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
      var next=files.invalidate(boot,UUID.randomUUID(),old.activation());
      if(!next.equals(files.current()) || next.state()!=StartupPermitRecords.State.INVALID
          || !next.activation().equals(old.activation()) || next.epoch().equals(old.epoch()))
        throw new IllegalStateException("INVALID readback");
      System.out.println(LABEL+" STAGE FRESH_INVALID_PRESERVED_ORIGINAL");
    }
  }
  /** SSC125 isolated provisioning only: exact old/new signed BOM, M/A and full stop held above.
   * Never repair UNKNOWN request/intent, change a drop-in, or admit arbitrary Unit differences.
   */
  static void installOwnedUnitDelta(ReleaseApproval old) throws Exception {
    Path installed=Path.of("/etc/systemd/system");
    Path prior=Path.of("/opt/schubert-nk/releases",old.version(),"systemd");
    Path next=RELEASE.resolve("systemd");
    var names=List.of("schubert-nk-morning-controller.service","schubert-nk-backup.service",
        "schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service",
        "schubert-nk-expiry-cleanup.service","schubert-nk-api.service",
        "schubert-nk-web.service","artemis.service");
    var allowed=Set.of("schubert-nk-morning-controller.service","schubert-nk-expiry-cleanup.service", "artemis.service","schubert-nk-api.service","schubert-nk-web.service");
    var changes=new LinkedHashMap<String,byte[]>();
    for(var name:names) {
      Path actual=installed.resolve(name);
      var attributes=Files.readAttributes(actual,"unix:uid,gid,mode,nlink",LinkOption.NOFOLLOW_LINKS);
      if(!Integer.valueOf(0).equals(attributes.get("uid")) || !Integer.valueOf(0).equals(attributes.get("gid"))
          || !Integer.valueOf(0100644).equals(attributes.get("mode")) || !Integer.valueOf(1).equals(attributes.get("nlink")))
        throw new IllegalStateException("fixed Unit metadata");
      byte[] before=Files.readAllBytes(actual), previous=Files.readAllBytes(prior.resolve(name)), candidate=Files.readAllBytes(next.resolve(name));
      if(!Arrays.equals(before,previous))throw new IllegalStateException("old signed Unit base mismatch");
      if(!Arrays.equals(previous,candidate)) {
        if(!allowed.contains(name))throw new IllegalStateException("unapproved Unit delta");
        if(name.equals("schubert-nk-api.service") || name.equals("schubert-nk-web.service")) {
          validateRootDelta(name,previous,candidate);
          changes.put(name,candidate);
          continue;
        }
        String addition=name.equals("schubert-nk-morning-controller.service")
            ? "LoadCredential=mq-ops:/etc/schubert-nk/credentials/mq-ops\n"
            : name.equals("schubert-nk-expiry-cleanup.service")
                ? "LoadCredential=maintenance-owner:/run/schubert-nk/expiry-request/maintenance-owner\n"
                : "SuccessExitStatus=143\n";
        String text=new String(candidate,StandardCharsets.UTF_8);
        if(!text.contains(addition) || !Arrays.equals(text.replace(addition,"").getBytes(StandardCharsets.UTF_8),previous))
          throw new IllegalStateException("closed credential-only Unit delta");
        changes.put(name,candidate);
      }
    }
    for(var entry:changes.entrySet()) {
      String name=entry.getKey();
      Path actual=installed.resolve(name), saved=PRESERVE.resolve(STEM+"-previous-"+name);
      Files.write(saved,Files.readAllBytes(actual),StandardOpenOption.CREATE_NEW);
      Files.setPosixFilePermissions(saved,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
      try(var f=FileChannel.open(saved,StandardOpenOption.READ)){f.force(true);}
      Path part=installed.resolve(STEM+"-"+name+".part");
      Files.write(part,entry.getValue(),StandardOpenOption.CREATE_NEW);
      Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r--r--"));
      try(var f=FileChannel.open(part,StandardOpenOption.READ)){f.force(true);}
      Files.move(part,actual,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
      sync(installed);
    }
    if(!changes.isEmpty()) {
      var reload=new ProcessBuilder("/usr/bin/systemctl","daemon-reload").inheritIO().start();
      if(!reload.waitFor(20,java.util.concurrent.TimeUnit.SECONDS) || reload.exitValue()!=0)
        throw new IllegalStateException("Unit reload unavailable; preserved before-image retained");
    }
    for(var name:names)if(!Arrays.equals(Files.readAllBytes(installed.resolve(name)),Files.readAllBytes(next.resolve(name))))
      throw new IllegalStateException("new signed Unit base mismatch");
    terminalAll();
    System.out.println(LABEL+" STAGE SIGNED_UNIT_DELTA_VERIFIED count="+changes.size()+" oldSignedBases=true dropInsUnchanged=true beforeImagesPreserved=true");
  }

  /** SSC141: one exact signed old-to-Root transform; other directives remain byte-identical. */
  static void validateRootDelta(String name,byte[] previous,byte[] candidate) {
    String role=switch(name) {
      case "schubert-nk-api.service" -> "api";
      case "schubert-nk-web.service" -> "web";
      default -> throw new IllegalArgumentException("closed Root Unit");
    };
    String before=new String(previous,StandardCharsets.UTF_8);
    String after=new String(candidate,StandardCharsets.UTF_8);
    if(!Arrays.equals(before.getBytes(StandardCharsets.UTF_8),previous)
        || !Arrays.equals(after.getBytes(StandardCharsets.UTF_8),candidate)
        || !before.endsWith("\n") || !after.endsWith("\n") || before.contains("\r") || after.contains("\r"))
      throw new IllegalStateException("canonical Unit bytes");
    String oldMain="-cp /opt/schubert-nk/current/"+role+"/"+role+".jar:/opt/schubert-nk/current/"+role+"/lib/* dev.codex.schubert.nk."+role+".bootstrap."+(role.equals("api")?"Api":"Web")+"ProcessMain";
    var expected=new ArrayList<String>(); int transformed=0;
    for(String line:before.split("\n",-1)) {
      if(line.startsWith("#")) continue;
      if(line.startsWith("ExecStart=")) {
        if(!line.startsWith("ExecStart=/usr/bin/java ") || !line.endsWith(oldMain))
          throw new IllegalStateException("prior fixed ordinary entry");
        expected.add(line.replace("ExecStart=/","ExecStart=!/").replace(oldMain,
            "-cp /opt/schubert-nk/current/operations/batch.jar:/opt/schubert-nk/current/operations/lib/* dev.codex.schubert.nk.batch.file.RootServiceLauncher "+role.toUpperCase(Locale.ROOT)));
        expected.add("CapabilityBoundingSet=CAP_SETUID CAP_SETGID CAP_SETPCAP CAP_SYS_PTRACE CAP_DAC_READ_SEARCH");
        transformed++;
      } else if(role.equals("api") && line.equals("Requires=schubert-nk-expiry-cleanup.service artemis.service postgresql.service"))
        expected.add("Requires=artemis.service postgresql.service");
      else expected.add(line);
    }
    List<String> actual=Arrays.stream(after.split("\n",-1)).filter(line -> !line.startsWith("#")).toList();
    if(transformed!=1 || !expected.equals(actual)) throw new IllegalStateException("closed Root Unit delta");
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
