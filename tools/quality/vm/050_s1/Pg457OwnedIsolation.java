import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** QA047/SS343 operator isolation ONLY of this actual timed-out graph.
 * Never invalidates/repairs/retires a permit or intent, never claims old normal30/0/10.
 * Continuous real M/A/DB, signed same source, actual known ordinary peers, reverse fixed stops.
 */
public final class Pg457OwnedIsolation {
  static final String SOURCE="559bf7eacb401d6d07037dbdd295b32f174976a0";
  static final String DIGEST="21affa1850d60f3a7d54f5dbcc37e12c6460563865771fa49a52a433fe91b424";
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static String stage="ARGUMENTS";
  static void require(boolean v) {if(!v)throw new IllegalStateException("fixed isolation proof differs");}
  static Map<String,String> status(byte[] raw) {
    var m=new HashMap<String,String>();
    for(String line:new String(raw,StandardCharsets.US_ASCII).split("\n")) {
      int colon=line.indexOf(':');if(colon>0)require(m.put(line.substring(0,colon),line.substring(colon+1).trim())==null);
    }
    return Map.copyOf(m);
  }
  static Map<String,String> identity(byte[] raw) {
    var fields=status(raw);var result=new TreeMap<String,String>();
    for(String key:List.of("Uid","Gid","Groups","NoNewPrivs","CapInh","CapPrm","CapEff","CapBnd","CapAmb"))
      result.put(key,Objects.requireNonNull(fields.get(key),"fixed ordinary identity field"));
    return Map.copyOf(result);
  }
  static void parent() throws Exception {
    var p=Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values();
    require(p.get("InvocationID").equals("0735b37478204b49a5b2810c882ee3be") && p.get("Result").equals("timeout")
        && p.get("ExecMainCode").equals("1") && p.get("ExecMainStatus").equals("143")
        && p.get("ActiveState").equals("failed") && p.get("SubState").equals("failed")
        && p.get("MainPID").equals("0") && p.get("ControlPID").equals("0") && p.get("Job").isEmpty()
        && Long.parseLong(p.get("ExecMainStartTimestampMonotonic"))>0
        && Long.parseLong(p.get("ExecMainExitTimestampMonotonic"))>=Long.parseLong(p.get("ExecMainStartTimestampMonotonic")));
    require(!Files.exists(Path.of("/proc/19114"),LinkOption.NOFOLLOW_LINKS));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    require(p.equals(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values()));
  }
  static void ordinary(InspectorUnitSnapshot.Target role,long pid,String invocation,
      StartupPermitRecords.Epoch epoch) throws Exception {
    var before=Pg410KnownAuthRecovery.show(role).values();
    require(before.get("InvocationID").equals(invocation) && before.get("MainPID").equals(Long.toString(pid))
        && before.get("ActiveState").equals("active") && before.get("SubState").equals("running")
        && before.get("ControlPID").equals("0") && before.get("Job").isEmpty());
    Path proc=Path.of("/proc",Long.toString(pid));
    byte[] rawStatus=Files.readAllBytes(proc.resolve("status")),argv=Files.readAllBytes(proc.resolve("cmdline"));
    var fields=status(rawStatus);var fixed=new FixedServiceIdentity().resolve(role==InspectorUnitSnapshot.Target.API?ServiceConfigFiles.Service.API:ServiceConfigFiles.Service.WEB);
    require(fields.get("Uid").trim().replaceAll("\\s+"," ").equals(String.join(" ",Collections.nCopies(4,Long.toString(fixed.uid()))))
        && fields.get("Gid").trim().replaceAll("\\s+"," ").equals(String.join(" ",Collections.nCopies(4,Long.toString(fixed.gid()))))
        && fields.get("Groups").trim().replaceAll("\\s+"," ").equals(String.join(" ",fixed.groups().stream().map(Object::toString).toList()))
        && fields.get("NoNewPrivs").equals("1"));
    for(String cap:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))require(fields.get(cap).equals("0000000000000000"));
    String main=role==InspectorUnitSnapshot.Target.API?"dev.codex.schubert.nk.api.bootstrap.ApiProcessMain":"dev.codex.schubert.nk.web.bootstrap.WebProcessMain";
    require(Arrays.stream(new String(argv,StandardCharsets.US_ASCII).split("\u0000",-1)).filter(main::equals).count()==1);
    require(Files.readString(proc.resolve("cgroup")).equals("0::/system.slice/"+role.unit()+"\n"));
    long ticks=Long.parseLong(Files.readString(proc.resolve("stat")).substring(Files.readString(proc.resolve("stat")).lastIndexOf(')')+2).split(" ")[19]);
    Path launch=STARTUP.resolve(epoch.epoch()+"."+role.name()+".launch");
    byte[] raw=Pg410KnownAuthRecovery.material(launch,1024);var a=Pg410KnownAuthRecovery.metadata(launch);
    require(Integer.valueOf(0).equals(a.get("uid")) && Integer.valueOf(0).equals(a.get("gid")) && Integer.valueOf(0100600).equals(a.get("mode")));
    String[] lines=new String(raw,StandardCharsets.US_ASCII).split("\n",-1);
    require(lines.length==10 && lines[0].equals("NKLAUNCH1") && lines[9].isEmpty());
    String[] keys={"service","boot","epoch","permit_sha256","owner_sha256","invocation","pid","start_ticks"};
    var values=new HashMap<String,String>();
    for(int i=0;i<8;i++){require(lines[i+1].startsWith(keys[i]+"="));values.put(keys[i],lines[i+1].substring(keys[i].length()+1));}
    require(values.get("service").equals(role.name()) && values.get("boot").equals(epoch.boot().toString()) && values.get("epoch").equals(epoch.epoch().toString())
        && values.get("permit_sha256").equals(epoch.permitDigest().orElseThrow())
        && values.get("owner_sha256").equals(Pg422SignedMigration.hash(Pg410KnownAuthRecovery.material(STARTUP.resolve(epoch.epoch()+".owner"),4096)))
        && values.get("invocation").equals(invocation) && values.get("pid").equals(Long.toString(pid)) && values.get("start_ticks").equals(Long.toString(ticks)));
    // /proc/status includes changing counters/memory; compare every authority field, not unrelated activity.
    require(identity(rawStatus).equals(identity(Files.readAllBytes(proc.resolve("status")))) && Arrays.equals(argv,Files.readAllBytes(proc.resolve("cmdline")))
        && before.equals(Pg410KnownAuthRecovery.show(role).values()) && Arrays.equals(raw,Files.readAllBytes(launch)));
  }
  static void stop(MaintenanceUnit unit) throws Exception {
    MaintenanceUnitStopPolicy.create().requireSafe(unit);
    var p=new ProcessBuilder("/usr/bin/systemctl","--system","--no-pager","--no-ask-password","stop",unit.serviceName())
        .redirectOutput(ProcessBuilder.Redirect.DISCARD).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    if(!p.waitFor(40,TimeUnit.SECONDS)) {
      p.destroy();if(!p.waitFor(5,TimeUnit.SECONDS))retain();
      retain(); // no fake successful stop, retain all M/A/DB owners on uncertain delivery
    }
    if(p.exitValue()!=0)retain();
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit.serviceName()));
  }
  static void retain() {for(;;)java.util.concurrent.locks.LockSupport.parkNanos(TimeUnit.SECONDS.toNanos(1));}
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG457_ISOLATION_REFUSED stage="+stage+" type="+e.getClass().getName()+" diagnosticsRedacted=true intentsUnrepaired=true");
      for(var f:e.getStackTrace())if(f.getClassName().equals("Pg457OwnedIsolation"))System.err.println("PG457_ISOLATION_FRAME "+f.getMethodName()+":"+f.getLineNumber());
    });
    require(args.length==0 && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01")
        && Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("e07aa706-1acd-4e65-b309-d7f330f79d54"));
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      stage="M_PARENT";parent();
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        stage="A_SIGNED_BOM";parent();Pg456SignedMigration.configure(SOURCE);
        var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals(DIGEST));
        require(Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);var db=Pg407FailedRootRecovery.openDatabase()) {
          stage="DB_ORIGINAL";db.setAutoCommit(false);
          try(var s=db.createStatement();var r=s.executeQuery("select pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
          require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.boot().toString().equals("e07aa706-1acd-4e65-b309-d7f330f79d54")
              && epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN) && epoch.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION)
              && files.readIssued().releaseDigest().equals(DIGEST));
          var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
          require(original.completed().isEmpty() && new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent());
          var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==261);
          var startup=Pg428ColdBootPreparation.snapshot(STARTUP);var originalFiles=Pg428ColdBootPreparation.original();var backups=Pg428ColdBootPreparation.backupSnapshot();
          stage="ORDINARY_IDENTITIES";ordinary(InspectorUnitSnapshot.Target.API,142079,"0f254ac7a80844afb0fef3c8654cb5ab",epoch);
          ordinary(InspectorUnitSnapshot.Target.WEB,143932,"8c9f2c9605034ed78b0ed2a7c0e5f93e",epoch);parent();
          require(startup.equals(Pg428ColdBootPreparation.snapshot(STARTUP)) && epoch.equals(files.current()));
          stage="REVERSE_STOP";
          for(var unit:MaintenanceUnit.values()){parent();stop(unit);}
          Pg387TrustedDeployment.terminalAll();parent();
          require(!Files.exists(Path.of("/proc/142079")) && !Files.exists(Path.of("/proc/143932"))
              && epoch.equals(files.current()) && startup.equals(Pg428ColdBootPreparation.snapshot(STARTUP))
              && originalFiles.equals(Pg428ColdBootPreparation.original()) && backups.equals(Pg428ColdBootPreparation.backupSnapshot())
              && rows.equals(Pg407FailedRootRecovery.databaseRows(db)));
          require(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty());
          db.rollback();
        }
        System.out.println("PG457_GRAPH_ISOLATED actualParentTimeout143=true all8KernelStopped=true sameOriginal261RowsBackupPreserved=true currentStillIssued=true intentRetired0=true normalExitClaimed=false permitsIssued0=true");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
