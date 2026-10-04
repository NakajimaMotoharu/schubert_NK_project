import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.backup.BackupProfile;
import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.sql.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.internal.resolver.ChecksumCalculator;
import org.flywaydb.core.internal.resource.StringResource;

/** SSC178: isolated signed 025->027 provisioning, NOT a runtime authority or UNKNOWN repair.
 * Existing SQL, original, all existing rows and sealed Backups are preserved. No tool PT credit.
 */
public final class Pg456SignedMigration {
  static final Path CANDIDATE=Path.of("/opt/schubert-nk/releases/0.1.0-PG456");
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG430");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg456-migration");
  static final Path PROFILE=Path.of("/etc/schubert-nk/backup-profile.json");
  static final String OLD_SOURCE="91b010509e715e2b097c955d04f21c23f3529966";
  static final String OLD_DIGEST="ecef234624ece66c69d81383f722aee046da7b0dcab8cf10ec4df3b3d2dd1375";
  static final String VENDOR_CADDY="66177d46fa761acb07208065db9b0274cb1b12c02ac43b9bfc9857b698b1ccfe";
  static final String OLD_POLICY="3710be0c023a4bbbf3a8f095cd2d91c5b97b40ed76056ddd4ff433d4f4e066bc";
  static final String ADDRESS="10.0.2.15"; // isolated QEMU interface, not production/site selection
  static final List<String> TABLES;
  static {
    var tables=new ArrayList<>(Pg422SignedMigration.TABLES);
    tables.addAll(List.of("schubert.batch_runs","schubert.inbox_inspection_progress","schubert.log_cleanup_progress"));
    TABLES=List.copyOf(tables);
  }
  record Data(long rows,String digest) {}
  static boolean schemaOnly(byte[] old,byte[] next) {
    if(old==null || next==null)return false;
    var before=BackupProfile.consume(old.clone());var after=BackupProfile.consume(next.clone());
    return before.versions().schema().equals("025") && after.versions().schema().equals("027")
        && new String(before.encode(),StandardCharsets.US_ASCII).replace("\"schema\":\"025\"","\"schema\":\"027\"")
            .equals(new String(after.encode(),StandardCharsets.US_ASCII));
  }
  static byte[] render(byte[] template) {
    if(template==null || template.length==0 || template.length>65536)throw new IllegalArgumentException("fixed template bounds");
    String text=new String(template,StandardCharsets.US_ASCII);
    if(!text.contains("https://<GLOBAL_IP>:55160 {\n") || !text.contains("    bind <GLOBAL_IP>\n")
        || text.split("<GLOBAL_IP>",-1).length!=3)throw new IllegalArgumentException("two fixed public placeholders required");
    return text.replace("<GLOBAL_IP>",ADDRESS).getBytes(StandardCharsets.US_ASCII);
  }
  static List<List<Object>> expected(Path candidate,Path old,int count) throws Exception {
    if(count!=25 && count!=27)throw new IllegalArgumentException("fixed approved inventory");
    var result=new ArrayList<List<Object>>();result.add(Arrays.asList(0,null,"SCHEMA","\"schubert_meta\"",null,true));
    try(var files=Files.list(candidate.resolve("db/migration"))) {
      var names=files.sorted().toList();if(names.size()!=27)throw new IllegalStateException("fixed27 SQL required");
      for(int i=0;i<27;i++) {
        var file=names.get(i);String name=file.getFileName().toString(),version=String.format(Locale.ROOT,"%03d",i+1);
        if(!name.matches("V"+version+"__[a-z0-9_]+\\.sql"))throw new IllegalStateException("contiguous approved inventory");
        byte[] bytes=Files.readAllBytes(file);
        if(i<25 && !Arrays.equals(bytes,Files.readAllBytes(old.resolve("db/migration").resolve(name))))
          throw new IllegalStateException("immutable old25 SQL differs");
        if(i<count)result.add(Arrays.asList(i+1,version,"SQL",name,
            ChecksumCalculator.calculate(new StringResource(new String(bytes,StandardCharsets.UTF_8))),true));
      }
    }
    return List.copyOf(result);
  }
  static Map<String,Data> business(Connection db) throws Exception {
    var result=new TreeMap<String,Data>();
    for(String table:TABLES) {
      var digest=MessageDigest.getInstance("SHA-256");long count=0;
      try(var query=db.createStatement()) {
        query.setQueryTimeout(5);
        // Preserve ALL old columns and values; no 023->025 state normalization or dropped fields.
        try(var rows=query.executeQuery("select row_value from (select to_jsonb(t)::text collate \"C\" row_value from "+table+" t) snapshot order by row_value")) {
          while(rows.next()) {
            byte[] bytes=Objects.requireNonNull(rows.getString(1)).getBytes(StandardCharsets.UTF_8);
            digest.update(ByteBuffer.allocate(4).putInt(bytes.length).array());digest.update(bytes);Arrays.fill(bytes,(byte)0);count++;
          }
        }
      }
      result.put(table,new Data(count,HexFormat.of().formatHex(digest.digest())));
    }
    return Map.copyOf(result);
  }
  static void original(Connection db) throws Exception {
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))) {
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
      UUID boot=UUID.fromString(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim());
      if(epoch.state()!=StartupPermitRecords.State.INVALID || !epoch.boot().equals(boot)
          || !epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
          || !epoch.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION))throw new IllegalStateException("current cold INVALID same original required");
      var observed=MaintenanceRunFiles.create().execute(session->session.observeStartup(epoch.activation()));
      if(!observed.activation().equals(epoch.activation()) || observed.completed().isPresent()
          || !new RunReferenceRepository(db).read(epoch.activation().run()).identityConsistent()
          || !epoch.equals(files.current()))throw new IllegalStateException("pending full original graph required");
    }
  }
  static void save(String name,byte[] value) throws Exception {
    Path file=SAVE.resolve(name);Files.write(file,value,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(file,PosixFilePermissions.fromString("rw-------"));
    try(var channel=FileChannel.open(file,StandardOpenOption.READ)){channel.force(true);}
    if(!Arrays.equals(value,Files.readAllBytes(file)))throw new IllegalStateException("private before-image readback");
    Pg387TrustedDeployment.sync(SAVE);
  }
  static void restorePoint() throws Exception {
    Path file=SAVE.resolve("before-v026027.dump");
    Files.createFile(file,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    var child=new ProcessBuilder("/usr/bin/sudo","-n","-u","postgres","/usr/bin/pg_dump","--format=custom","--dbname=schubert_nk")
        .redirectOutput(file.toFile()).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    if(!child.waitFor(30,TimeUnit.SECONDS)) {
      child.destroy();if(!child.waitFor(5,TimeUnit.SECONDS))throw new IllegalStateException("restore-point child ownership UNKNOWN");
      throw new IllegalStateException("restore point timed out");
    }
    if(child.exitValue()!=0 || Files.size(file)<1024)throw new IllegalStateException("private restore point unavailable");
    try(var reader=Files.newInputStream(file)) {if(!Arrays.equals(reader.readNBytes(5),"PGDMP".getBytes(StandardCharsets.US_ASCII)))throw new IllegalStateException("dump header");}
    try(var channel=FileChannel.open(file,StandardOpenOption.READ)){channel.force(true);}Pg387TrustedDeployment.sync(SAVE);
  }
  static void migrate() throws Exception {
    try(var credential=InspectorDbCredential.consume(Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/credentials/db-migration"),65536))) {
      char[] password=credential.copyPassword();
      try {
        var flyway=Flyway.configure().dataSource("jdbc:postgresql://127.0.0.1:5432/schubert_nk","schubert_migration",new String(password))
            .defaultSchema("schubert_meta").schemas("schubert_meta").createSchemas(false).initSql("SET ROLE nk_owner")
            .table("flyway_schema_history").locations("filesystem:"+CANDIDATE.resolve("db/migration"))
            .validateOnMigrate(true).cleanDisabled(true).target("027").load();
        var pending=flyway.info().pending();
        if(pending.length!=2 || !pending[0].getVersion().getVersion().equals("026") || !pending[1].getVersion().getVersion().equals("027"))throw new IllegalStateException("exact026027 pending required");
        var validation=flyway.validateWithResult();
        if(validation.validationSuccessful || validation.invalidMigrations.size()!=2
            || !validation.invalidMigrations.stream().allMatch(v->Set.of("026","027").contains(v.version)
              && v.errorDetails.errorCode.toString().equals("RESOLVED_VERSIONED_MIGRATION_NOT_APPLIED")))throw new IllegalStateException("old checksum validation differs");
        if(flyway.migrate().migrationsExecuted!=2)throw new IllegalStateException("two migration results required");flyway.validate();
      } finally {Arrays.fill(password,'\0');}
    }
  }
  static void postconditions(Connection db) throws Exception {
    String sql="""
        select (select count(*)=0 from schubert_web_session.web_receipt_references),
          (select not attnotnull from pg_catalog.pg_attribute where attrelid='schubert_web_session.pending_context_revocations'::regclass and attname='expires_at' and not attisdropped),
          has_table_privilege('schubert_web_session','schubert_web_session.web_receipt_references','SELECT,INSERT,DELETE'),
          not has_table_privilege('schubert_web_session','schubert_web_session.web_receipt_references','UPDATE'),
          has_table_privilege('schubert_backup','schubert_web_session.web_receipt_references','SELECT'),
          not has_table_privilege('schubert_app','schubert_web_session.web_receipt_references','SELECT'),
          not has_table_privilege('schubert_batch','schubert_web_session.web_receipt_references','SELECT'),
          has_function_privilege('schubert_batch','schubert.maintenance_cleanup_web_receipt_references(uuid,timestamptz,integer)','EXECUTE'),
          not has_function_privilege('schubert_app','schubert.maintenance_cleanup_web_receipt_references(uuid,timestamptz,integer)','EXECUTE'),
          (select count(*)=4 and bool_and(convalidated) from pg_catalog.pg_constraint where conrelid='schubert_web_session.web_receipt_references'::regclass),
          to_regclass('schubert_web_session.ix_web_receipt_references_question_id') is not null
        """;
    try(var query=db.createStatement()) {
      query.setQueryTimeout(5);try(var row=query.executeQuery(sql)) {
        if(!row.next())throw new IllegalStateException("schema postcondition absent");
        for(int i=1;i<=11;i++)if(!Boolean.TRUE.equals(row.getObject(i,Boolean.class)))throw new IllegalStateException("schema contract postcondition differs");
        if(row.next())throw new IllegalStateException("schema postcondition duplicate");
      }
    }
  }
  static void replace(Path file,byte[] value,int group,String mode) throws Exception {
    Path part=file.resolveSibling(file.getFileName()+".pg456.part");
    Files.write(part,value,StandardOpenOption.CREATE_NEW);Files.setAttribute(part,"unix:uid",0);Files.setAttribute(part,"unix:gid",group);
    Files.setPosixFilePermissions(part,PosixFilePermissions.fromString(mode));
    try(var channel=FileChannel.open(part,StandardOpenOption.READ)){channel.force(true);}
    Files.move(part,file,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(file.getParent());
    if(!Arrays.equals(value,Files.readAllBytes(file)))throw new IllegalStateException("fixed placement readback differs");
  }
  static void caddy() throws Exception {
    Path config=Path.of("/etc/caddy/Caddyfile"),directory=Path.of("/etc/systemd/system/caddy.service.d");
    Path oldPolicy=directory.resolve("schubert-nk-stop-policy.conf");
    byte[] before=Pg410KnownAuthRecovery.material(config,65536);
    var attributes=Pg410KnownAuthRecovery.metadata(config);
    if(!Pg422SignedMigration.hash(before).equals(VENDOR_CADDY) || !Integer.valueOf(0).equals(attributes.get("uid"))
        || !Integer.valueOf(0).equals(attributes.get("gid")) || !Integer.valueOf(0100644).equals(attributes.get("mode"))
        || !Integer.valueOf(1).equals(attributes.get("nlink")))throw new IllegalStateException("one untouched vendor Caddy before-image required");
    var dir=Pg410KnownAuthRecovery.metadata(directory);var policyMetadata=Pg410KnownAuthRecovery.metadata(oldPolicy);
    if(!Integer.valueOf(0).equals(dir.get("uid")) || !Integer.valueOf(0).equals(dir.get("gid")) || !Integer.valueOf(0040755).equals(dir.get("mode"))
        || !Integer.valueOf(0).equals(policyMetadata.get("uid")) || !Integer.valueOf(0).equals(policyMetadata.get("gid"))
        || !Integer.valueOf(0100644).equals(policyMetadata.get("mode")) || !Integer.valueOf(1).equals(policyMetadata.get("nlink")))throw new IllegalStateException("fixed old policy metadata required");
    try(var entries=Files.list(directory)) {
      if(!entries.map(p->p.getFileName().toString()).toList().equals(List.of("schubert-nk-stop-policy.conf")))throw new IllegalStateException("unknown Caddy policy isolated");
    }
    byte[] oldPolicyBytes=Pg410KnownAuthRecovery.material(oldPolicy,16384);
    if(!Pg422SignedMigration.hash(oldPolicyBytes).equals(OLD_POLICY))throw new IllegalStateException("fixed old stop-only policy differs");
    byte[] next=render(Files.readAllBytes(CANDIDATE.resolve("config/caddy/Caddyfile.template")));
    byte[] policy=Files.readAllBytes(CANDIDATE.resolve("systemd/caddy.service.d/schubert-nk-startup-policy.conf"));
    if(policy.length==0 || policy.length>16384)throw new IllegalStateException("signed fixed policy bounds");
    save("caddy-before.conf",before);save("caddy-before-metadata.txt",attributes.toString().getBytes(StandardCharsets.US_ASCII));
    save("caddy-stop-policy-before.conf",oldPolicyBytes);save("caddy-stop-policy-before-metadata.txt",policyMetadata.toString().getBytes(StandardCharsets.US_ASCII));
    int group=Math.toIntExact(new FixedServiceIdentity().resolveCaddy().gid());
    replace(config,next,group,"rw-r-----");
    replace(directory.resolve("schubert-nk-startup-policy.conf"),policy,0,"rw-r--r--");
    // Same-filesystem recoverable retirement of this exact already-saved stop-only file.
    // Its approved directives are contained in the new signed fixed policy. Never remove unknown drop-ins.
    Path retired=SAVE.resolve("caddy-stop-policy-original.conf");
    Files.move(oldPolicy,retired,StandardCopyOption.ATOMIC_MOVE);Files.setPosixFilePermissions(retired,PosixFilePermissions.fromString("rw-------"));
    Pg387TrustedDeployment.sync(SAVE);Pg387TrustedDeployment.sync(directory);
    if(!Arrays.equals(oldPolicyBytes,Files.readAllBytes(retired)))throw new IllegalStateException("retired policy before-image differs");
    var reload=new ProcessBuilder("/usr/bin/systemctl","daemon-reload").inheritIO().start();
    if(!reload.waitFor(20,TimeUnit.SECONDS)) {reload.destroy();if(!reload.waitFor(5,TimeUnit.SECONDS))throw new IllegalStateException("reload child ownership UNKNOWN");throw new IllegalStateException("reload deadline");}
    if(reload.exitValue()!=0)throw new IllegalStateException("signed policy reload failed");
    Pg387TrustedDeployment.terminalAll();
  }
  static void configure(String source) {
    Pg387TrustedDeployment.LABEL="PG456";Pg387TrustedDeployment.STEM="pg456";Pg387TrustedDeployment.SOURCE=source;
    Pg387TrustedDeployment.RELEASE=CANDIDATE;Pg387TrustedDeployment.expectedSchema("027");
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG456_MIGRATION_REFUSED type="+e.getClass().getName()+" diagnosticsRedacted=true preservationRetained=true");
      for(var frame:e.getStackTrace())if(frame.getClassName().equals("Pg456SignedMigration"))System.err.println("PG456_FRAME "+frame.getMethodName()+":"+frame.getLineNumber());
    });
    if(args.length!=2 || !args[0].matches("[0-9a-f]{40}") || !args[1].matches("[0-9a-f]{64}")
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new IllegalArgumentException("isolated fixed signed candidate only");
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      Pg387TrustedDeployment.requireNoUndeliveredWork();Pg387TrustedDeployment.terminalAll();
      if(!Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).snapshot().quiescent())throw new IllegalStateException("Morning not quiescent");
      Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        Pg387TrustedDeployment.terminalAll();
        Pg387TrustedDeployment.LABEL="PG430";Pg387TrustedDeployment.STEM="pg430";Pg387TrustedDeployment.SOURCE=OLD_SOURCE;Pg387TrustedDeployment.RELEASE=OLD;Pg387TrustedDeployment.expectedSchema("025");
        var old=Pg387TrustedDeployment.verify();
        if(!old.manifestSha256().equals(OLD_DIGEST) || !Arrays.equals(old.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))))throw new IllegalStateException("preserved signed025 current required");
        configure(args[0]);Pg387TrustedDeployment.freezeCandidate();var approval=Pg387TrustedDeployment.verify();
        if(!approval.manifestSha256().equals(args[1]))throw new IllegalStateException("host fixed signed digest differs");
        if(Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("existing partial preservation, no auto repair");
        Files.createDirectory(SAVE,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
        try(var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          db.setAutoCommit(false);
          try(var query=db.createStatement();var row=query.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
            if(!row.next() || !Boolean.TRUE.equals(row.getObject(1,Boolean.class)) || row.next())throw new IllegalStateException("same dedicated DB owner required");
          }
          original(db);var originals=Pg428ColdBootPreparation.original();var rows=Pg407FailedRootRecovery.databaseRows(db);
          if(rows.size()!=251)throw new IllegalStateException("saved251 full14-column rows required");
          var backup=Pg407FailedRootRecovery.backupSnapshot();var data=business(schema);
          if(!Pg422SignedMigration.history(schema).equals(expected(CANDIDATE,OLD,25)))throw new IllegalStateException("independent old26 history differs");
          byte[] before=Pg410KnownAuthRecovery.material(PROFILE,4096),next=Files.readAllBytes(CANDIDATE.resolve("config/effective/backup-profile.json"));
          var metadata=Pg410KnownAuthRecovery.metadata(PROFILE);
          if(!Integer.valueOf(0).equals(metadata.get("uid")) || !Integer.valueOf(Math.toIntExact(new FixedServiceIdentity().configurationGroup())).equals(metadata.get("gid"))
              || !Integer.valueOf(0100640).equals(metadata.get("mode")) || !schemaOnly(before,next))throw new IllegalStateException("one schema-only public profile delta");
          save("backup-profile-before.json",before);restorePoint();
          System.out.println("PG456_STAGE PRIVATE_RESTORE_POINT_OLD26_VERIFIED");migrate();postconditions(schema);
          if(!Pg422SignedMigration.history(schema).equals(expected(CANDIDATE,OLD,27)) || !rows.equals(Pg407FailedRootRecovery.databaseRows(db))
              || !data.equals(business(schema)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()) || !originals.equals(Pg428ColdBootPreparation.original()))throw new IllegalStateException("migration preservation differs");
          original(db);Pg387TrustedDeployment.terminalAll();caddy();
          replace(PROFILE,next,Math.toIntExact(new FixedServiceIdentity().configurationGroup()),"rw-r-----");Pg387TrustedDeployment.activate(approval);
          postconditions(schema);original(db);Pg387TrustedDeployment.terminalAll();
          if(!rows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !data.equals(business(schema)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot())
              || !originals.equals(Pg428ColdBootPreparation.original()))throw new IllegalStateException("activation preservation differs");db.rollback();
        }
        System.out.println("PG456_DEPLOYED source="+args[0]+" signatureAndBom=true migrations=2 history=28 existing251RowsOriginalBusinessBackupUnchanged=true profileSchema027=true permitsIssued=0 businessReady=false");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
