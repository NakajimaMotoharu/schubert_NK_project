import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SS341343/SSC198 fixed same-cohort owned TERM only. No service start/DB/epoch mutation. */
public final class Pg557NativeStop {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg557-native-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg557-native-stop-v1");
  static String phase="PREFLIGHT";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed completed readback refused");}
  static void retain(Throwable failure){
    System.err.println("PG557_RUNTIME_RESUME_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" currentScopeMustBeReauthenticated=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg557NativeStop"))System.err.println("PG557_RUNTIME_RESUME_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;final java.sql.Connection database;final int backend;
    References(int pid,java.sql.Connection db)throws Exception{
      database=Objects.requireNonNull(db);backend=pid;
      Path log=SAVE.resolve("refs-prepare.private.log");Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg557_native_refs.py").toString(),"stop",Integer.toString(pid)).redirectError(log.toFile()).start();input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(240);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){while(input.available()>0){int v=input.read();if(v<0 || bytes.size()==128)throw new IOException("reference unavailable");bytes.write(v);
        if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference unavailable");}
      throw new IOException("reference unavailable");
    }
    void check(String name)throws Exception{
      require("before".equals(name) || name.startsWith("stop:") || "terminal".equals(name));
      try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted)")){
        require(r.next() && r.getInt(1)==backend && r.getBoolean(2) && !r.next());}
      output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");
    }
    void release()throws Exception{output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();}
  }
  static void verifyOriginal()throws Exception{
    var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
    try{
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
      require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.boot().toString().equals("cc9ed874-7f4f-450e-a188-8de1e42c8441")
        && epoch.activation().run().id().toString().equals("b7e73994-b951-4696-bdd1-cfbc8a10e734")
        && epoch.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-08T04:03:00.714124Z"))
        && epoch.activation().id().toString().equals("12f1af04-180e-405c-8738-853bbd875443"));
      var done=MaintenanceRunFiles.create().execute(x->x.observeStartup(epoch.activation())).completed().orElseThrow();
      require(done.outcome()==MaintenanceCompletion.Outcome.SUCCESS
        && !done.endedAt().isBefore(java.time.Instant.parse("2026-10-08T04:03:00.714124Z"))
        && !done.endedAt().isAfter(epoch.activation().run().cutoff().plusSeconds(1800)));
      try(var entries=Files.list(Path.of("/run/schubert-nk/startup"))){require(entries.noneMatch(p->p.getFileName().toString().endsWith(".start.intent")));}
      require(epoch.equals(files.current()) && done.equals(MaintenanceRunFiles.create().execute(x->x.observeStartup(epoch.activation())).completed().orElseThrow()));
      phase="ORIGINAL_ROOT_CLOSE";root.close();
    }catch(Exception|Error failure){retain(failure);throw failure;}
  }
  public static void main(String[] args)throws Exception{
    require(args!=null && args.length==1 && "stop".equals(args[0]) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_CURRENT";Pg464CodeOnlyDeployment.configure("PG548","969d8ded10c0bf5841d9e3a5c531e922caf4a24a",Path.of("/opt/schubert-nk/releases/0.1.0-PG548"));Pg387TrustedDeployment.expectedSqlCount=28;var approval=Pg387TrustedDeployment.verify();
          require(approval.manifestSha256().equals("a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b") && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
          Pg428ColdBootPreparation.newDirectory(SAVE,0,0);
          var db=Pg407FailedRootRecovery.openDatabase();
          try{db.setReadOnly(true);db.setAutoCommit(false);int pid;
            try(var s=db.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG557-native-stop',false),pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
            phase="REFERENCE_SCOPE";var refs=new References(pid,db);
            try{refs.check("before");phase="COMPLETED_ORIGINAL";verifyOriginal();refs.check("before");
              for(var unit:dev.codex.schubert.nk.batch.platform.MaintenanceUnit.values()){phase="OWNED_STOP_"+unit.name();refs.check("stop:"+unit.serviceName());}
              phase="ALL_TERMINAL";refs.check("terminal");verifyOriginal();
              phase="DB_CLOSE";db.rollback();db.close();phase="REF_CLOSE";refs.release();}
            catch(Exception|Error failure){retain(failure);throw failure;}
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"genuineParentDone=true\nallEightOwnedTerminal=true\nallNewScopesReturnedNormally=true\noriginalBackupStartupRowsPreserved=true\nstarts0=true\noldUnknownNormalized=false\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG557_COMPLETED allNewScopesReturnedNormally=true starts0=true databaseUpdates0=true");
  }
}
