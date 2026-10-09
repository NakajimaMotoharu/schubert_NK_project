import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC242/DEP864001..004. Fixed completed data, not a successful-parent receipt. */
public final class Pg864CompletedDeployment {
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg864-completed-tools-v1");
  static final Path BASE=Path.of("/var/lib/pgpt-s1-preservation");
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG862");
  static final Path APPROVAL=Path.of("/etc/schubert-nk/release-approval/current");
  static final Path CURRENT=Path.of("/opt/schubert-nk/current");
  static final UUID BOOT=UUID.fromString("cc9ed874-7f4f-450e-a188-8de1e42c8441");
  static final UUID OLD_EPOCH=UUID.fromString("8b153538-1523-4987-a456-6cbea0d345ee");
  static final MaintenanceActivation ACTIVATION=new MaintenanceActivation(new BatchRun(UUID.fromString("9de2d03c-28c7-4647-97d9-c66ace06048c"),Instant.parse("2026-10-09T05:42:22.532331Z")),UUID.fromString("021111b4-6de5-4733-917d-5ac176240ffc"));
  static final String SOURCE="e01612fcd7f2752df5ae0836b78538fd5e87f120";
  static final String DIGEST="20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe";
  static Pg797OwnedDatabase batchLease,schemaLease;
  static Pg798DatabaseScope databases;
  static Path save;
  static String phase="PREFLIGHT";
  static UUID expectedEpoch=OLD_EPOCH;
  static long lastPulse;
  static void require(boolean b){if(!b)throw new IllegalStateException("fixed completed deployment refused");}
  static boolean arguments(String[] a){return a!=null&&a.length==1&&a[0]!=null&&Set.of("prepare-ro","verify","activate").contains(a[0]);}
  static boolean completion(MaintenanceRunFiles.StartupOriginal original){
    return original!=null&&original.activation().equals(ACTIVATION)&&original.completed().isPresent()
      &&original.completed().orElseThrow().activation().equals(ACTIVATION)
      &&original.completed().orElseThrow().outcome()==MaintenanceCompletion.Outcome.SUCCESS
      &&original.completed().orElseThrow().endedAt().equals(Instant.parse("2026-10-09T15:32:16.513983Z"));
  }
  static void original(MaintenanceRunFiles.Session session)throws Exception{
    var raw=Files.readAllBytes(STARTUP.resolve("epoch.current"));var epoch=StartupPermitRecords.readEpoch(raw);
    require(epoch.state()==StartupPermitRecords.State.INVALID&&epoch.boot().equals(BOOT)&&epoch.epoch().equals(expectedEpoch)&&epoch.activation().equals(ACTIVATION)&&epoch.permitDigest().isEmpty());
    var value=session.observeStartup(ACTIVATION);require(completion(value)&&value.equals(session.observeStartup(ACTIVATION)));
    require(Pg410KnownAuthRecovery.hash(Files.readAllBytes(Path.of("/var/lib/schubert-nk/maintenance/attempts/021111b4-6de5-4733-917d-5ac176240ffc.done"))).equals("37356ff23d0393924c22079bd4c87fce7c3070155d84704fb1cb143e7b1c60a5"));
    require(!Files.exists(Path.of("/var/lib/schubert-nk/maintenance/active"),LinkOption.NOFOLLOW_LINKS));
  }
  static Pg797OwnedDatabase lease(Connection db,String role,String app,boolean advisory)throws Exception{
    db.setReadOnly(true);db.setAutoCommit(false);
    int backend;
    try(var q=db.createStatement();var r=q.executeQuery("select pg_backend_pid(),set_config('application_name','"+app+"',false)"+(advisory?",pg_try_advisory_lock(71419602)":""))){
      require(r.next());backend=r.getInt(1);require(!r.wasNull()&&(!advisory||r.getBoolean(3))&&!r.next());
    }
    var owner=new Pg797OwnedDatabase(db,new Pg797OwnedDatabase.Expected(backend,role,app,"schubert_nk",true,advisory));owner.verify();return owner;
  }
  static void pulse()throws Exception{
    long now=System.nanoTime();if(lastPulse==0||now-lastPulse>=TimeUnit.SECONDS.toNanos(1)){if(databases!=null)databases.verify();lastPulse=System.nanoTime();}
  }
  static void retain(Throwable failure){
    System.err.println("PG864_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true old143NotNormalized=true");
    for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg864CompletedDeployment"))System.err.println("PG864_FRAME method="+frame.getMethodName()+" line="+frame.getLineNumber());
    boolean notified=false;
    for(;;){if(!notified)try{if(databases!=null)databases.verify();}catch(Exception|Error lost){System.err.println("PG864_DB_NOT_CONFIRMED ownershipNotInferred=true");notified=true;}try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}}
  }
  static void write(Path p,byte[] value)throws Exception{
    try(var f=FileChannel.open(p,Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE),java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")))){
      var buffer=java.nio.ByteBuffer.wrap(value);while(buffer.hasRemaining())f.write(buffer);f.force(true);
    }Pg387TrustedDeployment.sync(p.getParent());
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;
    References(int batch,int schema)throws Exception{
      Path log=save.resolve("refs.private.log");Files.createFile(log,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg864_completed_refs.py").toString(),Integer.toString(batch),Integer.toString(schema),save.toString()).redirectError(log.toFile()).start();
      input=child.getInputStream();output=child.getOutputStream();await("REF_READY",true);
    }
    void await(String expected,boolean live)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){
        if(live)pulse();
        while(input.available()>0){int v=input.read();require(v>=0&&bytes.size()<64);bytes.write(v);if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS)&&input.available()==0)throw new IOException("reference unavailable");
      }throw new IOException("reference unavailable");
    }
    void check(String name,MaintenanceRunFiles.Session session)throws Exception{
      require(Set.of("before","epoch","approval","after").contains(name));pulse();original(session);output.write((name+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED",true);pulse();original(session);
    }
    void release()throws Exception{
      output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED",false);
      require(child.waitFor(5,TimeUnit.SECONDS)&&child.exitValue()==0);output.close();input.close();child.getErrorStream().close();
    }
  }
  // Replaced by the independently tested literal mount parser at source assembly.
  static boolean readOnlyMount(String table,String target){throw new AssertionError("assembly required");}
  static void command(String... args)throws Exception{
    pulse();var child=new ProcessBuilder(args).inheritIO().start();long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);
    while(!child.waitFor(250,TimeUnit.MILLISECONDS)){pulse();require(System.nanoTime()<deadline);}pulse();require(child.exitValue()==0);
  }
  static void prepare(String mode)throws Exception{
    require(Files.readSymbolicLink(Path.of("/proc/self/ns/mnt")).equals(Files.readSymbolicLink(Path.of("/proc/1/ns/mnt"))));
    String table=Files.readString(Path.of("/proc/self/mountinfo"));
    if(!readOnlyMount(table,NEXT.toString())){
      require(mode.equals("prepare-ro"));
      // Reject an existing wrong/rw/submount rather than remounting an unknown authority.
      for(String line:table.split("\n")) {String[] f=line.split(" ");require(f.length>=6&&!f[4].equals(NEXT.toString())&&!f[4].startsWith(NEXT+"/"));}
      command("/usr/bin/mount","--bind",NEXT.toString(),NEXT.toString());command("/usr/bin/mount","-o","remount,bind,ro",NEXT.toString());
    }
    require(readOnlyMount(Files.readString(Path.of("/proc/self/mountinfo")),NEXT.toString()));
  }
  enum Publication { EPOCH, APPROVAL, CURRENT }
  @FunctionalInterface interface PublishAction {void execute(Publication step)throws Exception;}
  static void publications(PublishAction action)throws Exception{
    require(action!=null);action.execute(Publication.EPOCH);action.execute(Publication.APPROVAL);action.execute(Publication.CURRENT);
  }
  static void publish(ReleaseApproval next,StartupPermitFiles permits,References refs,MaintenanceRunFiles.Session session)throws Exception{
    require(next.version().equals("0.1.0-PG862")&&next.manifestSha256().equals(DIGEST));
    write(save.resolve("old-approval.private"),Files.readAllBytes(APPROVAL));write(save.resolve("old-current.private"),Files.readSymbolicLink(CURRENT).toString().getBytes(StandardCharsets.US_ASCII));write(save.resolve("old-epoch.private"),Files.readAllBytes(STARTUP.resolve("epoch.current")));
    UUID fresh=UUID.randomUUID();require(fresh.version()==4&&fresh.variant()==2&&!fresh.equals(OLD_EPOCH));
    var expected=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,BOOT,fresh,ACTIVATION,Optional.empty());
    write(save.resolve("new-epoch.private"),StartupPermitRecords.epoch(expected));
    publications(step->{switch(step){
      case EPOCH -> {phase="EPOCH_PUBLISH";pulse();require(permits.current().epoch().equals(OLD_EPOCH));var actual=permits.invalidate(BOOT,fresh,ACTIVATION);require(actual.equals(expected)&&permits.current().equals(expected));expectedEpoch=fresh;refs.check("epoch",session);}
      case APPROVAL -> {phase="APPROVAL_PUBLISH";Path part=APPROVAL.resolveSibling("pg864-approval.part");write(part,next.encode());Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));try(var f=FileChannel.open(part,StandardOpenOption.READ)){f.force(true);}Files.move(part,APPROVAL,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(APPROVAL.getParent());refs.check("approval",session);}
      case CURRENT -> {phase="CURRENT_PUBLISH";Path link=CURRENT.resolveSibling("pg864-current.part");Files.createSymbolicLink(link,NEXT);Pg387TrustedDeployment.sync(link.getParent());Files.move(link,CURRENT,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(CURRENT.getParent());require(Arrays.equals(next.encode(),Files.readAllBytes(APPROVAL))&&NEXT.equals(Files.readSymbolicLink(CURRENT)));pulse();StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(next);pulse();refs.check("after",session);}
    }});
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args));String mode=args[0];save=BASE.resolve("pg864-"+mode+"-v1");require(!Files.exists(save,LinkOption.NOFOLLOW_LINKS));
    Files.createDirectory(save,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));Pg387TrustedDeployment.sync(BASE);
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="DATABASE_PAIR";var batch=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema();
          batchLease=lease(batch,"schubert_batch","PG864-fixed-completed",true);schemaLease=lease(schema,"schubert_migration","PG864-fixed-snapshot",false);databases=new Pg798DatabaseScope(batchLease,schemaLease);pulse();
          int b,s;try(var q=batch.createStatement();var r=q.executeQuery("select pg_backend_pid()")){require(r.next());b=r.getInt(1);require(!r.wasNull()&&!r.next());}try(var q=schema.createStatement();var r=q.executeQuery("select pg_backend_pid()")){require(r.next());s=r.getInt(1);require(!r.wasNull()&&!r.next());}
          phase="TEN_REFS_FDS";var refs=new References(b,s);
          require(MaintenanceRunFiles.create().execute(session->Pg387TrustedDeployment.checked(()->{
            try(var startup=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)){
              var permits=new StartupPermitFiles(startup,LinuxInodeSecurity.create());refs.check("before",session);
              var old=ReleaseApproval.parse(Files.readAllBytes(APPROVAL));require(old.version().equals("0.1.0-PG832")&&old.manifestSha256().equals("8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977"));pulse();StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(old);pulse();
              Pg387TrustedDeployment.LABEL="PG862";Pg387TrustedDeployment.STEM="pg862";Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=NEXT;Pg387TrustedDeployment.expectedSqlCount=28;
              phase="SIGNED_CANDIDATE_RO";prepare(mode);refs.check("before",session);pulse();var next=Pg387TrustedDeployment.verify();pulse();require(next.manifestSha256().equals(DIGEST));
              if(mode.equals("activate"))publish(next,permits,refs,session);else refs.check("before",session);
              phase="DATABASE_CLOSE";pulse();batch.rollback();batch.close();batchLease.confirmClosed();schema.rollback();schema.close();schemaLease.confirmClosed();
              phase="REFERENCE_BUS_FD_CLOSE";refs.release();return Boolean.TRUE;
            }catch(Exception|Error failure){retain(failure);throw failure;}
          })));
          phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="COMPLETE";write(save.resolve("complete.private"),("completedDataOnly=true\nmode="+mode+"\nallNewScopesReturnedNormally=true\nold143NotNormalized=true\ndatabaseUpdates0=true\nstarts0=true\n").getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG864_ACCEPTED mode="+mode+" completedDataOnly=true allNewScopesReturnedNormally=true old143NotNormalized=true databaseUpdates0=true starts0=true");
  }
}
