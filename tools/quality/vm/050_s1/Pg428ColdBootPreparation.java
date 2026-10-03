import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;

/** SSC165/BUG527: one saved PG/PT instance's new cold boot, not failed-intent retirement.
 * Old9024 evidence remains private; no old current/receipt/intent is restored or inferred.
 * No worker, migration, fresh run, completion or runtime permit is issued here.
 */
public final class Pg428ColdBootPreparation {
  static final String BOOT="58006280-5301-4a1b-a0c2-66bce4a8a38e";
  static final String PRIOR_BOOT="9024b59c-41d0-4dbd-8a3e-96bfad1467c0";
  static final String SOURCE="a3c86daf3ea1ac7ea9f6a3ae50dc45ead68c3fd2";
  static final String SQL_HASH="75601476d31a4925f55ec2dad9a45fc7bf6ed7f45b86fde0424e575f192c7fe9";
  static final Path RUN=Path.of("/run/schubert-nk");
  static Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg428-cold-boot-v5");
  static String activeBoot=BOOT, activePriorBoot=PRIOR_BOOT, activeSource=SOURCE, activeSqlHash=SQL_HASH;
  static String activeLabel="PG425", activeDigest="55353381ea39d2ddda0c3a195dea05cffda1ad880974693a72095811cd122fd1";
  static int activeRows=232;
  static String stage="ENTRY";
  static String fixedFailure(String tag,Throwable failure) {
    if(tag==null || failure==null || !Set.of("PG428","PG431").contains(tag))throw new IllegalArgumentException("fixed failure contract");
    var allowed=Set.of("ENTRY","M_ADMISSION","A_ADMISSION","DB_ADVISORY","PRESERVATION_READ","FIXED_ASSET_CONFIG",
        "TRANSFER_TREE","BACKUP_TREE","SIGNED_BOM","NEW_NAMESPACE","INVALID_ONLY","OWNED_UNWIND","OWNED_CLOSED",
        "PAIR_INPUT","PAIR_OBSERVE","PAIR_PHYSICAL","PAIR_SIGNED","PAIR_RETIRE","PAIR_QUARANTINE","PAIR_ADMISSION_QUARANTINE");
    String fixedStage=stage!=null && allowed.contains(stage)?stage:"UNKNOWN_STAGE";
    var result=new StringBuilder(tag+"_FIXED_FAILURE stage="+fixedStage+" oldOwnerClose=UNKNOWN currentOwnerClose=UNKNOWN diagnosticsRedacted=true\n");
    record Node(Throwable value,String edge){}
    var nodes=new ArrayDeque<Node>();nodes.add(new Node(failure,"PRIMARY"));
    var seen=Collections.newSetFromMap(new IdentityHashMap<Throwable,Boolean>());
    while(!nodes.isEmpty() && seen.size()<16) {
      var node=nodes.remove();var value=node.value();if(!seen.add(value))continue;
      result.append(tag).append("_FAILURE_NODE ordinal=").append(seen.size()-1).append(" edge=").append(node.edge())
          .append(" type=").append(value.getClass().getName()).append(" knownIo=").append(value instanceof java.io.IOException)
          .append(" secondaryCount=").append(value.getSuppressed().length).append('\n');
      if(value.getCause()!=null && nodes.size()<32)nodes.add(new Node(value.getCause(),"CAUSE"));
      for(var secondary:value.getSuppressed())if(nodes.size()<32)nodes.add(new Node(secondary,"SECONDARY"));
    }
    return result.toString();
  }
  static <T> T checked(Pg387TrustedDeployment.Checked<T> work) throws java.io.IOException {
    try {return work.execute();}
    catch(java.io.IOException known){throw known;}
    catch(RuntimeException programming){throw programming;}
    catch(InterruptedException interrupted){Thread.currentThread().interrupt();throw new java.io.IOException("cold preparation interrupted",interrupted);}
    catch(Exception known){throw new java.io.IOException("cold preparation failed",known);}
  }
  static void admissionIdentity(StartupAdmissionFile.Admission admission,Map<String,Object> expected) throws Exception {
    require(admission!=null && expected!=null && admission.descriptor()>=0
        && Long.valueOf(admission.device()).equals(expected.get("dev"))
        && Long.valueOf(admission.inode()).equals(expected.get("ino")));
    var held=heldAttributes(Path.of("/proc/self/fd/"+admission.descriptor()));
    require(expected.entrySet().stream().allMatch(e->Objects.equals(e.getValue(),held.get(e.getKey()))));
  }
  // SSC174: fixed independently observed saved-guest profile, not arbitrary paths/permits.
  static void profile(String[] args) {
    if(args==null || args.length>1 || (args.length==1 && (args[0]==null || !Set.of("PG444","PG444-V2").contains(args[0]))))
      throw new IllegalArgumentException("fixed cold profile required");
    if(args.length==0)return;
    activeBoot="e07aa706-1acd-4e65-b309-d7f330f79d54";activePriorBoot=BOOT;
    // Cold preparation must not load the later PairEvidence ABI absent from approved PG430.
    activeSource="91b010509e715e2b097c955d04f21c23f3529966";activeLabel="PG430";
    activeDigest="ecef234624ece66c69d81383f722aee046da7b0dcab8cf10ec4df3b3d2dd1375";activeRows=251;
    activeSqlHash="9efa45bf3b61ca8a5d368449533ec28d35e9b04d810fd4fe6143796f78b9b45f";
    SAVE=Path.of("/var/lib/pgpt-s1-preservation/"+("PG444-V2".equals(args[0])?"pg444-cold-e07-v2":"pg444-cold-e07"));
  }
  static void require(boolean value) {if(!value)throw new IllegalStateException("cold boot preparation unavailable");}
  static boolean cold(Map<String,String> f) {
    return f!=null && f.keySet().equals(Pg410KnownAuthRecovery.FIELDS) && f.values().stream().allMatch(Objects::nonNull)
        && "loaded".equals(f.get("LoadState"))
        && "inactive".equals(f.get("ActiveState")) && "dead".equals(f.get("SubState"))
        && "0".equals(f.get("MainPID")) && "0".equals(f.get("ControlPID"))
        && "".equals(f.get("Job")) && "".equals(f.get("InvocationID")) && "success".equals(f.get("Result"))
        && List.of("ExecMainCode","ExecMainStatus","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic")
            .stream().allMatch(k->"0".equals(f.get(k))) && coldPolicy(f);
  }
  static boolean coldPolicy(Map<String,String> f) {
    String id=f.get("Id");
    if(!"control-group".equals(f.get("KillMode")) || !"no".equals(f.get("SendSIGKILL")))return false;
    if("schubert-nk-morning-controller.service".equals(id))
      return "oneshot".equals(f.get("Type")) && "no".equals(f.get("Restart")) && "no".equals(f.get("RemainAfterExit"));
    if("caddy.service".equals(id))
      return "notify".equals(f.get("Type")) && "no".equals(f.get("Restart")) && "no".equals(f.get("RemainAfterExit"));
    if(Set.of("artemis.service","schubert-nk-api.service","schubert-nk-web.service").contains(id))
      return "simple".equals(f.get("Type")) && "on-failure".equals(f.get("Restart")) && "no".equals(f.get("RemainAfterExit"));
    return Set.of("schubert-nk-backup.service","schubert-nk-cleanup.service","schubert-nk-inbox-inspector.service","schubert-nk-expiry-cleanup.service").contains(id)
        && "oneshot".equals(f.get("Type")) && "no".equals(f.get("Restart")) && "yes".equals(f.get("RemainAfterExit"));
  }
  static boolean newBoot(String actual) {return activeBoot.equals(actual) && !activePriorBoot.equals(actual);}
  static Map<String,String> showCold(String unit) throws Exception {
    var allowed=new HashSet<String>();for(var u:MaintenanceUnit.values())allowed.add(u.serviceName());
    allowed.add("schubert-nk-morning-controller.service");require(allowed.contains(unit));
    byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",unit,"--property="+String.join(",",Pg410KnownAuthRecovery.FIELDS));
    var f=new HashMap<String,String>();for(String line:new String(raw,StandardCharsets.US_ASCII).split("\n")) {
      int at=line.indexOf('=');require(at>0 && !f.containsKey(line.substring(0,at)));f.put(line.substring(0,at),line.substring(at+1));
    }
    require(unit.equals(f.get("Id")) && cold(f));return Map.copyOf(f);
  }
  static void physical() throws Exception {
    require(newBoot(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim()));
    var names=new ArrayList<String>();for(var u:MaintenanceUnit.values())names.add(u.serviceName());
    names.add("schubert-nk-morning-controller.service");
    for(String unit:names) {
      var before=showCold(unit);Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit));
      require(before.equals(showCold(unit)));
    }
  }
  static Map<String,Object> metadata(Path p) throws Exception {
    return Map.copyOf(Files.readAttributes(p,"unix:uid,gid,mode,nlink,dev,ino,ctime,lastModifiedTime,size",LinkOption.NOFOLLOW_LINKS));
  }
  static Map<String,String> original() throws Exception {
    return snapshot(Path.of("/var/lib/schubert-nk/maintenance"));
  }
  static Map<String,String> snapshot(Path root) throws Exception {
    var result=new TreeMap<String,String>();
    try(var paths=Files.walk(root)) {
      for(var p:paths.sorted().toList()) {
        var a=metadata(p);require(!Files.isSymbolicLink(p));
        var value=new TreeMap<>(a).toString();
        if(Files.isRegularFile(p,LinkOption.NOFOLLOW_LINKS)) {
          require((Long)a.get("size")<=1048576);
          value += "/"+Pg410KnownAuthRecovery.hash(Files.readAllBytes(p));
        }
        require(a.equals(metadata(p)));result.put(p.toString(),value);
      }
    }
    return Map.copyOf(result);
  }
  static String fixtureSnapshot() throws Exception {
    stage="FIXED_ASSET_CONFIG";
    var result=new TreeMap<String,Object>();
    for(var entry:Map.of("/srv/schubert-nk/data/assets/audio/pgpt-fixture.wav","114448ce435018eda5f4a8df39689d79fb4ff3dbfb5cc521002a42e8a6f625bb",
        "/srv/schubert-nk/data/assets/manifests/master.sha256","44f2bff22f62d9f4ae4c49bcc554e9a189427e7fe6f2bd3b24604bfdd4141bbc",
        "/etc/schubert-nk/api.yml","40573510ed295f9e7b343f832624cda63f2383fa87e59b2bddeb651e7717c6bc").entrySet()) {
      var p=Path.of(entry.getKey());var a=metadata(p);var digest=Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(p,65536));
      require(entry.getValue().equals(digest) && a.equals(metadata(p)));result.put(entry.getKey(),a.toString()+"/"+digest);
    }
    var common=Path.of("/etc/schubert-nk/common.yml");result.put(common.toString(),metadata(common).toString()+"/"+Pg410KnownAuthRecovery.hash(Pg410KnownAuthRecovery.material(common,65536)));
    result.put("assets",snapshot(Path.of("/srv/schubert-nk/data/assets")));
    stage="TRANSFER_TREE";
    result.put("transfer",transferSnapshot(Path.of("/srv/schubert-nk/data/transfer"),transferIdentity()));
    return result.toString();
  }
  static StorageIdentity transferIdentity(){return new StorageIdentity("schubert-api","schubert-web");}
  static void newDirectory(Path path,int uid,int gid) throws Exception {
    require(!Files.exists(path,LinkOption.NOFOLLOW_LINKS));
    Files.createDirectory(path,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    Files.setAttribute(path,"unix:uid",uid,LinkOption.NOFOLLOW_LINKS);
    Files.setAttribute(path,"unix:gid",gid,LinkOption.NOFOLLOW_LINKS);
    var a=metadata(path);
    require(Integer.valueOf(uid).equals(a.get("uid")) && Integer.valueOf(gid).equals(a.get("gid")) && Integer.valueOf(0040700).equals(a.get("mode")));
    Pg387TrustedDeployment.sync(path.getParent());
  }
  static Map<String,Object> heldAttributes(Path held) throws java.io.IOException {
    // Following /proc/self/fd itself is intentional: it denotes the owned inode, not a user path.
    return Map.copyOf(Files.readAttributes(held,"unix:uid,gid,owner,group,mode,nlink,dev,ino,ctime,lastModifiedTime,size"));
  }
  static Set<String> names(Path held) throws java.io.IOException {
    try(var entries=Files.list(held)) {
      var list=entries.map(p->p.getFileName().toString()).toList();require(list.size()<=4096);
      return Collections.unmodifiableSet(new TreeSet<>(list));
    }
  }
  static String heldHash(Path held,long size) throws java.io.IOException,java.security.NoSuchAlgorithmException {
    var digest=java.security.MessageDigest.getInstance("SHA-256");long total=0;
    try(var in=Files.newInputStream(held)) {
      var buffer=new byte[131072];for(;;) {
        int n=in.read(buffer);if(n<0)break;require(n>0);total=Math.addExact(total,n);require(total<=size);
        digest.update(buffer,0,n);
      }
    }
    require(total==size);return HexFormat.of().formatHex(digest.digest());
  }
  static Map<String,String> transferSnapshot(Path path,StorageIdentity identity) throws java.io.IOException {
    return transferSnapshot(path,identity,LinuxDirectoryCalls.create());
  }
  static Map<String,String> transferSnapshot(Path path,StorageIdentity identity,DirectoryCalls calls) throws java.io.IOException {
    if(path==null || identity==null || calls==null)throw new IllegalArgumentException("transfer observation contract");
    var first=transferPass(path,identity,calls);var second=transferPass(path,identity,calls);
    require(first.equals(second));return second;
  }
  static Map<String,String> transferPass(Path path,StorageIdentity identity,DirectoryCalls calls) throws java.io.IOException {
    var result=new TreeMap<String,String>();
    try(var root=OwnedTransferDirectory.open(calls,path)) {
      root.atDirectory(held->{
        var before=heldAttributes(held);StorageAttributeGuard.directory(before,identity);var dates=names(held);
        result.put("",new TreeMap<>(before).toString());
        for(String date:dates) {
          require(date.matches("[0-9]{8}"));
          var parsed=java.time.LocalDate.parse(date,java.time.format.DateTimeFormatter.BASIC_ISO_DATE);
          try(var day=root.openExistingDate(parsed)) {
            day.atDirectory(directory->{
              var da=heldAttributes(directory);StorageAttributeGuard.directory(da,identity);var files=names(directory);
              result.put(date,new TreeMap<>(da).toString());
              for(String name:files) {
                require(name.matches("[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\.(part|ready)"));
                var id=UUID.fromString(name.substring(0,36));boolean ready=name.endsWith(".ready");
                OwnedTransferDirectory.FileOperation<Boolean> operation=file->{
                  var fa=heldAttributes(file);long size=StorageAttributeGuard.transferSize(fa,identity,ready);
                  String hash=heldHash(file,size);require(fa.equals(heldAttributes(file)));
                  result.put(date+"/"+name,new TreeMap<>(fa)+"/"+hash);return Boolean.TRUE;
                };
                if(ready)day.atReadyHandle(id,operation);else day.atPartHandle(id,operation);
              }
              require(files.equals(names(directory)) && da.equals(heldAttributes(directory)));return Boolean.TRUE;
            });
          }
        }
        require(dates.equals(names(held)) && before.equals(heldAttributes(held)));return Boolean.TRUE;
      });
    }
    return Map.copyOf(result);
  }
  static Map<String,String> backupSnapshot() throws Exception {
    stage="BACKUP_TREE";
    // Read all files, not only the four canonical bundle artifacts; preserve unknown fixtures too.
    var base=Path.of("/srv/schubert-nk/backup");
    var first=backupPass(base);var second=backupPass(base);require(first.equals(second));
    require(second.size()==20);return second;
  }
  static Map<String,String> backupPass(Path base) throws java.io.IOException {
    var result=new TreeMap<String,String>();
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),base)){snapshotTree(root,"",result);}
    return Map.copyOf(result);
  }
  static void snapshotTree(OwnedTransferDirectory root,String prefix,Map<String,String> result) throws java.io.IOException {
    require(prefix.split("/",-1).length<=16 && result.size()<4096);
    root.atDirectory(held->{
      var before=heldAttributes(held);require(((Integer)before.get("mode") & 0170000)==0040000);
      var entries=names(held);result.put(prefix,new TreeMap<>(before).toString());
      for(String name:entries) {
        var type=Files.readAttributes(held.resolve(name),"unix:mode",LinkOption.NOFOLLOW_LINKS).get("mode");
        String key=prefix.isEmpty()?name:prefix+"/"+name;
        if(((Integer)type & 0170000)==0040000) {
          try(var child=root.openExistingChild(name)){snapshotTree(child,key,result);}
        }else {
          root.atExistingEntryHandle(name,file->{
            var a=heldAttributes(file);require(((Integer)a.get("mode") & 0170000)==0100000 && Integer.valueOf(1).equals(a.get("nlink")));
            require((Long)a.get("size")>=0 && (Long)a.get("size")<=4294967296L && result.size()<4096);
            String hash=heldHash(file,(Long)a.get("size"));require(a.equals(heldAttributes(file)));
            result.put(key,new TreeMap<>(a)+"/"+hash);return Boolean.TRUE;
          });
        }
      }
      require(entries.equals(names(held)) && before.equals(heldAttributes(held)));return Boolean.TRUE;
    });
  }
  static void emptyRoot(Path path) throws Exception {
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),path)) {
      root.atDirectory(held->{
        var a=heldAttributes(held);require(Integer.valueOf(0).equals(a.get("uid")) && Integer.valueOf(0).equals(a.get("gid"))
            && Integer.valueOf(0040700).equals(a.get("mode")) && names(held).isEmpty());
        var security=LinuxInodeSecurity.create();require(security.accessAcl(held,4096).length==0
            && !security.readOnlyFilesystem(held) && "tmpfs".equals(Files.getFileStore(held).type()));
        require(Files.isSameFile(path,held) && a.equals(heldAttributes(held)));return Boolean.TRUE;
      });
    }
  }
  static void ensureEmptyRoot(Path path) throws Exception {
    if(!Files.exists(path,LinkOption.NOFOLLOW_LINKS))newDirectory(path,0,0);
    emptyRoot(path);
  }
  static void save(String name,byte[] bytes) throws Exception {
    var p=SAVE.resolve(name);Files.write(p,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,PosixFilePermissions.fromString("r--------"));
    try(var f=java.nio.channels.FileChannel.open(p,StandardOpenOption.READ)){f.force(true);}
    require(Arrays.equals(bytes,Files.readAllBytes(p)));
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      // Fixed stage/exception shape only; no messages, DB results, epoch or private paths.
      System.err.print(fixedFailure("PG428",e));
      for(var f:e.getStackTrace())if(f.getClassName().equals("Pg428ColdBootPreparation"))System.err.println("PG428 FRAME "+f.getMethodName()+":"+f.getLineNumber());
    });
    profile(args);
    require(Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    require(Files.readString(Path.of("/proc/self/status")).contains("Uid:\t0\t0\t0\t0\n"));
    require(newBoot(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim()));
    require(cold(Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).values()));
    for(String n:List.of("startup","backup-request","cleanup-request","expiry-request"))
      if(Files.exists(RUN.resolve(n),LinkOption.NOFOLLOW_LINKS))emptyRoot(RUN.resolve(n));
    require(!Files.exists(RUN.resolve("pt-coverage"),LinkOption.NOFOLLOW_LINKS));
    var locks=Map.of("maintenance.lock",metadata(RUN.resolve("maintenance.lock")),"startup-admission.lock",metadata(RUN.resolve("startup-admission.lock")));
    for(var a:locks.values())require(Integer.valueOf(0).equals(a.get("uid")) && Integer.valueOf(0).equals(a.get("gid")) && Integer.valueOf(0100600).equals(a.get("mode")) && Integer.valueOf(1).equals(a.get("nlink")));
    require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    newDirectory(SAVE,0,0);
    stage="M_ADMISSION";
    require(MaintenanceFileLock.create().tryExclusive(()-> {
      return checked(()-> {
        physical();
        stage="A_ADMISSION";
        return StartupAdmissionFile.create().tryExclusiveObserved(admission->checked(()-> {
          admissionIdentity(admission,locks.get("startup-admission.lock"));
          physical();
          stage="DB_ADVISORY";
          try(var db=Pg407FailedRootRecovery.openDatabase()) {
            db.setAutoCommit(false);
            try(var s=db.createStatement();var r=s.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {require(r.next() && Boolean.TRUE.equals(r.getObject(1,Boolean.class)) && !r.next());}
            var activation=MaintenanceRecords.readActivation(Files.readAllBytes(Path.of("/var/lib/schubert-nk/maintenance/active")));
            require(activation.id().equals(Pg407FailedRootRecovery.ACTIVATION) && activation.run().id().equals(Pg407FailedRootRecovery.RUN)
                && activation.run().cutoff().equals(java.time.Instant.parse("2026-09-27T15:00:00Z")));
            return MaintenanceRunFiles.create().execute(session->checked(()-> {
              stage="PRESERVATION_READ";
              require(session.observe(activation).equals(activation) && new RunReferenceRepository(db).read(activation.run()).identityConsistent());
              var before=original();var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==activeRows);
              byte[] sql=Pg425KnownApiRecovery.command(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-");
              require(activeSqlHash.equals(Pg410KnownAuthRecovery.hash(sql)));
              var backup=backupSnapshot();var fixture=fixtureSnapshot();
              save("db"+activeRows+"-before.log",sql);save("original-before.properties",before.toString().getBytes(StandardCharsets.UTF_8));
              save("backup-before.properties",backup.toString().getBytes(StandardCharsets.UTF_8));save("fixture-before.properties",fixture.getBytes(StandardCharsets.UTF_8));
              Pg387TrustedDeployment.LABEL=activeLabel;Pg387TrustedDeployment.STEM=activeLabel.toLowerCase(Locale.ROOT);Pg387TrustedDeployment.SOURCE=activeSource;
              Pg387TrustedDeployment.RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-"+activeLabel);
              stage="SIGNED_BOM";
              Pg387TrustedDeployment.freezeCandidate();
              var approval=Pg387TrustedDeployment.verify();
              require(approval.manifestSha256().equals(activeDigest)
                  && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
                  && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
              physical();require(before.equals(original()) && backup.equals(backupSnapshot()) && fixture.equals(fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)));
              stage="NEW_NAMESPACE";
              for(String n:List.of("startup","backup-request","cleanup-request","expiry-request"))ensureEmptyRoot(RUN.resolve(n));
              newDirectory(RUN.resolve("pt-coverage"),0,0);
              for(String n:List.of("parent","cleanup","expiry","root-api"))newDirectory(RUN.resolve("pt-coverage").resolve(n),0,0);
              for(var e:Map.of("backup","schubert-backup","inspector","schubert-inbox-inspector").entrySet()) {
                var p=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-u",e.getValue());
                var g=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/id","-g",e.getValue());
                newDirectory(RUN.resolve("pt-coverage").resolve(e.getKey()),Integer.parseInt(new String(p,StandardCharsets.US_ASCII).trim()),Integer.parseInt(new String(g,StandardCharsets.US_ASCII).trim()));
              }
              // Parent directory traversal only; private per-worker output remains0700.
              Files.setPosixFilePermissions(RUN.resolve("pt-coverage"),PosixFilePermissions.fromString("rwx--x--x"));
              try(var directory=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),RUN.resolve("startup"))) {
                stage="INVALID_ONLY";
                var files=new StartupPermitFiles(directory,LinuxInodeSecurity.create());
                var next=files.invalidate(UUID.fromString(activeBoot),UUID.randomUUID(),activation);
                require(next.equals(files.current()) && next.state()==StartupPermitRecords.State.INVALID && next.activation().equals(activation));
                save("new-invalid.properties",Files.readAllBytes(RUN.resolve("startup/epoch.current")));
              }
              physical();require(session.observe(activation).equals(activation) && before.equals(original()) && backup.equals(backupSnapshot()) && fixture.equals(fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)));
              admissionIdentity(admission,locks.get("startup-admission.lock"));
              for(var e:locks.entrySet())require(e.getValue().equals(metadata(RUN.resolve(e.getKey()))));
              save("db"+activeRows+"-after.log",Pg425KnownApiRecovery.command(Pg425KnownApiRecovery.READBACK_SQL.getBytes(StandardCharsets.US_ASCII),"/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","schubert_nk","-f","-"));
              require(activeSqlHash.equals(Pg410KnownAuthRecovery.hash(Files.readAllBytes(SAVE.resolve("db"+activeRows+"-after.log")))));
              Pg387TrustedDeployment.sync(SAVE);db.rollback();
              stage="OWNED_UNWIND";
              return Boolean.TRUE;
            }));
          }
        })).orElseThrow();
      });
    }).orElseThrow());
    stage="OWNED_CLOSED";
    System.out.println("PG428 COLD_BOOT_PREPARED completed=true ownedUnwindReturned=true oldOwnerClose=UNKNOWN oldBootSuccessInferred=false oldIntentRetired=0 originalRows="+activeRows+" backupFixturePreserved=true locksSameInode=true freshInvalidOnly=true workersStarted=0 migrationApplied=0");
  }
}
