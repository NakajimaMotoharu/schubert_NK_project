import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** BOOT482001..004: one existing-only dedicated Unit, before/post DB scopes stay separate. */
public final class Pg482BootstrapExisting {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg482-bootstrap-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg482-bootstrap-existing");
  static String phase="PREFLIGHT";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed runtime resume refused");}
  static void retain(Throwable failure){
    System.err.println("PG482_BOOTSTRAP_RETIRE_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg482BootstrapExisting"))System.err.println("PG482_BOOTSTRAP_RETIRE_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;final java.sql.Connection database;final int backend;
    References(int pid,java.sql.Connection db)throws Exception{
      database=Objects.requireNonNull(db);backend=pid;
      Path log=TOOLS.resolve("refs-prepare.private.log");Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg482_bootstrap_existing.py").toString(),"execute",Integer.toString(pid)).redirectError(log.toFile()).start();input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){while(input.available()>0){int v=input.read();if(v<0 || bytes.size()==64)throw new IOException("reference unavailable");bytes.write(v);
        if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference unavailable");}
      throw new IOException("reference unavailable");
    }
    void check(String name)throws Exception{
      require((Set.of("prepare","run").contains(name) || name.matches("retire:[1-9][0-9]*")));
      output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");
    }
    void release()throws Exception{output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();}
  }
  static java.sql.Connection open()throws Exception {
    var database=Pg407FailedRootRecovery.openDatabase();
    try { database.setReadOnly(true);database.setAutoCommit(false);
      try(var q=database.createStatement();var r=q.executeQuery("select set_config('application_name','PG482-bootstrap-guard',false),pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(2) && !r.next());}
      return database;
    }catch(Exception|Error failure){retain(failure);throw failure;}
  }
  static int backend(java.sql.Connection database)throws Exception {
    try(var q=database.createStatement();var r=q.executeQuery("select pg_backend_pid(),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted)")){require(r.next() && r.getBoolean(2));int pid=r.getInt(1);require(!r.next());return pid;}
  }
  public static void main(String[] args)throws Exception{
    require(args.length==1 && "execute".equals(args[0]) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_CURRENT";Pg464CodeOnlyDeployment.configure("PG479","bab704707b8fd7e0dc7581c4489f0892236efe73",Path.of("/opt/schubert-nk/releases/0.1.0-PG479"));var approval=Pg387TrustedDeployment.verify();
          require(approval.manifestSha256().equals("a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286") && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);require(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg481-native-stop-v1/complete.private")).equals("allNewScopesReturnedNormally=true\noldUnknownNormalized=false\n"));
          phase="PREPARE_DATABASE_SCOPE";
          References refs;
          try(var database=open()){
            refs=new References(backend(database),database);refs.check("prepare");database.rollback();phase="PREPARE_DATABASE_SCOPE_CLOSE";
          }
          phase="DEDICATED_EXISTING_UNIT";refs.check("run");
          phase="POST_DATABASE_SCOPE";
          try(var database=open()){
            refs.check("retire:"+backend(database));database.rollback();phase="POST_DATABASE_SCOPE_CLOSE";
          }
          phase="REF_SCOPE_CLOSE";refs.release();
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"newSyntheticSourcesRetired=true\nallNewScopesReturnedNormally=true\nordinaryExistingExit20=true\nall24DatabaseUnchanged=true\noneDedicatedExistingStart=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG482_BOOTSTRAP_RETIRED allNewScopesReturnedNormally=true oneDedicatedExistingStart=true all24DatabaseUnchanged=true");
  }
}
