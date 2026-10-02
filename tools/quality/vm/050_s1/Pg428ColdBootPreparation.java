import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;

/** SSC165/BUG527: one saved PG/PT instance's new cold boot, not failed-intent retirement.
 * Old9024 evidence remains private; no old current/receipt/intent is restored or inferred.
 * No worker, migration, fresh run, completion or runtime permit is issued here.
 */
public final class Pg428ColdBootPreparation {
  static final String BOOT="58006280-5301-4a1b-a0c2-66bce4a8a38e";
  static final String PRIOR_BOOT="9024b59c-41d0-4dbd-8a3e-96bfad1467c0";
  static final String SOURCE="a3c86daf3ea1ac7ea9f6a3ae50dc45ead68c3fd2";
  static final String SQL_HASH="75601476d31a4925f55ec2dad9a45fc7bf6ed7f45b86fde0424e575f192c7fe9";
  static final Path RUN=Path.of("/run/schubert-nk"), SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg428-cold-boot-v5");
  static void require(boolean value) {if(!value)throw new IllegalStateException("cold boot preparation unavailable");}
  static boolean cold(Map<String,String> f) {
    return f!=null && f.keySet().equals(Pg410KnownAuthRecovery.FIELDS) && "loaded".equals(f.get("LoadState"))
        && "inactive".equals(f.get("ActiveState")) && "dead".equals(f.get("SubState"))
        && "0".equals(f.get("MainPID")) && "0".equals(f.get("ControlPID"))
        && "".equals(f.get("Job")) && "".equals(f.get("InvocationID"));
  }
  static boolean newBoot(String actual) {return BOOT.equals(actual) && !PRIOR_BOOT.equals(actual);}
  static void physical() throws Exception {
    require(newBoot(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim()));
    Pg387TrustedDeployment.terminalAll();
    for(var unit:MaintenanceUnit.values())
      Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit.serviceName()));
    var m=Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING);
    require(cold(m.values()));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    require(m.values().equals(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values()));
  }
  static Map<String,Object> metadata(Path p) throws Exception {
    return Map.copyOf(Files.readAttributes(p,"unix:uid,gid,mode,nlink,dev,ino,ctime,lastModifiedTime,size",LinkOption.NOFOLLOW_LINKS));
  }
  static Map<String,String> original() throws Exception {
    return snapshot(Path.of("/var/lib/schubert-nk/maintenance"));
  }
  static Map<String,String> snapshot(Path root) throws Exception {
    var result=new TreeMap<String,String>();
    try(var paths=Files.walk(root)) {
      for(var p:paths.sorted().toList()) {
        var a=metadata(p);require(!Files.isSymbolicLink(p));
        var value=new TreeMap<>(a).toString();
        if(Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)) {
          require((Long)a.get("size")<=1048576);
          value += "/"+Pg410KnownAuthRecovery.hash(Files.readAllBytes(p));
        }
        require(a.equals(metadata(p)));result.put(p.toString(),value);
      }
    }
    return Map.copyOf(result);
  }
  static String fixtureSnapshot() throws Exception {
    var result=new TreeMap<String,Object>();
    for(var entry:Map.of("/srv/schubert-nk/data/assets/audio/pgpt-fixture.wav","114448ce435018eda5f4a8df39689d79fb4ff3dbfb5cc521002a42e8a6f625bb",
        "/srv/schubert-nk/data/assets/manifests/master.sha256","44f2bff22f62d9f4ae4c49bcc554e9a189427e7fe6f2bd3b24604bfdd4141bbc",
        "/etc/schubert-nk/api.yml","40573510ed295f9e7b343f832624cda63f2383fa87e59b2bddeb651e7717c6bc").entrySet()) {
      var p=Path.of(entry.getKey());var a=metadata(p);var digest=Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(p,65536));
      require(entry.getValue().equals(digest) && a.equals(metadata(p)));result.put(entry.getKey(),a.toString()+"/"+digest);
    }
    var common=Path.of("/etc/schubert-nk/common.yml");result.put(common.toString(),metadata(common).toString()+"/"+Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(common,65536)));
    result.put("assets",snapshot(Path.of("/srv/schubert-nk/data/assets")));
    result.put("transfer",snapshot(Path.of("/srv/schubert-nk/data/transfer")));
    return result.toString();
  }
  static void newDirectory(Path path,int uid,int gid) throws Exception {
    require(!Files.exists(path,LinkOption.NOFOLLOW_LINKS));
    Files.createDirectory(path,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    Files.setAttribute(path,"unix:uid",uid,LinkOption.NOFOLLOW_LINKS);
    Files.setAttribute(path,"unix:gid",gid,LinkOption.NOFOLLOW_LINKS);
    var a=metadata(path);
    require(Integer.valueOf(uid).equals(a.get("uid")) && Integer.valueOf(gid).equals(a.get("gid")) && Integer.valueOf(0040700).equals(a.get("mode")));
    Pg387TrustedDeployment.sync(path.getParent());
  }
  static void save(String name,byte[] bytes) throws Exception {
    var p=SAVE.resolve(name);Files.write(p,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,PosixFilePermissions.fromString("r--------"));
    try(var f=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){f.force(true);}
    require(Arrays.equals(bytes,Files.readAllBytes(p)));
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG428_COLD_BOOT_REFUSED type="+e.getClass().getName()+" diagnosticsRedacted=true");
      for(var f:e.getStackTrace())if(f.getClassName().equals("Pg428ColdBootPreparation"))System.err.println("PG428 FRAME "+f.getMethodName()+":"+f.getLineNumber());
    });
    require(args.length==0 && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    require(Files.readString(Path.of("/proc/self/status")).contains("Uid:\t0\t0\t0\t0\n"));
    require(newBoot(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim()));
    require(cold(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values()));
    for(String n:List.of("startup","backup-request","cleanup-request","expiry-request","pt-coverage"))require(!Files.exists(RUN.resolve(n),LinkOption.NOFOLLOW_LINKS));
    var locks=Map.of("maintenance.lock",metadata(RUN.resolve("maintenance.lock")),"startup-admission.lock",metadata(RUN.resolve("startup-admission.lock")));
    for(var a:locks.values())require(Integer.valueOf(0).equals(a.get("uid")) && Integer.valueOf(0).equals(a.get("gid")) && Integer.valueOf(0100600).equals(a.get("mode")) && Integer.valueOf(1).equals(a.get("nlink")));
    require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    newDirectory(SAVE,0,0);
    require(MaintenanceFileLock.create().tryExclusive(()-> {
      return Pg387TrustedDeployment.checked(()-> {
        Pg387TrustedDeployment.stopAll();
        physical();
        return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
          physical();
          try(var db=Pg407FailedRootRecovery.openDatabase()) {
            db.setAutoCommit(false);
            try(var s=db.createStatement();var r=s.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {require(r.next() && Boolean.TRUE.equals(r.getObject(1,Boolean.class)) && !r.next());}
            var activation=MaintenanceRecords.readActivation(Files.readAllBytes(Path.of("/var/lib/schubert-nk/maintenance/active")));
            require(activation.id().equals(Pg407FailedRootRecovery.ACTIVATION) && activation.run().id().equals(Pg407FailedRootRecovery.RUN)
                && activation.run().cutoff().equals(java.time.Instant.parse("2026-09-27T15:00:00Z")));
            return MaintenanceRunFiles.create().execute(session->Pg387TrustedDeployment.checked(()-> {
              require(session.observe(activation).equals(activation) && new RunReferenceRepository(db).read(activation.run()).identityConsistent());
              var before=original();var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==232);
              byte[] sql=Pg425KnownApiRecovery.command(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-");
              require(SQL_HASH.equals(Pg410KnownAuthRecovery.hash(sql)));
              var backup=Pg407FailedRootRecovery.backupSnapshot();var fixture=fixtureSnapshot();
              save("db232-before.log",sql);save("original-before.properties",before.toString().getBytes(StandardCharsets.UTF_8));
              save("backup-before.properties",backup.toString().getBytes(StandardCharsets.UTF_8));save("fixture-before.properties",fixture.getBytes(StandardCharsets.UTF_8));
              Pg387TrustedDeployment.LABEL="PG425";Pg387TrustedDeployment.STEM="pg425";Pg387TrustedDeployment.SOURCE=SOURCE;
              Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG425");
              Pg387TrustedDeployment.freezeCandidate();
              var approval=Pg387TrustedDeployment.verify();
              require(approval.manifestSha256().equals("55353381ea39d2ddda0c3a195dea05cffda1ad880974693a72095811cd122fd1")
                  && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
                  && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
              physical();require(before.equals(original()) && backup.equals(Pg407FailedRootRecovery.backupSnapshot()) && fixture.equals(fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)));
              for(String n:List.of("startup","backup-request","cleanup-request","expiry-request"))newDirectory(RUN.resolve(n),0,0);
              newDirectory(RUN.resolve("pt-coverage"),0,0);
              for(String n:List.of("parent","cleanup","expiry","root-api"))newDirectory(RUN.resolve("pt-coverage").resolve(n),0,0);
              for(var e:Map.of("backup","schubert-backup","inspector","schubert-inbox-inspector").entrySet()) {
                var p=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-u",e.getValue());
                var g=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-g",e.getValue());
                newDirectory(RUN.resolve("pt-coverage").resolve(e.getKey()),Integer.parseInt(new String(p,StandardCharsets.US_ASCII).trim()),Integer.parseInt(new String(g,StandardCharsets.US_ASCII).trim()));
              }
              // Parent directory traversal only; private per-worker output remains0700.
              Files.setPosixFilePermissions(RUN.resolve("pt-coverage"),PosixFilePermissions.fromString("rwx--x--x"));
              try(var directory=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),RUN.resolve("startup"))) {
                var files=new StartupPermitFiles(directory,LinuxInodeSecurity.create());
                var next=files.invalidate(UUID.fromString(BOOT),UUID.randomUUID(),activation);
                require(next.equals(files.current()) && next.state()==StartupPermitRecords.State.INVALID && next.activation().equals(activation));
                save("new-invalid.properties",Files.readAllBytes(RUN.resolve("startup/epoch.current")));
              }
              physical();require(session.observe(activation).equals(activation) && before.equals(original()) && backup.equals(Pg407FailedRootRecovery.backupSnapshot()) && fixture.equals(fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)));
              for(var e:locks.entrySet())require(e.getValue().equals(metadata(RUN.resolve(e.getKey()))));
              save("db232-after.log",Pg425KnownApiRecovery.command(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-"));
              require(SQL_HASH.equals(Pg410KnownAuthRecovery.hash(Files.readAllBytes(SAVE.resolve("db232-after.log")))));
              Pg387TrustedDeployment.sync(SAVE);db.rollback();
              System.out.println("PG428 COLD_BOOT_PREPARED completed=true oldBootSuccessInferred=false oldIntentRetired=0 original232Preserved=true backupFixturePreserved=true locksSameInode=true freshInvalidOnly=true workersStarted=0 migrationApplied=0");
              return Boolean.TRUE;
            }));
          }
        })).orElseThrow();
      });
    }).orElseThrow());
  }
}
