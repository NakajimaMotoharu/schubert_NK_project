import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** SSC162/BUG519/RECFA30212: one isolated captured generation, NOT a general exit50 exception. */
public final class Pg425KnownApiRecovery {
  static final Path STAGED=Path.of("/home/ubuntu/pg425-recovery-stage");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg425-api-recovery");
  static final String EPOCH="8fbd510e-5485-4260-8699-490acffbd528";
  static final String MORNING="45b7821354e04a3baeaf283b2bbd8b14";
  static final String API="cf7dbd52fe094a84ac4513292ae9fce6";
  static final String RECEIPT_SHA="3ec308ee0af7d5950cf0cb9d4b4f39007ec62f41fa3eab76d1735b461ff566e4";
  static final String WATCH_SHA="b30491cc79698e4bb380fb7b70aec83fbe824d1850f06352d4ecdd62e86fe2f0";
  static final String ROWS_SHA="8c8c94ab456b6eb5a9e16acb1889801ec3ae73d64909373fc1411f8045a9343d";
  static final Set<String> NAMES=names();
  static Set<String> names() {
    var names=new HashSet<>(Pg424KnownApiRecovery.NAMES);
    names.remove(Pg424KnownApiRecovery.EPOCH+".API.start.intent");
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
        && MORNING.equals(e.owner().morning().invocation()) && e.owner().morning().pid()==1258602
        && e.owner().morning().startTicks()==20128681
        && API.equals(e.child().invocation()) && e.child().pid()==1356428
        && e.child().startTicks()==20195154 && e.service()==ServiceConfigFiles.Service.API;
  }
  static void watch(byte[] bytes) {
    boolean root=false,ordinary=false;
    String raw=new String(bytes,StandardCharsets.UTF_8);
    for(String line:raw.split("\n")) {
      var value=com.google.gson.JsonParser.parseString(line).getAsJsonObject();
      if(!value.has("api"))continue;
      var api=value.getAsJsonObject("api");
      if(!api.has("entry"))continue;
      if(!"1356428".equals(api.get("MainPID").getAsString())
          || !API.equals(api.get("InvocationID").getAsString()))throw new IllegalStateException("captured PID/Invocation differs");
      String entry=api.get("entry").getAsString();
      if(entry.equals("dev.codex.schubert.nk.batch.file.RootServiceLauncher"))root=true;
      if(entry.equals("dev.codex.schubert.nk.api.bootstrap.ApiProcessMain")) {
        var process=api.getAsJsonObject("process");
        if(!fourIds(process.get("Uid").getAsString(),"999")
            || !fourIds(process.get("Gid").getAsString(),"981")
            || !"1".equals(process.get("NoNewPrivs").getAsString()))throw new IllegalStateException("captured ordinary identity differs");
        for(String cap:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))
          if(!"0000000000000000".equals(process.get(cap).getAsString()))throw new IllegalStateException("captured capability differs");
        ordinary=true;
      }
    }
    if(!root || !ordinary)throw new IllegalStateException("genuine Root/ordinary observation required");
  }
  static boolean fourIds(String raw,String expected) {
    return raw!=null && Arrays.equals(raw.strip().split("\\s+"),new String[]{expected,expected,expected,expected});
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
  static void signed() throws Exception {
    var approved=Pg387TrustedDeployment.verify();
    if(!approved.version().equals("0.1.0-PG424") || !approved.manifestSha256().equals("a0a4f7f3f7dcff3fff936f9099368846430e94a51322c00a41fb11db122c9773")
        || !Arrays.equals(approved.encode(),Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/release-approval/current"),1024))
        || !Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG424")))
      throw new IllegalStateException("same actual signed candidate required");
  }
  static String fixtureSnapshot() throws Exception {
    var data=new TreeMap<String,Object>();
    Path assets=Path.of("/srv/schubert-nk/data/assets");
    for(String relative:List.of("","audio","manifests","audio/pgpt-fixture.wav","manifests/master.sha256")) {
      var path=assets.resolve(relative);var a=Pg410KnownAuthRecovery.metadata(path);
      boolean directory=List.of("","audio","manifests").contains(relative);
      if(!Integer.valueOf(975).equals(a.get("uid")) || !Integer.valueOf(982).equals(a.get("gid"))
          || !Integer.valueOf(directory?0040750:0100640).equals(a.get("mode")))throw new IllegalStateException("fixed data/read fixture metadata");
      data.put(relative,new TreeMap<>(a).toString());
      if(!directory)data.put(relative+".sha",Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(path,65536)));
    }
    if(!data.get("audio/pgpt-fixture.wav.sha").equals("114448ce435018eda5f4a8df39689d79fb4ff3dbfb5cc521002a42e8a6f625bb")
        || !data.get("manifests/master.sha256.sha").equals("44f2bff22f62d9f4ae4c49bcc554e9a189427e7fe6f2bd3b24604bfdd4141bbc"))throw new IllegalStateException("independent fixture digests");
    for(String name:List.of("api.yml","common.yml")) {
      Path path=Path.of("/etc/schubert-nk",name);
      var m=Pg410KnownAuthRecovery.metadata(path);
      if(!Integer.valueOf(0).equals(m.get("uid")) || !Integer.valueOf(986).equals(m.get("gid"))
          || !Integer.valueOf(0100640).equals(m.get("mode")))throw new IllegalStateException("fixed actual configuration");
      data.put(name,new TreeMap<>(m).toString());
      data.put(name+".sha",Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(path,65536)));
    }
    if(!data.get("api.yml.sha").equals("40573510ed295f9e7b343f832624cda63f2383fa87e59b2bddeb651e7717c6bc"))throw new IllegalStateException("independent count1 actual config digest");
    Path transfer=Path.of("/srv/schubert-nk/data/transfer");
    var t=Pg410KnownAuthRecovery.metadata(transfer);
    if(!Integer.valueOf(999).equals(t.get("uid")) || !Integer.valueOf(980).equals(t.get("gid"))
        || !Integer.valueOf(0040750).equals(t.get("mode")))throw new IllegalStateException("fixed Transfer metadata required");
    try(var entries=Files.list(transfer)) {
      if(entries.findAny().isPresent())throw new IllegalStateException("captured empty Transfer required");
    }
    data.put("transfer.metadata",new TreeMap<>(t).toString());
    return data.toString();
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG425_RECOVERY_REFUSED diagnosticsRedacted=true type="+e.getClass().getName());
      for(var frame:e.getStackTrace())if(frame.getClassName().equals("Pg425KnownApiRecovery")
          || frame.getClassName().equals("Pg410KnownAuthRecovery") || frame.getClassName().equals("Pg387TrustedDeployment"))
        System.err.println("PG425_FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
    });
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new IllegalStateException("isolated operator only");
    Pg387TrustedDeployment.LABEL="PG424";Pg387TrustedDeployment.STEM="pg424";
    Pg387TrustedDeployment.SOURCE="fa30f9cfc6810306c9fbc0de2e3774314d3fd8c3";
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG424");
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      var fixture=fixtureSnapshot();
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
          var oldRows=Pg407FailedRootRecovery.databaseRows(db);if(oldRows.size()!=212)throw new IllegalStateException("all212 required");
          if(!Arrays.equals(expectedRows,command(READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-")))
            throw new IllegalStateException("independent historical all14-column readback differs");
          var backup=Pg407FailedRootRecovery.backupSnapshot();var bytes=startup();
          for(String file:List.of("api.yml","common.yml"))save(file+".before",Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk",file),65536));
          save("fixture.before",fixture.getBytes(StandardCharsets.US_ASCII));
          Pg410KnownAuthRecovery.physical(m,a,e);Pg410KnownAuthRecovery.original(db,e);signed();
          if(!e.permit().releaseDigest().equals("a0a4f7f3f7dcff3fff936f9099368846430e94a51322c00a41fb11db122c9773"))throw new IllegalStateException("same signed release required");
          for(var item:bytes.entrySet())save(item.getKey(),item.getValue());Pg387TrustedDeployment.sync(SAVED);
          RootFailedStartRecovery.retire(root,LinuxInodeSecurity.create(),e,expected->Pg387TrustedDeployment.checked(()-> {
            if(!e.equals(expected))throw new IllegalStateException("same typed evidence required");
            Pg410KnownAuthRecovery.physical(m,a,e);Pg410KnownAuthRecovery.original(db,e);signed();
            if(!fixture.equals(fixtureSnapshot()) || !oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("preservation drift");
            for(var item:bytes.entrySet())if(!item.getKey().endsWith(".start.intent") && !item.getKey().equals("permit-start.intent")
                && !Arrays.equals(item.getValue(),Pg410KnownAuthRecovery.material(Pg410KnownAuthRecovery.STARTUP.resolve(item.getKey()),1024)))throw new IllegalStateException("old bytes changed");
            return Boolean.TRUE;
          }));
          if(!oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("post preservation drift");
          Pg410KnownAuthRecovery.original(db,e);Pg410KnownAuthRecovery.physical(m,a,e);
          if(!oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("fixture preservation drift");
          db.rollback();
        } catch(Exception | Error failure) {
          try(var restored=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg410KnownAuthRecovery.STARTUP)) {RootFailedStartRecovery.quarantine(restored,LinuxInodeSecurity.create(),e);}
          catch(Exception | Error unknown) {System.err.println("PG425_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");for(;;)java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);}
          throw failure;
        }
        System.out.println("PG425_RECOVERED exactOldGeneration=true currentWholeKernelTerminal=true all212AndBackupUnchanged=true typed2IntentsRetired=true assetAndConfigUnchanged=true phaseInferred=false historicalCloseClaimed=false permitIssued=false");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
