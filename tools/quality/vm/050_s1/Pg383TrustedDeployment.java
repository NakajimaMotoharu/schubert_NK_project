import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import java.nio.file.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import org.flywaydb.core.Flyway;

/** Isolated PG/PT VM trusted operator, NOT a Morning/worker probe or runtime authority fallback.
 * SS343 initial provisioning exception/SSC096/110. Fixed separately provisioned pin, genuine
 * original-byte signature/full Production BOM before any approval. Private input never printed.
 * Actual application source must already be built/tested/committed. No clean/repair/baseline.
 */
public final class Pg383TrustedDeployment {
  static final Path RELEASE=Path.of("/opt/schubert-nk/releases/0.1.0-PG383");
  static final Path PRESERVE=Path.of("/var/lib/pgpt-s1-preservation");
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e) -> {
      System.err.println("PG383 DEPLOYMENT_REFUSED diagnosticsRedacted=true type="+e.getClass().getName());
      for(var frame:e.getStackTrace()) {
        if(frame.getClassName().equals("Pg383TrustedDeployment"))
          System.err.println("PG383 FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
      }
    });
    if(args.length!=1 || !Set.of("verify","migrate","activate").contains(args[0])) throw new IllegalArgumentException("fixed mode");
    if(!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01")) throw new IllegalStateException("isolated VM only");
    var result=MaintenanceFileLock.create().tryExclusive(() -> {
      System.out.println("PG383 STAGE M_ACQUIRED");
      checked(() -> { stopAll(); return Boolean.TRUE; });
      System.out.println("PG383 STAGE ALL_STOPPED");
      return StartupAdmissionFile.create().tryExclusive(admission -> {
        System.out.println("PG383 STAGE A_ACQUIRED");
        return checked(() -> {
          terminalAll();
          freezeCandidate();
          var approval=verify();
          if(args[0].equals("migrate")) migrate();
          if(args[0].equals("activate")) activate(approval);
          terminalAll();
          return Boolean.TRUE;
        });
      }).orElseThrow();
    }).orElseThrow();
    if(!result) throw new IllegalStateException("deployment result");
    System.out.println("PG383 DEPLOYMENT "+args[0]+" completed=true signatureAndBom=true runtimePermitIssued=false");
  }
  interface Checked<T> { T execute() throws Exception; }
  static <T> T checked(Checked<T> work) throws java.io.IOException {
    try { return work.execute(); }
    catch (RuntimeException programming) { throw programming; }
    catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); throw new java.io.IOException("deployment interrupted"); }
    catch (Exception known) { throw new java.io.IOException("deployment failed"); }
  }
  static ReleaseApproval verify() throws Exception {
    byte[] pin=material(Path.of("/etc/schubert-nk/deployment-key/pin.der"),44);
    byte[] signature=material(PRESERVE.resolve("pg383-manifest.sig"),64);
    byte[] original=Files.readAllBytes(RELEASE.resolve("RELEASE-MANIFEST.json"));
    if(original.length==0 || original.length>1048576) throw new IllegalStateException("manifest bounds");
    new ReleaseSignatureVerifier(pin).verify(original,signature);
    System.out.println("PG383 STAGE PINNED_SIGNATURE_VERIFIED");
    var approval=new ReleaseApproval("0.1.0-PG383",HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(original)));
    var inspected=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verifyCandidate(approval);
    System.out.println("PG383 STAGE FULL_CANDIDATE_BOM_VERIFIED");
    if(!inspected.version().equals(approval.version()) || inspected.migrations().size()!=24) throw new IllegalStateException("BOM mismatch");
    return approval;
  }
  static void freezeCandidate() throws Exception {
    // BUG342: host immutable payload, not merely ProtectSystem's private RO view.
    // Fixed isolated candidate only; M/A and terminal stop set are held by caller.
    var mounted=new ProcessBuilder("/usr/bin/mountpoint","-q",RELEASE.toString()).start();
    int status=mounted.waitFor();
    if(status==1 || status==32) {
      var bind=new ProcessBuilder("/usr/bin/mount","--bind",RELEASE.toString(),RELEASE.toString()).inheritIO().start();
      if(bind.waitFor()!=0) throw new IllegalStateException("candidate bind failed");
    } else if(status!=0) throw new IllegalStateException("candidate mount query failed");
    var freeze=new ProcessBuilder("/usr/bin/mount","-o","remount,bind,ro",RELEASE.toString()).inheritIO().start();
    if(freeze.waitFor()!=0) throw new IllegalStateException("candidate immutable mount failed");
    System.out.println("PG383 STAGE FIXED_CANDIDATE_HOST_RO");
  }
  static void migrate() throws Exception {
    // Initial PGPT VM is never accepted/issued. Genuine pending original is preserved, not reset.
    if(Files.exists(Path.of("/run/schubert-nk/startup/epoch.current"),LinkOption.NOFOLLOW_LINKS)) throw new IllegalStateException("existing epoch needs operational migration workflow");
    if(!Files.isRegularFile(PRESERVE.resolve("db-pg381/schubert_nk-before-v023.dump"),LinkOption.NOFOLLOW_LINKS)) throw new IllegalStateException("restore point missing");
    byte[] owned=Files.readAllBytes(Path.of("/etc/schubert-nk/credentials/db-migration"));
    try(var credential=InspectorDbCredential.consume(owned)) {
      char[] secret=credential.copyPassword();
      try {
        try(var database=java.sql.DriverManager.getConnection("jdbc:postgresql://127.0.0.1:5432/schubert_nk","schubert_migration",new String(secret))) {
          database.setReadOnly(true);
          database.setAutoCommit(false);
          try(var statement=database.createStatement()) {
            statement.execute("SET ROLE nk_owner");
            for(String table:List.of("schubert.app_users","schubert.auth_sessions","schubert.login_ip_attempts","schubert.script_files","schubert.speakers","schubert.script_entries","schubert.audio_files","schubert.entry_audio_links","schubert.media_assets","schubert.questions","schubert.answers","schubert.async_jobs","schubert.notifications","schubert.request_inbox","schubert.mq_outbox","schubert.app_logs","schubert_web_session.web_http_sessions","schubert_web_session.pending_context_revocations","schubert_web_session.web_log_outbox")) {
              try(var rows=statement.executeQuery("select count(*) from "+table)) {
                if(!rows.next() || rows.getLong(1)!=0 || rows.wasNull() || rows.next()) throw new IllegalStateException("initial provisioning business rows present");
              }
            }
            // V004 approved immutable seed only. No master/session/payload content is exported.
            try(var rows=statement.executeQuery("select count(*)=2 and bool_and((id=1 and code='NUKITASHI1' and title='NUKITASHI' and display_order=1 or id=2 and code='NUKITASHI2' and title='NUKITASHI2' and display_order=2) and created_at=timestamptz '2026-09-01 00:00:00+00') from schubert.games")) {
              if(!rows.next() || !rows.getBoolean(1) || rows.wasNull() || rows.next()) throw new IllegalStateException("initial seed mismatch");
            }
          }
          database.rollback();
        }
        var flyway=Flyway.configure().dataSource("jdbc:postgresql://127.0.0.1:5432/schubert_nk","schubert_migration",new String(secret))
          .defaultSchema("schubert_meta").schemas("schubert_meta").createSchemas(false).initSql("SET ROLE nk_owner")
          .table("flyway_schema_history").locations("filesystem:"+RELEASE.resolve("db/migration"))
          .validateOnMigrate(true).cleanDisabled(true).target("023").load();
        var validation=flyway.validateWithResult();
        for(var invalid:validation.invalidMigrations)
          System.out.println("PG383 MIGRATION_VALIDATION version="+invalid.version+" code="+invalid.errorDetails.errorCode);
        if(validation.validationSuccessful || validation.invalidMigrations.size()!=1
            || !"023".equals(validation.invalidMigrations.get(0).version)
            || !"RESOLVED_VERSIONED_MIGRATION_NOT_APPLIED".equals(validation.invalidMigrations.get(0).errorDetails.errorCode.toString()))
          throw new IllegalStateException("unexpected migration validation inventory");
        var pending=flyway.info().pending();
        if(pending.length!=1 || !pending[0].getVersion().getVersion().equals("023")) throw new IllegalStateException("unexpected migration inventory");
        if(flyway.migrate().migrationsExecuted!=1) throw new IllegalStateException("migration result");
        flyway.validate();
      } finally { Arrays.fill(secret,'\0'); }
    }
  }
  static void activate(ReleaseApproval approval) throws Exception {
    if(Files.exists(Path.of("/run/schubert-nk/startup/epoch.current"),LinkOption.NOFOLLOW_LINKS)) throw new IllegalStateException("no operational permit replacement here");
    Path dir=Path.of("/etc/schubert-nk/release-approval");
    Files.createDirectory(dir,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
    Path part=dir.resolve("pg383.part");
    Files.write(part,approval.encode(),StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));
    try(var f=FileChannel.open(part,StandardOpenOption.READ)){f.force(true);}
    Files.move(part,dir.resolve("current"),StandardCopyOption.ATOMIC_MOVE);
    sync(dir);
    Path current=Path.of("/opt/schubert-nk/current"), next=current.resolveSibling("pg383-current.part");
    Path previous=Files.readSymbolicLink(current);
    Files.writeString(PRESERVE.resolve("pg383-previous-current.txt"),previous+"\n",StandardOpenOption.CREATE_NEW);
    Files.createSymbolicLink(next,RELEASE);
    Files.move(next,current,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
    sync(current.getParent());
    var result=StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(ReleaseApproval.parse(Files.readAllBytes(dir.resolve("current"))));
    if(!result.version().equals("0.1.0-PG383")) throw new IllegalStateException("activation readback");
  }
  static void stopAll() throws Exception {
    for(var unit:MaintenanceUnit.values()) {
      var p=new ProcessBuilder("/usr/bin/systemctl","stop",unit.serviceName()).inheritIO().start();
      if(p.waitFor()!=0)throw new IllegalStateException("stop failed");
    }
    terminalAll();
  }
  static void terminalAll() throws Exception {
    for(var unit:MaintenanceUnit.values()) {
      var p=new ProcessBuilder("/usr/bin/systemctl","show",unit.serviceName(),"--property=LoadState,ActiveState,MainPID,ControlPID,ControlGroup,Job").start();
      String raw=new String(p.getInputStream().readAllBytes(),StandardCharsets.US_ASCII);
      if(p.waitFor()!=0)throw new IllegalStateException("unit observation failed");
      var fields=new HashMap<String,String>();
      for(String line:raw.split("\n")){int split=line.indexOf('=');if(split<1 || fields.put(line.substring(0,split),line.substring(split+1))!=null)throw new IllegalStateException("unit profile");}
      if(!fields.keySet().equals(Set.of("LoadState","ActiveState","MainPID","ControlPID","ControlGroup","Job"))
          || !"loaded".equals(fields.get("LoadState")) || !Set.of("inactive","failed").contains(fields.get("ActiveState"))
          || !"0".equals(fields.get("MainPID")) || !"0".equals(fields.get("ControlPID")) || !"".equals(fields.get("Job")))throw new IllegalStateException("unit not terminal");
      Path cgroup=Path.of("/sys/fs/cgroup/system.slice",unit.serviceName());
      if(Files.exists(cgroup)) {
        if(!Files.readString(cgroup.resolve("cgroup.procs")).isBlank() || !Files.readString(cgroup.resolve("cgroup.events")).contains("populated 0\n"))throw new IllegalStateException("unit processes remain");
      }
    }
  }
  static byte[] material(Path p,int size) throws Exception {
    var before=Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS);
    if(!Integer.valueOf(0).equals(before.get("uid")) || !Integer.valueOf(0).equals(before.get("gid")) || !Integer.valueOf(0100400).equals(before.get("mode"))
       || !Integer.valueOf(1).equals(before.get("nlink")) || !Long.valueOf(size).equals(before.get("size")))throw new IllegalStateException("fixed public material metadata");
    byte[] value=Files.readAllBytes(p);
    if(value.length!=size || !before.equals(Files.readAttributes(p,"unix:uid,gid,mode,nlink,size,dev,ino,ctime,lastModifiedTime",LinkOption.NOFOLLOW_LINKS)))throw new IllegalStateException("public material changed");
    return value;
  }
  static void sync(Path dir) throws Exception {try(var f=FileChannel.open(dir,StandardOpenOption.READ)){f.force(true);}}
}
