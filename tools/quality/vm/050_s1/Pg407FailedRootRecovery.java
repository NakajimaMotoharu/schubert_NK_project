import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.*;
import java.util.*;

/** SSC144 isolated PG406 normal30 recovery. No inferred successful run or historical close.
 * Invoked only inside trusted operator's M, then M/A. Public process correlation stays private.
 * Native runtime authority remains Production RootFailedStartRecovery's typed inode operation.
 */
public final class Pg407FailedRootRecovery {
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg407-failed-root");
  static final Path PRIOR=Path.of("/var/lib/pgpt-s1-preservation/pg407-prior-receipts");
  static final String EPOCH="2f5f22a6-76dd-4e3e-a063-5f14b37c67ac";
  static final String OLD_PERMIT="5ae82ba7-bda0-442a-882a-29f94b5b286e.permit";
  static final UUID RUN=UUID.fromString("31100027-2222-4333-8444-555555555555");
  static final UUID ACTIVATION=UUID.fromString("31100027-6666-4777-8888-999999999999");
  static final Set<String> NAMES=Set.of("epoch.current",EPOCH+".permit",EPOCH+".owner",
      EPOCH+".API.launch",EPOCH+".API.start.intent","permit-start.intent",OLD_PERMIT);
  final RootFailedStartRecovery.Evidence evidence;
  final InspectorUnitSnapshot morning,api;
  final Map<String,byte[]> original;
  private Pg407FailedRootRecovery(RootFailedStartRecovery.Evidence e,
      InspectorUnitSnapshot m,InspectorUnitSnapshot a,Map<String,byte[]> bytes) {
    evidence=e; morning=m; api=a; original=bytes;
  }
  static Pg407FailedRootRecovery captureIfPresent() throws Exception {
    if(!Files.exists(STARTUP.resolve("permit-start.intent"),LinkOption.NOFOLLOW_LINKS))return null;
    if(!Set.of("PG407","PG408").contains(Pg387TrustedDeployment.LABEL))throw new IllegalStateException("fixed recovery candidate only");
    var bytes=captureBytes();
    try(var directory=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {
      var e=RootFailedStartRecovery.observe(directory,LinuxInodeSecurity.create());
      if(!e.invalid().epoch().toString().equals(EPOCH) || !e.invalid().activation().id().equals(ACTIVATION)
          || !e.invalid().activation().run().id().equals(RUN)
          || !e.invalid().activation().run().cutoff().equals(java.time.Instant.parse("2026-09-27T15:00:00Z"))
          || !e.owner().morning().invocation().equals("c64c649cf5dc4871b3288d5340f32308")
          || e.owner().morning().pid()!=627659 || e.owner().morning().startTicks()!=12240057
          || !e.child().invocation().equals("bdc0de30a4b2403f88c90887dedaaf62")
          || e.child().pid()!=729546 || e.child().startTicks()!=12303351
          || e.service()!=ServiceConfigFiles.Service.API)throw new IllegalStateException("fixed old generation");
      var m=InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.MORNING).read();
      var a=InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.API).read();
      var actualM=m; var actualA=a;
      // Genuine prior independent full manager observation, never reconstruct30 from cold.
      if(Files.exists(PRIOR,LinkOption.NOFOLLOW_LINKS)) {
        m=prior("morning-before.properties",InspectorUnitSnapshot.Target.MORNING,
            "3a672d61d862a243e8856b80920ba54b03426879845d9a5de47b345627e2b4f0");
        a=prior("api-before.properties",InspectorUnitSnapshot.Target.API,
            "e074f719c9b6bb1f4c9a4e2b6e718ac816c622746440516781f8d2806c1891fd");
      }
      if(!m.failedRootGeneration(e.owner().morning().invocation()) || !a.failedRootGeneration(e.child().invocation())
          || !actualM.failedRootStillStoppedAfter(m) || !actualA.failedRootStillStoppedAfter(a)
          || !actualM.matches(InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.MORNING).read())
          || !actualA.matches(InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.API).read()))
        throw new IllegalStateException("old normal30 receipts required");
      if(!Files.exists(PRIOR,LinkOption.NOFOLLOW_LINKS))persistObserved(m,a);
      return new Pg407FailedRootRecovery(e,m,a,bytes);
    }
  }
  void retire() throws Exception {
    // M/A are continuously owned by trusted deployment caller; no start/stop/new Epoch here.
    verifyOldRelease();
    try(var database=openDatabase();
        var directory=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {
      database.setAutoCommit(false);
      try(var lock=database.createStatement(); var rows=lock.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
        if(!rows.next() || !Boolean.TRUE.equals(rows.getObject(1,Boolean.class)) || rows.next())
          throw new IllegalStateException("dedicated advisory unavailable");
      }
      var before=databaseRows(database);
      if(before.size()!=152)throw new IllegalStateException("all prior full rows required");
      var backup=backupSnapshot();
      verifyPhysical(); verifyOriginal(database); verifyBytes(original);
      if(Files.exists(SAVED,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("preserved recovery exists");
      Files.createDirectory(SAVED,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(
          java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
      for(var entry:original.entrySet()) {
        var target=SAVED.resolve(entry.getKey());
        Files.write(target,entry.getValue(),StandardOpenOption.CREATE_NEW);
        Files.setPosixFilePermissions(target,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
        try(var channel=FileChannel.open(target,StandardOpenOption.READ)){channel.force(true);}
        if(!Arrays.equals(entry.getValue(),Files.readAllBytes(target)))throw new IllegalStateException("private readback");
      }
      Pg387TrustedDeployment.sync(SAVED); Pg387TrustedDeployment.sync(SAVED.getParent());
      RootFailedStartRecovery.retire(directory,LinuxInodeSecurity.create(),evidence,expected ->
          Pg387TrustedDeployment.checked(() -> {
            if(!expected.equals(evidence))throw new IllegalStateException("retirement binding");
            verifyPhysical(); verifyOriginal(database); verifyOldRelease();
            if(!before.equals(databaseRows(database)))throw new IllegalStateException("prior complete DB mutation");
            if(!backup.equals(backupSnapshot()))throw new IllegalStateException("prior backup mutation");
            verifyRemainingArtifacts();
            return Boolean.TRUE;
          }));
      if(!before.equals(databaseRows(database)))throw new IllegalStateException("post DB changed");
      if(!backup.equals(backupSnapshot()))throw new IllegalStateException("post backup changed");
      verifyOriginal(database); verifyPhysical(); verifyRemainingArtifacts();
      database.rollback();
    } catch(Exception | Error failure) {
      try(var restored=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {
        RootFailedStartRecovery.quarantine(restored,LinuxInodeSecurity.create(),evidence);
      } catch(Exception | Error unknown) {
        System.err.println("PG407_RECOVERY_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");
        // No return to enclosing M/A close on unknown restoration/close. Explicit operator
        // intervention is needed; new startup remains excluded by both live native locks.
        for(;;) java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);
      }
      throw failure;
    }
    System.out.println("PG407_FAILED_ROOT_RETIRED M_A_DB=true typedTwoOnly=true priorBytesPrivatelyDurable=true oldDB152Unchanged=true priorRunStillPending=true permitsIssued=0");
  }
  void verifyPhysical() throws Exception {
    var boot=UUID.fromString(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim());
    if(!boot.equals(evidence.invalid().boot()))throw new IllegalStateException("same boot required");
    var m=InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.MORNING).read();
    var a=InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.API).read();
    if(!m.failedRootStillStoppedAfter(morning) || !a.failedRootStillStoppedAfter(api))throw new IllegalStateException("old receipts changed");
    Pg387TrustedDeployment.terminalAll();
    // Morning is NOT added to MaintenanceUnit.values(): that would stop a future parent itself.
    checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    for(var parent:List.of(evidence.owner().morning(),evidence.child()))
      if(Files.exists(Path.of("/proc",Long.toString(parent.pid())),LinkOption.NOFOLLOW_LINKS))
        throw new IllegalStateException("captured PID remains or reused");
    if(!m.matches(InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.MORNING).read())
        || !a.matches(InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.API).read()))
      throw new IllegalStateException("kernel manager instability");
  }
  static void checkTree(Path tree) throws Exception {
    if(!Files.exists(tree,LinkOption.NOFOLLOW_LINKS))return;
    try(var paths=Files.walk(tree)) {
      for(var path:paths.filter(p->Files.isDirectory(p,LinkOption.NOFOLLOW_LINKS)).toList()) {
        if(Files.isSymbolicLink(path) || !Files.readString(path.resolve("cgroup.procs")).isBlank()
            || !Files.readString(path.resolve("cgroup.events")).contains("populated 0\n"))
          throw new IllegalStateException("whole kernel tree not empty");
      }
    }
  }
  void verifyOriginal(Connection connection) throws Exception {
    var observed=MaintenanceRunFiles.create().execute(s->s.observe(evidence.invalid().activation()));
    if(!observed.equals(evidence.invalid().activation()) || !new RunReferenceRepository(connection).read(observed.run()).identityConsistent())
      throw new IllegalStateException("original references differ");
  }
  void verifyOldRelease() throws Exception {
    var approval=ReleaseApproval.parse(Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")));
    if(!approval.version().equals("0.1.0-PG406"))throw new IllegalStateException("old signed release required");
    var manifest=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
    byte[] raw=Files.readAllBytes(Path.of("/opt/schubert-nk/releases/0.1.0-PG406/RELEASE-MANIFEST.json"));
    new ReleaseSignatureVerifier(Pg387TrustedDeployment.material(Path.of("/etc/schubert-nk/deployment-key/pin.der"),44))
        .verify(raw,Pg387TrustedDeployment.material(Path.of("/var/lib/pgpt-s1-preservation/pg406-manifest.sig"),64));
    if(!manifest.sha256().equals(evidence.permit().releaseDigest()))throw new IllegalStateException("old permit release differs");
  }
  static Connection openDatabase() throws Exception {
    Path source=Path.of("/etc/schubert-nk/credentials/db-batch");
    var attrs=Files.readAttributes(source,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS);
    if(!Integer.valueOf(0).equals(attrs.get("uid")) || !Integer.valueOf(0).equals(attrs.get("gid"))
        || !Integer.valueOf(0100600).equals(attrs.get("mode")) || !Integer.valueOf(1).equals(attrs.get("nlink"))
        || (Long)attrs.get("size")<1 || (Long)attrs.get("size")>65536)throw new IllegalStateException("fixed batch source");
    byte[] bytes=Files.readAllBytes(source);
    if(!attrs.equals(Files.readAttributes(source,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS)))
      throw new IllegalStateException("source drift");
    try(var password=InspectorDbCredential.consume(bytes)) {
      char[] chars=password.copyPassword(); var props=new Properties();
      props.setProperty("user","schubert_batch");props.setProperty("connectTimeout","3");props.setProperty("socketTimeout","5");
      try {
        props.setProperty("password",new String(chars));
        var connection=DriverManager.getConnection("jdbc:postgresql://127.0.0.1:5432/schubert_nk",props);
        try {
          connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);connection.setReadOnly(false);
          try(var s=connection.createStatement();var r=s.executeQuery("select current_user,session_user,current_database(),pg_is_in_recovery(),current_setting('transaction_read_only')")) {
            if(!r.next() || !"schubert_batch".equals(r.getString(1)) || !"schubert_batch".equals(r.getString(2))
                || !"schubert_nk".equals(r.getString(3)) || !Boolean.FALSE.equals(r.getObject(4,Boolean.class))
                || !"off".equals(r.getString(5)) || r.next())throw new IllegalStateException("fixed batch role");
          }
          return connection;
        } catch(Exception failure) { connection.close();throw failure; }
      } finally { Arrays.fill(chars,'\0');props.clear(); }
    }
  }
  static List<List<Object>> databaseRows(Connection c) throws Exception {
    var result=new ArrayList<List<Object>>();
    try(var s=c.createStatement()) {
      s.setQueryTimeout(5);
      try(var r=s.executeQuery("select id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary from schubert.batch_runs order by id")) {
        while(r.next()) {
          var row=new ArrayList<Object>();for(int index=1;index<=14;index++)row.add(r.getObject(index));
          if(!terminalRow(row))
            throw new IllegalStateException("complete same-run terminal rows required");
          result.add(Collections.unmodifiableList(row));
        }
      }
    }
    return List.copyOf(result);
  }
  static boolean terminalRow(List<Object> row) {
    if(row==null || row.size()!=14 || !RUN.equals(row.get(1)))return false;
    for(int index=0;index<12;index++)if(row.get(index)==null)return false;
    return Set.of("SUCCESS","WARNING","FAILED","SKIPPED").contains(row.get(7));
  }
  static InspectorUnitSnapshot prior(String name,InspectorUnitSnapshot.Target target,String expectedHash) throws Exception {
    var dir=Files.readAttributes(PRIOR,"unix:uid,gid,mode",LinkOption.NOFOLLOW_LINKS);
    if(!Integer.valueOf(0).equals(dir.get("uid")) || !Integer.valueOf(0).equals(dir.get("gid"))
        || !Integer.valueOf(0040700).equals(dir.get("mode")))throw new IllegalStateException("fixed prior private directory");
    var p=PRIOR.resolve(name);
    var before=Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS);
    if(!Integer.valueOf(0).equals(before.get("uid")) || !Integer.valueOf(0).equals(before.get("gid"))
        || !Integer.valueOf(0100600).equals(before.get("mode")) || !Integer.valueOf(1).equals(before.get("nlink"))
        || (Long)before.get("size")<1 || (Long)before.get("size")>2048)throw new IllegalStateException("fixed prior material");
    var bytes=Files.readAllBytes(p);
    if(!expectedHash.equals(HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)))
        || !before.equals(Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS)))
      throw new IllegalStateException("actual prior byte drift");
    return InspectorUnitSnapshot.parse(bytes,target);
  }
  static void persistObserved(InspectorUnitSnapshot morning,InspectorUnitSnapshot api) throws Exception {
    // This fixed PG406 recovery ordinarily imports the authentic pre-stop tool observation.
    // A fresh caller may capture and preserve matching genuine manager bytes, never serialize
    // claims into receipt evidence. Same fixed expected hashes remain independently required.
    Files.createDirectory(PRIOR,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(
        java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
    for(var entry:Map.of("morning-before.properties",InspectorUnitSnapshot.Target.MORNING,
        "api-before.properties",InspectorUnitSnapshot.Target.API).entrySet()) {
      var process=new ProcessBuilder("/usr/bin/systemctl","show",entry.getValue().unit(),
          "--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,Result,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL").start();
      byte[] raw=process.getInputStream().readNBytes(2049);
      if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS) || process.exitValue()!=0
          || raw.length>2048 || !(entry.getValue()==InspectorUnitSnapshot.Target.MORNING ? morning : api)
              .matches(InspectorUnitSnapshot.parse(raw,entry.getValue())))throw new IllegalStateException("capture changed");
      var p=PRIOR.resolve(entry.getKey());Files.write(p,raw,StandardOpenOption.CREATE_NEW);
      Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
      try(var channel=FileChannel.open(p,StandardOpenOption.READ)){channel.force(true);}
      if(!Arrays.equals(raw,Files.readAllBytes(p)))throw new IllegalStateException("capture private readback");
    }
    Pg387TrustedDeployment.sync(PRIOR);Pg387TrustedDeployment.sync(PRIOR.getParent());
  }
  static Map<String,byte[]> captureBytes() throws Exception {
    try(var paths=Files.list(STARTUP)) {
      if(!paths.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet()).equals(NAMES))
        throw new IllegalStateException("exact seven old entries required");
    }
    var result=new HashMap<String,byte[]>();
    for(var name:NAMES) {
      var p=STARTUP.resolve(name);
      var before=Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS);
      if(!Integer.valueOf(0).equals(before.get("uid")) || !Integer.valueOf(0).equals(before.get("gid"))
          || !Integer.valueOf(0100600).equals(before.get("mode")) || !Integer.valueOf(1).equals(before.get("nlink"))
          || (Long)before.get("size")>1024)throw new IllegalStateException("fixed prior metadata");
      var bytes=Files.readAllBytes(p);
      if(!before.equals(Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS)))
        throw new IllegalStateException("prior inode drift");
      result.put(name,bytes);
    }
    return Map.copyOf(result);
  }
  static Map<String,Map<String,Object>> backupSnapshot() throws Exception {
    Path root=Path.of("/srv/schubert-nk/backup");
    var result=new TreeMap<String,Map<String,Object>>();
    try(var paths=Files.walk(root,2)) {
      for(var p:paths.sorted().toList()) {
        var before=new HashMap<>(Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS));
        var attributes=new HashMap<>(before);
        var relative=root.relativize(p);
        if(relative.getNameCount()==2 && relative.getName(0).toString().matches("[0-9]{8}-[0-9]{6}-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
            && Set.of("MANIFEST.json","schubert_nk.dump","config.tar","credentials.tar.age").contains(relative.getName(1).toString())) {
          if(((Integer)before.get("mode") & 0170000)!=0100000)throw new IllegalStateException("sealed backup type");
          var digest=MessageDigest.getInstance("SHA-256");
          try(var channel=FileChannel.open(p,Set.of(StandardOpenOption.READ,LinkOption.NOFOLLOW_LINKS))) {
            var buffer=java.nio.ByteBuffer.allocate(131072);
            for(;;) { int count=channel.read(buffer);if(count==-1)break;if(count==0)throw new IllegalStateException("backup progress");buffer.flip();digest.update(buffer);buffer.clear(); }
          }
          attributes.put("sha256",HexFormat.of().formatHex(digest.digest()));
        }
        if(!before.equals(Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS)))
          throw new IllegalStateException("backup inode drift");
        result.put(relative.toString(),Map.copyOf(attributes));
      }
    }
    return Map.copyOf(result);
  }
  static void verifyBytes(Map<String,byte[]> expected) throws Exception {
    var actual=captureBytes();for(var name:NAMES)if(!Arrays.equals(actual.get(name),expected.get(name)))throw new IllegalStateException("old bytes changed");
  }
  void verifyRemainingArtifacts() throws Exception {
    try(var paths=Files.list(STARTUP)) {
      var names=paths.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet());
      if(!NAMES.containsAll(names))throw new IllegalStateException("unknown startup entry");
    }
    for(var entry:original.entrySet()) {
      if(entry.getKey().endsWith(".start.intent") || entry.getKey().equals("permit-start.intent"))continue;
      if(!Arrays.equals(entry.getValue(),Files.readAllBytes(STARTUP.resolve(entry.getKey()))))throw new IllegalStateException("original artifact changed");
    }
  }
}
