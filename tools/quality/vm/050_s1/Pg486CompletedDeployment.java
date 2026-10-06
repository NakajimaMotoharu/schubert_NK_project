import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SS343 SSC190 / DONE486: fixed current normal DONE code-only; no start/DDL/old close normalization. */
public final class Pg486CompletedDeployment {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg486-completed-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg486-completed-codeonly");
  static final Path APPROVAL=Path.of("/etc/schubert-nk/release-approval/current");
  static final Path CURRENT=Path.of("/opt/schubert-nk/current");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG486");
  static String phase="PREFLIGHT";
  static String source,digest;
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG479");
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed completed deployment refused");}
  static boolean arguments(String[] a){return a!=null && a.length==3 && "activate".equals(a[0]) && a[1]!=null && a[1].matches("[0-9a-f]{40}") && a[2]!=null && a[2].matches("[0-9a-f]{64}");}
  static void retain(Throwable failure){
    System.err.println("PG486_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg486CompletedDeployment"))System.err.println("PG486_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static void original()throws Exception{
    var epoch=StartupPermitRecords.readEpoch(Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));
    require(epoch.boot().toString().equals("e07aa706-1acd-4e65-b309-d7f330f79d54") && epoch.activation().run().id().toString().equals("49437eda-1681-43a9-883a-424eb55a6166") && epoch.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-06T06:28:43.734078Z")));
    var observed=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
    require(observed.activation().equals(epoch.activation()) && normalDone(observed));
  }
  static boolean normalDone(MaintenanceRunFiles.StartupOriginal original){
    return original!=null && original.activation().run().id().toString().equals("49437eda-1681-43a9-883a-424eb55a6166")
      && original.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-06T06:28:43.734078Z"))
      && original.completed().isPresent()
      && original.completed().orElseThrow().outcome()==dev.codex.schubert.nk.batch.repository.MaintenanceCompletion.Outcome.SUCCESS
      && !original.completed().orElseThrow().endedAt().isBefore(java.time.Instant.parse("2026-10-06T08:22:25Z"))
      && !original.completed().orElseThrow().endedAt().isAfter(java.time.Instant.parse("2026-10-06T08:52:26Z"));
  }
  static void signedFiles()throws Exception{
    for(String directory:List.of("db/migration","systemd","config")){
      try(var entries=Files.walk(OLD.resolve(directory))){
        for(Path p:entries.filter(Files::isRegularFile).toList())require(Arrays.equals(Files.readAllBytes(p),Files.readAllBytes(NEXT.resolve(OLD.relativize(p)))));
      }
    }
    try(var entries=Files.list(NEXT.resolve("db/migration"))){require(entries.count()==27);}
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
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg486_completed_refs.py").toString(),"activate",Integer.toString(pid),source,digest).redirectError(log.toFile()).start();
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
    require(next.version().equals("0.1.0-PG486") && next.manifestSha256().equals(digest));
    privateWrite(SAVE.resolve("old-approval.private"),Files.readAllBytes(APPROVAL));
    privateWrite(SAVE.resolve("old-current.private"),Files.readSymbolicLink(CURRENT).toString().getBytes(StandardCharsets.US_ASCII));
    privateWrite(SAVE.resolve("old-epoch.private"),Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))){
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var before=files.current();
      require(before.state()==StartupPermitRecords.State.ISSUED && files.readIssued().releaseDigest().equals("a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286"));
      var invalid=files.invalidate(before.boot(),UUID.randomUUID(),before.activation());
      require(invalid.state()==StartupPermitRecords.State.INVALID && invalid.activation().equals(before.activation()) && !invalid.epoch().equals(before.epoch()) && invalid.equals(files.current()));
    }
    Path part=APPROVAL.resolveSibling("pg486-approval.part");
    privateWrite(part,next.encode());Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var file=FileChannel.open(part,StandardOpenOption.READ)){file.force(true);}
    Files.move(part,APPROVAL,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(APPROVAL.getParent());
    Path link=CURRENT.resolveSibling("pg486-current.part");Files.createSymbolicLink(link,NEXT);Pg387TrustedDeployment.sync(link.getParent());
    Files.move(link,CURRENT,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(CURRENT.getParent());
    require(Arrays.equals(next.encode(),Files.readAllBytes(APPROVAL)) && NEXT.equals(Files.readSymbolicLink(CURRENT)));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(next);
    require(!Arrays.equals(Files.readAllBytes(SAVE.resolve("old-epoch.private")),Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current"))));
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));source=args[1];digest=args[2];
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_ORIGINAL";Pg464CodeOnlyDeployment.configure("PG479","bab704707b8fd7e0dc7581c4489f0892236efe73",OLD);
          var prior=Pg387TrustedDeployment.verify();require(prior.manifestSha256().equals("a1c34cddba7d02cc479ccbe311a7ef7210f31f8aa1070f7685a2985d5503f286") && Arrays.equals(prior.encode(),Files.readAllBytes(APPROVAL)) && OLD.equals(Files.readSymbolicLink(CURRENT)));
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(prior);original();
          Pg464CodeOnlyDeployment.configure("PG486",source,NEXT);Pg387TrustedDeployment.freezeCandidate();var next=Pg387TrustedDeployment.verify();require(next.manifestSha256().equals(digest));signedFiles();
          var database=Pg407FailedRootRecovery.openDatabase();
          try{
            database.setReadOnly(true);database.setAutoCommit(false);int pid;
            try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG486-completed-codeonly',false),pg_try_advisory_lock(71419602)")){
              require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
            phase="REFERENCE_SCOPE";var refs=new References(pid,database);
            try{
              refs.check("before");phase="NONEMPTY_TRANSFER_BEFORE";var fixture=Pg428ColdBootPreparation.fixtureSnapshot();
              privateWrite(SAVE.resolve("fixture-before.private"),fixture.getBytes(StandardCharsets.UTF_8));
              phase="CODE_ONLY_PUBLISH";publish(next);phase="DONE_AFTER";refs.check("after");
              require(fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()));
              phase="DATABASE_CLOSE";database.rollback();database.close();phase="REFERENCE_CLOSE";refs.release();
            }catch(Exception|Error failure){retain(failure);throw failure;}
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";privateWrite(SAVE.resolve("complete.private"),("normalDoneCodeOnly=true\nallNewScopesReturnedNormally=true\nnewInvalidSameActivation=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n").getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG486_ACCEPTED normalDoneCodeOnly=true allNewScopesReturnedNormally=true databaseUpdates0=true starts0=true");
  }
}
