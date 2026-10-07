import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC206 / N11 / PT-OPS-PG501: current fixed saved-guest cold preparation only.
 * No old runtime/permit restoration, new ISSUED, worker start, or database update.
 */
public final class Pg501ColdPreparation {
  static final String BOOT="cc9ed874-7f4f-450e-a188-8de1e42c8441";
  static final String SOURCE="a2e98ce9e96c42425921e3686e8ae7a94bff9e6c";
  static final String DIGEST="f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44";
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg501-cold-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg501-cold-preparation-v1");
  static final Path RUN=Path.of("/run/schubert-nk");
  static String phase="ENTRY";
  static void require(boolean v){if(!v)throw new IllegalStateException("fixed cold profile unavailable");}
  static void retain(Throwable failure){
    System.err.println("PG501_COLD_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" oldCloseNotInferred=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg501ColdPreparation"))
      System.err.println("PG501_COLD_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;
    References(int backend)throws Exception{
      Path log=SAVE.resolve("refs.private.err");Files.createFile(log,
          PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg501_cold_refs.py").toString(),
          Integer.toString(backend)).redirectError(log.toFile()).start();
      input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){
        while(input.available()>0){int v=input.read();require(v>=0 && bytes.size()<64);bytes.write(v);
          if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference ended");
      }
      throw new IOException("reference deadline");
    }
    void check(String point)throws Exception{
      require(Set.of("before","frozen","prepared").contains(point));
      output.write((point+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");
    }
    void release()throws Exception{
      output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");
      require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);
      output.close();input.close();child.getErrorStream().close();
    }
  }
  static void directory(String name,String owner)throws Exception{
    Path path=RUN.resolve("pt-coverage").resolve(name);require(!Files.exists(path,LinkOption.NOFOLLOW_LINKS));
    int uid=0,gid=0;
    if(!"root".equals(owner)){
      uid=Integer.parseInt(new String(Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-u",owner),StandardCharsets.US_ASCII).trim());
      gid=Integer.parseInt(new String(Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-g",owner),StandardCharsets.US_ASCII).trim());
    }
    Pg428ColdBootPreparation.newDirectory(path,uid,gid);
  }
  public static void main(String[] args)throws Exception{
    require(args.length==1 && "prepare".equals(args[0]));
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));
    require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusiveObserved(admission->Pg387TrustedDeployment.checked(()->{
        var db=Pg407FailedRootRecovery.openDatabase();
        try{
          phase="DB_ADVISORY";db.setReadOnly(true);db.setAutoCommit(false);int backend;
          try(var statement=db.createStatement();var result=statement.executeQuery(
              "select pg_backend_pid(),set_config('application_name','PG501-cold-preparation',false),pg_try_advisory_lock(71419602)")){
            require(result.next() && result.getBoolean(3));backend=result.getInt(1);require(!result.next());
          }
          Pg428ColdBootPreparation.newDirectory(SAVE,0,0);
          phase="REFERENCE_SCOPE";var refs=new References(backend);
          try{
            refs.check("before");phase="SIGNED_HOST_READONLY";
            Pg464CodeOnlyDeployment.configure("PG495",SOURCE,Path.of("/opt/schubert-nk/releases/0.1.0-PG495"));
            Pg387TrustedDeployment.expectedSqlCount=28;Pg387TrustedDeployment.freezeCandidate();
            var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals(DIGEST));
            require(Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
            StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
            refs.check("frozen");phase="NEW_NAMESPACE";
            var activation=MaintenanceRecords.readActivation(Files.readAllBytes(Path.of("/var/lib/schubert-nk/maintenance/active")));
            require(activation.run().id().equals(UUID.fromString("91a748b4-1abe-484c-9682-44f46429b324")));
            MaintenanceRunFiles.create().execute(session->Pg387TrustedDeployment.checked(()->{
              require(session.observe(activation).equals(activation)
                  && new RunReferenceRepository(db).read(activation.run()).identityConsistent());
              for(String name:List.of("startup","backup-request","cleanup-request","expiry-request"))
                Pg428ColdBootPreparation.ensureEmptyRoot(RUN.resolve(name));
              Pg428ColdBootPreparation.newDirectory(RUN.resolve("pt-coverage"),0,0);
              for(String name:List.of("parent","cleanup","expiry","root-api","root-web"))directory(name,"root");
              directory("backup","schubert-backup");directory("inspector","schubert-inbox-inspector");
              directory("ordinary-api","schubert-api");directory("ordinary-web","schubert-web");
              Files.setPosixFilePermissions(RUN.resolve("pt-coverage"),PosixFilePermissions.fromString("rwxr-xr-x"));
              try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),RUN.resolve("startup"))){
                var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());
                var invalid=files.invalidate(UUID.fromString(BOOT),UUID.randomUUID(),activation);
                require(invalid.state()==StartupPermitRecords.State.INVALID && invalid.equals(files.current())
                    && invalid.activation().equals(activation));
              }
              return Boolean.TRUE;
            }));
            refs.check("prepared");phase="DB_CLOSE";db.rollback();db.close();phase="REF_CLOSE";refs.release();
          }catch(Exception|Error failure){retain(failure);throw failure;}
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="NORMAL_PUBLISH";
    Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),
        "coldPrepared=true\nallNewScopesReturnedNormally=true\noldRuntimeRetired=0\noldCloseUnknown=true\ndatabaseUpdates0=true\nstarts0=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG501_COLD_PREPARED normalAllScopes=true oldRuntimeRetired=0 starts0=true databaseUpdates0=true");
  }
}
