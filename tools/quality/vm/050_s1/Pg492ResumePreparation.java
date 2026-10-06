import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC198 separate fixed runtime preparation only. No service start/DB mutation. */
public final class Pg492ResumePreparation {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg492-resume-tools-v3");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg492-resume-preparation-v3");
  static String phase="PREFLIGHT";
  static String SOURCE,DIGEST;
  static boolean arguments(String[] a){return a!=null && a.length==2 && a[0]!=null && a[1]!=null && a[0].matches("[0-9a-f]{40}") && a[1].matches("[0-9a-f]{64}");}
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed runtime resume refused");}
  static void retain(Throwable failure){
    System.err.println("PG492_RESUME_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg492ResumePreparation"))System.err.println("PG492_RESUME_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;final java.sql.Connection database;final int backend;
    References(int pid,java.sql.Connection db)throws Exception{
      database=Objects.requireNonNull(db);backend=pid;
      Path log=TOOLS.resolve("refs-prepare.private.log");Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg492_resume_refs.py").toString(),Integer.toString(pid),SOURCE,DIGEST).redirectError(log.toFile()).start();input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){while(input.available()>0){int v=input.read();if(v<0 || bytes.size()==64)throw new IOException("reference unavailable");bytes.write(v);
        if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference unavailable");}
      throw new IOException("reference unavailable");
    }
    void check(String name)throws Exception{
      require(Set.of("before","prepare").contains(name));
      try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted)")){
        require(r.next() && r.getInt(1)==backend && r.getBoolean(2) && !r.next());}
      output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");Pg491PendingDeployment.original();
    }
    void release()throws Exception{output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();}
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));SOURCE=args[0];DIGEST=args[1];
    require(Files.isRegularFile(TOOLS.resolve("pg492_resume_refs.py"),LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_CURRENT";Pg387TrustedDeployment.LABEL="PG489";Pg387TrustedDeployment.STEM="pg489";Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG489");Pg387TrustedDeployment.expectedSqlCount=28;var approval=Pg387TrustedDeployment.verify();
          require(approval.manifestSha256().equals(DIGEST) && approval.manifestSha256().equals("652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c") && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);Pg491PendingDeployment.original();
          var db=Pg407FailedRootRecovery.openDatabase();
          try{db.setReadOnly(true);db.setAutoCommit(false);int pid;
            try(var s=db.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG492-fixed-resume',false),pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
            phase="REFERENCE_SCOPE";var refs=new References(pid,db);
            try{refs.check("before");phase="FIXED_RUNTIME_PREPARATION";refs.check("prepare");phase="DB_CLOSE";db.rollback();db.close();phase="REF_CLOSE";refs.release();}
            catch(Exception|Error failure){retain(failure);throw failure;}
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";Pg491PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"onceResumePrepared=true\nallNewScopesReturnedNormally=true\noriginalRunCutoffUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG492_RESUME_PREPARED allNewScopesReturnedNormally=true starts0=true databaseUpdates0=true");
  }
}
