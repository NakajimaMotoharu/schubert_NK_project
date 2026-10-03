import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.Connection;
import java.util.*;

/** SSC168/ROOTPAIR008: exactly one isolated PG430 normal30/owned143/Web50 generation. */
public final class Pg431KnownPairRecovery {
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final Path STAGED=Path.of("/var/lib/pgpt-s1-preservation/pg431-pair-input");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg432-pair-recovery");
  static final String OLD_SOURCE="91b010509e715e2b097c955d04f21c23f3529966";
  static final String OLD_DIGEST="ecef234624ece66c69d81383f722aee046da7b0dcab8cf10ec4df3b3d2dd1375";
  static final String EPOCH="e603398b-c164-4709-afc1-25117eac9995";
  static final String BOOT="58006280-5301-4a1b-a0c2-66bce4a8a38e";
  static final String MORNING="334c1680493c41719f556f6eea92fadc";
  static final String API="61b650cebb7d42ab95cf96a12ee58a67";
  static final String WEB="a3437b2c9efb40c88bae8949dd6ae46a";
  static final Set<String> NAMES=Set.of("epoch.current","permit-start.intent",EPOCH+".permit",EPOCH+".owner",
      EPOCH+".API.launch",EPOCH+".WEB.launch",EPOCH+".API.start.intent",EPOCH+".WEB.start.intent");
  static final String RECEIPT_SHA="701943c75adebf51e5ca41e3e48f52b874c2f62ce2933111a4d4e8f98fb26e2b";
  static final String WATCH_SHA="af8a802001783fd5a3c3e8766b52fc943e81f4a9b6fb2b4f2cd40d694185fee0";

  static boolean known(RootFailedStartRecovery.PairEvidence pair) {
    if(pair==null)return false;
    var e=pair.api();
    return EPOCH.equals(e.invalid().epoch().toString()) && BOOT.equals(e.invalid().boot().toString())
        && e.invalid().activation().run().id().equals(Pg407FailedRootRecovery.RUN)
        && e.invalid().activation().id().equals(Pg407FailedRootRecovery.ACTIVATION)
        && e.invalid().activation().run().cutoff().equals(java.time.Instant.parse("2026-09-27T15:00:00Z"))
        && OLD_DIGEST.equals(e.permit().releaseDigest())
        && actor(e.owner().morning(),MORNING,32159,780417)
        && actor(e.child(),API,149131,848428) && actor(pair.web().child(),WEB,151035,849540);
  }
  static boolean actor(MaintenanceOwnerFrame.Parent actor,String invocation,long pid,long ticks) {
    return actor.invocation().equals(invocation) && actor.pid()==pid && actor.startTicks()==ticks;
  }
  static boolean known(List<Pg410KnownAuthRecovery.Receipt> receipts) {
    if(receipts==null || receipts.size()!=3)return false;
    String[] names={"morning-controller","api","web"}, invocations={MORNING,API,WEB}, exits={"30","143","50"};
    for(int i=0;i<3;i++) {
      var v=receipts.get(i).values();
      if(!v.keySet().equals(Pg410KnownAuthRecovery.FIELDS) || !v.get("Id").equals("schubert-nk-"+names[i]+".service")
          || !v.get("InvocationID").equals(invocations[i]) || !v.get("ExecMainCode").equals("1")
          || !v.get("ExecMainStatus").equals(exits[i]) || !v.get("Result").equals("exit-code")
          || !v.get("LoadState").equals("loaded") || !v.get("MainPID").equals("0")
          || !v.get("ControlPID").equals("0") || !v.get("Job").isEmpty() || !receipts.get(i).snapshot().quiescent())return false;
    }
    return true;
  }
  static byte[] pinned(String name,String sha) throws Exception {
    var d=Pg410KnownAuthRecovery.metadata(STAGED);var f=Pg410KnownAuthRecovery.metadata(STAGED.resolve(name));
    if(!Integer.valueOf(0).equals(d.get("uid")) || !Integer.valueOf(0040500).equals(d.get("mode"))
        || !Integer.valueOf(0).equals(f.get("uid")) || !Integer.valueOf(0100400).equals(f.get("mode")))throw new IllegalStateException("closed Root observations required");
    byte[] bytes=Pg410KnownAuthRecovery.material(STAGED.resolve(name),4194304);
    if(!Pg410KnownAuthRecovery.hash(bytes).equals(sha))throw new IllegalStateException("captured observations changed");return bytes;
  }
  static void save(String name,byte[] bytes) throws Exception {
    Path p=SAVED.resolve(name);Files.write(p,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var channel=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){channel.force(true);}
    if(!Arrays.equals(bytes,Pg410KnownAuthRecovery.material(p,4194304)))throw new IllegalStateException("private readback required");
  }
  static Map<String,byte[]> startup() throws Exception {
    try(var entries=Files.list(STARTUP)) {
      if(!entries.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet()).equals(NAMES))throw new IllegalStateException("fixed namespace required");
    }
    var result=new TreeMap<String,byte[]>();
    for(String name:NAMES) {
      Path p=STARTUP.resolve(name);var m=Pg410KnownAuthRecovery.metadata(p);
      if(!Integer.valueOf(0).equals(m.get("uid")) || !Integer.valueOf(0).equals(m.get("gid"))
          || !Integer.valueOf(0100600).equals(m.get("mode")))throw new IllegalStateException("root private original required");
      result.put(name,Pg410KnownAuthRecovery.material(p,1024));
    }return Map.copyOf(result);
  }
  static void configure(String label,String source) {
    Pg387TrustedDeployment.LABEL=label;Pg387TrustedDeployment.STEM=label.toLowerCase(Locale.ROOT);
    Pg387TrustedDeployment.SOURCE=source;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-"+label);
  }
  static void signed(String candidateSource) throws Exception {
    configure("PG430",OLD_SOURCE);var old=Pg387TrustedDeployment.verify();
    if(!old.manifestSha256().equals(OLD_DIGEST)
        || !Arrays.equals(old.encode(),Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/release-approval/current"),1024))
        || !Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE))throw new IllegalStateException("same old approval/current required");
    configure("PG432",candidateSource);Pg387TrustedDeployment.verify();configure("PG430",OLD_SOURCE);
  }
  static void physical(List<Pg410KnownAuthRecovery.Receipt> old,RootFailedStartRecovery.PairEvidence pair) throws Exception {
    if(!Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT) || !known(pair))throw new IllegalStateException("same boot/generation required");
    var targets=List.of(InspectorUnitSnapshot.Target.MORNING,InspectorUnitSnapshot.Target.API,InspectorUnitSnapshot.Target.WEB);
    var current=new ArrayList<Pg410KnownAuthRecovery.Receipt>();
    for(int i=0;i<3;i++) {
      var now=Pg410KnownAuthRecovery.show(targets.get(i));
      if(!Pg410KnownAuthRecovery.stoppedAfter(old.get(i).values(),now.values()))throw new IllegalStateException("captured generation drift");current.add(now);
    }
    var stopSet=stopSet();Pg387TrustedDeployment.terminalAll();
    for(var unit:MaintenanceUnit.values())Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit.serviceName()));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    for(var actor:List.of(pair.api().owner().morning(),pair.api().child(),pair.web().child()))
      if(Files.exists(Path.of("/proc",Long.toString(actor.pid())),LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("old PID remains or reused");
    for(int i=0;i<3;i++)if(!current.get(i).values().equals(Pg410KnownAuthRecovery.show(targets.get(i)).values()))throw new IllegalStateException("manager/kernel changed");
    var after=stopSet();for(var unit:MaintenanceUnit.values())if(!stopSet.get(unit).matches(after.get(unit)))throw new IllegalStateException("whole stop-set manager changed");
  }
  static Map<MaintenanceUnit,MaintenanceStopSnapshot> stopSet() throws Exception {
    var result=new EnumMap<MaintenanceUnit,MaintenanceStopSnapshot>(MaintenanceUnit.class);
    for(var unit:MaintenanceUnit.values()) {
      byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",unit.serviceName(),
          "--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,Slice,Delegate,ControlGroup,InvocationID,StateChangeTimestampMonotonic");
      var value=MaintenanceStopSnapshot.parse(unit,raw);if(!value.quiescent())throw new IllegalStateException("actual terminal stop set required");result.put(unit,value);
    }return Map.copyOf(result);
  }
  static void watch(byte[] raw) {
    boolean apiRoot=false,apiOrdinary=false,webRoot=false,webOrdinary=false,ready=false;
    for(String line:new String(raw,StandardCharsets.UTF_8).split("\n")) {
      var v=com.google.gson.JsonParser.parseString(line).getAsJsonObject();
      if(v.has("ready")) {
        if(!v.get("ready").getAsString().equals("api") || !v.get("sameRootOrdinary").getAsBoolean()
            || !v.get("sameParent").getAsBoolean() || !v.get("ownedSocket").getAsBoolean()
            || !com.google.gson.JsonParser.parseString("{\"commit\":\""+OLD_SOURCE+"\",\"app\":\"0.1.0-SNAPSHOT\",\"config\":\"1\",\"schema\":\"025\",\"protocol\":\"0.1.0-SNAPSHOT\"}").equals(v.get("info")))throw new IllegalStateException("actual same-peer ready required");ready=true;
      }
      if(!v.has("states"))continue;
      for(String role:List.of("api","web")) {
        var a=v.getAsJsonObject("states").getAsJsonObject(role);if(!a.has("entry"))continue;
        boolean api=role.equals("api");
        if(!a.get("MainPID").getAsString().equals(api?"149131":"151035") || !a.get("InvocationID").getAsString().equals(api?API:WEB)
            || a.get("startTicks").getAsLong()!=(api?848428:849540))throw new IllegalStateException("same captured child required");
        String entry=a.get("entry").getAsString();
        var process=a.getAsJsonObject("process");
        if(process==null || !process.keySet().equals(Set.of("Uid","Gid","Groups","NoNewPrivs","CapInh","CapPrm","CapEff","CapBnd","CapAmb")))throw new IllegalStateException("closed process fields required");
        if(entry.equals("dev.codex.schubert.nk.batch.file.RootServiceLauncher")) {
          if(!Pg425KnownApiRecovery.fourIds(process.get("Uid").getAsString(),"0"))throw new IllegalStateException("actual Root entry required");
          if(api)apiRoot=true;else webRoot=true;
        }
        if(entry.equals("dev.codex.schubert.nk."+role+".bootstrap."+(api?"Api":"Web")+"ProcessMain")) {
          var p=a.getAsJsonObject("process");
          if(!Pg425KnownApiRecovery.fourIds(p.get("Uid").getAsString(),api?"999":"997")
              || !Pg425KnownApiRecovery.fourIds(p.get("Gid").getAsString(),api?"981":"980")
              || !p.get("Groups").getAsString().equals(api?"980 981 982 986":"980 982 986")
              || !p.get("NoNewPrivs").getAsString().equals("1"))throw new IllegalStateException("fixed ordinary identity required");
          for(String cap:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))if(!p.get(cap).getAsString().equals("0000000000000000"))throw new IllegalStateException("capability drift");
          if(api)apiOrdinary=true;else webOrdinary=true;
        }
      }
    }
    if(!apiRoot || !apiOrdinary || !webRoot || !webOrdinary || !ready)throw new IllegalStateException("genuine complete pair observation required");
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println("PG431_PAIR_REFUSED diagnosticsRedacted=true type="+e.getClass().getName()));
    if(args.length!=1 || !args[0].matches("[0-9a-f]{40}") || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new IllegalStateException("isolated fixed candidate only");
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      byte[] full=pinned("full18.properties",RECEIPT_SHA), captured=pinned("watch.jsonl",WATCH_SHA);watch(captured);
      var blocks=new String(full,StandardCharsets.US_ASCII).stripTrailing().split("\n\n");if(blocks.length!=3)throw new IllegalStateException("full actual receipts required");
      var targets=List.of(InspectorUnitSnapshot.Target.MORNING,InspectorUnitSnapshot.Target.API,InspectorUnitSnapshot.Target.WEB);
      var receipts=new ArrayList<Pg410KnownAuthRecovery.Receipt>();
      for(int i=0;i<3;i++)receipts.add(Pg410KnownAuthRecovery.parsed((blocks[i]+"\n").getBytes(StandardCharsets.US_ASCII),targets.get(i)));
      if(!known(receipts))throw new IllegalStateException("fixed normal receipts required");
      if(Files.exists(SAVED,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("recovery already saved; reattach required");
      Files.createDirectory(SAVED,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
      save("full18.properties",full);save("watch.jsonl",captured);
      byte[] journal=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/journalctl","--no-pager","-o","short-monotonic","_SYSTEMD_INVOCATION_ID="+API);
      String text=new String(journal,StandardCharsets.UTF_8);if(!text.contains("API cleanup complete") || !text.contains("API process stopped"))throw new IllegalStateException("actual ordinary cleanup required");save("api-cleanup-journal.log",journal);
      Pg387TrustedDeployment.sync(SAVED);Pg387TrustedDeployment.sync(SAVED.getParent());
      RootFailedStartRecovery.PairEvidence capturedPair;
      try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)){capturedPair=RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create());}
      if(!known(capturedPair))throw new IllegalStateException("exact pre-stop pair required");
      configure("PG430",OLD_SOURCE);Pg387TrustedDeployment.stopAll();
      try {
      return StartupAdmissionFile.create().tryExclusive(fd->Pg387TrustedDeployment.checked(()-> {
        RootFailedStartRecovery.PairEvidence pair;
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)){pair=RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create());}
        if(!known(pair))throw new IllegalStateException("exact pair required");
        try(var db=Pg407FailedRootRecovery.openDatabase();var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {
          db.setAutoCommit(false);
          try(var s=db.createStatement();var rows=s.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
            if(!rows.next() || !Boolean.TRUE.equals(rows.getObject(1,Boolean.class)) || rows.next())throw new IllegalStateException("dedicated advisory required");
          }
          var rows=Pg407FailedRootRecovery.databaseRows(db);if(rows.size()!=251)throw new IllegalStateException("all251 required");
          byte[] dbRaw=Pg425KnownApiRecovery.command(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-");save("all14-db-before.log",dbRaw);
          var backup=Pg407FailedRootRecovery.backupSnapshot();save("backup-before.log",backup.toString().getBytes(StandardCharsets.UTF_8));
          var bytes=startup();for(var item:bytes.entrySet())save(item.getKey(),item.getValue());
          // BUG544/SSC174: preserve valid normal nonempty Transfer, not the old diagnostic empty fixture.
          var fixture=Pg428ColdBootPreparation.fixtureSnapshot();save("fixture-before.log",fixture.getBytes(StandardCharsets.UTF_8));
          physical(receipts,pair);Pg410KnownAuthRecovery.original(db,pair.api());
          // BUG543/YKT387: full host BOM requires an immutable candidate, not just file modes.
          // Freeze only here, inside the same M/A and authenticated complete terminal set.
          // The rejected-preflight PG431/source329 candidate stays unchanged and unactivated.
          configure("PG432",args[0]);Pg387TrustedDeployment.freezeCandidate();configure("PG430",OLD_SOURCE);
          signed(args[0]);Pg387TrustedDeployment.sync(SAVED);
          RootFailedStartRecovery.retirePair(root,LinuxInodeSecurity.create(),pair,expected->Pg387TrustedDeployment.checked(()-> {
            if(!pair.equals(expected))throw new IllegalStateException("same borrowed pair required");
            physical(receipts,pair);Pg410KnownAuthRecovery.original(db,pair.api());signed(args[0]);
            if(!rows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot())
                || !fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()))throw new IllegalStateException("preservation drift");
            for(var item:bytes.entrySet())if(!item.getKey().endsWith(".start.intent") && !item.getKey().equals("permit-start.intent")
                && !Arrays.equals(item.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(item.getKey()),1024)))throw new IllegalStateException("old artifact changed");
            return Boolean.TRUE;
          }));
          physical(receipts,pair);Pg410KnownAuthRecovery.original(db,pair.api());signed(args[0]);
          if(!rows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot())
              || !fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) || !Arrays.equals(dbRaw,Pg425KnownApiRecovery.command(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-")))throw new IllegalStateException("post preservation drift");db.rollback();
        } catch(Exception | Error failure) {
          try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)){RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),pair);}
          catch(Exception | Error unknown){failure.addSuppressed(unknown);}
          // Do not unwind the enclosing admission/M on uncertain retirement or owned close.
          System.err.println("PG431_PAIR_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");
          for(;;)java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);
        }
        System.out.println("PG431_PAIR_RECOVERED fixedNormalGeneration=true typedThreeIntentsRetired=true all251AndBackupUnchanged=true currentInvalidUnchanged=true historicalCloseInferred=false newPermitIssued=false");return Boolean.TRUE;
      })).orElseThrow();
      } catch(Exception | Error admissionUnknown) {
        // A may have closed or become uncertain after the callback. M still excludes a new
        // parent. Reauthenticate the fixed A inode before quarantine, then retain both locks.
        System.err.println("PG431_PAIR_ADMISSION_UNKNOWN M_RETAINED=true diagnosticsRedacted=true");
        for(;;) {
          try {
            StartupAdmissionFile.create().tryExclusive(fd->Pg387TrustedDeployment.checked(()-> {
              try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)){RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),capturedPair);}
              System.err.println("PG431_PAIR_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");
              for(;;)java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);
            }));
          } catch(Exception | Error stillUnknown) { /* No return while M owns this uncertainty. */ }
          java.util.concurrent.locks.LockSupport.parkNanos(1000000000L);
        }
      }
    })).orElseThrow();
  }
}
