import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.sql.Connection;
import java.util.*;

/** SSC204/QA047/BUG799/YKT570: fixed PG493 timeout with ZERO existing intents.
 * New operator ownership only; never claims old close, constructs Pair, starts or publishes DONE.
 * PT-OPS-REC204001..004; existing canonical revoke and owned stop primitives only.
 */
public final class Pg496TimeoutRecovery {
  static final String SOURCE="38899a05b5c2daeecfc5af8ea5ae748e29954c60";
  static final String DIGEST="652a5e4a31dd9251c5a89cb4f5dea031f157b17ab58f466fb329cdcbfbe1be1c";
  static final String PARENT="52accf6d68f44487b6e0b3635c20396f";
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static final String EPOCH="4d35762d-54b4-4187-ab03-cc9b7e9e3baf";
  static final UUID RUN=UUID.fromString("91a748b4-1abe-484c-9682-44f46429b324");
  static final UUID ACTIVATION=UUID.fromString("179758d2-5b77-443a-a743-bf0065e732ea");
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg496-timeout-no-intents-v1");
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg496-timeout-tools-v6");
  static String phase="ARGUMENTS";
  static boolean touched;
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed no-intent recovery refused");}
  static Set<String> names(){
    var n=new HashSet<>(Set.of("epoch.current",EPOCH+".permit",EPOCH+".owner",EPOCH+".API.launch",EPOCH+".WEB.launch"));
    for(String old:List.of("15e4559b-13ab-46d7-a7a8-c15f1de4a245","1ba8ece5-5297-47c3-9933-95b2330beeb0","1eecb7b9-1e98-478f-9084-201422b31bff","25020aa0-7b69-4554-be47-ea69588da569","29563d77-6e4d-40b2-8845-b1496e460fad","37599b0d-d64a-41e9-92b5-bfeec4e5e6b6","3ee3d362-630f-49e6-80a6-1b3e9177817b","42efb43b-658e-4771-8ad4-b01d658a677b","44f16eb0-565f-41d0-9105-aa95b3a658c7","452f7343-5257-4d82-9d5d-b633e4b0af6f","630a67d3-6df6-4088-abbb-cce84aca5898","6f95548f-43a6-456f-80df-a3f564477b5c","931b4954-8962-41a7-a656-4cacee6a43bc","bcd85e18-8926-4a3c-9e9c-78da9dba2670","d536cf5a-f5a8-4dd9-8679-3488fab17fdf","df0ac0a4-e348-4130-b6a3-eb0552816f81","e8cce97a-163b-4814-b435-8fc26466e550"))
      for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))n.add(old+suffix);
    return Set.copyOf(n);
  }
  static boolean parentValue(Map<String,String> p){
    return p!=null && p.keySet().equals(Pg410KnownAuthRecovery.FIELDS) && p.values().stream().noneMatch(Objects::isNull)
      && PARENT.equals(p.get("InvocationID")) && "timeout".equals(p.get("Result"))
      && "1".equals(p.get("ExecMainCode")) && "143".equals(p.get("ExecMainStatus"))
      && "failed".equals(p.get("ActiveState")) && "failed".equals(p.get("SubState"))
      && "0".equals(p.get("MainPID")) && "0".equals(p.get("ControlPID")) && "".equals(p.get("Job"));
  }
  static boolean retainRequired(String at,boolean mutated,Throwable failure){
    Objects.requireNonNull(at);Objects.requireNonNull(failure);
    return mutated || at.endsWith("_CLOSE") || failure.getSuppressed().length!=0;
  }
  static void retain(String owners){
    System.err.println("PG496_UNKNOWN phase="+phase+" retained="+owners+" oldCloseNotInferred=true diagnosticsRedacted=true");
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}
  }
  static void parent()throws Exception{
    var p=Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values();require(parentValue(p));
    require(!Files.exists(Path.of("/proc/3905484"),LinkOption.NOFOLLOW_LINKS)
      && Long.parseLong(p.get("ExecMainStartTimestampMonotonic"))==255346663838L
      && Long.parseLong(p.get("ExecMainExitTimestampMonotonic"))>=255346663838L);
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
    require(p.equals(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values()));
  }
  static void configureSigned(){
    Pg387TrustedDeployment.LABEL="PG489";Pg387TrustedDeployment.STEM="pg489";
    Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG489");
    // Immutable helper's schema setter supports only 025/027; approved SSC202 is exactly 28 SQL/29 history.
    Pg387TrustedDeployment.expectedSqlCount=28;
  }
  static void signed()throws Exception{
    configureSigned();var v=Pg387TrustedDeployment.verify();
    require(v.manifestSha256().equals(DIGEST) && Arrays.equals(v.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
      && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
  }
  static Set<String> actualNames()throws Exception{
    try(var s=Files.list(STARTUP)){return s.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toUnmodifiableSet());}
  }
  static void pending(StartupPermitRecords.Epoch epoch,Connection db)throws Exception{
    require(epoch.boot().toString().equals(BOOT) && epoch.epoch().toString().equals(EPOCH)
      && epoch.activation().run().id().equals(RUN) && epoch.activation().id().equals(ACTIVATION)
      && epoch.activation().run().cutoff().equals(java.time.Instant.parse("2026-10-06T12:06:14.564793Z")));
    require(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty()
      && new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent());
  }
  static void helper(String action)throws Exception{
    Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/python3","-B",TOOLS.resolve("pg496_timeout_owned.py").toString(),action);
  }
  static Map<String,Pg456SignedMigration.Data> business(Connection db)throws Exception{
    var result=new TreeMap<>(Pg456SignedMigration.business(db));
    var hash=java.security.MessageDigest.getInstance("SHA-256");long count=0;
    try(var q=db.createStatement()){
      q.setQueryTimeout(5);
      try(var rows=q.executeQuery("select row_value from (select to_jsonb(t)::text collate \"C\" row_value from schubert_web_session.web_receipt_references t) snapshot order by row_value")){
        while(rows.next()){
          byte[] bytes=Objects.requireNonNull(rows.getString(1)).getBytes(StandardCharsets.UTF_8);
          hash.update(java.nio.ByteBuffer.allocate(4).putInt(bytes.length).array());hash.update(bytes);Arrays.fill(bytes,(byte)0);count++;
        }
      }
    }
    require(result.put("schubert_web_session.web_receipt_references",new Pg456SignedMigration.Data(count,HexFormat.of().formatHex(hash.digest())))==null && result.keySet().equals(businessTableNames()));
    return Map.copyOf(result);
  }
  static Set<String> businessTableNames(){
    var names=new HashSet<>(Pg456SignedMigration.TABLES);require(names.size()==23);
    require(names.add("schubert_web_session.web_receipt_references") && names.size()==24);return Set.copyOf(names);
  }
  static void save(String name,String data)throws Exception{
    require(name!=null && name.matches("[a-z-]+\\.private") && data!=null);
    byte[] bytes=data.getBytes(StandardCharsets.UTF_8);
    try(var f=java.nio.channels.FileChannel.open(SAVE.resolve(name),Set.of(StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS),
        java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")))){
      var b=java.nio.ByteBuffer.wrap(bytes);while(b.hasRemaining())f.write(b);f.force(true);
    }
    try(var directory=java.nio.channels.FileChannel.open(SAVE,StandardOpenOption.READ)){directory.force(true);}
    require(Arrays.equals(bytes,Files.readAllBytes(SAVE.resolve(name))));
  }
  static void prepareDatabases(Connection db,Connection schema)throws Exception{
    Objects.requireNonNull(db);Objects.requireNonNull(schema);
    // DAO contract is RW/READ_COMMITTED/AC=false; this tool issues no business writes.
    db.setClientInfo("ApplicationName","PG496-fixed-recovery");schema.setClientInfo("ApplicationName","PG496-fixed-snapshot");
    db.setReadOnly(false);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
    require(db.getTransactionIsolation()==Connection.TRANSACTION_READ_COMMITTED && !db.isReadOnly() && !db.getAutoCommit()
      && schema.isReadOnly() && !schema.getAutoCommit());
  }
  static void body(boolean verify,OwnedTransferDirectory root,Connection db,Connection schema)throws Exception{
    phase="CURRENT_NAMESPACE";
    var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
    require(epoch.state()==StartupPermitRecords.State.ISSUED && actualNames().equals(names()) && names().size()==73);phase="PENDING_ORIGINAL";pending(epoch,db);
    phase="ISSUED_PERMIT";
    var permit=files.readIssued();require(permit.releaseDigest().equals(DIGEST));
    phase="ORIGINAL_BACKUP_SNAPSHOT";
    var originals=Pg428ColdBootPreparation.original();var backups=Pg481NativeStop.backup();
    phase="ALL24_DATABASE_SNAPSHOT";
    var data=business(schema);require(data.get("schubert.batch_runs").rows()==442);
    phase="STARTUP_RAW_SNAPSHOT";
    var startup=new TreeMap<String,byte[]>();var metadata=new TreeMap<String,Map<String,Object>>();
    for(String name:names()){
      var p=STARTUP.resolve(name);startup.put(name,Pg410KnownAuthRecovery.material(p,4096));metadata.put(name,Pg410KnownAuthRecovery.metadata(p));
    }
    phase="HELPER_LIVE_VERIFY";helper("verify");parent();signed();pending(epoch,db);
    phase="BEFORE_PRESERVATION";
    require(originals.equals(Pg428ColdBootPreparation.original()) && backups.equals(Pg481NativeStop.backup()) && data.equals(business(schema)));
    if(verify)return;
    Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
    save("original-before.private",originals.toString());
    save("backup-before.private",backups.toString());
    save("business-before.private",data.toString());
    helper("capture");phase="REVERSE_STOP";touched=true;
    // The helper authenticates the fixed generation immediately before issuing each stop.
    // It skips already quiescent same-generation units and records full TERM/native witnesses.
    for(var unit:MaintenanceUnit.values()){parent();helper("stop:"+unit.serviceName());}
    Pg387TrustedDeployment.terminalAll();helper("terminal");parent();signed();pending(epoch,db);
    require(epoch.equals(files.current()) && actualNames().equals(names())
      && originals.equals(Pg428ColdBootPreparation.original()) && backups.equals(Pg481NativeStop.backup()) && data.equals(business(schema)));
    for(var e:startup.entrySet())require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(e.getKey()),4096))
      && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(STARTUP.resolve(e.getKey()))));
    var invalid=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,epoch.boot(),epoch.epoch(),epoch.activation(),Optional.empty());
    phase="CANONICAL_REVOKE";require(files.revoke(invalid,permit).equals(invalid));
    helper("revoked");parent();signed();pending(invalid,db);
    require(invalid.equals(files.current()) && actualNames().equals(names())
      && originals.equals(Pg428ColdBootPreparation.original()) && backups.equals(Pg481NativeStop.backup()) && data.equals(business(schema)));
    for(var e:startup.entrySet())if(!e.getKey().equals("epoch.current"))require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(e.getKey()),4096))
      && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(STARTUP.resolve(e.getKey()))));
    save("body-complete.private","parentTimeout143=true\noldCloseNotInferred=true\nintentsRetired0=true\ncurrentSameEpochInvalid=true\nall24TablesPreserved=true\nallNewScopesNotYetReturned=true\n");
  }
  public static void main(String[] args)throws Exception{
    require(args.length==1 && Set.of("verify","recover").contains(args[0]));boolean verify=args[0].equals("verify");
    require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS)
      && Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT)
      && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    Thread.currentThread().setUncaughtExceptionHandler((thread,failure)->{
      System.err.println("PG496_REFUSED phase="+phase+" type="+failure.getClass().getName()+" diagnosticsRedacted=true");
      for(var frame:failure.getStackTrace())System.err.println("PG496_FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
    });
    try{
      require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
        try{
          phase="M_PARENT";parent();phase="M_SIGNED";signed();
          require(StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()->{
            try{
              phase="A_DATABASE_OPEN";
              try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);
                  var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
                try{
                  phase="DATABASE_BODY";prepareDatabases(db,schema);
                  try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
                  body(verify,root,db,schema);db.rollback();schema.rollback();phase="DATABASE_SCOPE_CLOSE";
                }catch(Exception|Error failure){
                  // Catch BEFORE try-with-resources unwinds: these are genuinely held owners.
                  if(retainRequired(phase,touched,failure))retain("M_A_DATABASE_ROOT");throw failure;
                }
              }
              phase="A_SCOPE_CLOSE";return Boolean.TRUE;
            }catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain("M_A_DATABASE_ROOT_UNKNOWN");throw failure;}
          })).orElseThrow());
          phase="M_SCOPE_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){if(retainRequired(phase,touched,failure))retain("M_A_UNKNOWN");throw failure;}
      })).orElseThrow());
    }catch(Exception|Error failure){
      // An outer close may already have returned/released: do not claim ownership here.
      if(retainRequired(phase,touched,failure))retain("NONE_CONFIRMED_PROCESS_QUARANTINED");throw failure;
    }
    phase="RETURNED";
    if(!verify)save("complete.private","allNewScopesReturnedNormally=true\noldCloseNotInferred=true\nintentsRetired0=true\ncurrentSameEpochInvalid=true\nstarts0=true\n");
    System.out.println("PG496_RECOVERY verifyOnly="+verify+" actualNormalReturn=true oldCloseNotInferred=true starts0=true formalAccepted=false");
  }
}
