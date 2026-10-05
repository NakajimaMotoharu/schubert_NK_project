import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Instant;
import java.util.*;

/** SSC190 / PT-ADM-DEPLOY001..005: completed-original code-only transition, not runtime/repair authority.
 * No start, DDL, restored original, issued permit, or old UNKNOWN normalization.
 */
public final class Pg465CompletedDeployment {
  static final String SOURCE="df9a33febf3703f0d18ac2c4ef56fd0225aac2b9";
  static final String DIGEST="8b8e82f43146f4a89e02237a0b28e010442c59d3e7c8066c96f13d8b414d8e9e";
  static final String BOOT="e07aa706-1acd-4e65-b309-d7f330f79d54";
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG464");
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG465");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg465-completed-deploy");
  static final Path STARTUP=Path.of("/run/schubert-nk/startup");
  static final String UNIT="schubert-nk-bootstrap-admin.service";
  static boolean touched;
  static String stage="PREFLIGHT";
  static final Map<String,String> LIVE=Map.of("caddy.service","1345626:5fab43f2da6d40c9a2bb3987e7d63088","schubert-nk-web.service","1340568:716bd4789cde40af97775e48641159fe","schubert-nk-api.service","1338494:9269078370384fdaab05ca9a0fcd50bd","artemis.service","1227864:c784737af61e48778d0c8fa2c4f68037");
  static Map<String,Map<String,String>> stops=Map.of();
  static Map<String,Long> ticks=Map.of();
  static void require(boolean value){if(!value)throw new IllegalStateException("completed deployment refused at "+stage);}
  static boolean arguments(String[] args){return args!=null && args.length==1 && args[0]!=null && Set.of("verify","activate").contains(args[0]);}
  static boolean normalDone(MaintenanceRunFiles.StartupOriginal original){
    return original!=null && original.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
        && original.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION)
        && original.completed().isPresent() && original.completed().orElseThrow().outcome()==MaintenanceCompletion.Outcome.SUCCESS
        && !original.completed().orElseThrow().endedAt().isBefore(Instant.parse("2026-10-05T00:35:52Z"))
        && !original.completed().orElseThrow().endedAt().isAfter(Instant.parse("2026-10-05T00:42:37Z"));
  }
  static boolean names(Set<String> actual, Set<String> historical,UUID epoch){
    if(actual==null || historical==null || epoch==null || historical.size()!=28)return false;
    var expected=new HashSet<>(historical);
    expected.add("epoch.current");for(String suffix:List.of(".permit",".owner",".API.launch",".WEB.launch"))expected.add(epoch+suffix);
    return expected.size()==33 && expected.equals(actual);
  }
  static void retain(){
    System.err.println("PG465_COMPLETED_UNKNOWN stage="+stage+" remainingOwnedScopesRetained=true nextStartIsolated=true historicalUnknownNotNormalized=true");
    boolean interrupted=false;for(;;){try{Thread.sleep(1000);}catch(InterruptedException e){interrupted=true;}if(interrupted)Thread.interrupted();}
  }
  static void save(String name,byte[] data)throws Exception{
    Path p=SAVE.resolve(name);Files.write(p,data,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(p,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var f=FileChannel.open(p,StandardOpenOption.READ)){f.force(true);}require(Arrays.equals(data,Files.readAllBytes(p)));
  }
  static Map<String,byte[]> startup()throws Exception{
    var result=new TreeMap<String,byte[]>();try(var entries=Files.list(STARTUP)){
      for(Path p:entries.toList())result.put(p.getFileName().toString(),Pg410KnownAuthRecovery.material(p,4096));
    }return result;
  }
  static void signedFiles()throws Exception{
    for(String path:List.of("config/effective/backup-profile.json","config/effective/backup-age-recipient",
        "config/caddy/Caddyfile.template","systemd/caddy.service.d/schubert-nk-startup-policy.conf"))
      require(Arrays.equals(Files.readAllBytes(OLD.resolve(path)),Files.readAllBytes(NEXT.resolve(path))));
    try(var entries=Files.list(OLD.resolve("db/migration"))){var sql=entries.toList();require(sql.size()==27);
      for(Path p:sql)require(Arrays.equals(Files.readAllBytes(p),Files.readAllBytes(NEXT.resolve("db/migration").resolve(p.getFileName()))));}
    var units=new ArrayList<String>();for(var u:MaintenanceUnit.values())if(u!=MaintenanceUnit.CADDY)units.add(u.serviceName());
    units.add("schubert-nk-morning-controller.service");
    for(String name:units){var previous=Files.readAllBytes(OLD.resolve("systemd").resolve(name));
      require(Arrays.equals(previous,Files.readAllBytes(NEXT.resolve("systemd").resolve(name))));
      require(Arrays.equals(previous,Files.readAllBytes(Path.of("/etc/systemd/system",name))));}
    require(Arrays.equals(Files.readAllBytes(Pg456SignedMigration.PROFILE),Files.readAllBytes(NEXT.resolve("config/effective/backup-profile.json"))));
    require(Arrays.equals(Files.readAllBytes(Path.of("/etc/caddy/Caddyfile")),Pg456SignedMigration.render(Files.readAllBytes(NEXT.resolve("config/caddy/Caddyfile.template")))));
    require(Arrays.equals(Files.readAllBytes(Path.of("/etc/systemd/system/caddy.service.d/schubert-nk-startup-policy.conf")),Files.readAllBytes(NEXT.resolve("systemd/caddy.service.d/schubert-nk-startup-policy.conf"))));
    require(!Files.exists(Path.of("/etc/systemd/system",UNIT),LinkOption.NOFOLLOW_LINKS));
  }
  static void terminal()throws Exception{
    Pg387TrustedDeployment.terminalAll();Pg387TrustedDeployment.requireNoUndeliveredWork();
    var parent=Pg464CompletedReadback.show("schubert-nk-morning-controller.service");
    require(parent.get("MainPID").equals("0") && parent.get("ControlPID").equals("0") && parent.get("Job").isEmpty()
        && parent.get("ActiveState").equals("inactive") && parent.get("Result").equals("success"));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
  }
  interface Stop {void run(String unit)throws Exception;}
  /** Fixed order and fail-fast; injected tool tests do not supply runtime success. */
  static void stopOwned(Stop stop)throws Exception{
    for(var unit:MaintenanceUnit.values())stop.run(unit.serviceName());
  }
  static Map<String,String> show(String unit)throws Exception{
    require(Arrays.stream(MaintenanceUnit.values()).anyMatch(u->u.serviceName().equals(unit)));
    byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",unit,"--property="+String.join(",",Pg410KnownAuthRecovery.FIELDS));
    var result=new HashMap<String,String>();for(String line:new String(raw,StandardCharsets.US_ASCII).split("\n")){int at=line.indexOf('=');require(at>0 && result.putIfAbsent(line.substring(0,at),line.substring(at+1))==null);}
    require(result.keySet().equals(Pg410KnownAuthRecovery.FIELDS) && unit.equals(result.get("Id")));return Map.copyOf(result);
  }
  static boolean capturedNormal(Map<String,String> state,String live){
    if(state==null || !"loaded".equals(state.get("LoadState")) || !"success".equals(state.get("Result")) || !"0".equals(state.get("ControlPID")) || !"".equals(state.get("Job")))return false;
    if(live!=null)return (state.get("MainPID")+":"+state.get("InvocationID")).equals(live) && "active".equals(state.get("ActiveState")) && "running".equals(state.get("SubState"));
    return "0".equals(state.get("MainPID")) && (("active".equals(state.get("ActiveState")) && "exited".equals(state.get("SubState")) && "1".equals(state.get("ExecMainCode")) && "0".equals(state.get("ExecMainStatus"))) || ("inactive".equals(state.get("ActiveState")) && "dead".equals(state.get("SubState"))));
  }
  static long tick(String pid)throws Exception{
    String raw=Files.readString(Path.of("/proc",pid,"stat"));return Long.parseLong(raw.substring(raw.lastIndexOf(')')+1).strip().split("\\s+")[19]);
  }
  static void captureStops()throws Exception{
    var states=new HashMap<String,Map<String,String>>();var starts=new HashMap<String,Long>();
    for(var unit:MaintenanceUnit.values()){
      String name=unit.serviceName();var state=show(name);require(capturedNormal(state,LIVE.get(name)));
      if(!state.get("MainPID").equals("0")){starts.put(name,tick(state.get("MainPID")));require(Files.readString(Path.of("/proc",state.get("MainPID"),"cgroup")).equals("0::/system.slice/"+name+"\n"));}
      else Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",name));
      require(state.equals(show(name)));states.put(name,state);
    }stops=Map.copyOf(states);ticks=Map.copyOf(starts);
  }
  static void stop(String unit)throws Exception{
    var captured=stops.get(unit);require(captured!=null && captured.equals(show(unit)));
    if(ticks.containsKey(unit))require(ticks.get(unit).longValue()==tick(captured.get("MainPID")));
    var p=new ProcessBuilder("/usr/bin/systemctl","stop",unit).redirectError(ProcessBuilder.Redirect.DISCARD).redirectOutput(ProcessBuilder.Redirect.DISCARD).start();
    try(var input=p.getOutputStream()){input.flush();}
    require(p.waitFor(120,java.util.concurrent.TimeUnit.SECONDS) && p.exitValue()==0);
    byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",unit,"--property=ActiveState,SubState,Result,MainPID,ControlPID,Job");
    var v=new HashMap<String,String>();for(String line:new String(raw,StandardCharsets.US_ASCII).split("\n")){int at=line.indexOf('=');require(at>0 && v.putIfAbsent(line.substring(0,at),line.substring(at+1))==null);}
    require(v.keySet().equals(Set.of("ActiveState","SubState","Result","MainPID","ControlPID","Job"))
        && v.get("ActiveState").equals("inactive") && v.get("Result").equals("success")
        && v.get("MainPID").equals("0") && v.get("ControlPID").equals("0") && v.get("Job").isEmpty());
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",unit));
    if(ticks.containsKey(unit))require(!Files.exists(Path.of("/proc",captured.get("MainPID")),LinkOption.NOFOLLOW_LINKS));
    System.out.println("PG465_COMPLETED_OWNED_STOP unit="+unit+" client0=true normalManager=true kernelEmpty=true");
  }
  static void activate(ReleaseApproval next,StartupPermitFiles files,StartupPermitRecords.Epoch before,MaintenanceRunFiles.StartupOriginal original)throws Exception{
    require(normalDone(original) && original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()))));
    require(before.equals(files.current()));save("epoch-before.private",Files.readAllBytes(STARTUP.resolve("epoch.current")));
    var invalid=files.invalidate(before.boot(),UUID.randomUUID(),before.activation());
    require(invalid.equals(files.current()) && invalid.state()==StartupPermitRecords.State.INVALID && !invalid.epoch().equals(before.epoch()) && invalid.activation().equals(before.activation()));
    Path installed=Path.of("/etc/systemd/system",UNIT);
    Files.copy(NEXT.resolve("systemd").resolve(UNIT),installed);Files.setPosixFilePermissions(installed,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r--r--"));
    try(var f=FileChannel.open(installed,StandardOpenOption.READ)){f.force(true);}Pg387TrustedDeployment.sync(installed.getParent());
    var reload=new ProcessBuilder("/usr/bin/systemctl","daemon-reload").redirectError(ProcessBuilder.Redirect.DISCARD).start();require(reload.waitFor()==0);
    Path directory=Path.of("/etc/schubert-nk/release-approval"),current=directory.resolve("current");
    save("approval-before.private",Files.readAllBytes(current));
    Path part=directory.resolve("pg465.part");Files.write(part,next.encode(),StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var f=FileChannel.open(part,StandardOpenOption.READ)){f.force(true);}Files.move(part,current,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(directory);
    Path link=Path.of("/opt/schubert-nk/current"),temporary=link.resolveSibling("pg465-current.part");
    save("current-before.private",Files.readSymbolicLink(link).toString().getBytes(StandardCharsets.US_ASCII));
    Files.createSymbolicLink(temporary,NEXT);Files.move(temporary,link,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(link.getParent());
    require(Arrays.equals(next.encode(),Files.readAllBytes(current)) && Files.readSymbolicLink(link).equals(NEXT));
    StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(next);
    require(Arrays.equals(Files.readAllBytes(installed),Files.readAllBytes(NEXT.resolve("systemd").resolve(UNIT))));
    byte[] enabled=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",UNIT,"--property=UnitFileState,ActiveState,MainPID,ControlPID,Job");
    require(new String(enabled,StandardCharsets.US_ASCII).contains("UnitFileState=static\n") && new String(enabled,StandardCharsets.US_ASCII).contains("ActiveState=inactive\n"));
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args));boolean verify=args[0].equals("verify");
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals(BOOT));
    require(Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"));
    require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()->{
        try{
          Pg464CodeOnlyDeployment.configure("PG464",Pg464CompletedReadback.SOURCE,OLD);var old=Pg387TrustedDeployment.verify();
          require(old.manifestSha256().equals(Pg464CompletedReadback.DIGEST) && Arrays.equals(old.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))) && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(OLD));
          Pg464CodeOnlyDeployment.configure("PG465",SOURCE,NEXT);Pg387TrustedDeployment.freezeCandidate();var next=Pg387TrustedDeployment.verify();require(next.manifestSha256().equals(DIGEST));signedFiles();
          Pg464CompletedReadback.peer("schubert-nk-api.service",1338494,"9269078370384fdaab05ca9a0fcd50bd");
          Pg464CompletedReadback.peer("schubert-nk-web.service",1340568,"716bd4789cde40af97775e48641159fe");
          Pg464CompletedReadback.peer("caddy.service",1345626,"5fab43f2da6d40c9a2bb3987e7d63088");
          require(new String(Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/python3","/var/lib/pgpt-s1-preservation/pg465-completed-tool-v1/pg465_live_peer_check.py"),StandardCharsets.US_ASCII).equals("PG465_OLD_PEERS_VERIFIED sameGeneration=true ordinaryZeroCaps=true ownedSockets=true info5=true tlsHandshake=true originalParentDone=true\n"));
          Pg387TrustedDeployment.requireNoUndeliveredWork();
          try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),STARTUP);var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
            try{
              db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
              try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && Boolean.TRUE.equals(r.getObject(1,Boolean.class)) && !r.next());}
              var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var before=files.current();require(before.state()==StartupPermitRecords.State.ISSUED && before.boot().toString().equals(BOOT));
              require(files.readIssued().releaseDigest().equals(Pg464CompletedReadback.DIGEST));
              var original=MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()));require(normalDone(original));
              var bytes=startup();var historical=new HashSet<String>();try(var entries=Files.list(Pg464CompletedReadback.BEFORE)){for(Path p:entries.toList())if(p.getFileName().toString().matches("[0-9a-f-]{36}\\.(permit|owner|API\\.launch|WEB\\.launch)")){String n=p.getFileName().toString();historical.add(n);require(Arrays.equals(Files.readAllBytes(p),bytes.get(n)));}}
              require(names(bytes.keySet(),historical,before.epoch()));
              var originalBytes=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();require(backup.size()==20);var fixture=Pg428ColdBootPreparation.fixtureSnapshot();var rows=Pg407FailedRootRecovery.databaseRows(db);require(rows.size()==331);
              var business=Pg456SignedMigration.business(schema);var history=Pg422SignedMigration.history(schema);require(history.equals(Pg456SignedMigration.expected(NEXT,OLD,27)));
              require(new RunReferenceRepository(db).read(before.activation().run()).identityConsistent());
              captureStops();
              if(verify){db.rollback();schema.rollback();stage="VERIFY_SCOPE_CLOSE";return Boolean.TRUE;}
              Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
              for(var e:bytes.entrySet())save(e.getKey(),e.getValue());save("rows-before.private",rows.toString().getBytes(StandardCharsets.UTF_8));save("business-before.private",business.toString().getBytes(StandardCharsets.US_ASCII));save("backup-before.private",backup.toString().getBytes(StandardCharsets.UTF_8));Pg387TrustedDeployment.sync(SAVE);
              stage="OWNED_STOP";touched=true;stopOwned(Pg465CompletedDeployment::stop);terminal();
              require(original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()))) && before.equals(files.current()));
              require(originalBytes.equals(Pg428ColdBootPreparation.original()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()));
              stage="ACTIVATE_COMPLETED";activate(next,files,before,original);terminal();
              var after=startup();require(after.keySet().equals(bytes.keySet()));for(var e:bytes.entrySet())if(!e.getKey().equals("epoch.current"))require(Arrays.equals(e.getValue(),after.get(e.getKey())));
              require(originalBytes.equals(Pg428ColdBootPreparation.original()) && original.equals(MaintenanceRunFiles.create().execute(s->s.observeStartup(before.activation()))) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && business.equals(Pg456SignedMigration.business(schema)) && history.equals(Pg422SignedMigration.history(schema)) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()));
              db.rollback();schema.rollback();stage="OWNED_SCOPE_CLOSE";
            }catch(Exception|Error failure){if(touched || stage.endsWith("SCOPE_CLOSE") || failure.getSuppressed().length!=0)retain();throw failure;}
          }catch(Exception|Error failure){if(touched || stage.endsWith("SCOPE_CLOSE") || failure.getSuppressed().length!=0)retain();throw failure;}
          return Boolean.TRUE;
        }catch(Exception|Error failure){if(touched || stage.endsWith("SCOPE_CLOSE") || failure.getSuppressed().length!=0)retain();throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){if(touched || stage.endsWith("SCOPE_CLOSE") || failure.getSuppressed().length!=0)retain();throw failure;}
      return Boolean.TRUE;
    })).orElseThrow();
    if(!verify){save("complete.private","allOwnedScopesReturnedNormally=true\noriginalDonePreserved=true\nrows331=true\nbackup20=true\nstarts0=true\npermits0=true\nddl0=true\n".getBytes(StandardCharsets.US_ASCII));Pg387TrustedDeployment.sync(SAVE);}
    System.out.println("PG465_COMPLETED_"+(verify?"VERIFIED":"ACTIVATED")+" normalOwnedClose=true originalDone=true historicalUnknownNotNormalized=true starts0=true permits0=true ddl0=true formal=false");
  }
}
