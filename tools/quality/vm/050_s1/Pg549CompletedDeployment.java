import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SS343 SSC190 / PT-OPS-PG549-C001..005: exact PG522 SUCCESS, fresh INVALID code-only. No old DONE resume/start/DDL. */
public final class Pg549CompletedDeployment {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg549-completed-tools-v4");
  static Path SAVE;
  static String mode;
  static final Path APPROVAL=Path.of("/etc/schubert-nk/release-approval/current");
  static final Path CURRENT=Path.of("/opt/schubert-nk/current");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG548");
  static String phase="PREFLIGHT";
  static final String source="969d8ded10c0bf5841d9e3a5c531e922caf4a24a",digest="a224ea9cf421b06e7029b1f8845f2a7eb3d620b5ec2bdf90bfe64c731b99515b";
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG495");
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed completed deployment refused");}
  static boolean arguments(String[] a){return a!=null && a.length==1 && a[0]!=null && Set.of("verify","activate").contains(a[0]);}
  static void retain(Throwable failure){
    System.err.println("PG549_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg549CompletedDeployment"))System.err.println("PG549_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
  }
  static void original()throws Exception{
    var epoch=StartupPermitRecords.readEpoch(Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));
    require(epoch.boot().toString().equals("cc9ed874-7f4f-450e-a188-8de1e42c8441") && epoch.activation().run().id().toString().equals("91a748b4-1abe-484c-9682-44f46429b324") && epoch.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-06T12:06:14.564793Z")));
    var observed=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
    require(observed.activation().equals(epoch.activation()) && normalDone(observed) && epoch.activation().id().toString().equals("179758d2-5b77-443a-a743-bf0065e732ea"));
  }
  static boolean normalDone(MaintenanceRunFiles.StartupOriginal original){
    return original!=null && original.activation().run().id().toString().equals("91a748b4-1abe-484c-9682-44f46429b324")
      && original.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-06T12:06:14.564793Z"))
      && original.completed().isPresent()
      && original.completed().orElseThrow().outcome()==dev.codex.schubert.nk.batch.repository.MaintenanceCompletion.Outcome.SUCCESS
      && original.completed().orElseThrow().endedAt().equals(java.time.Instant.parse("2026-10-07T20:08:48.159294Z"));
  }
  static void signedFiles()throws Exception{
    for(String directory:List.of("db/migration","systemd","config")){
      try(var entries=Files.walk(OLD.resolve(directory))){
        for(Path p:entries.filter(Files::isRegularFile).toList())require(Arrays.equals(Files.readAllBytes(p),Files.readAllBytes(NEXT.resolve(OLD.relativize(p)))));
      }
    }
    try(var entries=Files.list(NEXT.resolve("db/migration"))){require(entries.count()==28);}
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
      Path log=SAVE.resolve("refs-prepare.private.log");
      Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg549_completed_refs.py").toString(),mode,Integer.toString(pid)).redirectError(log.toFile()).start();
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
    require(next.version().equals("0.1.0-PG548") && next.manifestSha256().equals(digest));
    privateWrite(SAVE.resolve("old-approval.private"),Files.readAllBytes(APPROVAL));
    privateWrite(SAVE.resolve("old-current.private"),Files.readSymbolicLink(CURRENT).toString().getBytes(StandardCharsets.US_ASCII));
    privateWrite(SAVE.resolve("old-epoch.private"),Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))){
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var before=files.current();
      require(before.state()==StartupPermitRecords.State.ISSUED && files.readIssued().releaseDigest().equals("f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44"));
      var invalid=files.invalidate(before.boot(),UUID.randomUUID(),before.activation());
      require(invalid.state()==StartupPermitRecords.State.INVALID && invalid.activation().equals(before.activation()) && !invalid.epoch().equals(before.epoch()) && invalid.equals(files.current()));
    }
    Path part=APPROVAL.resolveSibling("pg549-approval.part");
    privateWrite(part,next.encode());Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var file=FileChannel.open(part,StandardOpenOption.READ)){file.force(true);}
    Files.move(part,APPROVAL,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(APPROVAL.getParent());
    Path link=CURRENT.resolveSibling("pg549-current.part");Files.createSymbolicLink(link,NEXT);Pg387TrustedDeployment.sync(link.getParent());
    Files.move(link,CURRENT,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(CURRENT.getParent());
    require(Arrays.equals(next.encode(),Files.readAllBytes(APPROVAL)) && NEXT.equals(Files.readSymbolicLink(CURRENT)));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(next);
    require(!Arrays.equals(Files.readAllBytes(SAVE.resolve("old-epoch.private")),Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current"))));
  }
  static void immutableCandidate()throws Exception {
    var p=new ProcessBuilder("/usr/bin/findmnt","--noheadings","--output","OPTIONS","--mountpoint",NEXT.toString()).redirectInput(Path.of("/dev/null").toFile()).start();
    try(var input=p.getInputStream();var error=p.getErrorStream()){
      byte[] raw=input.readNBytes(4097);require(raw.length<=4096 && error.readNBytes(4097).length==0);int result=p.waitFor();
      require(result==0 || result==1);
      if(result==0)require(Arrays.asList(new String(raw,StandardCharsets.US_ASCII).trim().split(",")).contains("ro"));
      else Pg387TrustedDeployment.freezeCandidate();
    }
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args));mode=args[0];SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg549-completed-"+mode+"-v4");require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_ORIGINAL";Pg464CodeOnlyDeployment.configure("PG495","a2e98ce9e96c42425921e3686e8ae7a94bff9e6c",OLD);Pg387TrustedDeployment.expectedSqlCount=28;
          var prior=Pg387TrustedDeployment.verify();require(prior.manifestSha256().equals("f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44") && Arrays.equals(prior.encode(),Files.readAllBytes(APPROVAL)) && OLD.equals(Files.readSymbolicLink(CURRENT)));
          StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(prior);original();
          Pg428ColdBootPreparation.newDirectory(SAVE,0,0);var database=Pg407FailedRootRecovery.openDatabase();
          try{
            database.setReadOnly(true);database.setAutoCommit(false);int pid;
            try(var s=database.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG549-completed-codeonly',false),pg_try_advisory_lock(71419602)")){
              require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
            phase="REFERENCE_SCOPE";var refs=new References(pid,database);
            try{
              refs.check("before");phase="CANDIDATE_READONLY";
              Pg464CodeOnlyDeployment.configure("PG548",source,NEXT);Pg387TrustedDeployment.expectedSqlCount=28;
              immutableCandidate();phase="CANDIDATE_TYPED_BOM";var next=Pg387TrustedDeployment.verify();require(next.manifestSha256().equals(digest));signedFiles();refs.check("before");
              if(mode.equals("activate")){phase="CODE_ONLY_PUBLISH";publish(next);}phase="DONE_AFTER";refs.check("after");
              
              phase="DATABASE_CLOSE";database.rollback();database.close();phase="REFERENCE_CLOSE";refs.release();
            }catch(Exception|Error failure){retain(failure);throw failure;}
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE_PUBLISH";privateWrite(SAVE.resolve("complete.private"),("completedCurrentVerified=true\nmode="+mode+"\nallNewScopesReturnedNormally=true\nrequestsUnchanged=true\ndatabaseUpdates0=true\nstarts0=true\n").getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG549_COMPLETED mode="+mode+" allNewScopesReturnedNormally=true databaseUpdates0=true starts0=true");
  }
}
