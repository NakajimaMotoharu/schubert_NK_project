import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.sql.Connection;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC209/N10/PT-OPS-PG515: new operator ownership. Parent143 NEVER normalizes. */
public final class Pg515SingleApiRecovery {
  static final String SOURCE="a2e98ce9e96c42425921e3686e8ae7a94bff9e6c";
  static final String DIGEST="f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44";
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg515-issued-api-recovery-v1");
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg515-issued-api-tools-v3");
  static String phase="ARGUMENTS";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed single API profile refused");}
  static boolean arguments(String[] args){return args!=null && args.length==1 && "recover".equals(args[0]);}
  static void retain(Throwable failure,String confirmed,String unknown){
    System.err.println("PG515_UNKNOWN phase="+phase+" confirmed="+confirmed+" unknown="+unknown+" oldCloseNotInferred=true diagnosticsRedacted=true");
    for(var f:failure.getStackTrace())if(f.getClassName().startsWith("Pg513") || f.getClassName().endsWith("Pg513SingleApiIntent"))System.err.println("PG515_FRAME method="+f.getMethodName()+" line="+f.getLineNumber());
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}
  }
  static final class References {
    final Process child; final InputStream input; final OutputStream output; final Connection db;
    boolean databaseClosed;
    References(int backend,Connection database)throws Exception{
      db=database;
      Path log=SAVE.resolve("refs.private.err");Files.createFile(log,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg515_single_api_refs.py").toString(),Integer.toString(backend)).redirectError(log.toFile()).start();
      input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void heartbeat()throws Exception{
      if(databaseClosed)return;
      try(var s=db.createStatement()){
        s.setQueryTimeout(5);
        try(var r=s.executeQuery("select exists(select 1 from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419602 and objsubid=1 and granted)")){require(r.next() && r.getBoolean(1) && !r.next());}
      }
    }
    void await(String expected)throws Exception{
      long began=System.nanoTime(),ping=began;var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()-began<TimeUnit.SECONDS.toNanos(180)){
        while(input.available()>0){int v=input.read();require(v>=0 && bytes.size()<64);bytes.write(v);
          if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        long now=System.nanoTime();if(now-ping>TimeUnit.SECONDS.toNanos(2)){heartbeat();ping=now;}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference channel unavailable");
      }
      throw new IOException("reference deadline");
    }
    void check(String point)throws IOException{
      try{heartbeat();output.write((point+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");}
      catch(IOException failure){throw failure;}catch(Exception failure){throw new IOException("owned reference unavailable",failure);}
    }
    void release()throws Exception{
      require(databaseClosed);output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");
      require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();
    }
  }
  static void signed()throws Exception{
    Pg387TrustedDeployment.LABEL="PG495";Pg387TrustedDeployment.STEM="pg495";Pg387TrustedDeployment.SOURCE=SOURCE;
    Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG495");Pg387TrustedDeployment.expectedSqlCount=28;
    var approval=Pg387TrustedDeployment.verify();require(approval.manifestSha256().equals(DIGEST));
    require(Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(approval);
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("cc9ed874-7f4f-450e-a188-8de1e42c8441")
        && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
  }
  static void work()throws Exception{
    phase="SIGNATURE";signed();Pg428ColdBootPreparation.newDirectory(SAVE,0,0);
    var db=Pg407FailedRootRecovery.openDatabase();
    var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"));
    boolean dbClosed=false,refsClosed=false,rootCloseBegun=false;
    StartupPermitRecords.Epoch observed=null;MaintenanceActivation original=null;
    try{
      phase="DB_ADVISORY";db.setReadOnly(false);db.setAutoCommit(false);
      require(!db.isReadOnly() && !db.getAutoCommit() && db.getTransactionIsolation()==Connection.TRANSACTION_READ_COMMITTED);
      int backend;
      try(var s=db.createStatement();var r=s.executeQuery("select pg_backend_pid(),set_config('application_name','PG515-fixed-recovery',false),pg_try_advisory_lock(71419602)")){
        require(r.next() && r.getBoolean(3));backend=r.getInt(1);require(!r.next());
      }
      phase="TEN_REFERENCE_SCOPE";var refs=new References(backend,db);
      refs.check("before");
      var activation=MaintenanceRecords.readActivation(Files.readAllBytes(Path.of("/var/lib/schubert-nk/maintenance/active")));
      var permits=new StartupPermitFiles(root,LinuxInodeSecurity.create());var issued=permits.current();
      var invalid=Pg515IssuedApiRecovery.invalid(issued);
      observed=issued;original=activation;
      require(issued.state()==StartupPermitRecords.State.ISSUED && invalid.boot().toString().equals("cc9ed874-7f4f-450e-a188-8de1e42c8441")
          && invalid.activation().equals(activation) && activation.run().id().toString().equals("91a748b4-1abe-484c-9682-44f46429b324"));
      require(MaintenanceRunFiles.create().execute(s->s.observeStartup(activation)).completed().isEmpty()
          && new RunReferenceRepository(db).read(activation.run()).identityConsistent());
      var actualPermit=Pg515IssuedApiRecovery.issued(root,issued,activation,DIGEST);
      phase="OWNED_REVERSE_STOP";
      for(String unit:List.of("schubert-nk-expiry-cleanup.service","schubert-nk-cleanup.service","artemis.service"))refs.check("stop:"+unit);
      phase="FULL_TERMINAL";refs.check("terminal");signed();
      phase="CANONICAL_REVOKE";
      require(actualPermit.equals(Pg515IssuedApiRecovery.issued(root,issued,activation,DIGEST)));
      refs.check("terminal");require(invalid.equals(permits.revoke(invalid,actualPermit)));
      refs.check("revoked");Pg513SingleApiIntent.correlate(root,invalid,activation,DIGEST);
      phase="SINGLE_API_RETIRE";
      Pg513SingleApiIntent.retire(root,invalid,activation,DIGEST,()->refs.check("terminal"),()->refs.check("ownership"));
      refs.check("retired");require(invalid.equals(permits.current()));
      phase="DB_CLOSE";db.rollback();db.close();dbClosed=true;refs.databaseClosed=true;
      phase="REF_CLOSE";refs.release();refsClosed=true;
      phase="ROOT_CLOSE";rootCloseBegun=true;root.close();
    }catch(Exception|Error failure){
      // Keep lexical M/A callbacks from unwinding. Consumed inner resources remain UNKNOWN.
      String isolation="NOT_ATTEMPTED_NO_CORRELATION";
      if(observed!=null && original!=null && !rootCloseBegun){
        try{
          Pg515IssuedApiRecovery.isolate(root,observed,original,DIGEST,()->{
            try{byte[] result=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/python3","-B",TOOLS.resolve("pg515_confirm_ma.py").toString());
              require(Arrays.equals(result,"PG515_CURRENT_MA confirmed=true databaseOrRefsClaimed=false\n".getBytes(StandardCharsets.US_ASCII)));}
            catch(Exception secondary){throw new IOException("current M/A unavailable",secondary);}
          });isolation="API_MARKER_RESTORED_CURRENT_MA";
        }catch(Exception|Error secondary){failure.addSuppressed(secondary);isolation="API_REISOLATION_UNKNOWN";}
      }else if(rootCloseBegun)isolation="SKIPPED_ROOT_CONSUMED";
      System.err.println("PG515_ISOLATION "+isolation+" furtherBusinessActions0=true");
      retain(failure,"M_A",(dbClosed?"DB_CLOSED":"DB_UNKNOWN")+"_"+(refsClosed?"REF_CLOSED":"REF_UNKNOWN")+"_"+(rootCloseBegun?"ROOT_CONSUMED_UNKNOWN":"ROOT_HELD_OR_UNKNOWN"));
      throw failure;
    }
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    try{
      require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
        try{
          require(StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
            work();phase="A_CLOSE";return Boolean.TRUE;
          })).orElseThrow());
          phase="M_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure,"M","A_UNKNOWN");throw failure;}
      })).orElseThrow());
    }catch(Exception|Error failure){retain(failure,"NONE","M_UNKNOWN_A_UNKNOWN");throw failure;}
    phase="COMPLETE_PUBLISH";
    Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),"singleApiIntentRetired=true\nallNewScopesReturnedNormally=true\noriginal24TablesAnd452BatchPreserved=true\noldParentTimeout143=true\noldCloseNotInferred=true\nstarts0=true\ndatabaseUpdates0=true\n".getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG515_RECOVERY_COMPLETE allNewScopesNormal=true singleApiIntentRetired=true oldParent143Retained=true starts0=true databaseUpdates0=true");
  }
}
