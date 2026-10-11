import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC263/N11/PT-OPS-ROLE1372001: only one missing Bootstrap role, no Unit/business actions. */
public final class Pg1372BootstrapRolePreparation {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg1372-bootstrap-role-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg1372-bootstrap-role-prepare-v1");
  static String phase="ARGUMENTS";
  static Pg797OwnedDatabase lease;
  static boolean lossReported;
  static long lastPulse;
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed Bootstrap role unavailable");}
  static boolean arguments(String[] args){return args!=null&&args.length==1&&"prepare".equals(args[0]);}
  static void pulse()throws Exception{
    if(lease==null)return;
    long now=System.nanoTime();if(lastPulse!=0&&now-lastPulse>=TimeUnit.SECONDS.toNanos(30))throw new java.sql.SQLException("owned observer interval exceeded");
    lease.verify();lastPulse=now;
  }
  static void retain(Throwable failure){
    System.err.println("PG1372_ROLE_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldNormalClose=false");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg1372BootstrapRolePreparation"))System.err.println("PG1372_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;){if(lease!=null&&!lossReported)try{pulse();}catch(Exception|Error lost){lossReported=true;System.err.println("PG1372_DB_NOT_CONFIRMED");}try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;
    References(int backend)throws Exception{
      Path log=SAVE.resolve("refs.private.log");Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg1372_bootstrap_role_refs.py").toString(),"prepare",Integer.toString(backend)).redirectError(log.toFile()).start();input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){pulse();while(input.available()>0){int v=input.read();if(v<0||bytes.size()==64)throw new IOException("reference unavailable");bytes.write(v);
        if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS)&&input.available()==0)throw new IOException("reference unavailable");}
      throw new IOException("reference deadline");
    }
    void check(String point)throws Exception{require(Set.of("before","prepared","closed").contains(point));output.write((point+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");}
    void release()throws Exception{output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");require(child.waitFor(5,TimeUnit.SECONDS)&&child.exitValue()==0);output.close();input.close();child.getErrorStream().close();}
  }
  static java.sql.Connection open()throws Exception{
    var database=Pg407FailedRootRecovery.openDatabase();
    try{database.setReadOnly(true);database.setAutoCommit(false);
      try(var q=database.createStatement();var r=q.executeQuery("select set_config('application_name','PG998-bootstrap-role',false),pg_try_advisory_lock(71419602)")){require(r.next()&&r.getBoolean(2)&&!r.next());}
      int backend;try(var q=database.createStatement();var r=q.executeQuery("select pg_backend_pid()")){require(r.next());backend=r.getInt(1);require(!r.next());}
      lease=new Pg797OwnedDatabase(database,new Pg797OwnedDatabase.Expected(backend,"schubert_batch","PG998-bootstrap-role","schubert_nk",true,true));lastPulse=0;pulse();return database;
    }catch(Exception|Error failure){retain(failure);throw failure;}
  }
  static void signedOriginal()throws Exception{
    Pg387TrustedDeployment.LABEL="PG1292";Pg387TrustedDeployment.STEM="pg1292";Pg387TrustedDeployment.SOURCE="769ddb15cd735c25fef581b5f9850ef9d0053c0f";Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG1292");Pg387TrustedDeployment.expectedSqlCount=28;
    var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals("ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99")&&Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("cbca8738-3b24-4090-b77c-bf029677cdd6"));
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))){
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
      require(epoch.state()==StartupPermitRecords.State.ISSUED&&epoch.boot().toString().equals("cbca8738-3b24-4090-b77c-bf029677cdd6")&&epoch.activation().run().id().toString().equals("d2e3a86f-27a4-4c2a-be21-b512eebf1216")&&epoch.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-10T23:30:23.481632Z"))&&epoch.activation().id().toString().equals("841b507c-2713-4ffe-8882-68f5fb3f87f5"));
      var done=MaintenanceRunFiles.create().execute(x->x.observeStartup(epoch.activation())).completed().orElseThrow();require(done.outcome()==MaintenanceCompletion.Outcome.SUCCESS&&done.endedAt().equals(java.time.Instant.parse("2026-10-10T23:54:39.918039Z")));
      require(epoch.equals(files.current()));
    }
  }
  static void work()throws Exception{
    phase="SIGNED_ORIGINAL";signedOriginal();Pg428ColdBootPreparation.newDirectory(SAVE,0,0);
    try{
      References refs;
      phase="READONLY_DATABASE";
      try(var database=open()){
        int backend;try(var q=database.createStatement();var r=q.executeQuery("select pg_backend_pid()")){require(r.next());backend=r.getInt(1);require(!r.next());}
        phase="TEN_REFS";refs=new References(backend);refs.check("before");
        var identity=new FixedServiceIdentity().resolve(ServiceConfigFiles.Service.API);require(identity.uid()==999&&identity.gid()==981);
        phase="HELD_ONE_ROLE";
        try(var common=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/pt-coverage"))){Pg1370BootstrapRoleDirectory.prepare(common,"ordinary-bootstrap196",999,981);}
        phase="PREPARED_CHECK";refs.check("prepared");signedOriginal();database.rollback();phase="DATABASE_CLOSE";
      }
      lease.confirmClosed();lease=null;lastPulse=0;refs.check("closed");phase="REF_CLOSE";refs.release();phase="ALL_INNER_NORMAL";
    }catch(Exception|Error failure){retain(failure);throw failure;}
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args)&&!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{try{work();phase="A_CLOSE";return Boolean.TRUE;}catch(Exception|Error failure){retain(failure);throw failure;}})).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"oneBootstrapRolePrepared=true\nallNewScopesReturnedNormally=true\nallOriginalValuesPreserved=true\nstartsStopsReloadsSqlWrites0=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG1372_ROLE_COMPLETE normalScopes=true oneNewRole=true businessActions0=true");
  }
}
