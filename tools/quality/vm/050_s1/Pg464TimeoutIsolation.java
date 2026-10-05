import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** QA047/SS343: isolate ONLY observed PG463 timeout143; no intent/permit/original mutation.
 * Old ownership/normal return stays UNKNOWN. This new operator owns M/A/DB during reverse stops.
 * PT-OPS-ISO464001..003. No old known30 receipt/captured Root authority is reused.
 */
public final class Pg464TimeoutIsolation {
  static final String SOURCE="11c1feb1c0b51543f98c28e3f54213274648f06f";
  static final String DIGEST="0cfd6453948feff4e63912c3169224b0800a0d2c1246f5e06207cab7964386d1";
  static final String PARENT="f010f29e17ec4e5e9a38378185041e3e";
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static final String EPOCH="1ba8ece5-5297-47c3-9933-95b2330beeb0";
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final Path CAPTURE=Path.of("/var/lib/pgpt-s1-preservation/pg464-parent-timeout-private");
  static String phase="ARGUMENTS";
  static void require(boolean v){if(!v)throw new IllegalStateException("fixed timeout isolation proof differs");}
  static boolean parentValue(Map<String,String> p){
    return p!=null && p.keySet().equals(Pg410KnownAuthRecovery.FIELDS) && p.values().stream().noneMatch(Objects::isNull) && PARENT.equals(p.get("InvocationID")) && "timeout".equals(p.get("Result"))
        && "1".equals(p.get("ExecMainCode")) && "143".equals(p.get("ExecMainStatus"))
        && "failed".equals(p.get("ActiveState")) && "failed".equals(p.get("SubState"))
        && "0".equals(p.get("MainPID")) && "0".equals(p.get("ControlPID")) && "".equals(p.get("Job"));
  }
  static Set<String> names(){
    var names=new HashSet<>(Set.of("epoch.current",EPOCH+".permit",EPOCH+".owner",EPOCH+".API.launch",EPOCH+".WEB.launch",EPOCH+".API.start.intent",EPOCH+".WEB.start.intent"));
    for(String old:List.of("1eecb7b9-1e98-478f-9084-201422b31bff","d536cf5a-f5a8-4dd9-8679-3488fab17fdf","e8cce97a-163b-4814-b435-8fc26466e550","25020aa0-7b69-4554-be47-ea69588da569","15e4559b-13ab-46d7-a7a8-c15f1de4a245","bcd85e18-8926-4a3c-9e9c-78da9dba2670"))
      for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))names.add(old+suffix);
    return Set.copyOf(names);
  }
  static boolean liveValue(Map<String,String> v,String pid,String invocation){
    return v!=null && pid!=null && invocation!=null && pid.equals(v.get("MainPID")) && invocation.equals(v.get("InvocationID"))
        && "0".equals(v.get("ControlPID")) && "".equals(v.get("Job"))
        && "active".equals(v.get("ActiveState")) && "running".equals(v.get("SubState"));
  }
  static boolean authority(Map<String,String> p,String uid,String gid,String groups){
    if(p==null || uid==null || gid==null || groups==null || !p.keySet().equals(Set.of("Uid","Gid","Groups","NoNewPrivs","CapInh","CapPrm","CapEff","CapBnd","CapAmb")) || p.values().stream().anyMatch(Objects::isNull))return false;
    return Pg425KnownApiRecovery.fourIds(p.get("Uid"),uid) && Pg425KnownApiRecovery.fourIds(p.get("Gid"),gid)
        && groups.equals(p.get("Groups")) && "1".equals(p.get("NoNewPrivs"))
        && List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb").stream().allMatch(k->"0000000000000000".equals(p.get(k)));
  }
  static void parent() throws Exception {
    var p=Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values();require(parentValue(p));
    require(!Files.exists(Path.of("/proc/944286"),LinkOption.NOFOLLOW_LINKS));
    require(Long.parseLong(p.get("ExecMainStartTimestampMonotonic"))==110399747777L);
    require(Long.parseLong(p.get("ExecMainExitTimestampMonotonic"))>=110399747777L);
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    require(p.equals(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values()));
  }
  static void ordinary(InspectorUnitSnapshot.Target role,String pid,String invocation,long ticks) throws Exception {
    var before=Pg410KnownAuthRecovery.show(role).values();require(liveValue(before,pid,invocation));
    Path proc=Path.of("/proc",pid);byte[] raw=Files.readAllBytes(proc.resolve("status"));
    var identity=Pg461OwnedIsolation.identity(raw);boolean api=role==InspectorUnitSnapshot.Target.API;
    require(authority(identity,api?"999":"997",api?"981":"980",api?"980 981 982 986":"980 982 986"));
    String stat=Files.readString(proc.resolve("stat"));String[] tail=stat.substring(stat.lastIndexOf(')')+2).split(" ");
    require(Long.parseLong(tail[19])==ticks);
    var args=new String(Files.readAllBytes(proc.resolve("cmdline")),StandardCharsets.UTF_8);
    require(args.contains("dev.codex.schubert.nk."+(api?"api.bootstrap.Api":"web.bootstrap.Web")+"ProcessMain\0"));
    require(before.equals(Pg410KnownAuthRecovery.show(role).values()) && identity.equals(Pg461OwnedIsolation.identity(Files.readAllBytes(proc.resolve("status")))));
  }
  static void caddy() throws Exception {
    byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show","caddy.service","--property="+String.join(",",Pg410KnownAuthRecovery.FIELDS));
    var before=new HashMap<String,String>();for(String line:new String(raw,StandardCharsets.US_ASCII).split("\n")){int equal=line.indexOf('=');require(equal>0 && before.put(line.substring(0,equal),line.substring(equal+1))==null);}
    require(before.keySet().equals(Pg410KnownAuthRecovery.FIELDS) && liveValue(before,"1092488","b4f41f1681fa43bb888dd95f9f89ad00"));
    require(authority(Pg461OwnedIsolation.identity(Files.readAllBytes(Path.of("/proc/1092488/status"))),"993","978","978"));
    require(Arrays.equals(raw,Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show","caddy.service","--property="+String.join(",",Pg410KnownAuthRecovery.FIELDS))));
  }
  static void capturedMetadata() throws Exception {
    Pg464CapturedPeers.watch(Pg410KnownAuthRecovery.material(CAPTURE.resolve("external-watch.private.jsonl"),1048576));
    var json=com.google.gson.JsonParser.parseString(new String(Pg410KnownAuthRecovery.material(CAPTURE.resolve("startup-original-metadata.private.json"),1048576),StandardCharsets.UTF_8)).getAsJsonObject();
    for(var entry:json.entrySet()){
      Path p=Path.of(entry.getKey());require(p.startsWith(STARTUP) || p.startsWith(Path.of("/var/lib/schubert-nk/maintenance")));
      var expected=entry.getValue().getAsJsonObject();var actual=Pg410KnownAuthRecovery.metadata(p);
      for(String k:List.of("dev","ino","mode","uid","gid","nlink","size"))require(expected.get(k).getAsLong()==((Number)actual.get(k)).longValue());
      require(expected.get("ctimeNs").getAsLong()==((java.nio.file.attribute.FileTime)actual.get("ctime")).to(java.util.concurrent.TimeUnit.NANOSECONDS) && expected.get("mtimeNs").getAsLong()==((java.nio.file.attribute.FileTime)actual.get("lastModifiedTime")).to(java.util.concurrent.TimeUnit.NANOSECONDS));
      if(expected.has("sha256"))require(expected.get("sha256").getAsString().equals(Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(p,1048576))));
    }
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println("PG464_ISOLATION_REFUSED phase="+phase+" type="+e.getClass().getName()+" diagnosticsRedacted=true"));
    require(args.length==1 && Set.of("verify","isolate").contains(args[0]));boolean verify=args[0].equals("verify");
    require(Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01") && Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));
    boolean[] stopping={false};
    try {
      MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
        phase="M_PARENT";parent();
        return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
          phase="A_SIGNED";parent();
          Pg387TrustedDeployment.LABEL="PG463";Pg387TrustedDeployment.STEM="pg463";Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG463");Pg387TrustedDeployment.expectedSchema("027");
          var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals(DIGEST) && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
          var capture=Pg410KnownAuthRecovery.metadata(CAPTURE);require(Integer.valueOf(0).equals(capture.get("uid")) && Integer.valueOf(0040700).equals(capture.get("mode")));
          require(parentValue(Pg410KnownAuthRecovery.parsed(Pg410KnownAuthRecovery.material(CAPTURE.resolve("unit-0-before.properties"),4096),InspectorUnitSnapshot.Target.MORNING).values()));
          capturedMetadata();
          try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
            phase="DB_ORIGINAL";schema.setReadOnly(true);db.setAutoCommit(false);
            try(var s=db.createStatement();var r=s.executeQuery("select pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
            var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
            require(epoch.epoch().toString().equals(EPOCH) && epoch.boot().toString().equals(BOOT) && epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN) && epoch.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION));
            var startup=Pg428ColdBootPreparation.snapshot(STARTUP);var leafNames=new HashSet<String>();for(String p:startup.keySet())if(!p.equals(STARTUP.toString()))leafNames.add(Path.of(p).getFileName().toString());require(leafNames.equals(names()));
            var original=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();var fixture=Pg428ColdBootPreparation.fixtureSnapshot();var rows=Pg407FailedRootRecovery.databaseRows(db);var business=Pg456SignedMigration.business(schema);
            require(rows.size()==321 && MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty() && new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent());
            phase="CURRENT_ORDINARY";ordinary(InspectorUnitSnapshot.Target.API,"1085387","eda2df544e7e4b4d9e3f33eb46801c96",11109164);ordinary(InspectorUnitSnapshot.Target.WEB,"1087473","b6612dc72c6141a7a93cff14991731a8",11110271);caddy();parent();
            if(!verify){phase="REVERSE_STOP";for(var unit:MaintenanceUnit.values()){parent();stopping[0]=true;Pg461OwnedIsolation.stop(unit);}Pg387TrustedDeployment.terminalAll();parent();}
            phase="POST_PRESERVATION";
            capturedMetadata();
            require(epoch.equals(files.current()) && startup.equals(Pg428ColdBootPreparation.snapshot(STARTUP)) && original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
            require(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty());db.rollback();
          }
          return Boolean.TRUE;
        })).orElseThrow();
      })).orElseThrow();
    } catch(Exception|Error failure){if(stopping[0] || failure.getSuppressed().length>0){System.err.println("PG464_ISOLATION_UNKNOWN newOwnersRetained=true oldNormalReturnClaimed=false diagnosticsRedacted=true");Pg461OwnedIsolation.retain();}throw failure;}
    System.out.println("PG464_ISOLATION "+(verify?"verifyOnly=true":"all9Terminal=true")+" rows321OriginalBackupPreserved=true intentPermitMutation0=true oldNormalReturnClaimed=false newOwnedScopesReturnedNormally=true");
  }
}
