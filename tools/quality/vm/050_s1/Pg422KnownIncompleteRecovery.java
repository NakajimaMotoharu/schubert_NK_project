import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** SSC159/PG-D335/REC50: one isolated captured generation, NOT a general exit50 exception. */
public final class Pg422KnownIncompleteRecovery {
  static final Path STAGED=Path.of("/home/ubuntu/pg422-recovery-stage");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg422-incomplete");
  static final String EPOCH="adc7cb94-b23d-45ea-824a-3ae6c293b09d";
  static final String MORNING="0d39056c1d374f9dbe4938683e4ae20b";
  static final String API="05b8d33d64294727bcff84543e968256";
  static final String RECEIPT_SHA="ca3eb18daa132c8a7b5a3bcac5de4fe3cb24e8c2d55f0dc5f38cde8cd95a9d8d";
  static final String WATCH_SHA="61a3b5d67144913f92f7b09ff927a9c8fa779b5bc74652736605931344590315";
  static final String ROWS_SHA="088e54f4f0d6c8ec69f1917aac8b530ea02c3cf2042551823debbed64c9878f9";
  static final Set<String> NAMES=names();
  static Set<String> names() {
    var names=new HashSet<>(Pg410KnownAuthRecovery.NAMES);
    names.remove(Pg410KnownAuthRecovery.EPOCH+".API.start.intent");
    for(String suffix:List.of(".permit",".owner",".API.launch",".API.start.intent"))names.add(EPOCH+suffix);
    return Set.copyOf(names);
  }
  static byte[] pinned(String name,String sha) throws Exception {
    var root=Pg410KnownAuthRecovery.metadata(STAGED);
    var entry=Pg410KnownAuthRecovery.metadata(STAGED.resolve(name));
    if(!Integer.valueOf(0).equals(root.get("uid")) || !Integer.valueOf(0).equals(root.get("gid"))
        || !Integer.valueOf(0040500).equals(root.get("mode")) || !Integer.valueOf(0).equals(entry.get("uid"))
        || !Integer.valueOf(0).equals(entry.get("gid")) || !Integer.valueOf(0100400).equals(entry.get("mode")))
      throw new IllegalStateException("trusted private observation required");
    byte[] bytes=Pg410KnownAuthRecovery.material(STAGED.resolve(name),4194304);
    if(!Pg410KnownAuthRecovery.hash(bytes).equals(sha))throw new IllegalStateException("captured observation changed");
    return bytes;
  }
  static boolean known(Map<String,String> m,Map<String,String> a) {
    if(m==null || a==null || !m.keySet().equals(Pg410KnownAuthRecovery.FIELDS)
        || !a.keySet().equals(Pg410KnownAuthRecovery.FIELDS))return false;
    return "schubert-nk-morning-controller.service".equals(m.get("Id"))
        && "schubert-nk-api.service".equals(a.get("Id"))
        && MORNING.equals(m.get("InvocationID")) && API.equals(a.get("InvocationID"))
        && "1".equals(m.get("ExecMainCode")) && "30".equals(m.get("ExecMainStatus"))
        && "1".equals(a.get("ExecMainCode")) && "50".equals(a.get("ExecMainStatus"))
        && "exit-code".equals(m.get("Result")) && "exit-code".equals(a.get("Result"))
        && List.of(m,a).stream().allMatch(v->"0".equals(v.get("MainPID"))
          && "0".equals(v.get("ControlPID")) && "".equals(v.get("Job")));
  }
  static boolean known(RootFailedStartRecovery.Evidence e) {
    return e!=null && EPOCH.equals(e.invalid().epoch().toString())
        && e.invalid().activation().run().id().equals(Pg407FailedRootRecovery.RUN)
        && e.invalid().activation().id().equals(Pg407FailedRootRecovery.ACTIVATION)
        && MORNING.equals(e.owner().morning().invocation()) && e.owner().morning().pid()==947482
        && e.owner().morning().startTicks()==13509351
        && API.equals(e.child().invocation()) && e.child().pid()==1049738
        && e.child().startTicks()==13574975 && e.service()==ServiceConfigFiles.Service.API;
  }
  static void watch(byte[] bytes) {
    boolean root=false,ordinary=false;
    for(String line:new String(bytes,StandardCharsets.UTF_8).split("\n")) {
      var value=com.google.gson.JsonParser.parseString(line).getAsJsonObject();
      if(!value.has("units"))continue;
      var api=value.getAsJsonObject("units").getAsJsonObject("schubert-nk-api.service");
      if(!api.has("entry"))continue;
      if(!"1049738".equals(api.get("MainPID").getAsString())
          || !API.equals(api.get("InvocationID").getAsString()))throw new IllegalStateException("captured PID/Invocation differs");
      String entry=api.get("entry").getAsString();
      if(entry.equals("dev.codex.schubert.nk.batch.file.RootServiceLauncher"))root=true;
      if(entry.equals("dev.codex.schubert.nk.api.bootstrap.ApiProcessMain")) {
        var process=api.getAsJsonObject("process");
        if(!"999 999 999 999".equals(process.get("Uid").getAsString())
            || !"981 981 981 981".equals(process.get("Gid").getAsString())
            || !"1".equals(process.get("NoNewPrivs").getAsString()))throw new IllegalStateException("captured ordinary identity differs");
        for(String cap:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))
          if(!"0000000000000000".equals(process.get(cap).getAsString()))throw new IllegalStateException("captured capability differs");
        ordinary=true;
      }
    }
    if(!root || !ordinary)throw new IllegalStateException("genuine Root/ordinary observation required");
  }
  static Map<String,byte[]> startup() throws Exception {
    var path=Pg410KnownAuthRecovery.STARTUP;
    try(var files=Files.list(path)) {
      if(!files.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet()).equals(NAMES))
        throw new IllegalStateException("exact old namespace required");
    }
    var result=new TreeMap<String,byte[]>();
    for(String name:NAMES) {
      Path p=path.resolve(name);var m=Pg410KnownAuthRecovery.metadata(p);
      if(!Integer.valueOf(0).equals(m.get("uid")) || !Integer.valueOf(0).equals(m.get("gid"))
          || !Integer.valueOf(0100600).equals(m.get("mode")))throw new IllegalStateException("root private old source required");
      result.put(name,Pg410KnownAuthRecovery.material(p,1024));
    }
    return Map.copyOf(result);
  }
  static void save(String name,byte[] bytes) throws Exception {
    var target=SAVED.resolve(name);Files.write(target,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(target,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var channel=java.nio.channels.FileChannel.open(target,StandardOpenOption.READ)){channel.force(true);}
    if(!Arrays.equals(bytes,Files.readAllBytes(target)))throw new IllegalStateException("private readback required");
  }
  static final String READBACK_SQL="\\pset format unaligned\n\\pset tuples_only on\nSET TIME ZONE 'UTC';\nSELECT id,run_id,business_date,step,attempt,started_at,ended_at,status,\n       target_count,success_count,failure_count,byte_count,error_code,error_summary\nFROM schubert.batch_runs ORDER BY id;\n";
  static byte[] command(byte[] input,String... args) throws Exception {
    var p=new ProcessBuilder(args).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    try(var writer=p.getOutputStream()){writer.write(input);}
    byte[] bytes=p.getInputStream().readNBytes(4194305);
    if(!p.waitFor(5,java.util.concurrent.TimeUnit.SECONDS) || p.exitValue()!=0 || bytes.length>4194304)
      throw new IllegalStateException("bounded independent readback failed");
    return bytes;
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println("PG422_RECOVERY_REFUSED diagnosticsRedacted=true type="+e.getClass().getName()));
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new IllegalStateException("isolated operator only");
    Pg410KnownAuthRecovery.configureVerifier();
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      byte[] full=pinned("full18.properties",RECEIPT_SHA),captured=pinned("watch.jsonl",WATCH_SHA);
      byte[] expectedRows=pinned("db-final.log",ROWS_SHA);
      watch(captured);
      var blocks=new String(full,StandardCharsets.US_ASCII).stripTrailing().split("\n\n");
      if(blocks.length!=3)throw new IllegalStateException("full manager observation required");
      var m=Pg410KnownAuthRecovery.parsed((blocks[0]+"\n").getBytes(StandardCharsets.US_ASCII),InspectorUnitSnapshot.Target.MORNING);
      var a=Pg410KnownAuthRecovery.parsed((blocks[1]+"\n").getBytes(StandardCharsets.US_ASCII),InspectorUnitSnapshot.Target.API);
      if(!known(m.values(),a.values()) || !m.snapshot().quiescent() || !a.snapshot().quiescent()
          || !Pg410KnownAuthRecovery.stoppedAfter(m.values(),Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values())
          || !Pg410KnownAuthRecovery.stoppedAfter(a.values(),Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.API).values()))
        throw new IllegalStateException("single captured normal generation required");
      if(Files.exists(SAVED,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("preserved operator already exists");
      Files.createDirectory(SAVED,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
      save("full18.properties",full);save("watch.jsonl",captured);save("db-final.log",expectedRows);
      Pg387TrustedDeployment.sync(SAVED);Pg387TrustedDeployment.sync(SAVED.getParent());
      Pg387TrustedDeployment.stopAll();
      return StartupAdmissionFile.create().tryExclusive(fd->Pg387TrustedDeployment.checked(()-> {
        RootFailedStartRecovery.Evidence evidence;
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg410KnownAuthRecovery.STARTUP)) {
          evidence=RootFailedStartRecovery.observe(root,LinuxInodeSecurity.create());
        }
        var e=evidence;if(!known(e))throw new IllegalStateException("known old bindings required");
        try(var db=Pg407FailedRootRecovery.openDatabase();
            var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg410KnownAuthRecovery.STARTUP)) {
          db.setAutoCommit(false);
          try(var s=db.createStatement();var rows=s.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
            if(!rows.next() || !Boolean.TRUE.equals(rows.getObject(1,Boolean.class)) || rows.next())throw new IllegalStateException("dedicated advisory required");
          }
          var oldRows=Pg407FailedRootRecovery.databaseRows(db);if(oldRows.size()!=182)throw new IllegalStateException("all182 required");
          if(!Arrays.equals(expectedRows,command(READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-")))
            throw new IllegalStateException("independent historical all14-column readback differs");
          var backup=Pg407FailedRootRecovery.backupSnapshot();var bytes=startup();
          Pg410KnownAuthRecovery.physical(m,a,e);Pg410KnownAuthRecovery.original(db,e);Pg410KnownAuthRecovery.signed();
          if(!e.permit().releaseDigest().equals("33dda6beb4e17f7b6fc59a94f8a8dd4dfe29d904861fd338bf12c0de1ceec272"))throw new IllegalStateException("same signed release required");
          for(var item:bytes.entrySet())save(item.getKey(),item.getValue());Pg387TrustedDeployment.sync(SAVED);
          RootFailedStartRecovery.retire(root,LinuxInodeSecurity.create(),e,expected->Pg387TrustedDeployment.checked(()-> {
            if(!e.equals(expected))throw new IllegalStateException("same typed evidence required");
            Pg410KnownAuthRecovery.physical(m,a,e);Pg410KnownAuthRecovery.original(db,e);Pg410KnownAuthRecovery.signed();
            if(!oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("preservation drift");
            for(var item:bytes.entrySet())if(!item.getKey().endsWith(".start.intent") && !item.getKey().equals("permit-start.intent")
                && !Arrays.equals(item.getValue(),Pg410KnownAuthRecovery.material(Pg410KnownAuthRecovery.STARTUP.resolve(item.getKey()),1024)))throw new IllegalStateException("old bytes changed");
            return Boolean.TRUE;
          }));
          if(!oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("post preservation drift");
          Pg410KnownAuthRecovery.original(db,e);Pg410KnownAuthRecovery.physical(m,a,e);db.rollback();
        } catch(Exception | Error failure) {
          try(var restored=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg410KnownAuthRecovery.STARTUP)) {RootFailedStartRecovery.quarantine(restored,LinuxInodeSecurity.create(),e);}
          catch(Exception | Error unknown) {System.err.println("PG422_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");for(;;)java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);}
          throw failure;
        }
        System.out.println("PG422_RECOVERED exactOldGeneration=true currentWholeKernelTerminal=true all182AndBackupUnchanged=true typed2IntentsRetired=true phaseInferred=false historicalCloseClaimed=false permitIssued=false");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
