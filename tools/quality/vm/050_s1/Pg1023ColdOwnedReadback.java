import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** SSC243: completed/no-active cold ownership readback only. No epoch, directory or mount writes. */
public final class Pg1023ColdOwnedReadback {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg1023-cold-tools-v1");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg1023-cold-owned-v1");
  static final String BOOT="cbca8738-3b24-4090-b77c-bf029677cdd6";
  static final MaintenanceActivation ORIGINAL=new MaintenanceActivation(
      new BatchRun(UUID.fromString("eeae04ea-713c-4f2d-888d-358fb4bed274"),
          java.time.Instant.parse("2026-10-09T23:31:22.087768Z")),
      UUID.fromString("091663ce-1cf4-47e7-8311-218ebb0c8653"));
  static String phase="ENTRY";
  static void arguments(String[] args) {
    require(args!=null && args.length==1 && "verify".equals(args[0]));
  }
  static void require(boolean value) {
    if(!value)throw new IllegalStateException("completed cold readback refused");
  }
  static void retain(Throwable failure) {
    System.err.println("PG1023_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true");
    boolean lossReported=false;
    for(;;) {
      if(Pg983BootstrapExisting.lease!=null&&!lossReported) {
        try {Pg983BootstrapExisting.pulse();}
        catch(Exception|Error lost) {System.err.println("PG1023_DATABASE_UNKNOWN ownershipNotInferred=true");lossReported=true;}
      }
      try {Thread.sleep(1000);}catch(InterruptedException notification){Thread.interrupted();}
    }
  }
  static void original(MaintenanceRunFiles.Session session)throws Exception {
    var proof=session.observeStartup(ORIGINAL);
    var done=proof.completed().orElseThrow();
    require(done.outcome()==MaintenanceCompletion.Outcome.SUCCESS
        && done.endedAt().equals(java.time.Instant.parse("2026-10-09T23:56:48.112404Z")));
    require(proof.equals(session.observeStartup(ORIGINAL)));
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;
    References(int backend)throws Exception {
      Path log=SAVE.resolve("refs.private.log");
      Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(
          java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg1023_cold_refs.py").toString(),
          "verify",Integer.toString(backend)).redirectError(log.toFile()).start();
      input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception {
      long deadline=System.nanoTime()+java.util.concurrent.TimeUnit.SECONDS.toNanos(60);
      var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline) {
        Pg983BootstrapExisting.pulse();
        while(input.available()>0) {
          int value=input.read();if(value<0||bytes.size()==64)throw new IOException("cold references unavailable");
          bytes.write(value);
          if(value==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}
        }
        if(child.waitFor(10,java.util.concurrent.TimeUnit.MILLISECONDS)&&input.available()==0)
          throw new IOException("cold references unavailable");
      }
      throw new IOException("cold references unavailable");
    }
    void check(String name)throws Exception {
      require(Set.of("prepare","run").contains(name));
      output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");
    }
    void release()throws Exception {
      output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");
      require(child.waitFor(5,java.util.concurrent.TimeUnit.SECONDS)&&child.exitValue()==0);
      output.close();input.close();child.getErrorStream().close();
    }
  }
  public static void main(String[] args)throws Exception {
    arguments(args);
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).strip().equals(BOOT));
    require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    // New private receipt namespace only; no business/runtime state is created.
    Pg428ColdBootPreparation.newDirectory(SAVE,0,0);
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try {
        return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
          try {
            phase="SIGNED_CURRENT";
            Pg387TrustedDeployment.LABEL="PG932";Pg387TrustedDeployment.STEM="pg932";
            Pg387TrustedDeployment.SOURCE="40ef6e894573d2ffab1d1732124960f9c98d5f97";
            Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG932");
            Pg387TrustedDeployment.expectedSqlCount=28;
            var approval=Pg387TrustedDeployment.verify();
            require(approval.manifestSha256().equals("b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524")
                && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
            phase="DATABASE_ADMISSION";
            var database=Pg407FailedRootRecovery.openDatabase();
            database.setReadOnly(true);database.setAutoCommit(false);
            // Pg797's frozen 3-digit application grammar is preserved; this fixed alias
            // identifies SSC243, while operator source/run remain PG1023.
            try(var q=database.createStatement();var r=q.executeQuery("select set_config('application_name','PG243-cold-empty',false),pg_try_advisory_lock(71419602)")) {
              require(r.next() && r.getBoolean(2) && !r.wasNull() && !r.next());
            }
            int backend=Pg983BootstrapExisting.backend(database);
            Pg983BootstrapExisting.lease=new Pg797OwnedDatabase(database,
                new Pg797OwnedDatabase.Expected(backend,"schubert_batch","PG243-cold-empty","schubert_nk",true,true));
            Pg983BootstrapExisting.lastPulse=0;Pg983BootstrapExisting.pulse();
            // Reuse the qualified framing/heartbeat/normal-close protocol, not its
            // old ISSUED-original readback or existingADMIN Unit execution.
            var refs=new References(backend);
            phase="HELD_ORIGINAL_AND_REFS";
            MaintenanceRunFiles.create().execute(session->Pg387TrustedDeployment.checked(()->{
              original(session);refs.check("prepare");original(session);
              Pg983BootstrapExisting.pulse();database.rollback();
              phase="DATABASE_NORMAL_CLOSE";database.close();
              Pg983BootstrapExisting.lease.confirmClosed();Pg983BootstrapExisting.lease=null;
              Pg983BootstrapExisting.lastPulse=0;
              // Child independently observes actual server peer/advisory removal.
              refs.check("run");original(session);
              phase="REF_FD_BUS_NORMAL_CLOSE";refs.release();
              return Boolean.TRUE;
            }));
            phase="ADMISSION_NORMAL_CLOSE";return Boolean.TRUE;
          }catch(Exception|Error failure){retain(failure);throw failure;}
        })).orElseThrow();
      }catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="ALL_SCOPES_NORMAL";
    Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),
        "allScopesReturnedNormally=true\nreadbackOnly=true\nepochNamespaceMountWrites=0\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG1023_DONE readbackOnly=true allScopesReturnedNormally=true preparationAccepted=false");
  }
}
