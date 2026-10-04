import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** SSC181 administrator-only exact NSS correction. No runtime gate relaxation/start/DDL. */
public final class Pg460CaddyNssPreparation {
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg460-caddy-nss");
  static String stage="ARGUMENTS";
  static void require(boolean b){if(!b)throw new IllegalStateException("fixed NSS preservation differs");}
  static byte[] removeMember(byte[] bytes,boolean shadow) {
    Objects.requireNonNull(bytes);String text=new String(bytes,StandardCharsets.US_ASCII);
    require(bytes.length<=65536 && Arrays.equals(bytes,text.getBytes(StandardCharsets.US_ASCII)) && text.endsWith("\n") && !text.contains("\r"));
    String[] rows=text.substring(0,text.length()-1).split("\n",-1);var names=new HashSet<String>();boolean found=false;
    for(int i=0;i<rows.length;i++) {
      String[] f=rows[i].split(":",-1);require(f.length==4 && !f[0].isEmpty() && names.add(f[0]));
      if(!f[0].equals("www-data"))continue;
      require(!found);found=true;if(!shadow)require(f[2].equals("33"));
      var members=new ArrayList<>(f[3].isEmpty()?List.of():Arrays.asList(f[3].split(",",-1)));
      require(members.stream().allMatch(m->m.matches("[a-z_][a-z0-9_-]*[$]?")) && new HashSet<>(members).size()==members.size());
      if(!shadow)require(members.contains("caddy"));
      members.remove("caddy");f[3]=String.join(",",members);rows[i]=String.join(":",f);
    }
    require(found);return (String.join("\n",rows)+"\n").getBytes(StandardCharsets.US_ASCII);
  }
  static Set<String> groupIds(byte[] raw) {
    Objects.requireNonNull(raw);String s=new String(raw,StandardCharsets.US_ASCII);
    require(s.matches("[1-9][0-9]*(?: [1-9][0-9]*)*\n"));var values=new HashSet<>(Arrays.asList(s.trim().split(" ")));require(values.size()==s.trim().split(" ").length);return Set.copyOf(values);
  }
  static byte[] query(String... command) throws Exception {
    var p=new ProcessBuilder(command).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    if(!p.waitFor(5,TimeUnit.SECONDS)){p.destroy();throw new IllegalStateException("fixed NSS query unavailable");}
    require(p.exitValue()==0);try(var input=p.getInputStream()){byte[] raw=input.readNBytes(65537);require(raw.length<=65536);return raw;}
  }
  static void save(String name,byte[] bytes) throws Exception {
    Path p=SAVE.resolve(name);Files.write(p,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var c=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){c.force(true);}
  }
  static void terminal() throws Exception {Pg460OwnedIsolation.parent();Pg387TrustedDeployment.terminalAll();Pg387TrustedDeployment.requireNoUndeliveredWork();}
  static void retained() {System.err.println("PG460_NSS_UNKNOWN stage="+stage+" M_RETAINED=true A_OWNERSHIP_NOT_INFERRED=true nextStartIsolated=true privateDiagnostics=true");for(;;)java.util.concurrent.locks.LockSupport.parkNanos(TimeUnit.SECONDS.toNanos(1));}
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println("PG460_NSS_REFUSED stage="+stage+" type="+e.getClass().getName()+" privateDiagnostics=true"));
    require(args.length==0 && Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("e07aa706-1acd-4e65-b309-d7f330f79d54"));
    boolean[] changing={false};
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      stage="M_TERMINAL";terminal();
      try {
        return StartupAdmissionFile.create().tryExclusive(fd->Pg387TrustedDeployment.checked(()-> {
          stage="A_SIGNED";terminal();Pg460Known30PairRecovery.signed();
          try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Pg460OwnedIsolation.STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
            db.setAutoCommit(false);schema.setReadOnly(true);
            try(var q=db.createStatement();var r=q.executeQuery("select pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
            var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
            require(epoch.state()==StartupPermitRecords.State.INVALID && epoch.epoch().toString().equals("e8cce97a-163b-4814-b435-8fc26466e550") && Pg460Known30PairRecovery.fullyRetired(Pg460Known30PairRecovery.actualNames(),epoch.epoch()));
            require(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty() && new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent());
            var original=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();var fixture=Pg428ColdBootPreparation.fixtureSnapshot();
            var rows=Pg407FailedRootRecovery.databaseRows(db);var business=Pg456SignedMigration.business(schema);require(rows.size()==281);
            var startup=new TreeMap<String,byte[]>();var metadata=new TreeMap<String,Map<String,Object>>();
            for(String n:Pg460Known30PairRecovery.actualNames()){Path p=Pg460OwnedIsolation.STARTUP.resolve(n);startup.put(n,Pg410KnownAuthRecovery.material(p,4096));metadata.put(n,Pg410KnownAuthRecovery.metadata(p));}
            var nss=new TreeMap<String,byte[]>();var nssMetadata=new TreeMap<String,Map<String,Object>>();
            for(String n:List.of("group","gshadow","passwd","nsswitch.conf","group-","gshadow-")) {
              Path p=Path.of("/etc",n);if(!Files.exists(p,LinkOption.NOFOLLOW_LINKS)){require(n.endsWith("-"));continue;}
              var m=Pg410KnownAuthRecovery.metadata(p);require(Integer.valueOf(0).equals(m.get("uid")) && Integer.valueOf(1).equals(m.get("nlink")) && (((Number)m.get("mode")).intValue()&0022)==0);
              nss.put(n,Pg410KnownAuthRecovery.material(p,65536));require(m.equals(Pg410KnownAuthRecovery.metadata(p)));nssMetadata.put(n,m);
            }
            require(groupIds(query("/usr/bin/id","-G","caddy")).equals(Set.of("33","978")));
            byte[] account=query("/usr/bin/getent","passwd","caddy");String[] fields=new String(account,StandardCharsets.US_ASCII).stripTrailing().split(":",-1);
            require(fields.length==7 && fields[0].equals("caddy") && fields[2].equals("993") && fields[3].equals("978"));
            byte[] primary=query("/usr/bin/getent","group","caddy");require(new String(primary,StandardCharsets.US_ASCII).equals("caddy:x:978:\n"));
            byte[] expectedGroup=removeMember(nss.get("group"),false),expectedShadow=removeMember(nss.get("gshadow"),true);
            require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
            for(var e:nss.entrySet())save(e.getKey()+"-before.private",e.getValue());
            save("nss-metadata-before.private",nssMetadata.toString().getBytes(StandardCharsets.UTF_8));
            Pg387TrustedDeployment.sync(SAVE);Pg387TrustedDeployment.sync(SAVE.getParent());
            stage="BEFORE_NSS_MUTATION";terminal();Pg460Known30PairRecovery.signed();require(epoch.equals(files.current()));
            for(var e:nss.entrySet())require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(Path.of("/etc",e.getKey()),65536)) && nssMetadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(Path.of("/etc",e.getKey()))));
            for(var e:startup.entrySet()){Path p2=Pg460OwnedIsolation.STARTUP.resolve(e.getKey());require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(p2,4096)) && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(p2)));}
            require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
            changing[0]=true;
            try {
              stage="REMOVE_KNOWN_MEMBER";var p=new ProcessBuilder("/usr/bin/gpasswd","-d","caddy","www-data").redirectOutput(ProcessBuilder.Redirect.DISCARD).redirectError(ProcessBuilder.Redirect.DISCARD).start();
              if(!p.waitFor(5,TimeUnit.SECONDS) || p.exitValue()!=0)retained();
              stage="POST_NSS";require(Arrays.equals(expectedGroup,Pg410KnownAuthRecovery.material(Path.of("/etc/group"),65536)) && Arrays.equals(expectedShadow,Pg410KnownAuthRecovery.material(Path.of("/etc/gshadow"),65536)));
              require(Arrays.equals(nss.get("group"),Pg410KnownAuthRecovery.material(Path.of("/etc/group-"),65536)) && Arrays.equals(nss.get("gshadow"),Pg410KnownAuthRecovery.material(Path.of("/etc/gshadow-"),65536)));
              for(String n:List.of("group","gshadow")){var before=nssMetadata.get(n);var after=Pg410KnownAuthRecovery.metadata(Path.of("/etc",n));for(String k:List.of("uid","gid","mode","nlink"))require(before.get(k).equals(after.get(k)));}
              for(String n:List.of("passwd","nsswitch.conf"))require(Arrays.equals(nss.get(n),Pg410KnownAuthRecovery.material(Path.of("/etc",n),65536)) && nssMetadata.get(n).equals(Pg410KnownAuthRecovery.metadata(Path.of("/etc",n))));
              require(Arrays.equals(account,query("/usr/bin/getent","passwd","caddy")) && Arrays.equals(primary,query("/usr/bin/getent","group","caddy")) && groupIds(query("/usr/bin/id","-G","caddy")).equals(Set.of("978")));
              terminal();Pg460Known30PairRecovery.signed();require(epoch.equals(files.current()) && Pg460Known30PairRecovery.fullyRetired(Pg460Known30PairRecovery.actualNames(),epoch.epoch()));
              for(var e:startup.entrySet()){Path p2=Pg460OwnedIsolation.STARTUP.resolve(e.getKey());require(Arrays.equals(e.getValue(),Pg410KnownAuthRecovery.material(p2,4096)) && metadata.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(p2)));}
              require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)));
              require(MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation())).completed().isEmpty());
              save("mutation-body.private","onlyKnownWwwDataMemberRemoved=true\nprimaryPasswdOtherGroupsOtherMembersPreserved=true\nall281OriginalBackupStartupPreserved=true\nouterScopesNotYetClosed=true\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);db.rollback();
            }catch(Exception|Error unknown){retained();}
          }catch(Exception|Error unknownClose){if(changing[0] || unknownClose.getSuppressed().length!=0)retained();throw unknownClose;}
          return Boolean.TRUE;
        })).orElseThrow();
      }catch(Exception|Error unknownAdmission){if(changing[0] || unknownAdmission.getSuppressed().length!=0)retained();throw unknownAdmission;}
    })).orElseThrow());
    save("complete.private","onlyKnownMemberRemoved=true\nallOwnedScopesReturnedNormally=true\nstartsPermitsDdl0=true\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);
    System.out.println("PG460_NSS_PREPARED primaryOnly978=true onlyKnownWwwDataMemberRemoved=true all281BusinessOriginalBackupStartupPreserved=true all9KernelEmpty=true allOwnedScopesReturnedNormally=true startsPermitsDdl0=true privateBeforeImagesPreserved=true");
  }
}
