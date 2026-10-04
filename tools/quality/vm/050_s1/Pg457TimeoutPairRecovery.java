import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.FileTime;
import java.sql.Connection;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC179/QA047: only the privately captured PG456 timeout143/owned stop143 generation.
 * Reuses canonical revoke and typed Pair quarantine/retirement, never old normal30 authority.
 * No start/deploy/migration/new epoch/new permit/original completion or historical close claim.
 */
public final class Pg457TimeoutPairRecovery {
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static final String CAPTURE_SHA="c9a01ff80c118373f474e0d1993f72601808d4cc4bbbc8227b62714ca7edf215";
  static final Path STARTUP=Pg457OwnedIsolation.STARTUP;
  static final Path CAPTURE=Path.of("/var/lib/pgpt-s1-preservation/pg457-parent-timeout-private");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg457-timeout-pair-recovery");
  static final List<InspectorUnitSnapshot.Target> ROLES=List.of(InspectorUnitSnapshot.Target.MORNING,InspectorUnitSnapshot.Target.API,InspectorUnitSnapshot.Target.WEB);
  static final String[] INV={"0735b37478204b49a5b2810c882ee3be","0f254ac7a80844afb0fef3c8654cb5ab","8c9f2c9605034ed78b0ed2a7c0e5f93e"};
  static final long[] PID={19114,142079,143932};
  static String stage="ARGUMENTS";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed timeout recovery proof differs");}
  static Set<String> names(StartupPermitRecords.Epoch e,boolean quarantined) {
    var n=new HashSet<>(List.of("epoch.current",e.epoch()+".permit",e.epoch()+".owner",e.epoch()+".API.launch",e.epoch()+".WEB.launch",e.epoch()+".API.start.intent",e.epoch()+".WEB.start.intent"));
    if(quarantined)n.add("permit-start.intent");return Set.copyOf(n);
  }
  static Set<String> actualNames() throws Exception {
    try(var paths=Files.list(STARTUP)){return paths.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toUnmodifiableSet());}
  }
  static int retirementStage(Set<String> actual,UUID epoch,int prior) {
    Objects.requireNonNull(actual);Objects.requireNonNull(epoch);require(prior>=0 && prior<=3);
    var allowed=new HashSet<>(List.of("epoch.current",epoch+".permit",epoch+".owner",epoch+".API.launch",epoch+".WEB.launch",epoch+".API.start.intent",epoch+".WEB.start.intent","permit-start.intent"));
    String[] reverse={epoch+".WEB.start.intent",epoch+".API.start.intent","permit-start.intent"};
    for(int i=0;i<prior;i++)allowed.remove(reverse[i]);
    if(actual.equals(allowed))return prior;
    if(prior<3){allowed.remove(reverse[prior]);if(actual.equals(allowed))return prior+1;}
    throw new IllegalStateException("retirement namespace phase differs");
  }
  static void quarantineAfterUnknown(Throwable primary,Pg387TrustedDeployment.Checked<Boolean> work) {
    Objects.requireNonNull(primary);Objects.requireNonNull(work);
    try{require(Boolean.TRUE.equals(work.execute()));}catch(Exception|Error secondary){if(primary!=secondary)primary.addSuppressed(secondary);diagnostic(secondary);}
  }
  static Map<String,String> launch(byte[] raw) {
    Objects.requireNonNull(raw);String text=new String(raw,StandardCharsets.US_ASCII);
    require(Arrays.equals(raw,text.getBytes(StandardCharsets.US_ASCII)) && raw.length<=1024);
    String[] lines=text.split("\n",-1),keys={"service","boot","epoch","permit_sha256","owner_sha256","invocation","pid","start_ticks"};
    require(lines.length==10 && lines[0].equals("NKLAUNCH1") && lines[9].isEmpty());
    var result=new LinkedHashMap<String,String>();
    for(int i=0;i<keys.length;i++){String prefix=keys[i]+"=";require(lines[i+1].startsWith(prefix));result.put(keys[i],lines[i+1].substring(prefix.length()));}
    require(Set.of("API","WEB").contains(result.get("service")));
    for(String k:List.of("boot","epoch")){String v=result.get(k);require(UUID.fromString(v).toString().equals(v) && !v.equals("00000000-0000-0000-0000-000000000000"));}
    for(String k:List.of("permit_sha256","owner_sha256"))require(result.get(k).matches("[0-9a-f]{64}"));
    require(result.get("invocation").matches("[0-9a-f]{32}") && !result.get("invocation").equals("0".repeat(32)));
    for(String k:List.of("pid","start_ticks"))require(result.get(k).matches("[1-9][0-9]*") && Long.parseLong(result.get(k))>0);
    return Map.copyOf(result);
  }
  static boolean terminal(Map<String,String> value,int role) {
    if(value==null || role<0 || role>=3 || !value.keySet().equals(Pg410KnownAuthRecovery.FIELDS) || value.values().stream().anyMatch(Objects::isNull))return false;
    try {
      return value.get("Id").equals(ROLES.get(role).unit()) && value.get("LoadState").equals("loaded")
          && value.get("ActiveState").equals("failed") && value.get("SubState").equals("failed")
          && value.get("InvocationID").equals(INV[role]) && value.get("Job").isEmpty()
          && value.get("MainPID").equals("0") && value.get("ControlPID").equals("0")
          && value.get("ExecMainCode").equals("1") && value.get("ExecMainStatus").equals("143")
          && value.get("Result").equals(role==0?"timeout":"exit-code")
          && value.get("KillMode").equals("control-group") && value.get("SendSIGKILL").equals("no")
          && value.get("Restart").equals(role==0?"no":"on-failure") && value.get("RemainAfterExit").equals("no")
          && value.get("Type").equals(role==0?"oneshot":"simple")
          && Long.parseLong(value.get("ExecMainStartTimestampMonotonic"))>0
          && Long.parseLong(value.get("ExecMainExitTimestampMonotonic"))>=Long.parseLong(value.get("ExecMainStartTimestampMonotonic"));
    } catch(NumberFormatException malformed){return false;}
  }
  static byte[] privateBytes(Path p,long maximum,int mode) throws Exception {
    var m=Pg410KnownAuthRecovery.metadata(p);require(Integer.valueOf(0).equals(m.get("uid")) && Integer.valueOf(0).equals(m.get("gid")) && Integer.valueOf(0100000|mode).equals(m.get("mode")));
    return Pg410KnownAuthRecovery.material(p,maximum);
  }
  static void capture() throws Exception {
    var d=Pg410KnownAuthRecovery.metadata(CAPTURE);require(Integer.valueOf(0).equals(d.get("uid")) && Integer.valueOf(0040700).equals(d.get("mode")));
    var hashes=new TreeMap<String,String>();
    try(var entries=Files.list(CAPTURE)){for(var p:entries.toList())hashes.put(p.getFileName().toString(),Pg410KnownAuthRecovery.hash(privateBytes(p,2097152,0600)));}
    require(hashes.size()==21 && CAPTURE_SHA.equals(Pg410KnownAuthRecovery.hash(new Gson().toJson(hashes).getBytes(StandardCharsets.UTF_8))));
    require(d.equals(Pg410KnownAuthRecovery.metadata(CAPTURE)));
  }
  static void originalMetadata() throws Exception {
    var json=JsonParser.parseString(new String(privateBytes(CAPTURE.resolve("startup-original-metadata.private.json"),1048576,0600),StandardCharsets.UTF_8)).getAsJsonObject();
    for(var entry:json.entrySet()) {
      Path p=Path.of(entry.getKey());require(p.startsWith(STARTUP) || p.startsWith(Path.of("/var/lib/schubert-nk/maintenance")));
      var expected=entry.getValue().getAsJsonObject();var actual=Pg410KnownAuthRecovery.metadata(p);
      for(String k:List.of("dev","ino","mode","uid","gid","nlink","size"))require(expected.get(k).getAsLong()==((Number)actual.get(k)).longValue());
      require(expected.get("ctimeNs").getAsLong()==((FileTime)actual.get("ctime")).to(TimeUnit.NANOSECONDS)
          && expected.get("mtimeNs").getAsLong()==((FileTime)actual.get("lastModifiedTime")).to(TimeUnit.NANOSECONDS));
      if(expected.has("sha256"))require(expected.get("sha256").getAsString().equals(Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(p,1048576))));
    }
  }
  static void physical(List<Pg410KnownAuthRecovery.Receipt> receipts) throws Exception {
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));
    var before=stopSet();Pg387TrustedDeployment.terminalAll();
    for(int i=0;i<3;i++) {
      var now=Pg410KnownAuthRecovery.show(ROLES.get(i));require(terminal(now.values(),i) && now.values().equals(receipts.get(i).values()));
      require(!Files.exists(Path.of("/proc",Long.toString(PID[i])),LinkOption.NOFOLLOW_LINKS));
      Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",ROLES.get(i).unit()));
    }
    for(var unit:MaintenanceUnit.values())Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit.serviceName()));
    var after=stopSet();for(var unit:MaintenanceUnit.values())require(before.get(unit).matches(after.get(unit)));
  }
  static Map<MaintenanceUnit,MaintenanceStopSnapshot> stopSet() throws Exception {
    var result=new EnumMap<MaintenanceUnit,MaintenanceStopSnapshot>(MaintenanceUnit.class);
    for(var unit:MaintenanceUnit.values()) {
      byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",unit.serviceName(),"--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,Slice,Delegate,ControlGroup,InvocationID,StateChangeTimestampMonotonic");
      var value=MaintenanceStopSnapshot.parse(unit,raw);require(value.quiescent());result.put(unit,value);
    }
    return Map.copyOf(result);
  }
  static void signed() throws Exception {
    Pg456SignedMigration.configure(Pg457OwnedIsolation.SOURCE);var a=Pg387TrustedDeployment.verify();
    require(a.manifestSha256().equals(Pg457OwnedIsolation.DIGEST) && Arrays.equals(a.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
  }
  static void save(String name,byte[] raw) throws Exception {
    Path p=SAVE.resolve(name);Files.write(p,raw,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var c=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){c.force(true);}
    require(Arrays.equals(raw,privateBytes(p,2097152,0600)));
  }
  static MaintenanceOwnerFrame.Parent child(Map<String,String> v,int i,StartupPermitRecords.Epoch e,MaintenanceOwnerFrame owner,byte[] ownerRaw) throws Exception {
    require(v.get("service").equals(i==1?"API":"WEB") && v.get("boot").equals(BOOT) && v.get("epoch").equals(e.epoch().toString())
        && v.get("permit_sha256").equals(e.permitDigest().orElseThrow()) && v.get("owner_sha256").equals(Pg410KnownAuthRecovery.hash(ownerRaw))
        && v.get("invocation").equals(INV[i]) && v.get("pid").equals(Long.toString(PID[i])));
    var old=Pg410KnownAuthRecovery.parsed(privateBytes(CAPTURE.resolve("unit-"+i+"-before.properties"),4096,0600),ROLES.get(i)).values();
    require(old.get("InvocationID").equals(INV[i]) && old.get("MainPID").equals(Long.toString(PID[i])) && old.get("ActiveState").equals("active") && old.get("SubState").equals("running") && old.get("Job").isEmpty());
    Path prefix=CAPTURE.resolve(i==1?"api":"web");
    var identity=Pg457OwnedIsolation.identity(privateBytes(Path.of(prefix+"-status.private"),65536,0600));
    var fixed=new FixedServiceIdentity().resolve(i==1?ServiceConfigFiles.Service.API:ServiceConfigFiles.Service.WEB);
    require(identity.get("Uid").replaceAll("\\s+"," ").equals(String.join(" ",Collections.nCopies(4,Long.toString(fixed.uid()))))
        && identity.get("Gid").replaceAll("\\s+"," ").equals(String.join(" ",Collections.nCopies(4,Long.toString(fixed.gid()))))
        && identity.get("Groups").replaceAll("\\s+"," ").equals(String.join(" ",fixed.groups().stream().map(Object::toString).toList())) && identity.get("NoNewPrivs").equals("1"));
    for(String cap:List.of("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))require(identity.get(cap).equals("0000000000000000"));
    String stat=new String(privateBytes(Path.of(prefix+"-stat.private"),65536,0600),StandardCharsets.US_ASCII);
    long ticks=Long.parseLong(stat.substring(stat.lastIndexOf(')')+2).split(" ")[19]);require(v.get("start_ticks").equals(Long.toString(ticks)));
    String argv=new String(privateBytes(Path.of(prefix+"-cmdline.private"),65536,0600),StandardCharsets.US_ASCII);
    String main=i==1?"dev.codex.schubert.nk.api.bootstrap.ApiProcessMain":"dev.codex.schubert.nk.web.bootstrap.WebProcessMain";
    require(Arrays.stream(argv.split("\u0000",-1)).filter(main::equals).count()==1 && new String(privateBytes(Path.of(prefix+"-cgroup.private"),65536,0600),StandardCharsets.US_ASCII).equals("0::/system.slice/"+ROLES.get(i).unit()+"\n"));
    require(!owner.morning().invocation().equals(INV[i]) && owner.morning().pid()!=PID[i]);
    return new MaintenanceOwnerFrame.Parent(INV[i],PID[i],ticks);
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->diagnostic(e));
    require((args.length==0 || (args.length==1 && args[0].equals("verify"))) && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    boolean verifyOnly=args.length==1;
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      stage="M_CAPTURE";capture();Pg457OwnedIsolation.parent();
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        stage="A_FULL_STOP";var receipts=new ArrayList<Pg410KnownAuthRecovery.Receipt>();for(var r:ROLES)receipts.add(Pg410KnownAuthRecovery.show(r));physical(receipts);signed();originalMetadata();
        boolean[] mutating={false};
        RootFailedStartRecovery.PairEvidence[] borrowedPair={null};
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          schema.setReadOnly(true);
          stage="DB_PREPARE";db.setAutoCommit(false);try(var s=db.createStatement();var r=s.executeQuery("select pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          stage="CURRENT_READ";var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var issued=files.current();require(issued.state()==StartupPermitRecords.State.ISSUED && actualNames().equals(names(issued,false)));
          stage="PERMIT_READ";var permit=files.readIssued();require(permit.releaseDigest().equals(Pg457OwnedIsolation.DIGEST) && issued.boot().toString().equals(BOOT)
              && issued.activation().run().id().equals(Pg407FailedRootRecovery.RUN) && issued.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION));
          stage="ORIGINAL_SNAPSHOT";var original=Pg428ColdBootPreparation.original();stage="BACKUP_SNAPSHOT";var backup=Pg428ColdBootPreparation.backupSnapshot();stage="FIXTURE_SNAPSHOT";var fixture=Pg428ColdBootPreparation.fixtureSnapshot();stage="DB_ROWS";var rows=Pg407FailedRootRecovery.databaseRows(db);stage="DB_BUSINESS";var business=Pg456SignedMigration.business(schema);require(rows.size()==261);
          var startup=new TreeMap<String,byte[]>();var metadata=new TreeMap<String,Map<String,Object>>();
          for(String n:actualNames()){startup.put(n,Pg410KnownAuthRecovery.material(STARTUP.resolve(n),4096));metadata.put(n,Pg410KnownAuthRecovery.metadata(STARTUP.resolve(n)));}
          stage="OWNER_LAUNCH_CAPTURE";var owner=MaintenanceOwnerFrame.consume(startup.get(issued.epoch()+".owner").clone());require(owner.cleanup().isEmpty() && owner.boot().equals(issued.boot()) && owner.epoch().equals(issued.epoch())
              && owner.run().equals(issued.activation().run().id()) && owner.activation().equals(issued.activation().id()) && owner.cutoff().equals(issued.activation().run().cutoff())
              && owner.morning().pid()==PID[0] && owner.morning().invocation().equals(INV[0]));
          var invalid=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,issued.boot(),issued.epoch(),issued.activation(),Optional.empty());
          var api=child(launch(startup.get(issued.epoch()+".API.launch")),1,issued,owner,startup.get(issued.epoch()+".owner"));
          var web=child(launch(startup.get(issued.epoch()+".WEB.launch")),2,issued,owner,startup.get(issued.epoch()+".owner"));
          for(int i=0;i<3;i++){var old=Pg410KnownAuthRecovery.parsed(privateBytes(CAPTURE.resolve("unit-"+i+"-before.properties"),4096,0600),ROLES.get(i));
            if(i==0)require(old.values().equals(receipts.get(i).values()));else require(old.values().get("ExecMainStartTimestampMonotonic").equals(receipts.get(i).values().get("ExecMainStartTimestampMonotonic")));}
          var pair=new RootFailedStartRecovery.PairEvidence(new RootFailedStartRecovery.Evidence(invalid,permit,issued.permitDigest().orElseThrow(),owner,ServiceConfigFiles.Service.API,api),new RootFailedStartRecovery.Evidence(invalid,permit,issued.permitDigest().orElseThrow(),owner,ServiceConfigFiles.Service.WEB,web));
          borrowedPair[0]=pair;
          stage="ORIGINAL_SESSION";require(MaintenanceRunFiles.create().execute(s->s.observeStartup(issued.activation())).completed().isEmpty() && new RunReferenceRepository(db).read(issued.activation().run()).identityConsistent());
          stage="PRESERVATION_GATE";capture();originalMetadata();physical(receipts);signed();require(issued.equals(files.current()));
          require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
          require(MaintenanceRunFiles.create().execute(s->s.observeStartup(issued.activation())).completed().isEmpty() && new RunReferenceRepository(db).read(issued.activation().run()).identityConsistent());
          require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
          if(verifyOnly){db.rollback();stage="VERIFY_OWNED_CLOSE";return Boolean.TRUE;}
          Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
          for(var e:startup.entrySet())save(e.getKey(),e.getValue());for(int i=0;i<3;i++)save("terminal-"+i+".properties",receipts.get(i).raw());
          save("original-before.private",original.toString().getBytes(StandardCharsets.UTF_8));save("backup-before.private",backup.toString().getBytes(StandardCharsets.UTF_8));save("rows-before.private",rows.toString().getBytes(StandardCharsets.UTF_8));save("fixture-before.private",fixture.getBytes(StandardCharsets.UTF_8));Pg387TrustedDeployment.sync(SAVE);Pg387TrustedDeployment.sync(SAVE.getParent());
          stage="PRESERVATION_GATE";capture();originalMetadata();physical(receipts);signed();require(issued.equals(files.current()));
          require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
          require(MaintenanceRunFiles.create().execute(s->s.observeStartup(issued.activation())).completed().isEmpty() && new RunReferenceRepository(db).read(issued.activation().run()).identityConsistent());
          try {
            mutating[0]=true;stage="SAME_EPOCH_REVOKE";require(invalid.equals(files.revoke(invalid,permit)));
            stage="PUBLICATION_FIRST_QUARANTINE";RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),pair);require(actualNames().equals(names(issued,true)) && pair.equals(RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create())));
            stage="TYPED_PAIR_RETIRE";
            int[] retired={0};
            RootFailedStartRecovery.retirePair(root,LinuxInodeSecurity.create(),pair,expected->Pg387TrustedDeployment.checked(()-> {
              require(expected.equals(pair) && invalid.equals(files.current()));physical(receipts);signed();capture();
              retired[0]=retirementStage(actualNames(),issued.epoch(),retired[0]);
              require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
              require(MaintenanceRunFiles.create().execute(s->s.observeStartup(issued.activation())).completed().isEmpty());
              for(var e:startup.entrySet())if(!e.getKey().equals("epoch.current") && !e.getKey().endsWith(".start.intent"))require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(e.getKey()),4096)) && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(STARTUP.resolve(e.getKey()))));
              return Boolean.TRUE;
            }));
            stage="POSTCONDITIONS";physical(receipts);signed();require(invalid.equals(files.current()) && retired[0]==3);var expected=new HashSet<>(names(issued,false));expected.remove(issued.epoch()+".API.start.intent");expected.remove(issued.epoch()+".WEB.start.intent");require(actualNames().equals(expected));
            require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
            save("recovery-complete.private","actualTimeout143=true\nnormalExitClaimed=false\nsameEpochRevoked=true\ntypedThreeIntentsRetired=true\nnewPermitIssued=false\noriginalPending=true\nall261Preserved=true\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);db.rollback();
          } catch(Exception|Error unknown) {
            diagnostic(unknown);stage="RE_QUARANTINE";quarantineAfterUnknown(unknown,()->{RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),pair);return Boolean.TRUE;});retain();
          }
        } catch(Exception|Error ownershipUnknown){
          diagnostic(ownershipUnknown);
          if(!mutating[0] && !stage.equals("VERIFY_OWNED_CLOSE") && ownershipUnknown.getSuppressed().length==0)throw ownershipUnknown;
          if(mutating[0] && borrowedPair[0]!=null){stage="OWNED_CLOSE_RE_QUARANTINE";quarantineAfterUnknown(ownershipUnknown,()->{try(var held=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)){RootFailedStartRecovery.quarantinePair(held,LinuxInodeSecurity.create(),borrowedPair[0]);}return Boolean.TRUE;});}
          retain();
        }
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
    if(verifyOnly)System.out.println("PG457_TIMEOUT_PREFLIGHT_VERIFIED currentIssuedUnchanged=true all261OriginalBackupTransferPreserved=true all9KernelEmpty=true mutation0=true normalExitClaimed=false");
    else System.out.println("PG457_TIMEOUT_PAIR_RECOVERED actualTimeout143=true sameEpochInvalid=true typedThreeIntentsRetired=true all261OriginalBackupTransferPreserved=true all9KernelEmpty=true newPermitIssued=false normalExitClaimed=false missingExternalWebRootStillMissing=true");
  }
  static void diagnostic(Throwable e){String sql=e instanceof java.sql.SQLException s && s.getSQLState()!=null && s.getSQLState().matches("[0-9A-Z]{5}")?s.getSQLState():"NONE";System.err.println("PG457_RECOVERY_REFUSED stage="+stage+" type="+e.getClass().getName()+" sqlState="+sql+" secondaryCount="+e.getSuppressed().length+" diagnosticsRedacted=true");int count=0;for(var f:e.getStackTrace())if((f.getClassName().startsWith("Pg4") || f.getClassName().startsWith("dev.codex.schubert.nk.")) && count++<12)System.err.println("PG457_RECOVERY_FRAME "+f.getClassName()+"."+f.getMethodName()+":"+f.getLineNumber());}
  static void retain(){System.err.println("PG457_RECOVERY_UNKNOWN M_A_RETAINED=true DB_OWNERSHIP_UNCERTAIN=true nextStartQuarantined=true");for(;;)java.util.concurrent.locks.LockSupport.parkNanos(TimeUnit.SECONDS.toNanos(1));}
}
