import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC198 separate fixed runtime preparation only. No service start/DB mutation. */
public final class Pg519RuntimeRetirement {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg519-retirement-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg519-runtime-retirement-v1");
  static String phase="PREFLIGHT";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed runtime resume refused");}
  static void retain(Throwable failure){
    System.err.println("PG519_RUNTIME_RETIRE_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" currentScopeMustBeReauthenticated=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg519RuntimeRetirement"))System.err.println("PG519_RUNTIME_RETIRE_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;final java.sql.Connection database;final int backend;
    References(int pid,java.sql.Connection db)throws Exception{
      database=Objects.requireNonNull(db);backend=pid;
      Path log=SAVE.resolve("refs-prepare.private.log");Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg519_runtime_retirement_refs.py").toString(),"retire",Integer.toString(pid)).redirectError(log.toFile()).start();input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){while(input.available()>0){int v=input.read();if(v<0 || bytes.size()==64)throw new IOException("reference unavailable");bytes.write(v);
        if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference unavailable");}
      throw new IOException("reference unavailable");
    }
    void check(String name)throws Exception{
      require(Set.of("before","removed").contains(name));
      try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted)")){
        require(r.next() && r.getInt(1)==backend && r.getBoolean(2) && !r.next());}
      output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");
    }
    void release()throws Exception{output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();}
  }
  public static void main(String[] args)throws Exception{
    require(args.length==1 && "retire".equals(args[0]) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_CURRENT";Pg464CodeOnlyDeployment.configure("PG495","a2e98ce9e96c42425921e3686e8ae7a94bff9e6c",Path.of("/opt/schubert-nk/releases/0.1.0-PG495"));Pg387TrustedDeployment.expectedSqlCount=28;var approval=Pg387TrustedDeployment.verify();
          require(approval.manifestSha256().equals("f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44") && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
          Pg428ColdBootPreparation.newDirectory(SAVE,0,0);
          var db=Pg407FailedRootRecovery.openDatabase();
          try{db.setReadOnly(true);db.setAutoCommit(false);int pid;
            try(var s=db.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG519-runtime-retirement',false),pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
            phase="REFERENCE_SCOPE";var refs=new References(pid,db);
            try{refs.check("before");phase="FIXED_RUNTIME_RETIREMENT";
              try(var runtime=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/systemd/system/schubert-nk-morning-controller.service.d"))){
                byte[] expected=Files.readAllBytes(SAVE.resolve("runtime-before.private"));
                runtime.atExistingEntryHandle("pg492-once-resume.conf",held->{require(Arrays.equals(expected,Files.readAllBytes(held)));return Boolean.TRUE;});
                refs.check("before");runtime.unlinkEntry("pg492-once-resume.conf");
                require(!Files.exists(Path.of("/run/systemd/system/schubert-nk-morning-controller.service.d/pg492-once-resume.conf"),LinkOption.NOFOLLOW_LINKS));
                Pg387TrustedDeployment.sync(Path.of("/run/systemd/system/schubert-nk-morning-controller.service.d"));
                Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","daemon-reload");refs.check("removed");
              }
              phase="DB_CLOSE";db.rollback();db.close();phase="REF_CLOSE";refs.release();}
            catch(Exception|Error failure){retain(failure);throw failure;}
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"onceResumeRetired=true\nallNewScopesReturnedNormally=true\noriginalPendingUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG519_RUNTIME_RETIRED allNewScopesReturnedNormally=true starts0=true databaseUpdates0=true");
  }
}
