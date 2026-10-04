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

/** SSC168/QA047: only the privately captured PG458 normal30/owned API-Web143 generation.
 * Reuses canonical revoke and typed Pair quarantine/retirement, never old timeout authority.
 * No start/deploy/migration/new epoch/new permit/original completion or historical close claim.
 */
public final class Pg459Known30PairRecovery {
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static final String CAPTURE_SHA="9733dd823ccdcdd0cdfdaf8e664757220a001262e14c795ae8f7ed9432b0db5a";
  static final Path STARTUP=Pg459OwnedIsolation.STARTUP;
  static final Path CAPTURE=Path.of("/var/lib/pgpt-s1-preservation/pg459-parent-known30-private");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg459-known30-pair-recovery");
  static final List<InspectorUnitSnapshot.Target> ROLES=List.of(InspectorUnitSnapshot.Target.MORNING,InspectorUnitSnapshot.Target.API,InspectorUnitSnapshot.Target.WEB);
  static final String[] INV={"fb3eaf763a8c4a5e8172d3c42f8fc954","386729898874494ebff10f86647d3e3a","5b8cd47d114d465582216725317d6788"};
  static final long[] PID={162624,304687,306804};
  static String stage="ARGUMENTS";
  static Set<String> retainedNames() {
    String old="1eecb7b9-1e98-478f-9084-201422b31bff";
    return Set.of(old+".permit",old+".owner",old+".API.launch",old+".WEB.launch");
  }
  static boolean retainedRecord(String name,UUID epoch) {
    Objects.requireNonNull(name);Objects.requireNonNull(epoch);
    return retainedNames().contains(name) || Set.of("epoch.current",epoch+".permit",epoch+".owner",epoch+".API.launch",epoch+".WEB.launch").contains(name);
  }
  static boolean afterAdmissionFailure(Throwable primary,boolean mutated,Pg387TrustedDeployment.Checked<Boolean> restore) {
    Objects.requireNonNull(primary);Objects.requireNonNull(restore);
    if(!mutated && primary.getSuppressed().length==0)return false;
    if(mutated)quarantineAfterUnknown(primary,restore);
    return true;
  }
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed timeout recovery proof differs");}
  static Set<String> names(StartupPermitRecords.Epoch e,boolean quarantined) {
    var n=new HashSet<>(List.of("epoch.current",e.epoch()+".permit",e.epoch()+".owner",e.epoch()+".API.launch",e.epoch()+".WEB.launch",e.epoch()+".API.start.intent",e.epoch()+".WEB.start.intent"));
    n.addAll(retainedNames());if(quarantined)n.add("permit-start.intent");return Set.copyOf(n);
  }
  static Set<String> actualNames() throws Exception {
    try(var paths=Files.list(STARTUP)){return paths.map(p->p.getFileName().toString()).collect(java.util.stream.Collectors.toUnmodifiableSet());}
  }
  static int retirementStage(Set<String> actual,UUID epoch,int prior) {
    Objects.requireNonNull(actual);Objects.requireNonNull(epoch);require(prior>=0 && prior<=3);
    var allowed=new HashSet<>(List.of("epoch.current",epoch+".permit",epoch+".owner",epoch+".API.launch",epoch+".WEB.launch",epoch+".API.start.intent",epoch+".WEB.start.intent","permit-start.intent"));
    allowed.addAll(retainedNames());
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
          && value.get("ExecMainCode").equals("1") && value.get("ExecMainStatus").equals(role==0?"30":"143")
          && value.get("Result").equals("exit-code")
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
    try(var entries=Files.list(CAPTURE)){for(var p:entries.toList())hashes.put(p.getFileName().toString(),Pg410KnownAuthRecovery.hash(privateBytes(p,4194304,0600)));}
    require(hashes.size()==14 && CAPTURE_SHA.equals(Pg410KnownAuthRecovery.hash(new Gson().toJson(hashes).getBytes(StandardCharsets.UTF_8))));
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
    Pg387TrustedDeployment.expectedSchema("027");
    Pg387TrustedDeployment.LABEL="PG458";Pg387TrustedDeployment.STEM="pg458";Pg387TrustedDeployment.SOURCE=Pg459OwnedIsolation.SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG458");var a=Pg387TrustedDeployment.verify();
    require(a.manifestSha256().equals(Pg459OwnedIsolation.DIGEST) && Arrays.equals(a.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
  }
  static void save(String name,byte[] raw) throws Exception {
    Path p=SAVE.resolve(name);Files.write(p,raw,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var c=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){c.force(true);}
    require(Arrays.equals(raw,privateBytes(p,4194304,0600)));
  }
  static MaintenanceOwnerFrame.Parent child(Map<String,String> v,int i,StartupPermitRecords.Epoch e,MaintenanceOwnerFrame owner,byte[] ownerRaw,String permitSha256) throws Exception {
    require(v.get("service").equals(i==1?"API":"WEB") && v.get("boot").equals(BOOT) && v.get("epoch").equals(e.epoch().toString())
        && v.get("permit_sha256").equals(permitSha256) && v.get("owner_sha256").equals(Pg410KnownAuthRecovery.hash(ownerRaw))
        && v.get("invocation").equals(INV[i]) && v.get("pid").equals(Long.toString(PID[i])));
    Pg459CapturedPeers.watch(privateBytes(CAPTURE.resolve("external-watch.private.jsonl"),4194304,0600));
    long ticks=i==1?8483207:8484334;require(v.get("start_ticks").equals(Long.toString(ticks)));
    require(!owner.morning().invocation().equals(INV[i]) && owner.morning().pid()!=PID[i]);
    return new MaintenanceOwnerFrame.Parent(INV[i],PID[i],ticks);
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->diagnostic(e));
    require((args.length==0 || (args.length==1 && args[0].equals("verify"))) && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    boolean verifyOnly=args.length==1;
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      stage="M_CAPTURE";capture();Pg459OwnedIsolation.parent();
      boolean[] mutating={false};
      RootFailedStartRecovery.PairEvidence[] borrowedPair={null};
      try {
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        stage="A_FULL_STOP";var receipts=new ArrayList<Pg410KnownAuthRecovery.Receipt>();for(var r:ROLES)receipts.add(Pg410KnownAuthRecovery.show(r));physical(receipts);signed();originalMetadata();
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          schema.setReadOnly(true);
          stage="DB_PREPARE";db.setAutoCommit(false);try(var s=db.createStatement();var r=s.executeQuery("select pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          stage="CURRENT_READ";var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var issued=files.current();require(issued.state()==StartupPermitRecords.State.INVALID && issued.epoch().toString().equals("d536cf5a-f5a8-4dd9-8679-3488fab17fdf") && actualNames().equals(names(issued,true)));
          stage="PERMIT_READ";var observed=RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create());require(issued.equals(observed.api().invalid()));var permit=observed.api().permit();require(permit.releaseDigest().equals(Pg459OwnedIsolation.DIGEST) && issued.boot().toString().equals(BOOT)
              && issued.activation().run().id().equals(Pg407FailedRootRecovery.RUN) && issued.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION));
          stage="ORIGINAL_SNAPSHOT";var original=Pg428ColdBootPreparation.original();stage="BACKUP_SNAPSHOT";var backup=Pg428ColdBootPreparation.backupSnapshot();stage="FIXTURE_SNAPSHOT";var fixture=Pg428ColdBootPreparation.fixtureSnapshot();stage="DB_ROWS";var rows=Pg407FailedRootRecovery.databaseRows(db);stage="DB_BUSINESS";var business=Pg456SignedMigration.business(schema);require(rows.size()==271);
          var startup=new TreeMap<String,byte[]>();var metadata=new TreeMap<String,Map<String,Object>>();
          for(String n:actualNames()){startup.put(n,Pg410KnownAuthRecovery.material(STARTUP.resolve(n),4096));metadata.put(n,Pg410KnownAuthRecovery.metadata(STARTUP.resolve(n)));}
          stage="OWNER_LAUNCH_CAPTURE";var owner=MaintenanceOwnerFrame.consume(startup.get(issued.epoch()+".owner").clone());require(owner.cleanup().isEmpty() && owner.boot().equals(issued.boot()) && owner.epoch().equals(issued.epoch())
              && owner.run().equals(issued.activation().run().id()) && owner.activation().equals(issued.activation().id()) && owner.cutoff().equals(issued.activation().run().cutoff())
              && owner.morning().pid()==PID[0] && owner.morning().invocation().equals(INV[0]) && owner.morning().startTicks()==8411500);
          var invalid=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,issued.boot(),issued.epoch(),issued.activation(),Optional.empty());
          var api=child(launch(startup.get(issued.epoch()+".API.launch")),1,issued,owner,startup.get(issued.epoch()+".owner"),observed.api().permitSha256());
          var web=child(launch(startup.get(issued.epoch()+".WEB.launch")),2,issued,owner,startup.get(issued.epoch()+".owner"),observed.api().permitSha256());
          for(int i=0;i<3;i++){var old=Pg410KnownAuthRecovery.parsed(privateBytes(CAPTURE.resolve("unit-"+i+"-before.properties"),4096,0600),ROLES.get(i));
            if(i==0)require(old.values().equals(receipts.get(i).values()));else require(old.values().get("ExecMainStartTimestampMonotonic").equals(receipts.get(i).values().get("ExecMainStartTimestampMonotonic")));}
          var pair=new RootFailedStartRecovery.PairEvidence(new RootFailedStartRecovery.Evidence(invalid,permit,observed.api().permitSha256(),owner,ServiceConfigFiles.Service.API,api),new RootFailedStartRecovery.Evidence(invalid,permit,observed.api().permitSha256(),owner,ServiceConfigFiles.Service.WEB,web));require(pair.equals(observed));
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
            mutating[0]=true;stage="ALREADY_INVALID_RECHECK";require(invalid.equals(files.current()));
            stage="PUBLICATION_FIRST_QUARANTINE";RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),pair);require(actualNames().equals(names(issued,true)) && pair.equals(RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create())));
            stage="TYPED_PAIR_RETIRE";
            int[] retired={0};
            RootFailedStartRecovery.retirePair(root,LinuxInodeSecurity.create(),pair,expected->Pg387TrustedDeployment.checked(()-> {
              require(expected.equals(pair) && invalid.equals(files.current()));physical(receipts);signed();capture();
              retired[0]=retirementStage(actualNames(),issued.epoch(),retired[0]);
              require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
              require(MaintenanceRunFiles.create().execute(s->s.observeStartup(issued.activation())).completed().isEmpty());
              for(var e:startup.entrySet())if(retainedRecord(e.getKey(),issued.epoch()))require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(STARTUP.resolve(e.getKey()),4096)) && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(STARTUP.resolve(e.getKey()))));
              return Boolean.TRUE;
            }));
            stage="POSTCONDITIONS";physical(receipts);signed();require(invalid.equals(files.current()) && retired[0]==3);var expected=new HashSet<>(names(issued,false));expected.remove(issued.epoch()+".API.start.intent");expected.remove(issued.epoch()+".WEB.start.intent");require(actualNames().equals(expected) && expected.size()==9);
            require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
            save("retirement-body.private","actualParentKnownFailure30=true\nnormalExitClaimed=false\ncurrentAlreadyInvalid=true\ntypedThreeIntentsRetired=true\nnewPermitIssued=false\noriginalPending=true\nall271Preserved=true\nouterScopesNotYetClosed=true\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);db.rollback();
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
      } catch(Exception|Error admissionUnknown) {
        stage="POST_ADMISSION_UNKNOWN";diagnostic(admissionUnknown);
        if(afterAdmissionFailure(admissionUnknown,mutating[0],()-> {
          require(borrowedPair[0]!=null);
          return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()-> {
            try(var held=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP)) {
              RootFailedStartRecovery.quarantinePair(held,LinuxInodeSecurity.create(),borrowedPair[0]);
            }
            return Boolean.TRUE;
          })).orElseThrow();
        })) {
          System.err.println("PG459_POST_ADMISSION_UNKNOWN M_RETAINED=true A_OWNERSHIP_NOT_INFERRED=true normalExitClaimed=false");
          for(;;)java.util.concurrent.locks.LockSupport.parkNanos(TimeUnit.SECONDS.toNanos(1));
        }
        throw admissionUnknown;
      }
    })).orElseThrow();
    if(verifyOnly)System.out.println("PG459_KNOWN30_PREFLIGHT_VERIFIED currentInvalidUnchanged=true all271OriginalBackupTransferPreserved=true all9KernelEmpty=true mutation0=true normalExitClaimed=false");
    else {
      save("recovery-complete.private","actualParentKnownFailure30=true\nallOwnedScopesReturnedNormally=true\ntypedThreeIntentsRetired=true\nretainedOldRecordsPreserved=true\nnormalExitClaimed=false\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);
      System.out.println("PG459_KNOWN30_PAIR_RECOVERED actualParentKnownFailure30=true sameEpochInvalid=true typedThreeIntentsRetired=true all271OriginalBackupTransferPreserved=true all9KernelEmpty=true newPermitIssued=false normalExitClaimed=false bothExternalRootsCaptured=true allOwnedScopesReturnedNormally=true");
    }
  }
  static void diagnostic(Throwable e){String sql=e instanceof java.sql.SQLException s && s.getSQLState()!=null && s.getSQLState().matches("[0-9A-Z]{5}")?s.getSQLState():"NONE";System.err.println("PG459_RECOVERY_REFUSED stage="+stage+" type="+e.getClass().getName()+" sqlState="+sql+" secondaryCount="+e.getSuppressed().length+" diagnosticsRedacted=true");int count=0;for(var f:e.getStackTrace())if((f.getClassName().startsWith("Pg4") || f.getClassName().startsWith("dev.codex.schubert.nk.")) && count++<12)System.err.println("PG459_RECOVERY_FRAME "+f.getClassName()+"."+f.getMethodName()+":"+f.getLineNumber());}
  static void retain(){System.err.println("PG459_RECOVERY_UNKNOWN M_A_RETAINED=true DB_OWNERSHIP_UNCERTAIN=true nextStartQuarantined=true");for(;;)java.util.concurrent.locks.LockSupport.parkNanos(TimeUnit.SECONDS.toNanos(1));}
}
