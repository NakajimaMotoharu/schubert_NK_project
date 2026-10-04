import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** QA047/SS343: newly owned limited retirement of PG461 ISSUED/2-intent timeout cohort.
 * Never calls known30 recovery, never restores old owner/budget or declares old close successful.
 * Actual isolation, same signed source, original/301 rows/Backup/old16 preserved under M/A/DB.
 * PT-OPS-RET462001..003; operator is not a Production automatic recovery entry.
 */
public final class Pg462TimeoutRetirement {
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg462-timeout-retirement");
  static String phase="ARGUMENTS";
  static void require(boolean v){if(!v)throw new IllegalStateException("fixed timeout retirement proof differs");}
  static Set<String> retiredNames(){var n=new HashSet<>(Pg462TimeoutIsolation.names());n.remove(Pg462TimeoutIsolation.EPOCH+".API.start.intent");n.remove(Pg462TimeoutIsolation.EPOCH+".WEB.start.intent");return Set.copyOf(n);}
  static Set<String> actualNames() throws Exception {try(var p=Files.list(Pg462TimeoutIsolation.STARTUP)){return p.map(v->v.getFileName().toString()).collect(java.util.stream.Collectors.toUnmodifiableSet());}}
  static void physical() throws Exception {
    Pg462TimeoutIsolation.parent();Pg387TrustedDeployment.terminalAll();
    for(long pid:new long[]{628952,771339,773290,776564})require(!Files.exists(Path.of("/proc",Long.toString(pid)),LinkOption.NOFOLLOW_LINKS));
    for(var unit:MaintenanceUnit.values())Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit.serviceName()));
  }
  static void signed() throws Exception {
    Pg387TrustedDeployment.LABEL="PG461";Pg387TrustedDeployment.STEM="pg461";Pg387TrustedDeployment.SOURCE=Pg462TimeoutIsolation.SOURCE;Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG461");Pg387TrustedDeployment.expectedSchema("027");
    var a=Pg387TrustedDeployment.verify();require(a.manifestSha256().equals(Pg462TimeoutIsolation.DIGEST) && Arrays.equals(a.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))));
  }
  static MaintenanceOwnerFrame.Parent child(byte[] raw,String service,long pid,String invocation,long ticks,StartupPermitRecords.Epoch epoch,MaintenanceOwnerFrame owner,String permitHash,byte[] ownerRaw) throws Exception {
    var v=Pg461Known30PairRecovery.launch(raw);
    require(v.get("service").equals(service) && v.get("boot").equals(Pg462TimeoutIsolation.BOOT) && v.get("epoch").equals(epoch.epoch().toString()) && v.get("invocation").equals(invocation) && v.get("pid").equals(Long.toString(pid)) && v.get("start_ticks").equals(Long.toString(ticks)) && v.get("permit_sha256").equals(permitHash) && v.get("owner_sha256").equals(Pg410KnownAuthRecovery.hash(ownerRaw)));
    require(owner.morning().pid()!=pid && !owner.morning().invocation().equals(invocation));return new MaintenanceOwnerFrame.Parent(invocation,pid,ticks);
  }
  static void save(String name,byte[] raw) throws Exception {
    Path p=SAVE.resolve(name);Files.write(p,raw,StandardOpenOption.CREATE_NEW);Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var f=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){f.force(true);}require(Arrays.equals(raw,Files.readAllBytes(p)));
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println("PG462_RETIREMENT_REFUSED phase="+phase+" type="+e.getClass().getName()+" diagnosticsRedacted=true"));
    require(args.length==1 && Set.of("verify","retire").contains(args[0]));boolean verify=args[0].equals("verify");
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(Pg462TimeoutIsolation.BOOT) && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    boolean[] changed={false};
    try {
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      phase="M_TERMINAL";physical();
      try {
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        phase="A_SIGNED";physical();signed();Pg462TimeoutIsolation.capturedMetadata();
        boolean[] mutating={false};RootFailedStartRecovery.PairEvidence[] heldPair={null};
        try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg462TimeoutIsolation.STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          phase="DB_CAPTURE";schema.setReadOnly(true);db.setAutoCommit(false);
          try(var s=db.createStatement();var r=s.executeQuery("select pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
          var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var issued=files.current();
          require(issued.state()==StartupPermitRecords.State.ISSUED && issued.epoch().toString().equals(Pg462TimeoutIsolation.EPOCH) && issued.boot().toString().equals(Pg462TimeoutIsolation.BOOT) && issued.activation().run().id().equals(Pg407FailedRootRecovery.RUN) && issued.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION) && actualNames().equals(Pg462TimeoutIsolation.names()));
          var permit=files.readIssued();require(permit.releaseDigest().equals(Pg462TimeoutIsolation.DIGEST));
          var startup=new TreeMap<String,byte[]>();var metadata=new TreeMap<String,Map<String,Object>>();for(String name:actualNames()){var p=Pg462TimeoutIsolation.STARTUP.resolve(name);startup.put(name,Pg410KnownAuthRecovery.material(p,4096));metadata.put(name,Pg410KnownAuthRecovery.metadata(p));}
          var ownerRaw=startup.get(issued.epoch()+".owner");var owner=MaintenanceOwnerFrame.consume(ownerRaw.clone());
          require(owner.cleanup().isEmpty() && owner.boot().equals(issued.boot()) && owner.epoch().equals(issued.epoch()) && owner.run().equals(issued.activation().run().id()) && owner.activation().equals(issued.activation().id()) && owner.cutoff().equals(issued.activation().run().cutoff()) && owner.morning().pid()==628952 && owner.morning().invocation().equals(Pg462TimeoutIsolation.PARENT) && owner.morning().startTicks()==9934910);
          var invalid=new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,issued.boot(),issued.epoch(),issued.activation(),Optional.empty());String hash=issued.permitDigest().orElseThrow();
          var api=child(startup.get(issued.epoch()+".API.launch"),"API",771339,"bbf96d392f424aa195e8cceb80d02115",10008163,issued,owner,hash,ownerRaw);
          var web=child(startup.get(issued.epoch()+".WEB.launch"),"WEB",773290,"6c6d91f9022c47aa86cb9d7eea8f0bd7",10009411,issued,owner,hash,ownerRaw);
          var pair=new RootFailedStartRecovery.PairEvidence(new RootFailedStartRecovery.Evidence(invalid,permit,hash,owner,ServiceConfigFiles.Service.API,api),new RootFailedStartRecovery.Evidence(invalid,permit,hash,owner,ServiceConfigFiles.Service.WEB,web));heldPair[0]=pair;
          var original=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();var fixture=Pg428ColdBootPreparation.fixtureSnapshot();var rows=Pg407FailedRootRecovery.databaseRows(db);var business=Pg456SignedMigration.business(schema);
          require(rows.size()==301 && MaintenanceRunFiles.create().execute(s->s.observeStartup(issued.activation())).completed().isEmpty() && new RunReferenceRepository(db).read(issued.activation().run()).identityConsistent());
          if(!verify){
            require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));Files.createDirectory(SAVE);Files.setPosixFilePermissions(SAVE,java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
            for(var entry:startup.entrySet())save(entry.getKey(),entry.getValue());Pg387TrustedDeployment.sync(SAVE);
            phase="CANONICAL_REVOKE";mutating[0]=true;changed[0]=true;require(invalid.equals(files.revoke(invalid,permit)));
            phase="PUBLICATION_FIRST_QUARANTINE";RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),pair);require(pair.equals(RootFailedStartRecovery.observePair(root,LinuxInodeSecurity.create())));
            phase="TYPED_RETIREMENT";RootFailedStartRecovery.retirePair(root,LinuxInodeSecurity.create(),pair,expected->Pg387TrustedDeployment.checked(()-> {
              require(expected.equals(pair) && invalid.equals(files.current()));physical();signed();
              require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
              require(MaintenanceRunFiles.create().execute(s->s.observeStartup(issued.activation())).completed().isEmpty());
              for(var entry:startup.entrySet())if(!entry.getKey().equals("epoch.current") && !entry.getKey().endsWith(".start.intent")){Path p=Pg462TimeoutIsolation.STARTUP.resolve(entry.getKey());require(Arrays.equals(entry.getValue(),Pg410KnownAuthRecovery.material(p,4096)) && metadata.get(entry.getKey()).equals(Pg410KnownAuthRecovery.metadata(p)));}
              return Boolean.TRUE;
            }));
            phase="POSTCONDITIONS";require(invalid.equals(files.current()) && retiredNames().size()==21 && actualNames().equals(retiredNames()));physical();signed();
            require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
            save("body.private","oldParentTimeout143=true\noldNormalReturnClaimed=false\noriginalPending=true\nrows301Preserved=true\ntypedIntentsRetired=true\ncurrentInvalid=true\nnewPermitIssued=false\nouterScopesNotYetReturned=true\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);
          }
          phase="OWNED_CLOSE";db.rollback();
        } catch(Exception|Error unknown){
          if(mutating[0] || unknown.getSuppressed().length>0){System.err.println("PG462_RETIREMENT_UNKNOWN oldCloseClaimed=false newOwnersRetained=true diagnosticsRedacted=true");if(mutating[0] && heldPair[0]!=null){try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg462TimeoutIsolation.STARTUP)){RootFailedStartRecovery.quarantinePair(root,LinuxInodeSecurity.create(),heldPair[0]);}catch(Exception|Error quarantineUnknown){System.err.println("PG462_RETIREMENT_REQUARANTINE_UNKNOWN diagnosticsRedacted=true");}}Pg461OwnedIsolation.retain();}throw unknown;
        }
        return Boolean.TRUE;
      })).orElseThrow();
      } catch(Exception|Error admissionUnknown){if(changed[0] || admissionUnknown.getSuppressed().length>0){System.err.println("PG462_RETIREMENT_ADMISSION_UNKNOWN M_RETAINED=true A_OWNERSHIP_NOT_INFERRED=true oldCloseClaimed=false diagnosticsRedacted=true");Pg461OwnedIsolation.retain();}throw admissionUnknown;}
    })).orElseThrow();
    } catch(Exception|Error maintenanceUnknown){if(changed[0] || maintenanceUnknown.getSuppressed().length>0){System.err.println("PG462_RETIREMENT_M_UNKNOWN M_OWNERSHIP_NOT_INFERRED=true oldCloseClaimed=false diagnosticsRedacted=true");Pg461OwnedIsolation.retain();}throw maintenanceUnknown;}
    System.out.println("PG462_RETIREMENT "+(verify?"verifyOnly=true":"currentInvalid=true typedIntentsRetired=true namespace21=true")+" rows301OriginalBackupPreserved=true all9Terminal=true oldNormalReturnClaimed=false newOwnedScopesReturnedNormally=true");
  }
}
