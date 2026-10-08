import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC228 distinct one-use e492 resume preparation; no start or DB/epoch/original mutation. */
public final class Pg635ResumePreparation {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg635-resume-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg635-resume-preparation-v1");
  static final String mode="prepare";
  static final String SOURCE="36fe7a0b938489d61d17d49c1c30a6fbbef699d5";
  static final String DIGEST="57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe";
  static String phase="PREFLIGHT";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed fresh resume preparation refused");}
  static boolean arguments(String[] a){return a!=null && a.length==1 && "prepare".equals(a[0]);}
  static void retain(Throwable failure){
    System.err.println("PG635_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg635ResumePreparation"))System.err.println("PG635_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;final java.sql.Connection database;final int backend;
    References(int pid,java.sql.Connection db)throws Exception{
      database=Objects.requireNonNull(db);backend=pid;
      Path log=SAVE.resolve("refs-prepare.private.log");
      Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg635_resume_refs.py").toString(),mode,Integer.toString(pid)).redirectError(log.toFile()).start();
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
    void check(String name)throws Exception{
      require(Set.of("before","prepare").contains(name));
      try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted)")){
        require(r.next() && r.getInt(1)==backend && r.getBoolean(2) && !r.next());}
      output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");Pg633PendingDeployment.original();
    }
    void release()throws Exception{
      output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");
      require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();
    }
  }

  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(Files.isRegularFile(TOOLS.resolve("pg635_resume_refs.py"),LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_CURRENT";
          Pg464CodeOnlyDeployment.configure("PG631",SOURCE,Path.of("/opt/schubert-nk/releases/0.1.0-PG631"));Pg387TrustedDeployment.expectedSqlCount=28;
          var prior=Pg387TrustedDeployment.verify();
          require(prior.manifestSha256().equals(DIGEST) && Arrays.equals(prior.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
          require(Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Path.of("/opt/schubert-nk/releases/0.1.0-PG631")));
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(prior);Pg633PendingDeployment.original();
          Pg428ColdBootPreparation.newDirectory(SAVE,0,0);
          var database=Pg407FailedRootRecovery.openDatabase();
          try{
            database.setReadOnly(true);database.setAutoCommit(false);int pid;
            try(var q=database.createStatement();var row=q.executeQuery("select pg_backend_pid(),set_config('application_name','PG635-fixed-resume',false),pg_try_advisory_lock(71419602)")){
              require(row.next() && row.getBoolean(3));pid=row.getInt(1);require(!row.next());
            }
            phase="REFERENCE_SCOPE";var held=new References(pid,database);
            try{
              held.check("before");phase="FIXED_RUNTIME_PREPARATION";held.check("prepare");
              phase="DATABASE_CLOSE";database.rollback();database.close();phase="REFERENCE_CLOSE";held.release();
            }catch(Exception|Error failure){retain(failure);throw failure;}
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";Pg633PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"onceResumePrepared=true\nallNewScopesReturnedNormally=true\noriginalRunCutoffUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG635_RESUME_PREPARED allNewScopesReturnedNormally=true starts0=true databaseUpdates0=true");
  }
}
