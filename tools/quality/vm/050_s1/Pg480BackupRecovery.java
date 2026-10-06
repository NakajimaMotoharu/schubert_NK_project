import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC198/BREC198009: isolated fixed Backup recovery, not generic admission or deployment. */
public final class Pg480BackupRecovery {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg480-backup-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg480-backup-recovery");
  static final Path REQUEST=Path.of("/run/schubert-nk/backup-request");
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static String phase="PREFLIGHT";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed Backup recovery refused");}
  static boolean arguments(String[] a){return a!=null && a.length==1 && a[0]!=null && Set.of("verify","retire").contains(a[0]);}
  static boolean pending(StartupPermitRecords.Epoch e){
    return e!=null && e.state()==StartupPermitRecords.State.INVALID && e.permitDigest().isEmpty()
        && e.boot().toString().equals(BOOT)
        && e.activation().run().id().toString().equals("49437eda-1681-43a9-883a-424eb55a6166")
        && e.activation().run().cutoff().equals(Instant.parse("2026-10-06T06:28:43.734078Z"));
  }
  static void retain(){System.err.println("PG480_UNKNOWN phase="+phase+" ownershipRetained=true oldCloseNotInferred=true");for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}
  static void signature()throws Exception{
    Pg464CodeOnlyDeployment.configure("PG477","cce61f63900b1479f9f8dbdc338e222b1c8c38a3",Path.of("/opt/schubert-nk/releases/0.1.0-PG477"));
    var approval=Pg387TrustedDeployment.verify();
    require(approval.manifestSha256().equals("613b71a06c2b215887219cd3502d3db34542fea957e0d88dbb9c54c8bab18667")
        && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
    Pg464CodeOnlyDeployment.configure("PG479","bab704707b8fd7e0dc7581c4489f0892236efe73",Path.of("/opt/schubert-nk/releases/0.1.0-PG479"));
    var candidate=Pg387TrustedDeployment.verify();
    require(candidate.manifestSha256().equals("a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286"));
    for(String name:List.of("systemd","db/migration","config"))try(var paths=Files.walk(Path.of("/opt/schubert-nk/releases/0.1.0-PG477",name))){
      for(Path p:paths.filter(Files::isRegularFile).toList())require(Arrays.equals(Files.readAllBytes(p),Files.readAllBytes(Path.of("/opt/schubert-nk/releases/0.1.0-PG479").resolve(Path.of("/opt/schubert-nk/releases/0.1.0-PG477").relativize(p)))));
    }
  }
  static void original()throws Exception{
    var e=StartupPermitRecords.readEpoch(Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));require(pending(e));
    require(e.activation().equals(MaintenanceRunFiles.create().execute(s->s.observe(e.activation()))));
  }
  static void quarantineGuard()throws IOException{
    try{
      require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));original();
      var expected=com.google.gson.JsonParser.parseString(Files.readString(SAVE.resolve("before.private.json"))).getAsJsonObject().getAsJsonObject("units");
      for(var entry:expected.entrySet()){
        String unit=entry.getKey();require(Set.of("caddy.service","schubert-nk-web.service","schubert-nk-api.service","schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service","schubert-nk-expiry-cleanup.service","schubert-nk-backup.service","artemis.service","schubert-nk-morning-controller.service","schubert-nk-bootstrap-admin.service").contains(unit));
        var props=entry.getValue().getAsJsonObject();String fields=String.join(",",props.keySet());
        var p=new ProcessBuilder("/usr/bin/systemctl","show",unit,"--property="+fields).redirectError(ProcessBuilder.Redirect.DISCARD).start();
        p.getOutputStream().close();byte[] raw=p.getInputStream().readNBytes(65537);
        require(p.waitFor(5,TimeUnit.SECONDS) && p.exitValue()==0 && raw.length<=65536);p.getInputStream().close();p.getErrorStream().close();
        var got=new HashMap<String,String>();for(String row:new String(raw,StandardCharsets.UTF_8).split("\n")){int split=row.indexOf('=');require(split>0 && got.put(row.substring(0,split),row.substring(split+1))==null);}
        require(got.keySet().equals(props.keySet()));for(var v:got.entrySet())require(v.getValue().equals(props.get(v.getKey()).getAsString()));
        Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit));
      }
    }catch(Exception failure){throw new IOException("fixed quarantine proof unavailable",failure);}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;
    References(String mode,int pid)throws Exception{
      Path log=TOOLS.resolve("refs-"+mode+".private.log");
      Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg480_backup_refs.py").toString(),mode,Integer.toString(pid)).redirectError(log.toFile()).start();
      input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){
        while(input.available()>0){int v=input.read();if(v<0 || bytes.size()==64)throw new IOException("reference unavailable");bytes.write(v);
          if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference unavailable");
      }throw new IOException("reference unavailable");
    }
    void check(BackupInterruptedStartRecovery.Phase value)throws IOException{
      try{output.write((value.name()+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");original();}
      catch(Exception failure){throw new IOException("continuous recovery proof refused",failure);}
    }
    void release()throws Exception{output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");
      require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();}
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));
    boolean retire=args[0].equals("retire");
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{var result=StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_ORIGINAL";signature();original();
          var db=Pg407FailedRootRecovery.openDatabase();
          try{
            db.setReadOnly(true);db.setAutoCommit(false);int pid;
            try(var s=db.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG480-fixed-recovery',false),pg_try_advisory_lock(71419602)")){
              require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
            phase="REFERENCE_SCOPE";var refs=new References(args[0],pid);
            try{
              phase="BORROWED_ROOT";var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),REQUEST);
              boolean touched=false;
              try{
                refs.check(BackupInterruptedStartRecovery.Phase.OBSERVING);
                if(retire){phase="TYPED_RETIRE";touched=true;BackupInterruptedStartRecovery.retire(root,LinuxInodeSecurity.create(),refs::check);}
                else refs.check(BackupInterruptedStartRecovery.Phase.BEFORE_RETIRE);
                phase="ROOT_SCOPE_CLOSE";root.close();
                phase="DATABASE_SCOPE_CLOSE";db.rollback();db.close();
                phase="REFERENCE_SCOPE_CLOSE";refs.release();
              }catch(Exception|Error failure){
                if(touched){try{var recoveryRoot=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),REQUEST);
                  // Quarantine is fail-closed only; unresolved later closure never becomes acceptance.
                  BackupInterruptedStartRecovery.quarantine(recoveryRoot,LinuxInodeSecurity.create(),p->quarantineGuard());
                  recoveryRoot.close();}catch(Exception|Error secondary){if(secondary!=failure)failure.addSuppressed(secondary);}}
                retain();throw failure;
              }
            }catch(Exception|Error failure){retain();throw failure;}
          }catch(Exception|Error failure){retain();throw failure;}
          phase="A_SCOPE_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain();throw failure;}
      })).orElseThrow();phase="M_SCOPE_CLOSE";return result;}catch(Exception|Error failure){retain();throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";Path done=SAVE.resolve("complete.private");
    try(var f=FileChannel.open(done,Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE),java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")))){
      var bytes=java.nio.ByteBuffer.wrap(("typedBackupMarkerRetired="+retire+"\nallNewScopesReturnedNormally=true\noldCloseNotInferred=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n").getBytes(StandardCharsets.US_ASCII));while(bytes.hasRemaining())f.write(bytes);f.force(true);}
    Pg387TrustedDeployment.sync(SAVE);System.out.println("PG480_ACCEPTED typedRetire="+retire+" allNewScopesReturnedNormally=true databaseUpdates0=true starts0=true");
  }
}
