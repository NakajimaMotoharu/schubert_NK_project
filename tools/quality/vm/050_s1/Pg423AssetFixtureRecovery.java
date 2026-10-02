import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** SSC160/BUG512/FIXTURE1: one isolated captured generation, NOT a general exit50 exception. */
public final class Pg423AssetFixtureRecovery {
  static final Path STAGED=Path.of("/home/ubuntu/pg423-fixture-stage");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg423-asset-fixture");
  static final String EPOCH="058eaf2b-45ce-410e-b7e0-1c794a246192";
  static final String MORNING="04a7b1f712284e6693f2e6b6532c5dcb";
  static final String API="7f22eb6b58144e378aa77ff9f856ec4e";
  static final String RECEIPT_SHA="c463ce55638b860b14471a3e758f0cc751af7f706cf08d4d4163076ba1772ceb";
  static final String WATCH_SHA="853f55345d20148b99f72e212784e152f8c1b63b0c18c2c79129bd8b70956d24";
  static final String ROWS_SHA="1e1d0055fc0848d6b64c6350f0f16c2301819ae0e6c1f7e900acae0cba8aeff3";
  static final Set<String> NAMES=names();
  static Set<String> names() {
    var names=new HashSet<>(Pg422KnownIncompleteRecovery.NAMES);
    names.remove(Pg422KnownIncompleteRecovery.EPOCH+".API.start.intent");
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
        && MORNING.equals(e.owner().morning().invocation()) && e.owner().morning().pid()==1060939
        && e.owner().morning().startTicks()==19562146
        && API.equals(e.child().invocation()) && e.child().pid()==1153910
        && e.child().startTicks()==19627043 && e.service()==ServiceConfigFiles.Service.API;
  }
  static void watch(byte[] bytes) {
    boolean root=false,ordinary=false;
    for(String line:new String(bytes,StandardCharsets.UTF_8).split("\n")) {
      var value=com.google.gson.JsonParser.parseString(line).getAsJsonObject();
      if(!value.has("api"))continue;
      var api=value.getAsJsonObject("api");
      if(!api.has("entry"))continue;
      if(!"1153910".equals(api.get("MainPID").getAsString())
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
  static final Path ASSET=Path.of("/srv/schubert-nk/data/assets"), API_CONFIG=Path.of("/etc/schubert-nk/api.yml");
  static final String CONFIG_SHA="55fbc411fa9921867bb67cdb33dd377685435c881b4821043074d3a38e7ccee0";
  static final String WAV_HEX="524946462800000057415645666d74201000000001000100401f0000803e000002001000646174610400000000000000";
  static final String WAV_SHA="114448ce435018eda5f4a8df39689d79fb4ff3dbfb5cc521002a42e8a6f625bb";
  static void signed() throws Exception {
    var approved=Pg387TrustedDeployment.verify();
    if(!approved.version().equals("0.1.0-PG421") || !approved.manifestSha256().equals("2348f978fafc1cdd521e1d866ca8fa3ae13d220668b266e0d989d0087cfa7979")
        || !Arrays.equals(approved.encode(),Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/release-approval/current"),1024))
        || !Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg422SignedMigration.CANDIDATE))
      throw new IllegalStateException("same actual signed candidate required");
  }
  static byte[] fixtureBytes() {return HexFormat.of().parseHex(WAV_HEX);}
  static byte[] manifestBytes() {return (WAV_SHA+"  audio/pgpt-fixture.wav\n").getBytes(StandardCharsets.US_ASCII);}
  static byte[] configured(byte[] old) {
    String raw=new String(old,StandardCharsets.UTF_8);
    if(raw.contains("nk.api.storage.asset-manifest-entries") || !raw.endsWith("\n"))
      throw new IllegalStateException("one unchanged flat YAML count insertion required");
    return (raw+"\"nk.api.storage.asset-manifest-entries\": \"1\"\n").getBytes(StandardCharsets.UTF_8);
  }
  static void fixturePreflight() throws Exception {
    var root=Pg410KnownAuthRecovery.metadata(ASSET);
    if(!Integer.valueOf(975).equals(root.get("uid")) || !Integer.valueOf(982).equals(root.get("gid"))
        || !Integer.valueOf(0040750).equals(root.get("mode")))throw new IllegalStateException("fixed actual asset root identity");
    try(var files=Files.list(ASSET)) {if(files.findAny().isPresent())throw new IllegalStateException("new-only empty isolated asset root required");}
    var config=Pg410KnownAuthRecovery.metadata(API_CONFIG);
    if(!Integer.valueOf(0).equals(config.get("uid")) || !Integer.valueOf(986).equals(config.get("gid"))
        || !Integer.valueOf(0100640).equals(config.get("mode")) || !Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(API_CONFIG,65536)).equals(CONFIG_SHA))
      throw new IllegalStateException("unchanged actual effective config required");
    if(!Pg410KnownAuthRecovery.hash(fixtureBytes()).equals(WAV_SHA))throw new IllegalStateException("independent fixed WAV digest");
    // Definitive prerequisite failure; not an inference about the former API's actual last phase.
    try(var rootOwner=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),ASSET)) {
      try {new dev.codex.schubert.nk.api.file.AssetManifestLoader(rootOwner,new StorageIdentity("schubert-data","schubert-read")).load(59627);}
      catch(dev.codex.schubert.nk.api.file.MediaIntegrityException expected) {return;}
      throw new IllegalStateException("mandatory missing manifest precondition differs");
    }
  }
  static void fixtureDirectory(Path path) throws Exception {
    Files.createDirectory(path,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwxr-x---")));
    Files.setAttribute(path,"unix:uid",975);Files.setAttribute(path,"unix:gid",982);
    Pg387TrustedDeployment.sync(path);Pg387TrustedDeployment.sync(path.getParent());
  }
  static void fixtureFile(Path path,byte[] bytes) throws Exception {
    Files.write(path,bytes,StandardOpenOption.CREATE_NEW);
    Files.setAttribute(path,"unix:uid",975);Files.setAttribute(path,"unix:gid",982);
    Files.setPosixFilePermissions(path,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r-----"));
    try(var c=java.nio.channels.FileChannel.open(path,StandardOpenOption.READ)) {c.force(true);}
    Pg387TrustedDeployment.sync(path.getParent());
    var attributes=Pg410KnownAuthRecovery.metadata(path);
    if(!Integer.valueOf(0100640).equals(attributes.get("mode")) || !Integer.valueOf(975).equals(attributes.get("uid"))
        || !Integer.valueOf(982).equals(attributes.get("gid")) || !Integer.valueOf(1).equals(attributes.get("nlink"))
        || !Arrays.equals(bytes,Pg410KnownAuthRecovery.material(path,65536)))throw new IllegalStateException("fixture independent byte and metadata readback");
  }
  static void provisionFixture() throws Exception {
    fixturePreflight();signed();
    byte[] old=Pg410KnownAuthRecovery.material(API_CONFIG,65536),next=configured(old);
    var configMeta=Pg410KnownAuthRecovery.metadata(API_CONFIG);
    save("api.yml.before",old);Pg387TrustedDeployment.sync(SAVED);
    String common=new String(Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/common.yml"),65536),StandardCharsets.UTF_8);
    var parsed=dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfig.parse(common,new String(next,StandardCharsets.UTF_8));
    if(!parsed.value("nk.api.storage.asset-manifest-entries").equals("1"))throw new IllegalStateException("independent configured count1");
    fixtureDirectory(ASSET.resolve("audio"));fixtureDirectory(ASSET.resolve("manifests"));
    fixtureFile(ASSET.resolve("audio/pgpt-fixture.wav"),fixtureBytes());
    fixtureFile(ASSET.resolve("manifests/master.sha256"),manifestBytes());
    try(var owned=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),ASSET)) {
      if(new dev.codex.schubert.nk.api.file.AssetManifestLoader(owned,new StorageIdentity("schubert-data","schubert-read")).load(1).entryCount()!=1)
        throw new IllegalStateException("independent manifest entries1");
    }
    Path part=API_CONFIG.resolveSibling("api.yml.pg423.part");
    Files.write(part,next,StandardOpenOption.CREATE_NEW);
    Files.setAttribute(part,"unix:uid",configMeta.get("uid"));Files.setAttribute(part,"unix:gid",configMeta.get("gid"));
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r-----"));
    try(var c=java.nio.channels.FileChannel.open(part,StandardOpenOption.READ)) {c.force(true);}
    if(!Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(API_CONFIG,65536)).equals(CONFIG_SHA))throw new IllegalStateException("config changed before swap");
    Files.move(part,API_CONFIG,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(API_CONFIG.getParent());
    var after=Pg410KnownAuthRecovery.metadata(API_CONFIG);
    if(!Integer.valueOf(0100640).equals(after.get("mode")) || !after.get("uid").equals(configMeta.get("uid"))
        || !after.get("gid").equals(configMeta.get("gid")) || !Arrays.equals(next,Pg410KnownAuthRecovery.material(API_CONFIG,65536)))
      throw new IllegalStateException("config private atomic metadata and byte readback");
    signed();
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG423_RECOVERY_REFUSED diagnosticsRedacted=true type="+e.getClass().getName());
      for(var frame:e.getStackTrace())if(frame.getClassName().equals("Pg423AssetFixtureRecovery")
          || frame.getClassName().equals("Pg410KnownAuthRecovery") || frame.getClassName().equals("Pg387TrustedDeployment"))
        System.err.println("PG423_FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
    });
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new IllegalStateException("isolated operator only");
    Pg422SignedMigration.configure();
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      fixturePreflight();
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
          var oldRows=Pg407FailedRootRecovery.databaseRows(db);if(oldRows.size()!=192)throw new IllegalStateException("all192 required");
          if(!Arrays.equals(expectedRows,command(READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-")))
            throw new IllegalStateException("independent historical all14-column readback differs");
          var backup=Pg407FailedRootRecovery.backupSnapshot();var bytes=startup();
          Pg410KnownAuthRecovery.physical(m,a,e);Pg410KnownAuthRecovery.original(db,e);signed();
          if(!e.permit().releaseDigest().equals("2348f978fafc1cdd521e1d866ca8fa3ae13d220668b266e0d989d0087cfa7979"))throw new IllegalStateException("same signed release required");
          for(var item:bytes.entrySet())save(item.getKey(),item.getValue());Pg387TrustedDeployment.sync(SAVED);
          RootFailedStartRecovery.retire(root,LinuxInodeSecurity.create(),e,expected->Pg387TrustedDeployment.checked(()-> {
            if(!e.equals(expected))throw new IllegalStateException("same typed evidence required");
            Pg410KnownAuthRecovery.physical(m,a,e);Pg410KnownAuthRecovery.original(db,e);signed();
            if(!oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("preservation drift");
            for(var item:bytes.entrySet())if(!item.getKey().endsWith(".start.intent") && !item.getKey().equals("permit-start.intent")
                && !Arrays.equals(item.getValue(),Pg410KnownAuthRecovery.material(Pg410KnownAuthRecovery.STARTUP.resolve(item.getKey()),1024)))throw new IllegalStateException("old bytes changed");
            return Boolean.TRUE;
          }));
          if(!oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("post preservation drift");
          Pg410KnownAuthRecovery.original(db,e);Pg410KnownAuthRecovery.physical(m,a,e);
          provisionFixture();
          if(!oldRows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("fixture preservation drift");
          db.rollback();
        } catch(Exception | Error failure) {
          try(var restored=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg410KnownAuthRecovery.STARTUP)) {RootFailedStartRecovery.quarantine(restored,LinuxInodeSecurity.create(),e);}
          catch(Exception | Error unknown) {System.err.println("PG423_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");for(;;)java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);}
          throw failure;
        }
        System.out.println("PG423_RECOVERED exactOldGeneration=true currentWholeKernelTerminal=true all192AndBackupUnchanged=true typed2IntentsRetired=true fixtureEntries=1 productionCountUnchanged=true phaseInferred=false historicalCloseClaimed=false permitIssued=false");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}

