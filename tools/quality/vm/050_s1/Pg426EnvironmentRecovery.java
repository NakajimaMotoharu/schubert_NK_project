import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** SSC163/BUG522: one unstarted Expiry request after captured apt restart, not worker success. */
public final class Pg426EnvironmentRecovery {
  static final Path STAGE=Path.of("/home/ubuntu/pg426-environment-stage");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg426-environment");
  static final Path REQUEST=Path.of("/run/schubert-nk/expiry-request");
  static final String BOOT="9024b59c-41d0-4dbd-8a3e-96bfad1467c0";
  static final String EPOCH="5f4912b8-2ed9-4a66-aa4e-1c47a15a75ec";
  static final String MORNING="b75c537a39574815b2c2bdb4d8c42140";
  static final String EXPIRY="09e0dedfdec24c0ea87ae5d645525e18";
  static final String MANIFEST="55353381ea39d2ddda0c3a195dea05cffda1ad880974693a72095811cd122fd1";

  static void require(boolean value) {if(!value)throw new IllegalStateException("fixed environmental case required");}
  static byte[] pin(String name,String digest) throws Exception {
    var d=Pg410KnownAuthRecovery.metadata(STAGE);var f=Pg410KnownAuthRecovery.metadata(STAGE.resolve(name));
    require(Integer.valueOf(0).equals(d.get("uid")) && Integer.valueOf(0).equals(d.get("gid"))
        && Integer.valueOf(0040500).equals(d.get("mode")) && Integer.valueOf(0).equals(f.get("uid"))
        && Integer.valueOf(0).equals(f.get("gid")) && Integer.valueOf(0100400).equals(f.get("mode")));
    byte[] bytes=Pg410KnownAuthRecovery.material(STAGE.resolve(name),4194304);
    require(Pg410KnownAuthRecovery.hash(bytes).equals(digest));return bytes;
  }
  static void save(String name,byte[] bytes) throws Exception {
    Path p=SAVE.resolve(name);Files.write(p,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var c=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){c.force(true);}
    require(Arrays.equals(bytes,Files.readAllBytes(p)));
  }
  static boolean known(Map<String,String> m,Map<String,String> e) {
    if(m==null || e==null || !m.keySet().equals(Pg410KnownAuthRecovery.FIELDS)
        || !e.keySet().equals(Pg410KnownAuthRecovery.FIELDS))return false;
    return "schubert-nk-morning-controller.service".equals(m.get("Id"))
        && "schubert-nk-expiry-cleanup.service".equals(e.get("Id"))
        && MORNING.equals(m.get("InvocationID")) && EXPIRY.equals(e.get("InvocationID"))
        && "1".equals(m.get("ExecMainCode")) && "30".equals(m.get("ExecMainStatus"))
        && "204730222079".equals(m.get("ExecMainStartTimestampMonotonic"))
        && "1".equals(e.get("ExecMainCode")) && "243".equals(e.get("ExecMainStatus"))
        && "203068112706".equals(e.get("ExecMainStartTimestampMonotonic"))
        && "203068124127".equals(e.get("ExecMainExitTimestampMonotonic"))
        && List.of(m,e).stream().allMatch(v->"0".equals(v.get("MainPID")) && "0".equals(v.get("ControlPID"))
          && "".equals(v.get("Job")) && "failed".equals(v.get("ActiveState"))
          && "failed".equals(v.get("SubState")) && "exit-code".equals(v.get("Result")));
  }
  static void signed() throws Exception {
    var a=Pg387TrustedDeployment.verify();
    require(a.version().equals("0.1.0-PG425") && a.manifestSha256().equals(MANIFEST)
        && Arrays.equals(a.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
        && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
  }
  static Map<String,byte[]> startup() throws Exception {
    var names=new HashSet<>(Pg425KnownApiRecovery.NAMES);names.remove(Pg425KnownApiRecovery.EPOCH+".API.start.intent");names.remove("permit-start.intent");
    try(var files=Files.list(Pg410KnownAuthRecovery.STARTUP)) {
      require(files.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet()).equals(names));
    }
    var map=new TreeMap<String,byte[]>();
    for(String name:names)map.put(name,Pg410KnownAuthRecovery.material(Pg410KnownAuthRecovery.STARTUP.resolve(name),1024));
    return map;
  }
  static void physical() throws Exception {
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT)
        && Files.readSymbolicLink(Path.of("/proc/1/exe")).toString().equals("/usr/lib/systemd/systemd")
        && !Files.exists(Path.of("/proc/1361114"),LinkOption.NOFOLLOW_LINKS)
        && !Files.exists(Path.of("/proc/1359256"),LinkOption.NOFOLLOW_LINKS));
    Pg387TrustedDeployment.terminalAll();
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-expiry-cleanup.service"));
  }
  static void timersInactive() throws Exception {
    for(String unit:List.of("apt-daily.timer","apt-daily-upgrade.timer","apt-daily.service","apt-daily-upgrade.service")) {
      byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",unit,"--property=ActiveState,MainPID,Job");
      String s=new String(raw,StandardCharsets.US_ASCII);
      require(s.contains("ActiveState=inactive\n") && s.contains("Job=\n"));
      if(unit.endsWith(".service"))require(s.contains("MainPID=0\n"));
    }
  }
  static byte[] properties(Map<String,String> values) {
    var out=new StringBuilder();new TreeMap<>(values).forEach((k,v)->out.append(k).append('=').append(v).append('\n'));
    return out.toString().getBytes(StandardCharsets.US_ASCII);
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG426_ENVIRONMENT_REFUSED diagnosticsRedacted=true type="+e.getClass().getName());
      for(var f:e.getStackTrace())if(f.getClassName().equals("Pg426EnvironmentRecovery"))
        System.err.println("PG426_FRAME "+f.getMethodName()+":"+f.getLineNumber());
    });
    require(args.length==0 && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    Pg387TrustedDeployment.LABEL="PG425";Pg387TrustedDeployment.STEM="pg425";
    Pg387TrustedDeployment.SOURCE="a3c86daf3ea1ac7ea9f6a3ae50dc45ead68c3fd2";
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG425");
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      byte[] raw=pin("full18.properties","4e9e3835b34c4afccd9100b4e0f7afd5b18770e5f3f1445e0fd35f06e767caf2");
      byte[] sql=pin("db-final.log","f0663f67b63abb09739f61a12b9e08ba2a71332a588e061bee3923dc27c681f8");
      var blocks=new String(raw,StandardCharsets.US_ASCII).stripTrailing().split("\n\n");require(blocks.length==3);
      var m=Pg410KnownAuthRecovery.parsed((blocks[0]+"\n").getBytes(StandardCharsets.US_ASCII),InspectorUnitSnapshot.Target.MORNING);
      var e=Pg410KnownAuthRecovery.parsed((blocks[1]+"\n").getBytes(StandardCharsets.US_ASCII),InspectorUnitSnapshot.Target.EXPIRY);
      require(known(m.values(),e.values()) && m.values().equals(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values())
          && e.values().equals(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.EXPIRY).values()));
      require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));Files.createDirectory(SAVE,
          java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
      save("full18.properties",raw);save("db-final.log",sql);
      save("timer-before.properties",Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",
          "apt-daily.timer","apt-daily-upgrade.timer","--property=Id,ActiveState,UnitFileState,NextElapseUSecRealtime"));
      Pg387TrustedDeployment.sync(SAVE);Pg387TrustedDeployment.sync(SAVE.getParent());
      // Runtime stop only; installed enablement/mask/configuration remains unchanged.
      Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","stop","apt-daily.timer","apt-daily-upgrade.timer");
      timersInactive();Pg387TrustedDeployment.stopAll();
      return StartupAdmissionFile.create().tryExclusive(fd->Pg387TrustedDeployment.checked(()-> {
        physical();signed();timersInactive();
        try(var db=Pg407FailedRootRecovery.openDatabase();
            var current=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg410KnownAuthRecovery.STARTUP);
            var requestsRoot=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),REQUEST)) {
          db.setAutoCommit(false);
          try(var s=db.createStatement();var r=s.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
            require(r.next() && Boolean.TRUE.equals(r.getObject(1,Boolean.class)) && !r.next());
          }
          var epoch=new StartupPermitFiles(current,LinuxInodeSecurity.create()).current();
          require(epoch.state()==StartupPermitRecords.State.INVALID && epoch.boot().toString().equals(BOOT)
              && epoch.epoch().toString().equals(EPOCH) && epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
              && epoch.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION));
          var original=MaintenanceRunFiles.create().execute(s->s.observe(epoch.activation()));
          require(original.equals(epoch.activation()) && new RunReferenceRepository(db).read(original.run()).identityConsistent());
          var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==222);
          require(Arrays.equals(sql,Pg425KnownApiRecovery.command(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII),
              "/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-")));
          var backup=Pg407FailedRootRecovery.backupSnapshot();var namespace=startup();var fixture=Pg425KnownApiRecovery.fixtureSnapshot();
          try(var names=Files.list(REQUEST)) {
            require(names.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toSet()).equals(Set.of("expiry-request","maintenance-owner")));
          }
          var security=LinuxInodeSecurity.create();var requests=CleanupWorkerRequestFiles.forExpiry(requestsRoot,security);
          var owners=CleanupWorkerRequestFiles.forOwner(requestsRoot,security,CleanupWorkerRequestFiles.OwnerSource.PARENT);
          var owner=owners.readOwner();var request=requests.readExpiry();
          require(owner.boot().toString().equals(BOOT) && owner.epoch().toString().equals(EPOCH)
              && owner.run().equals(original.run().id()) && owner.activation().equals(original.id())
              && owner.morning().invocation().equals(MORNING) && owner.morning().pid()==1361114
              && owner.morning().startTicks()==20473022 && owner.cleanup().isEmpty()
              && owner.deadlineNanos()==206530222079000L);
          require(Pg410KnownAuthRecovery.hash(owner.encode()).equals("7346d5225fb557d2c14d025dd5cfd8cdf0838edcaeacf6d06660d6f965e1b719")
              && Pg410KnownAuthRecovery.hash(request.encode()).equals("fec758df85686ae22d1c35e81c1727b60e2deb61ee1adef1294028b3911369c5")
              && request.encode().length==443 && request.stepId()==222 && request.attempt()==17
              && request.boot().equals(epoch.boot()) && request.epoch().equals(epoch.epoch())
              && request.run().equals(original.run().id()) && request.activation().equals(original.id()));
          save("owner.before",owner.encode());save("request.before",request.encode());
          for(var item:namespace.entrySet())save(item.getKey(),item.getValue());
          save("fixture.before",fixture.getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);
          physical();signed();timersInactive();
          require(known(m.values(),e.values()) && Pg410KnownAuthRecovery.stoppedAfter(m.values(),Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values())
              && Pg410KnownAuthRecovery.stoppedAfter(e.values(),Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.EXPIRY).values()));
          requests.retireExpiry(request);owners.retireOwner(owner);
          physical();require(rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && backup.equals(Pg407FailedRootRecovery.backupSnapshot())
              && fixture.equals(Pg425KnownApiRecovery.fixtureSnapshot()));
          for(var item:namespace.entrySet())require(Arrays.equals(item.getValue(),Pg410KnownAuthRecovery.material(Pg410KnownAuthRecovery.STARTUP.resolve(item.getKey()),1024)));
          require(original.equals(MaintenanceRunFiles.create().execute(s->s.observe(original)))
              && new RunReferenceRepository(db).read(original.run()).identityConsistent());
          try(var names=Files.list(REQUEST)){require(names.findAny().isEmpty());}
          save("expiry-before-reset.properties",properties(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.EXPIRY).values()));
          Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","reset-failed","schubert-nk-expiry-cleanup.service");
          var reset=Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.EXPIRY);
          require(reset.snapshot().quiescent() && "inactive".equals(reset.values().get("ActiveState")));
          save("expiry-after-reset.properties",properties(reset.values()));
          physical();timersInactive();signed();
          require(rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && backup.equals(Pg407FailedRootRecovery.backupSnapshot()));
          Pg387TrustedDeployment.sync(SAVE);db.rollback();
        }
        System.out.println("PG426_ENVIRONMENT_RECOVERED all222AndBackupUnchanged=true ownedUndeliveredRequestRetired=true runtimeTimersPaused=true old243Preserved=true workerSuccessClaimed=false permitIssued=false");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
