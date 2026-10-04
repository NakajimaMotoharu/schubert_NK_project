import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** QA047/SS343 operator isolation ONLY of this actual known30 graph.
 * Never invalidates/repairs/retires a permit or intent, never claims old normal30/0/10.
 * Continuous real M/A/DB, signed same source, actual known ordinary peers, reverse fixed stops.
 */
public final class Pg459OwnedIsolation {
  static final String SOURCE="ea1c13aa6a1b0fca2c2f4de1769a7c5afd70244a";
  static final String DIGEST="d0413fc29171dc69363ec173e1d37dcc8bf3d25da2f26cc474ca80b7b316d6b2";
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
    require(p.get("InvocationID").equals("fb3eaf763a8c4a5e8172d3c42f8fc954") && p.get("Result").equals("exit-code")
        && p.get("ExecMainCode").equals("1") && p.get("ExecMainStatus").equals("30")
        && p.get("ActiveState").equals("failed") && p.get("SubState").equals("failed")
        && p.get("MainPID").equals("0") && p.get("ControlPID").equals("0") && p.get("Job").isEmpty()
        && Long.parseLong(p.get("ExecMainStartTimestampMonotonic"))>0
        && Long.parseLong(p.get("ExecMainExitTimestampMonotonic"))>=Long.parseLong(p.get("ExecMainStartTimestampMonotonic")));
    require(!Files.exists(Path.of("/proc/162624"),LinkOption.NOFOLLOW_LINKS));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    require(p.equals(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values()));
  }
  static void ordinary(InspectorUnitSnapshot.Target role,long pid,String invocation,
      StartupPermitRecords.Epoch epoch, String permitSha256) throws Exception {
    var before=Pg410KnownAuthRecovery.show(role).values();
    require(before.get("InvocationID").equals(invocation) && before.get("MainPID").equals("0")
        && before.get("ActiveState").equals("failed") && before.get("SubState").equals("failed")
        && before.get("ControlPID").equals("0") && before.get("Job").isEmpty());
    require(before.get("MainPID").equals("0") && before.get("Result").equals("exit-code") && before.get("ExecMainCode").equals("1") && before.get("ExecMainStatus").equals("143"));
    require(!Files.exists(Path.of("/proc",Long.toString(pid)),LinkOption.NOFOLLOW_LINKS));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",role.unit()));
    long ticks=role==InspectorUnitSnapshot.Target.API?8483207:8484334;
    Path launch=STARTUP.resolve(epoch.epoch()+"."+role.name()+".launch");
    byte[] raw=Pg410KnownAuthRecovery.material(launch,1024);var a=Pg410KnownAuthRecovery.metadata(launch);
    require(Integer.valueOf(0).equals(a.get("uid")) && Integer.valueOf(0).equals(a.get("gid")) && Integer.valueOf(0100600).equals(a.get("mode")));
    String[] lines=new String(raw,StandardCharsets.US_ASCII).split("\n",-1);
    require(lines.length==10 && lines[0].equals("NKLAUNCH1") && lines[9].isEmpty());
    String[] keys={"service","boot","epoch","permit_sha256","owner_sha256","invocation","pid","start_ticks"};
    var values=new HashMap<String,String>();
    for(int i=0;i<8;i++){require(lines[i+1].startsWith(keys[i]+"="));values.put(keys[i],lines[i+1].substring(keys[i].length()+1));}
    require(values.get("service").equals(role.name()) && values.get("boot").equals(epoch.boot().toString()) && values.get("epoch").equals(epoch.epoch().toString())
        && values.get("permit_sha256").equals(permitSha256)
        && values.get("owner_sha256").equals(Pg422SignedMigration.hash(Pg410KnownAuthRecovery.material(STARTUP.resolve(epoch.epoch()+".owner"),4096)))
        && values.get("invocation").equals(invocation) && values.get("pid").equals(Long.toString(pid)) && values.get("start_ticks").equals(Long.toString(ticks)));
    require(before.equals(Pg410KnownAuthRecovery.show(role).values()) && Arrays.equals(raw,Files.readAllBytes(launch)));

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
      System.err.println("PG459_ISOLATION_REFUSED stage="+stage+" type="+e.getClass().getName()+" diagnosticsRedacted=true intentsUnrepaired=true");
      for(var f:e.getStackTrace())if(f.getClassName().equals("Pg459OwnedIsolation"))System.err.println("PG459_ISOLATION_FRAME "+f.getMethodName()+":"+f.getLineNumber());
    });
    require(args.length==0 && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01")
        && Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("e07aa706-1acd-4e65-b309-d7f330f79d54"));
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      stage="M_PARENT";parent();
      boolean[] stopping={false};
      try {
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        stage="A_SIGNED_BOM";parent();
        Pg387TrustedDeployment.expectedSchema("027");
        byte[] watch=Pg410KnownAuthRecovery.material(Path.of("/var/lib/pgpt-s1-preservation/pg459-parent-known30-private/external-watch.private.jsonl"),4194304);
        require(Pg410KnownAuthRecovery.hash(watch).equals("58274a05166aafbab06eeae7f82cb4f326c86137510346de2f985a57d423237b"));Pg459CapturedPeers.watch(watch);Pg387TrustedDeployment.LABEL="PG458";Pg387TrustedDeployment.STEM="pg458";Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG458");
        var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals(DIGEST));
        require(Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          schema.setReadOnly(true);
          stage="DB_ORIGINAL";db.setAutoCommit(false);
          try(var s=db.createStatement();var r=s.executeQuery("select pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
          var pair=RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create());
          require(epoch.equals(pair.api().invalid()) && epoch.epoch().toString().equals("d536cf5a-f5a8-4dd9-8679-3488fab17fdf"));
          require(epoch.state()==StartupPermitRecords.State.INVALID && epoch.boot().toString().equals("e07aa706-1acd-4e65-b309-d7f330f79d54")
              && epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN) && epoch.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION)
              && pair.api().permit().releaseDigest().equals(DIGEST));
          var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
          require(original.completed().isEmpty() && new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent());
          var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==271);
          var business=Pg456SignedMigration.business(schema);var fixture=Pg428ColdBootPreparation.fixtureSnapshot();
          var startup=Pg428ColdBootPreparation.snapshot(STARTUP);var originalFiles=Pg428ColdBootPreparation.original();var backups=Pg428ColdBootPreparation.backupSnapshot();
          stage="ORDINARY_IDENTITIES";ordinary(InspectorUnitSnapshot.Target.API,304687,"386729898874494ebff10f86647d3e3a",epoch,pair.api().permitSha256());
          ordinary(InspectorUnitSnapshot.Target.WEB,306804,"5b8cd47d114d465582216725317d6788",epoch,pair.api().permitSha256());parent();
          require(startup.equals(Pg428ColdBootPreparation.snapshot(STARTUP)) && epoch.equals(files.current()));
          stage="REVERSE_STOP";
          for(var unit:MaintenanceUnit.values()){parent();stopping[0]=true;stop(unit);}
          Pg387TrustedDeployment.terminalAll();parent();
          require(!Files.exists(Path.of("/proc/304687")) && !Files.exists(Path.of("/proc/306804"))
              && epoch.equals(files.current()) && startup.equals(Pg428ColdBootPreparation.snapshot(STARTUP))
              && originalFiles.equals(Pg428ColdBootPreparation.original()) && backups.equals(Pg428ColdBootPreparation.backupSnapshot())
              && rows.equals(Pg407FailedRootRecovery.databaseRows(db))
              && business.equals(Pg456SignedMigration.business(schema)) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()));
          require(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty());
          db.rollback();
        } catch(Exception|Error unknown) {
          if(stopping[0] || unknown.getSuppressed().length!=0) {
            System.err.println("PG459_ISOLATION_UNKNOWN M_A_RETAINED=true diagnosticsRedacted=true");retain();
          }
          throw unknown;
        }
        return Boolean.TRUE;
      })).orElseThrow();
      } catch(Exception|Error admissionUnknown) {
        if(stopping[0] || admissionUnknown.getSuppressed().length!=0) {
          System.err.println("PG459_ISOLATION_POST_ADMISSION_UNKNOWN M_RETAINED=true A_OWNERSHIP_NOT_INFERRED=true normalExitClaimed=false");retain();
        }
        throw admissionUnknown;
      }
    })).orElseThrow();
    System.out.println("PG459_GRAPH_ISOLATED actualParentKnownFailure30=true all8KernelStopped=true sameOriginal271RowsBackupPreserved=true currentStillInvalid=true intentRetired0=true normalExitClaimed=false permitsIssued0=true allOwnedScopesReturnedNormally=true");
  }
}
