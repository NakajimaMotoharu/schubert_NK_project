import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC198/BREC198010: fixed code-only pending deployment, never generic activation. */
public final class Pg498PendingDeployment {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg498-pending-tools-v2");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg498-pending-codeonly");
  static final Path APPROVAL=Path.of("/etc/schubert-nk/release-approval/current");
  static final Path CURRENT=Path.of("/opt/schubert-nk/current");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG495");
  static String phase="PREFLIGHT";
  static String SOURCE,DIGEST;
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed pending deployment refused");}
  static boolean arguments(String[] a){return a!=null && a.length==2 && a[0]!=null && a[1]!=null && a[0].matches("[0-9a-f]{40}") && a[1].matches("[0-9a-f]{64}");}
  static void retain(Throwable failure){
    System.err.println("PG498_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg498PendingDeployment"))System.err.println("PG498_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static void original()throws Exception{
    var epoch=StartupPermitRecords.readEpoch(Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));
    require(epoch.state()==StartupPermitRecords.State.INVALID && epoch.boot().equals(UUID.fromString(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim())) && epoch.activation().run().id().equals(Pg490PendingMigration.RUN) && epoch.activation().run().cutoff().equals(Pg490PendingMigration.CUTOFF) && epoch.activation().id().equals(Pg490PendingMigration.ACTIVATION));
    var observed=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
    require(observed.activation().equals(epoch.activation()) && observed.completed().isEmpty());
  }
  static void privateWrite(Path name,byte[] data)throws Exception{
    try(var file=FileChannel.open(name,Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE),java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")))){
      var buffer=java.nio.ByteBuffer.wrap(data);while(buffer.hasRemaining())file.write(buffer);file.force(true);
    }
    Pg387TrustedDeployment.sync(name.getParent());
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;final java.sql.Connection database;final int backend;
    References(int pid,java.sql.Connection db)throws Exception{
      database=Objects.requireNonNull(db);backend=pid;
      Path log=TOOLS.resolve("refs-activate.private.log");
      Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg498_pending_refs.py").toString(),Integer.toString(pid),SOURCE,DIGEST).redirectError(log.toFile()).start();
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
      require(Set.of("before","after").contains(name));
      try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted)")){
        require(r.next() && r.getInt(1)==backend && r.getBoolean(2) && !r.next());}
      output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");original();
    }
    void release()throws Exception{
      output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");
      require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();
    }
  }
  static void publish(ReleaseApproval next)throws Exception{
    require(next.version().equals("0.1.0-PG495") && next.manifestSha256().equals("f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44"));
    privateWrite(SAVE.resolve("old-approval.private"),Files.readAllBytes(APPROVAL));
    privateWrite(SAVE.resolve("old-current.private"),Files.readSymbolicLink(CURRENT).toString().getBytes(StandardCharsets.US_ASCII));
    privateWrite(SAVE.resolve("old-epoch.private"),Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));
    Path part=APPROVAL.resolveSibling("pg498-approval.part");
    privateWrite(part,next.encode());Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var file=FileChannel.open(part,StandardOpenOption.READ)){file.force(true);}
    Files.move(part,APPROVAL,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(APPROVAL.getParent());
    Path link=CURRENT.resolveSibling("pg498-current.part");Files.createSymbolicLink(link,NEXT);Pg387TrustedDeployment.sync(link.getParent());
    Files.move(link,CURRENT,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(CURRENT.getParent());
    require(Arrays.equals(next.encode(),Files.readAllBytes(APPROVAL)) && NEXT.equals(Files.readSymbolicLink(CURRENT)));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(next);
    require(Arrays.equals(Files.readAllBytes(SAVE.resolve("old-epoch.private")),Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current"))));
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));SOURCE=args[0];DIGEST=args[1];
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_ORIGINAL";original();var old=ReleaseApproval.parse(Files.readAllBytes(APPROVAL));require(old.version().equals("0.1.0-PG489") && old.manifestSha256().equals("652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c"));StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(old);
          Pg387TrustedDeployment.LABEL="PG495";Pg387TrustedDeployment.STEM="pg495";Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=NEXT;Pg387TrustedDeployment.expectedSqlCount=28;var pin=Pg387TrustedDeployment.material(Path.of("/etc/schubert-nk/deployment-key/pin.der"),44);
          var signature=Pg387TrustedDeployment.material(Path.of("/var/lib/pgpt-s1-preservation/pg495-manifest.sig"),64);
          var manifest=Files.readAllBytes(NEXT.resolve("RELEASE-MANIFEST.json"));
          require(manifest.length>0 && manifest.length<=1048576 && HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(manifest)).equals(DIGEST));
          new ReleaseSignatureVerifier(pin).verify(manifest,signature);
          var guard=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg498_before_freeze.py").toString()).inheritIO().start();
          require(guard.waitFor(60,TimeUnit.SECONDS) && guard.exitValue()==0);
          phase="FIXED_FREEZE";Pg387TrustedDeployment.freezeCandidate();
          var next=Pg387TrustedDeployment.verify();require(next.manifestSha256().equals(DIGEST));
          var database=Pg407FailedRootRecovery.openDatabase();
          try{
            database.setReadOnly(true);database.setAutoCommit(false);int pid;
            try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG498-fixed-pending',false),pg_try_advisory_lock(71419602)")){
              require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
            phase="REFERENCE_SCOPE";var refs=new References(pid,database);
            try{
              refs.check("before");phase="CODE_ONLY_PUBLISH";publish(next);phase="PENDING_AFTER";refs.check("after");
              phase="DATABASE_CLOSE";database.rollback();database.close();phase="REFERENCE_CLOSE";refs.release();
            }catch(Exception|Error failure){retain(failure);throw failure;}
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";privateWrite(SAVE.resolve("complete.private"),("pendingCodeOnly=true\nallNewScopesReturnedNormally=true\nepochUnchanged=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n").getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG498_ACCEPTED pendingCodeOnly=true allNewScopesReturnedNormally=true databaseUpdates0=true starts0=true");
  }
}
