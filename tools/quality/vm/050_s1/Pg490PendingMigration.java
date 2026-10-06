import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.backup.BackupProfile;
import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.*;
import java.io.*;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.sql.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.internal.resolver.ChecksumCalculator;
import org.flywaydb.core.internal.resource.StringResource;

/** SSC202: bounded isolated 027->028 only; no current/Unit/epoch/DB-business mutation. */
public final class Pg490PendingMigration {
  static final Path NEXT=Path.of("/opt/schubert-nk/releases/0.1.0-PG489");
  static final Path OLD=Path.of("/opt/schubert-nk/releases/0.1.0-PG486");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg490-schema028");
  static final Path TOOLS=Path.of("/var/lib/pgpt-s1-preservation/pg490-migration-tools-v2");
  static final List<String> BUSINESS_ROLES=List.of("schubert_batch","schubert_app","schubert_web_session","schubert_inbox_inspector","schubert_backup");
  static final Path PROFILE=Path.of("/etc/schubert-nk/backup-profile.json");
  static final UUID RUN=UUID.fromString("91a748b4-1abe-484c-9682-44f46429b324");
  static final UUID ACTIVATION=UUID.fromString("179758d2-5b77-443a-a743-bf0065e732ea");
  static final Instant CUTOFF=Instant.parse("2026-10-06T12:06:14.564793Z");
  static String phase="PREFLIGHT";
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed pending migration refused");}
  static boolean arguments(String[] a){return a!=null && a.length==2 && a[0]!=null && a[1]!=null && a[0].matches("[0-9a-f]{40}") && a[1].matches("[0-9a-f]{64}");}
  static boolean schemaOnly(byte[] old,byte[] next){
    if(old==null || next==null)return false;
    var before=BackupProfile.consume(old.clone());var after=BackupProfile.consume(next.clone());
    return before.versions().schema().equals("027") && after.versions().schema().equals("028")
        && new String(before.encode(),StandardCharsets.US_ASCII).replace("\"schema\":\"027\"","\"schema\":\"028\"")
           .equals(new String(after.encode(),StandardCharsets.US_ASCII));
  }
  static void retain(Throwable failure){
    System.err.println("PG490_UNKNOWN phase="+phase+" type="+failure.getClass().getName()+" ownershipRetained=true oldCloseNotInferred=true");
    for(;;)try{Thread.sleep(1000);}catch(InterruptedException ignored){Thread.interrupted();}
  }
  static void original()throws Exception{
    var epoch=StartupPermitRecords.readEpoch(Files.readAllBytes(Path.of("/run/schubert-nk/startup/epoch.current")));
    require(epoch.state()==StartupPermitRecords.State.INVALID && epoch.boot().equals(UUID.fromString(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim()))
        && epoch.activation().run().id().equals(RUN) && epoch.activation().run().cutoff().equals(CUTOFF) && epoch.activation().id().equals(ACTIVATION));
    var observed=MaintenanceRunFiles.create().execute(s->s.observeStartup(epoch.activation()));
    require(observed.activation().equals(epoch.activation()) && observed.completed().isEmpty());
  }
  static List<List<Object>> expected(int count)throws Exception{
    require(count==27 || count==28);var rows=new ArrayList<List<Object>>();
    rows.add(Arrays.asList(0,null,"SCHEMA","\"schubert_meta\"",null,true));
    try(var files=Files.list(NEXT.resolve("db/migration"))){
      var names=files.sorted().toList();require(names.size()==28);
      for(int i=0;i<28;i++){
        Path p=names.get(i);String name=p.getFileName().toString(),version=String.format(Locale.ROOT,"%03d",i+1);
        require(name.matches("V"+version+"__[a-z0-9_]+\\.sql"));byte[] bytes=Files.readAllBytes(p);
        if(i<27)require(Arrays.equals(bytes,Files.readAllBytes(OLD.resolve("db/migration").resolve(name))));
        if(i<count)rows.add(Arrays.asList(i+1,version,"SQL",name,ChecksumCalculator.calculate(new StringResource(new String(bytes,StandardCharsets.UTF_8))),true));
      }
    }return List.copyOf(rows);
  }
  static final class References {
    final Process child;final InputStream input;final OutputStream output;
    References(int backend,String source,String digest)throws Exception{
      Path log=SAVE.resolve("refs.private.log");Files.createFile(log,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
      child=new ProcessBuilder("/usr/bin/python3","-B",TOOLS.resolve("pg490_migration_refs.py").toString(),Integer.toString(backend),source,digest).redirectError(log.toFile()).start();
      input=child.getInputStream();output=child.getOutputStream();await("REF_READY");
    }
    void await(String expected)throws Exception{
      long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);var bytes=new ByteArrayOutputStream();
      while(System.nanoTime()<deadline){
        while(input.available()>0){int v=input.read();if(v<0 || bytes.size()==64)throw new IOException("reference unavailable");bytes.write(v);
          if(v==10){require(Arrays.equals(bytes.toByteArray(),(expected+"\n").getBytes(StandardCharsets.US_ASCII)));return;}}
        if(child.waitFor(10,TimeUnit.MILLISECONDS) && input.available()==0)throw new IOException("reference unavailable");
      }throw new IOException("reference deadline");
    }
    void check(String value)throws Exception{require(Set.of("before","after").contains(value));output.write((value+"\n").getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_CHECKED");original();}
    void release()throws Exception{output.write("release\n".getBytes(StandardCharsets.US_ASCII));output.flush();await("REF_RELEASED");require(child.waitFor(5,TimeUnit.SECONDS) && child.exitValue()==0);output.close();input.close();child.getErrorStream().close();}
  }
  static void restorePoint()throws Exception{
    Path file=SAVE.resolve("before-v028.dump");Files.createFile(file,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    var child=new ProcessBuilder("/usr/bin/sudo","-n","-u","postgres","/usr/bin/pg_dump","--format=custom","--dbname=schubert_nk").redirectOutput(file.toFile()).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    if(!child.waitFor(30,TimeUnit.SECONDS)){child.destroy();require(child.waitFor(5,TimeUnit.SECONDS));throw new IOException("private dump deadline");}
    require(child.exitValue()==0 && Files.size(file)>1024);
    try(var input=Files.newInputStream(file)){require(Arrays.equals(input.readNBytes(5),"PGDMP".getBytes(StandardCharsets.US_ASCII)));}
    var list=new ProcessBuilder("/usr/bin/pg_restore","--list",file.toString()).redirectOutput(ProcessBuilder.Redirect.DISCARD).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    if(!list.waitFor(30,TimeUnit.SECONDS)){list.destroy();require(list.waitFor(5,TimeUnit.SECONDS));throw new IOException("private list deadline");}require(list.exitValue()==0);
    try(var channel=FileChannel.open(file,StandardOpenOption.READ)){channel.force(true);}Pg387TrustedDeployment.sync(SAVE);
  }
  static void migrate()throws Exception{
    try(var credential=InspectorDbCredential.consume(Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/credentials/db-migration"),65536))){
      char[] password=credential.copyPassword();try{
        var flyway=Flyway.configure().dataSource("jdbc:postgresql://127.0.0.1:5432/schubert_nk","schubert_migration",new String(password)).defaultSchema("schubert_meta").schemas("schubert_meta").createSchemas(false).initSql("SET ROLE nk_owner").table("flyway_schema_history").locations("filesystem:"+NEXT.resolve("db/migration")).validateOnMigrate(true).cleanDisabled(true).target("028").load();
        var pending=flyway.info().pending();require(pending.length==1 && pending[0].getVersion().getVersion().equals("028"));
        var validation=flyway.validateWithResult();require(!validation.validationSuccessful && validation.invalidMigrations.size()==1 && validation.invalidMigrations.getFirst().version.equals("028") && validation.invalidMigrations.getFirst().errorDetails.errorCode.toString().equals("RESOLVED_VERSIONED_MIGRATION_NOT_APPLIED"));
        require(flyway.migrate().migrationsExecuted==1);flyway.validate();
      }finally{Arrays.fill(password,'\0');}
    }
  }
  static void postconditions(Connection schema)throws Exception{
    String function="schubert.maintenance_read_success_progress(uuid,timestamptz,text,timestamptz)";
    try(var q=schema.createStatement()){q.setQueryTimeout(5);
      try(var r=q.executeQuery("select pg_get_userbyid(proowner)='nk_owner',prosecdef,proconfig @> array['search_path=pg_catalog, schubert','TimeZone=UTC']::text[] from pg_proc where oid='"+function+"'::regprocedure")){require(r.next() && r.getBoolean(1) && r.getBoolean(2) && r.getBoolean(3) && !r.next());}
      for(String role:BUSINESS_ROLES){
        try(var r=q.executeQuery("select has_function_privilege('"+role+"','"+function+"','EXECUTE')")){require(r.next() && r.getBoolean(1)==role.equals("schubert_batch") && !r.next());}
      }
      try(var r=q.executeQuery("select not exists(select 1 from pg_proc p, lateral aclexplode(p.proacl) a where p.oid='"+function+"'::regprocedure and a.grantee=0)")){require(r.next() && r.getBoolean(1) && !r.next());}
    }
  }
  static List<String> catalog(Connection schema)throws Exception{
    var values=new ArrayList<String>();
    for(String sql:List.of(
        "select json_build_array(n.nspname,c.relname,c.relkind,c.relowner,c.relacl,c.reloptions)::text from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('schubert','schubert_web_session','schubert_meta') order by n.nspname,c.relname",
        "select json_build_array(n.nspname,c.relname,a.attnum,a.attname,a.atttypid,a.atttypmod,a.attnotnull,a.attidentity,a.attgenerated,a.attacl,a.attcollation)::text from pg_attribute a join pg_class c on c.oid=a.attrelid join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('schubert','schubert_web_session','schubert_meta') and a.attnum>0 and not a.attisdropped order by n.nspname,c.relname,a.attnum",
        "select to_jsonb(p)::text from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname in ('schubert','schubert_web_session','schubert_meta') and p.oid is distinct from to_regprocedure('schubert.maintenance_read_success_progress(uuid,timestamptz,text,timestamptz)') order by p.oid")){
      try(var q=schema.createStatement()){q.setQueryTimeout(5);try(var r=q.executeQuery(sql)){while(r.next())values.add(Objects.requireNonNull(r.getString(1)));}}
    }return List.copyOf(values);
  }
  public static void main(String[] args)throws Exception{
    require(arguments(args) && Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01") && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));
    require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
        try{
          phase="SIGNED_ORIGINAL";original();
          var old=ReleaseApproval.parse(Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")));
          require(old.version().equals("0.1.0-PG486") && old.manifestSha256().equals("230c6174931a8d98a34e4369086619c54cb0668e0793baf2f1efce3e0993bd1d"));StartupReleaseManifest.createHost(new FixedServiceIdentity().configurationGroup()).verify(old);
          Pg387TrustedDeployment.LABEL="PG489";Pg387TrustedDeployment.STEM="pg489";Pg387TrustedDeployment.SOURCE=args[0];Pg387TrustedDeployment.RELEASE=NEXT;Pg387TrustedDeployment.expectedSqlCount=28;
          Files.createDirectory(SAVE,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
          var database=Pg407FailedRootRecovery.openDatabase();database.setReadOnly(true);database.setAutoCommit(false);int pid;
          try(var q=database.createStatement();var r=q.executeQuery("select pg_backend_pid(),set_config('application_name','PG490-fixed-migration',false),pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(3));pid=r.getInt(1);require(!r.next());}
          phase="REFERENCES";var refs=new References(pid,args[0],args[1]);refs.check("before");
          Pg387TrustedDeployment.freezeCandidate();var next=Pg387TrustedDeployment.verify();require(next.manifestSha256().equals(args[1]));
          try(var schema=Pg422SignedMigration.openSchema()){
            require(Pg422SignedMigration.history(schema).equals(expected(27)));var business=Pg456SignedMigration.business(schema);var oldCatalog=catalog(schema);
            byte[] before=Pg410KnownAuthRecovery.material(PROFILE,4096),after=Files.readAllBytes(NEXT.resolve("config/effective/backup-profile.json"));require(schemaOnly(before,after));
            Pg481PendingDeployment.privateWrite(SAVE.resolve("backup-profile-before.private.json"),before);
            refs.check("before");phase="RESTORE_POINT";restorePoint();refs.check("before");phase="MIGRATE";migrate();postconditions(schema);
            require(Pg422SignedMigration.history(schema).equals(expected(28)) && business.equals(Pg456SignedMigration.business(schema)) && oldCatalog.equals(catalog(schema)));refs.check("before");
            phase="PROFILE";Pg456SignedMigration.replace(PROFILE,after,Math.toIntExact(new FixedServiceIdentity().configurationGroup()),"rw-r-----");refs.check("after");
            require(Pg422SignedMigration.history(schema).equals(expected(28)) && business.equals(Pg456SignedMigration.business(schema)) && oldCatalog.equals(catalog(schema)));postconditions(schema);
          }
          phase="DATABASE_CLOSE";database.rollback();database.close();phase="REFERENCE_CLOSE";refs.release();phase="A_CLOSE";return Boolean.TRUE;
        }catch(Exception|Error failure){retain(failure);throw failure;}
      })).orElseThrow();}catch(Exception|Error failure){retain(failure);throw failure;}
    })).orElseThrow());
    phase="M_CLOSE";Pg481PendingDeployment.privateWrite(SAVE.resolve("complete.private"),("PG490_SCHEMA028_NORMAL\nsource="+args[0]+"\nmanifest="+args[1]+"\ncurrentUnchanged=true\noriginalUnchanged=true\n").getBytes(StandardCharsets.US_ASCII));
    System.out.println("PG490_SCHEMA028_NORMAL privateRestorePointVerified=true migration1=true businessUnchanged=true pendingOriginalBackupUnchanged=true currentUnitEpochUnchanged=true starts0=true oldCloseNotInferred=true");
  }
}
