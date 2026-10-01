import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.Connection;
import java.util.*;

/** SSC147 isolated operator for the single independently diagnosed PG408 app-auth failure. */
public final class Pg410KnownAuthRecovery {
  static final Path STAGED=Path.of("/home/ubuntu/pg410-auth-stage");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg410-known-auth");
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final Path ETC=Path.of("/var/lib/schubert-nk/artemis/etc");
  static final String SOURCE="32c6a7b1e79abf114901003c4a8f1300b33bf0c0";
  static final String EPOCH="5689f481-b4e3-4d8f-b450-74b980f5c15c";
  static final Set<String> NAMES=Set.of("epoch.current","permit-start.intent",EPOCH+".permit",EPOCH+".owner",
      EPOCH+".API.launch",EPOCH+".API.start.intent",
      "0a835a89-010d-4ace-9b59-928cbe3d8a8f.permit","0a835a89-010d-4ace-9b59-928cbe3d8a8f.owner","0a835a89-010d-4ace-9b59-928cbe3d8a8f.API.launch","2f5f22a6-76dd-4e3e-a063-5f14b37c67ac.permit",
      "2f5f22a6-76dd-4e3e-a063-5f14b37c67ac.owner","2f5f22a6-76dd-4e3e-a063-5f14b37c67ac.API.launch",
      "5ae82ba7-bda0-442a-882a-29f94b5b286e.permit");
  static final Set<String> FIELDS=Set.of("Id","LoadState","ActiveState","SubState","Job","InvocationID",
      "Type","Restart","RemainAfterExit","MainPID","ControlPID","Result","ExecMainStartTimestampMonotonic",
      "ExecMainExitTimestampMonotonic","ExecMainCode","ExecMainStatus","KillMode","SendSIGKILL");
  record Receipt(byte[] raw,Map<String,String> values,InspectorUnitSnapshot snapshot) {}
  static Receipt parsed(byte[] raw,InspectorUnitSnapshot.Target target) {
    var fields=new HashMap<String,String>();
    for(String line:new String(raw,StandardCharsets.US_ASCII).split("\n")) {
      int equal=line.indexOf('='); if(equal<=0 || fields.putIfAbsent(line.substring(0,equal),line.substring(equal+1))!=null)
        throw new IllegalArgumentException("receipt shape");
    }
    if(!fields.keySet().equals(FIELDS))throw new IllegalArgumentException("full18 required");
    return new Receipt(raw.clone(),Map.copyOf(fields),InspectorUnitSnapshot.parse(raw,target));
  }
  static boolean stoppedAfter(Map<String,String> before,Map<String,String> after) {
    if(before==null || after==null || !before.keySet().equals(FIELDS) || !after.keySet().equals(FIELDS))return false;
    for(String field:FIELDS)if(before.get(field)==null || after.get(field)==null)return false;
    if(!Set.of("inactive/dead","failed/failed").contains(after.get("ActiveState")+"/"+after.get("SubState")))return false;
    var same=new HashMap<>(before);same.put("ActiveState",after.get("ActiveState"));same.put("SubState",after.get("SubState"));
    same.put("Result",after.get("Result"));
    if(Set.of("exit-code","success").contains(after.get("Result")) && same.equals(after))return true;
    var cold=new HashMap<>(before);cold.put("ActiveState","inactive");cold.put("SubState","dead");cold.put("Result","success");
    cold.put("InvocationID","");
    for(String field:List.of("ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic"))cold.put(field,"0");
    return cold.equals(after);
  }
  static Receipt show(InspectorUnitSnapshot.Target target) throws Exception {
    var process=new ProcessBuilder("/usr/bin/systemctl","show",target.unit(),"--property="+String.join(",",FIELDS)).start();
    byte[] raw=process.getInputStream().readNBytes(2049);
    if(!process.waitFor(5,java.util.concurrent.TimeUnit.SECONDS) || process.exitValue()!=0 || raw.length>2048)
      throw new IllegalStateException("bounded manager unavailable");
    return parsed(raw,target);
  }
  static String hash(byte[] bytes) throws Exception {return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));}
  static Map<String,Object> metadata(Path path) throws Exception {
    return Files.readAttributes(path,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS);
  }
  static byte[] material(Path path,long maximum) throws Exception {
    var before=metadata(path);
    if(((Integer)before.get("mode") & 0170000)!=0100000 || !Integer.valueOf(1).equals(before.get("nlink"))
        || (Long)before.get("size")>maximum)throw new IllegalStateException("held regular material");
    var bytes=Files.readAllBytes(path);
    if(!before.equals(metadata(path)))throw new IllegalStateException("material changed");return bytes;
  }
  static byte[] pinned(String name,String sha) throws Exception {
    var bytes=material(STAGED.resolve(name),4194304);
    if(!hash(bytes).equals(sha))throw new IllegalStateException("actual observation hash");return bytes;
  }
  static void save(String name,byte[] bytes) throws Exception {
    var target=SAVED.resolve(name);Files.write(target,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(target,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var channel=FileChannel.open(target,StandardOpenOption.READ)){channel.force(true);}
    if(!Arrays.equals(bytes,Files.readAllBytes(target)))throw new IllegalStateException("private readback");
  }
  static Map<String,byte[]> startup() throws Exception {
    try(var paths=Files.list(STARTUP)) {
      if(!paths.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet()).equals(NAMES))
        throw new IllegalStateException("exact old namespace");
    }
    var result=new HashMap<String,byte[]>();
    for(String name:NAMES) {
      var p=STARTUP.resolve(name);var m=metadata(p);
      if(!Integer.valueOf(0).equals(m.get("uid")) || !Integer.valueOf(0).equals(m.get("gid"))
          || !Integer.valueOf(0100600).equals(m.get("mode")))throw new IllegalStateException("old root material");
      result.put(name,material(p,1024));
    }return Map.copyOf(result);
  }
  static Properties properties(byte[] bytes) throws Exception {
    var result=new Properties();try(var input=new java.io.ByteArrayInputStream(bytes)){result.load(input);}return result;
  }
  static byte[] encoded(Properties values) throws Exception {
    var output=new java.io.ByteArrayOutputStream();values.store(output,"SSC146 fixed app login, secrets private");return output.toByteArray();
  }
  static void replace(Path target,byte[] bytes,Map<String,Object> original) throws Exception {
    var part=target.resolveSibling(target.getFileName()+".pg410.part");
    Files.write(part,bytes,StandardOpenOption.CREATE_NEW);
    Files.setAttribute(part,"unix:uid",original.get("uid"));Files.setAttribute(part,"unix:gid",original.get("gid"));
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var file=FileChannel.open(part,StandardOpenOption.READ)){file.force(true);}
    Files.move(part,target,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
    Pg387TrustedDeployment.sync(target.getParent());
    if(!Arrays.equals(bytes,material(target,65536)))throw new IllegalStateException("auth readback");
    var m=metadata(target);
    if(!m.get("uid").equals(original.get("uid")) || !m.get("gid").equals(original.get("gid"))
        || !Integer.valueOf(0100600).equals(m.get("mode")))throw new IllegalStateException("auth metadata");
  }
  static void original(Connection db,RootFailedStartRecovery.Evidence e) throws Exception {
    var a=MaintenanceRunFiles.create().execute(s->s.observe(e.invalid().activation()));
    if(!a.equals(e.invalid().activation()) || !new RunReferenceRepository(db).read(a.run()).identityConsistent())
      throw new IllegalStateException("same original graph");
  }
  static void signed() throws Exception {
    var approval=Pg387TrustedDeployment.verify();
    if(!sameApproval(approval,Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))))
      throw new IllegalStateException("same signed source");
  }
  static boolean sameApproval(ReleaseApproval approval,byte[] actual) {
    return approval.version().equals("0.1.0-PG408")
        && approval.manifestSha256().equals("33dda6beb4e17f7b6fc59a94f8a8dd4dfe29d904861fd338bf12c0de1ceec272")
        && Arrays.equals(approval.encode(),actual);
  }
  static void configureVerifier() {
    Pg387TrustedDeployment.LABEL="PG408";Pg387TrustedDeployment.STEM="pg408";Pg387TrustedDeployment.SOURCE=SOURCE;
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG408");
  }
  static void physical(Receipt m,Receipt a,RootFailedStartRecovery.Evidence e) throws Exception {
    var currentM=show(InspectorUnitSnapshot.Target.MORNING);var currentA=show(InspectorUnitSnapshot.Target.API);
    if(!stoppedAfter(m.values(),currentM.values()) || !stoppedAfter(a.values(),currentA.values()))
      throw new IllegalStateException("captured normal generation changed");
    if(!Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(e.invalid().boot().toString()))
      throw new IllegalStateException("same boot required");
    Pg387TrustedDeployment.terminalAll();Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    for(var actor:List.of(e.owner().morning(),e.child()))if(Files.exists(Path.of("/proc",Long.toString(actor.pid())),LinkOption.NOFOLLOW_LINKS))
      throw new IllegalStateException("old actor still exists or PID reused");
    if(!currentM.snapshot().matches(show(InspectorUnitSnapshot.Target.MORNING).snapshot())
        || !currentA.snapshot().matches(show(InspectorUnitSnapshot.Target.API).snapshot()))throw new IllegalStateException("manager/kernel drift");
  }
  public static void main(String[] arguments) throws Exception {
    if(arguments.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new IllegalStateException("isolated operator only");
    configureVerifier();
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      byte[] receipt=pinned("full18.properties","07ed0fb4023b4b4e0053d7c0b16e2058cd81b6f3452a9d9a03982322a16275bf");
      byte[] watch=pinned("watch.jsonl","53a3cad179ef5ea8f46523ba372cb071dd13998f664c2f7b1bbf5b414c06521a");
      byte[] journal=pinned("broker-journal.txt","e6a69756dee802929862e0ef10216fb9845ebd8fa4e6933d1090ade33b48c021");
      if(!new String(journal,StandardCharsets.UTF_8).contains("AMQ229031: Unable to validate user")
          || !new String(journal,StandardCharsets.UTF_8).contains("Username: nk_api;"))throw new IllegalStateException("known actual auth failure");
      var blocks=new String(receipt,StandardCharsets.US_ASCII).stripTrailing().split("\n\n");if(blocks.length!=3)throw new IllegalStateException("actual complete observations");
      var m=parsed((blocks[0]+"\n").getBytes(StandardCharsets.US_ASCII),InspectorUnitSnapshot.Target.MORNING);
      var a=parsed((blocks[1]+"\n").getBytes(StandardCharsets.US_ASCII),InspectorUnitSnapshot.Target.API);
      if(!m.snapshot().failedRootGeneration("315974bbc5a547a78e16c0a5d4c8b4ea") || !a.values().get("ExecMainCode").equals("1")
          || !a.values().get("ExecMainStatus").equals("1") || !a.values().get("InvocationID").equals("20a6b9b613d14ca6a7f11922ee14ee97")
          || !a.values().get("Result").equals("exit-code") || !a.snapshot().quiescent())throw new IllegalStateException("known normal receipts only");
      if(!stoppedAfter(m.values(),show(InspectorUnitSnapshot.Target.MORNING).values()) || !stoppedAfter(a.values(),show(InspectorUnitSnapshot.Target.API).values()))
        throw new IllegalStateException("pre-stop manager changed");
      if(Files.exists(SAVED,LinkOption.NOFOLLOW_LINKS)) {
        var directory=metadata(SAVED);
        if(!Integer.valueOf(0).equals(directory.get("uid")) || !Integer.valueOf(0).equals(directory.get("gid"))
            || !Integer.valueOf(0040700).equals(directory.get("mode")))throw new IllegalStateException("private owner");
        try(var paths=Files.list(SAVED)) {
          if(!paths.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet())
              .equals(Set.of("full18.properties","watch.jsonl","broker-journal.txt")))throw new IllegalStateException("partial operation remains");
        }
        for(var entry:Map.of("full18.properties",receipt,"watch.jsonl",watch,"broker-journal.txt",journal).entrySet()) {
          var p=SAVED.resolve(entry.getKey());var pm=metadata(p);
          if(!Integer.valueOf(0).equals(pm.get("uid")) || !Integer.valueOf(0).equals(pm.get("gid"))
              || !Integer.valueOf(0100600).equals(pm.get("mode")) || !Arrays.equals(entry.getValue(),material(p,4194304)))
            throw new IllegalStateException("genuine durable observation changed");
        }
      } else {
        if(!m.snapshot().matches(show(InspectorUnitSnapshot.Target.MORNING).snapshot()) || !a.snapshot().matches(show(InspectorUnitSnapshot.Target.API).snapshot()))
          throw new IllegalStateException("fresh capture must precede stop");
        Files.createDirectory(SAVED,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
        save("full18.properties",receipt);save("watch.jsonl",watch);save("broker-journal.txt",journal);
      }
      Pg387TrustedDeployment.sync(SAVED);Pg387TrustedDeployment.sync(SAVED.getParent());
      Pg387TrustedDeployment.stopAll();
      return StartupAdmissionFile.create().tryExclusive(fd->Pg387TrustedDeployment.checked(()-> {
        RootFailedStartRecovery.Evidence evidence;
        System.out.println("PG410_STAGE OBSERVE_REVOKED");
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {
          evidence=RootFailedStartRecovery.observe(root,LinuxInodeSecurity.create());
        }
        var e=evidence;
        if(!e.invalid().epoch().toString().equals(EPOCH) || !e.invalid().activation().run().id().equals(Pg407FailedRootRecovery.RUN)
            || !e.owner().morning().invocation().equals("315974bbc5a547a78e16c0a5d4c8b4ea") || e.owner().morning().pid()!=841311
            || e.owner().morning().startTicks()!=13385233 || !e.child().invocation().equals("20a6b9b613d14ca6a7f11922ee14ee97")
            || e.child().pid()!=943448 || e.child().startTicks()!=13450049 || e.service()!=ServiceConfigFiles.Service.API)
          throw new IllegalStateException("exact captured generation required");
        System.out.println("PG410_STAGE DEDICATED_DB");
        try(var db=Pg407FailedRootRecovery.openDatabase();var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {
          db.setAutoCommit(false);
          try(var s=db.createStatement();var r=s.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
            if(!r.next() || !Boolean.TRUE.equals(r.getObject(1,Boolean.class)) || r.next())throw new IllegalStateException("dedicated DB advisory");
          }
          System.out.println("PG410_STAGE FULL_ROWS");
          var rows=Pg407FailedRootRecovery.databaseRows(db);if(rows.size()!=172)throw new IllegalStateException("all172 unchanged");
          var backup=Pg407FailedRootRecovery.backupSnapshot();var bytes=startup();
          System.out.println("PG410_STAGE PHYSICAL_ORIGINAL_SIGNED");
          physical(m,a,e);original(db,e);signed();
          for(var entry:bytes.entrySet())save(entry.getKey(),entry.getValue());
          var users=Path.of("/etc/schubert-nk/credentials/artemis-users");var roles=ETC.resolve("artemis-roles.properties");
          save("host-artemis-users.properties",material(ETC.resolve("artemis-users.properties"),65536));
          var um=metadata(users);var rm=metadata(roles);byte[] oldUsers=material(users,65536),oldRoles=material(roles,65536);
          var up=properties(oldUsers);var rp=properties(oldRoles);
          if(!up.stringPropertyNames().equals(Set.of("schubert_api","schubert_web","schubert_ops","schubert_maintenance"))
              || !rp.stringPropertyNames().equals(Set.of("nk_api","nk_web","nk_ops","nk_mq_maintenance")))throw new IllegalStateException("fixed auth catalog");
          for(String app:List.of("api","web")) {
            String old="schubert_"+app, next="nk_"+app;
            if(!next.equals(rp.getProperty(next)))throw new IllegalStateException("old app binding");
            up.setProperty(next,Objects.requireNonNull(up.getProperty(old)));up.remove(old);rp.setProperty(next,next);
          }
          save("artemis-users.properties",oldUsers);save("artemis-roles.properties",oldRoles);Pg387TrustedDeployment.sync(SAVED);
          byte[] nextUsers=encoded(up),nextRoles=oldRoles;
          try { replace(users,nextUsers,um); }
          catch(Exception | Error failure) { replace(users,oldUsers,um);throw failure; }
          RootFailedStartRecovery.retire(root,LinuxInodeSecurity.create(),e,expected->Pg387TrustedDeployment.checked(()-> {
            if(!e.equals(expected))throw new IllegalStateException("typed same evidence");
            physical(m,a,e);original(db,e);signed();
            if(!rows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot())
                || !Arrays.equals(nextUsers,material(users,65536)) || !Arrays.equals(nextRoles,material(roles,65536)))throw new IllegalStateException("preservation drift");
            for(var entry:bytes.entrySet())if(!entry.getKey().endsWith(".start.intent") && !entry.getKey().equals("permit-start.intent")
                && !Arrays.equals(entry.getValue(),material(STARTUP.resolve(entry.getKey()),1024)))throw new IllegalStateException("original bytes changed");
            return Boolean.TRUE;
          }));
          if(!rows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("post preservation");
          original(db,e);physical(m,a,e);db.rollback();
        } catch(Exception | Error failure) {
          try(var restored=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {RootFailedStartRecovery.quarantine(restored,LinuxInodeSecurity.create(),e);}
          catch(Exception | Error unknown) {System.err.println("PG410_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");for(;;)java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);}
          throw failure;
        }
        System.out.println("PG410_KNOWN_AUTH_RECOVERED sameSignedSource=true old172AndBackupUnchanged=true app2LoginFixed=true typed2IntentsRetired=true historicalCloseClaimed=false newPermitIssued=false");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
