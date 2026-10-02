import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.backup.BackupProfile;
import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.RunReferenceRepository;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.sql.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.internal.resolver.ChecksumCalculator;
import org.flywaydb.core.internal.resource.StringResource;

/** SSC159/MIG025. One signed isolated 23->25 deployment, never runtime authority/auto repair. */
public final class Pg422SignedMigration {
  static final Path CANDIDATE=Path.of("/opt/schubert-nk/releases/0.1.0-PG421");
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG408");
  static final Path SAVED=Path.of("/var/lib/pgpt-s1-preservation/pg422-migration");
  static final Path PROFILE=Path.of("/etc/schubert-nk/backup-profile.json");
  static final String SOURCE="995d3c5386f09b89bc4af4a2e7c9d3fdb9f603e3";
  static final List<String> TABLES=List.of("schubert.app_users","schubert.auth_sessions","schubert.login_ip_attempts",
      "schubert.script_files","schubert.speakers","schubert.script_entries","schubert.audio_files","schubert.entry_audio_links",
      "schubert.media_assets","schubert.questions","schubert.answers","schubert.async_jobs","schubert.notifications",
      "schubert.request_inbox","schubert.mq_outbox","schubert.app_logs","schubert_web_session.web_http_sessions",
      "schubert_web_session.pending_context_revocations","schubert_web_session.web_log_outbox","schubert.games");
  record Data(long rows,String sha256) {}
  static void configure() {
    Pg387TrustedDeployment.LABEL="PG421";Pg387TrustedDeployment.STEM="pg421";
    Pg387TrustedDeployment.SOURCE=SOURCE;Pg387TrustedDeployment.RELEASE=CANDIDATE;
  }
  static String hash(byte[] bytes) throws Exception {return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));}
  static boolean schemaOnly(byte[] old,byte[] next) {
    var before=BackupProfile.consume(old.clone());var after=BackupProfile.consume(next.clone());
    return before.versions().schema().equals("023") && after.versions().schema().equals("025")
        && new String(before.encode(),StandardCharsets.US_ASCII).replace("\"schema\":\"023\"","\"schema\":\"025\"")
            .equals(new String(after.encode(),StandardCharsets.US_ASCII));
  }
  static Map<String,Data> business(Connection database) throws Exception {
    var result=new TreeMap<String,Data>();
    for(String table:TABLES) {
      String value=table.equals("schubert.notifications")
          ? "jsonb_set(to_jsonb(t),'{state}',to_jsonb(case when state='ACCEPTED' then 'RECEIVED' else state end))"
          : table.equals("schubert.mq_outbox")
              ? "to_jsonb(t)-array['dlq_original_message_id','dlq_original_transport_id','dlq_delivery_count','dlq_error_code','dlq_detected_at']::text[]"
              : "to_jsonb(t)";
      var digest=MessageDigest.getInstance("SHA-256");long count=0;
      try(var query=database.createStatement()) {
        query.setQueryTimeout(5);
        try(var rows=query.executeQuery("select row_value from (select ("+value+")::text collate \"C\" as row_value from "+table+" t) snapshot order by row_value")) {
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
  static List<List<Object>> history(Connection database) throws Exception {
    var result=new ArrayList<List<Object>>();
    try(var query=database.createStatement()) {
      query.setQueryTimeout(5);
      try(var rows=query.executeQuery("select installed_rank,version,type,script,checksum,success from schubert_meta.flyway_schema_history order by installed_rank")) {
        while(rows.next()) {
          var row=new ArrayList<Object>();for(int i=1;i<=6;i++)row.add(rows.getObject(i));
          result.add(Collections.unmodifiableList(row));
        }
      }
    }
    return List.copyOf(result);
  }
  static List<List<Object>> expected(int sqlCount) throws Exception {
    if(sqlCount!=23 && sqlCount!=25)throw new IllegalArgumentException("fixed schema inventory");
    var result=new ArrayList<List<Object>>();
    result.add(Arrays.asList(0,null,"SCHEMA","\"schubert_meta\"",null,true));
    try(var files=Files.list(CANDIDATE.resolve("db/migration"))) {
      var names=files.sorted().toList();if(names.size()!=25)throw new IllegalStateException("fixed25 SQL files required");
      for(int i=0;i<sqlCount;i++) {
        Path file=names.get(i);String name=file.getFileName().toString();String version=String.format(Locale.ROOT,"%03d",i+1);
        if(!name.matches("V"+version+"__[a-z0-9_]+\\.sql"))throw new IllegalStateException("contiguous approved SQL required");
        String sql=Files.readString(file,StandardCharsets.UTF_8);
        if(i<23 && !Arrays.equals(Files.readAllBytes(file),Files.readAllBytes(OLD.resolve("db/migration").resolve(name))))
          throw new IllegalStateException("old23 SQL bytes changed");
        result.add(Arrays.asList(i+1,version,"SQL",name,ChecksumCalculator.calculate(new StringResource(sql)),true));
      }
    }
    return List.copyOf(result);
  }
  static void original(Connection database) throws Exception {
    try(var root=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),Path.of("/run/schubert-nk/startup"))) {
      var files=new StartupPermitFiles(root,LinuxInodeSecurity.create());var epoch=files.current();
      if(epoch.state()!=StartupPermitRecords.State.INVALID || !epoch.activation().run().id().equals(Pg407FailedRootRecovery.RUN)
          || !epoch.activation().id().equals(Pg407FailedRootRecovery.ACTIVATION))throw new IllegalStateException("same incomplete original required");
      var observed=MaintenanceRunFiles.create().execute(session->session.observe(epoch.activation()));
      if(!observed.equals(epoch.activation()) || !new RunReferenceRepository(database).read(observed.run()).identityConsistent()
          || !epoch.equals(files.current()))throw new IllegalStateException("complete same original graph required");
    }
  }
  static void save(String name,byte[] bytes) throws Exception {
    Path file=SAVED.resolve(name);Files.write(file,bytes,StandardOpenOption.CREATE_NEW);
    Files.setPosixFilePermissions(file,java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    try(var channel=FileChannel.open(file,StandardOpenOption.READ)){channel.force(true);}
    if(!Arrays.equals(bytes,Files.readAllBytes(file)))throw new IllegalStateException("private durable readback required");
  }
  static void restorePoint() throws Exception {
    Path file=SAVED.resolve("before-v024025.dump");
    Files.createFile(file,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rw-------")));
    var child=new ProcessBuilder("/usr/bin/sudo","-n","-u","postgres","/usr/bin/pg_dump","--format=custom","--dbname=schubert_nk")
        .redirectOutput(file.toFile()).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    if(!child.waitFor(30,TimeUnit.SECONDS)) {
      child.destroy();if(!child.waitFor(5,TimeUnit.SECONDS))throw new IllegalStateException("dump owner unresolved");
      throw new IllegalStateException("private dump timed out");
    }
    if(child.exitValue()!=0 || Files.size(file)<1024)throw new IllegalStateException("private restore point failed");
    try(var reader=Files.newInputStream(file)) {
      if(!Arrays.equals("PGDMP".getBytes(StandardCharsets.US_ASCII),reader.readNBytes(5)))throw new IllegalStateException("custom dump header required");
    }
    try(var channel=FileChannel.open(file,StandardOpenOption.READ)){channel.force(true);}
    Pg387TrustedDeployment.sync(SAVED);
  }
  static void migrate() throws Exception {
    byte[] source=Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/credentials/db-migration"),65536);
    try(var credential=InspectorDbCredential.consume(source)) {
      char[] secret=credential.copyPassword();
      try {
        var flyway=Flyway.configure().dataSource("jdbc:postgresql://127.0.0.1:5432/schubert_nk","schubert_migration",new String(secret))
            .defaultSchema("schubert_meta").schemas("schubert_meta").createSchemas(false).initSql("SET ROLE nk_owner")
            .table("flyway_schema_history").locations("filesystem:"+CANDIDATE.resolve("db/migration"))
            .validateOnMigrate(true).cleanDisabled(true).target("025").load();
        var pending=flyway.info().pending();
        if(pending.length!=2 || !pending[0].getVersion().getVersion().equals("024") || !pending[1].getVersion().getVersion().equals("025"))
          throw new IllegalStateException("exact V024 V025 pending required");
        var validation=flyway.validateWithResult();
        if(validation.validationSuccessful || validation.invalidMigrations.size()!=2
            || !validation.invalidMigrations.stream().allMatch(v->Set.of("024","025").contains(v.version)
              && v.errorDetails.errorCode.toString().equals("RESOLVED_VERSIONED_MIGRATION_NOT_APPLIED")))
          throw new IllegalStateException("old checksum validation differs");
        if(flyway.migrate().migrationsExecuted!=2)throw new IllegalStateException("two migration results required");
        flyway.validate();
      } finally {Arrays.fill(secret,'\0');}
    }
  }
  static Connection openSchema() throws Exception {
    Path path=Path.of("/etc/schubert-nk/credentials/db-migration");var metadata=Pg410KnownAuthRecovery.metadata(path);
    if(!Integer.valueOf(0).equals(metadata.get("uid")) || !Integer.valueOf(0).equals(metadata.get("gid"))
        || !Integer.valueOf(0100600).equals(metadata.get("mode")))throw new IllegalStateException("fixed migration source required");
    try(var credential=InspectorDbCredential.consume(Pg410KnownAuthRecovery.material(path,65536))) {
      char[] secret=credential.copyPassword();var properties=new Properties();
      properties.setProperty("user","schubert_migration");properties.setProperty("connectTimeout","3");properties.setProperty("socketTimeout","5");
      try {
        properties.setProperty("password",new String(secret));
        var connection=DriverManager.getConnection("jdbc:postgresql://127.0.0.1:5432/schubert_nk",properties);
        try {
          connection.setAutoCommit(true);
          try(var statement=connection.createStatement()) {
            statement.setQueryTimeout(5);statement.execute("SET ROLE nk_owner");
            try(var result=statement.executeQuery("select current_user,session_user,current_database(),pg_is_in_recovery()")) {
              if(!result.next() || !"nk_owner".equals(result.getString(1)) || !"schubert_migration".equals(result.getString(2))
                  || !"schubert_nk".equals(result.getString(3)) || !Boolean.FALSE.equals(result.getObject(4,Boolean.class)) || result.next())
                throw new IllegalStateException("dedicated migration role/db required");
            }
          }
          connection.setReadOnly(true);return connection;
        } catch(Exception | Error failure) {connection.close();throw failure;}
      } finally {Arrays.fill(secret,'\0');properties.clear();}
    }
  }
  static <T> T checked(Pg387TrustedDeployment.Checked<T> work) throws java.io.IOException {
    return Pg387TrustedDeployment.checked(()-> {
      try {return work.execute();}
      catch(Exception | Error failure) {
        System.err.println("PG422_INNER_REFUSED type="+failure.getClass().getName()+" diagnosticsRedacted=true");
        for(var frame:failure.getStackTrace())if(frame.getClassName().equals("Pg422SignedMigration"))
          System.err.println("PG422_INNER_FRAME "+frame.getMethodName()+":"+frame.getLineNumber());
        throw failure;
      }
    });
  }
  static void profile(byte[] next,Map<String,Object> oldMetadata) throws Exception {
    Path part=PROFILE.resolveSibling("backup-profile.json.pg422.part");
    Files.write(part,next,StandardOpenOption.CREATE_NEW);
    Files.setAttribute(part,"unix:uid",oldMetadata.get("uid"));Files.setAttribute(part,"unix:gid",oldMetadata.get("gid"));
    Files.setPosixFilePermissions(part,java.nio.file.attribute.PosixFilePermissions.fromString("rw-r-----"));
    try(var channel=FileChannel.open(part,StandardOpenOption.READ)){channel.force(true);}
    Files.move(part,PROFILE,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);Pg387TrustedDeployment.sync(PROFILE.getParent());
    var metadata=Pg410KnownAuthRecovery.metadata(PROFILE);
    if(!Arrays.equals(next,Files.readAllBytes(PROFILE)) || !metadata.get("uid").equals(oldMetadata.get("uid"))
        || !metadata.get("gid").equals(oldMetadata.get("gid")) || !metadata.get("mode").equals(oldMetadata.get("mode"))
        || !Integer.valueOf(1).equals(metadata.get("nlink")))throw new IllegalStateException("profile readback differs");
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG422_MIGRATION_REFUSED diagnosticsRedacted=true type="+e.getClass().getName());
      for(var frame:e.getStackTrace())if(frame.getClassName().equals("Pg422SignedMigration") || frame.getClassName().equals("Pg387TrustedDeployment"))
        System.err.println("PG422_FRAME "+frame.getClassName()+"."+frame.getMethodName()+":"+frame.getLineNumber());
    });
    if(args.length!=0 || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new IllegalStateException("isolated operator only");
    MaintenanceFileLock.create().tryExclusive(()->checked(()-> {
      Pg387TrustedDeployment.requireNoUndeliveredWork();Pg387TrustedDeployment.stopAll();
      return StartupAdmissionFile.create().tryExclusive(fd->checked(()-> {
        Pg387TrustedDeployment.terminalAll();
        if(!Pg410KnownAuthRecovery.show(dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot.Target.MORNING).snapshot().quiescent())
          throw new IllegalStateException("Morning manager not quiescent");
        Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
        Pg410KnownAuthRecovery.configureVerifier();Pg410KnownAuthRecovery.signed();
        configure();Pg387TrustedDeployment.freezeCandidate();var approval=Pg387TrustedDeployment.verify();
        if(!approval.manifestSha256().equals("2348f978fafc1cdd521e1d866ca8fa3ae13d220668b266e0d989d0087cfa7979"))throw new IllegalStateException("one fixed candidate required");
        if(Files.exists(SAVED,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("partial preservation exists, not auto repair");
        Files.createDirectory(SAVED,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));
        try(var db=Pg407FailedRootRecovery.openDatabase();var schema=openSchema()) {
          db.setAutoCommit(false);
          try(var s=db.createStatement();var row=s.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
            if(!row.next() || !Boolean.TRUE.equals(row.getObject(1,Boolean.class)) || row.next())throw new IllegalStateException("dedicated advisory required");
          }
          original(db);var rows=Pg407FailedRootRecovery.databaseRows(db);if(rows.size()!=182)throw new IllegalStateException("all old182 required");
          var backup=Pg407FailedRootRecovery.backupSnapshot();var data=business(schema);
          if(!history(schema).equals(expected(23)))throw new IllegalStateException("independent old24 history differs");
          byte[] oldProfile=Pg410KnownAuthRecovery.material(PROFILE,4096),nextProfile=Files.readAllBytes(CANDIDATE.resolve("config/effective/backup-profile.json"));
          var metadata=Pg410KnownAuthRecovery.metadata(PROFILE);
          if(!Integer.valueOf(0).equals(metadata.get("uid")) || !Long.valueOf(new FixedServiceIdentity().configurationGroup()).equals(((Integer)metadata.get("gid")).longValue())
              || !Integer.valueOf(0100640).equals(metadata.get("mode")) || !hash(oldProfile).equals("cf4da30c449e3fb00ab2e23d308fc6e0b26903d590d3e3f96af0a3d2bb074c55")
              || !schemaOnly(oldProfile,nextProfile))throw new IllegalStateException("one schema-only profile change required");
          save("backup-profile-before.json",oldProfile);restorePoint();
          System.out.println("PG422_STAGE PRIVATE_RESTORE_POINT_OLD24_VERIFIED");
          migrate();
          if(!history(schema).equals(expected(25)) || !rows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !data.equals(business(schema))
              || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("migration independent preservation differs");
          original(db);Pg387TrustedDeployment.terminalAll();
          profile(nextProfile,metadata);Pg387TrustedDeployment.activate(approval);
          if(!rows.equals(Pg407FailedRootRecovery.databaseRows(db)) || !data.equals(business(schema)) || !backup.equals(Pg407FailedRootRecovery.backupSnapshot()))throw new IllegalStateException("activation preservation differs");
          original(db);Pg387TrustedDeployment.terminalAll();db.rollback();
        }
        System.out.println("PG422_DEPLOYED source="+SOURCE+" signatureAndBom=true migrations=2 history=26 all182AndBusinessAndBackupUnchanged=true profileSchema025=true permitsIssued=0 businessReady=false");
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
