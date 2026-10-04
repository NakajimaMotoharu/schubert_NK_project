import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot;
import dev.codex.schubert.nk.bootstrap.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.sql.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** BUG666/667: finish this exact already-applied migration, never repeat DDL or restore /run.
 * The old dump is restored ONLY to a new inaccessible scratch DB. No production row is written.
 * Two entry modes: verify preserves isolation; complete requires the same independently verified
 * old25 snapshot and old current before applying the remaining signed placement/activation.
 */
public final class Pg456AppliedCompletion {
  static final String SCRATCH="pgpt_pg456_before_20261004";
  static final String DUMP_SHA="d77412eeeb88159bd56b2d2f099195480cc99baebf4843b2e4d069c790bd271e";
  static final Path COLD=Path.of("/var/lib/pgpt-s1-preservation/pg444-cold-e07-v2");
  static final Path SAVE=Pg456SignedMigration.SAVE;
  static final String ORIGINAL_SHA="bb62fe9b0d77202720eebb55aa00675a4d91a02beaaba5529ac8558fd08723b3";
  static final String BACKUP_SHA="c7f43d4df2801bf3aadca47ca154cfa8e08903ccc3b12e3c8fbea8335fed1b0f";
  static String stage="ARGUMENTS";

  // Legacy snapshots use Map.toString, whose Map.copyOf order differs between JVMs.
  // Parse balanced maps, reject duplicate/malformed keys and compare all fields; drop none.
  static String canonical(String value) {
    if(value==null || value.length()==0 || value.length()>1048576)throw new IllegalArgumentException("snapshot bounds");
    if(value.charAt(0)!='{')return value;
    int depth=0,end=-1,start=1;var entries=new TreeMap<String,String>();
    for(int i=0;i<value.length();i++) {
      char c=value.charAt(i);
      if(c=='{')depth++;
      if(c=='}') {
        if(--depth<0)throw new IllegalArgumentException("snapshot braces");
        if(depth==0) { add(entries,value.substring(start,i));end=i;break; }
      }
      if(c==',' && depth==1) { add(entries,value.substring(start,i));start=i+1; }
    }
    if(end<0 || depth!=0)throw new IllegalArgumentException("snapshot braces");
    String tail=value.substring(end+1);
    if(!tail.isEmpty() && !tail.matches("/[0-9a-f]{64}"))throw new IllegalArgumentException("snapshot suffix");
    return entries.toString()+tail;
  }
  static void add(Map<String,String> entries,String item) {
    item=item.trim();if(item.isEmpty())return;
    int split=item.indexOf('=');
    // Backup root is the empty relative path, not an absent entry. Preserve its inode fields.
    if(split<0 || split==item.length()-1)throw new IllegalArgumentException("snapshot pair");
    if(entries.putIfAbsent(item.substring(0,split),canonical(item.substring(split+1)))!=null)
      throw new IllegalArgumentException("snapshot duplicate");
  }
  static boolean privateMetadata(Map<String,Object> before,int mode) {
    return before!=null && (mode==0100400 || mode==0100600)
        && Integer.valueOf(0).equals(before.get("uid")) && Integer.valueOf(0).equals(before.get("gid"))
        && Integer.valueOf(mode).equals(before.get("mode")) && Integer.valueOf(1).equals(before.get("nlink"));
  }
  static byte[] privateBytes(Path file,String expected,int mode) throws Exception {
    var before=Pg410KnownAuthRecovery.metadata(file);
    if(!privateMetadata(before,mode))
      throw new IllegalStateException("private fixed evidence metadata");
    byte[] bytes=Pg410KnownAuthRecovery.material(file,1048576);
    if(!Pg422SignedMigration.hash(bytes).equals(expected) || !before.equals(Pg410KnownAuthRecovery.metadata(file)))
      throw new IllegalStateException("private fixed evidence changed");
    return bytes;
  }
  static void filesPreserved() throws Exception {
    String original=new String(privateBytes(COLD.resolve("original-before.properties"),ORIGINAL_SHA,0100400),StandardCharsets.UTF_8).trim();
    String backup=new String(privateBytes(COLD.resolve("backup-before.properties"),BACKUP_SHA,0100400),StandardCharsets.UTF_8).trim();
    if(!canonical(original).equals(canonical(Pg428ColdBootPreparation.original().toString()))
        || !canonical(backup).equals(canonical(Pg428ColdBootPreparation.backupSnapshot().toString())))
      throw new IllegalStateException("complete original or Backup before-image differs");
  }
  static void child(List<String> command,String logName) throws Exception {
    Path log=SAVE.resolve(logName);Files.createFile(log,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    Process child=new ProcessBuilder(command).redirectOutput(log.toFile()).redirectErrorStream(true).start();
    if(!child.waitFor(60,TimeUnit.SECONDS)) {
      child.destroy();if(!child.waitFor(5,TimeUnit.SECONDS))throw new IllegalStateException("owned private child UNKNOWN");
      throw new IllegalStateException("owned private child deadline");
    }
    if(child.exitValue()!=0)throw new IllegalStateException("owned private child failed; private diagnostics retained");
    try(var channel=java.nio.channels.FileChannel.open(log,StandardOpenOption.READ)){channel.force(true);}
  }
  static void scratch(Connection schema) throws Exception {
    privateBytes(SAVE.resolve("before-v026027.dump"),DUMP_SHA,0100600);
    int exists;
    try(var q=schema.createStatement();var r=q.executeQuery("select count(*) from pg_catalog.pg_database where datname='"+SCRATCH+"'")) {
      if(!r.next())throw new IllegalStateException("scratch presence absent");exists=r.getInt(1);
      if(r.next() || exists<0 || exists>1)throw new IllegalStateException("scratch presence ambiguous");
    }
    Path marker=SAVE.resolve("scratch-restored.sha256");
    if(exists==1) {
      byte[] expected=(DUMP_SHA+"\n").getBytes(StandardCharsets.US_ASCII);
      if(!Arrays.equals(Pg410KnownAuthRecovery.material(marker,128),expected)
          || !Integer.valueOf(0100600).equals(Pg410KnownAuthRecovery.metadata(marker).get("mode")))
        throw new IllegalStateException("existing unproven scratch isolated; no overwrite");
      return;
    }
    if(Files.exists(marker,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("scratch marker without database");
    child(List.of("/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","postgres","-c",
        "CREATE DATABASE "+SCRATCH+" OWNER nk_owner TEMPLATE template0"),"scratch-create.log");
    child(List.of("/usr/bin/sudo","-n","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1","-d","postgres","-c",
        "REVOKE ALL ON DATABASE "+SCRATCH+" FROM PUBLIC; GRANT CONNECT ON DATABASE "+SCRATCH+" TO schubert_migration"),"scratch-restrict.log");
    // postgres cannot traverse the root0700 SAVE. Root opens dump on stdin; child reads stdin.
    Path log=SAVE.resolve("scratch-restore.log");Files.createFile(log,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    Process restore=new ProcessBuilder("/usr/bin/sudo","-n","-u","postgres","/usr/bin/pg_restore","--exit-on-error","--no-owner","--no-privileges","--role=nk_owner","--dbname="+SCRATCH)
        .redirectInput(SAVE.resolve("before-v026027.dump").toFile()).redirectOutput(log.toFile()).redirectErrorStream(true).start();
    if(!restore.waitFor(60,TimeUnit.SECONDS)) {
      restore.destroy();if(!restore.waitFor(5,TimeUnit.SECONDS))throw new IllegalStateException("scratch restore child UNKNOWN");
      throw new IllegalStateException("scratch restore deadline");
    }
    if(restore.exitValue()!=0)throw new IllegalStateException("scratch restore refused; isolated clone retained");
    try(var old=openScratch()) {
      if(!Pg422SignedMigration.history(old).equals(Pg456SignedMigration.expected(Pg456SignedMigration.CANDIDATE,Pg456SignedMigration.OLD,25)))
        throw new IllegalStateException("scratch independent old25 history differs");
    }
    Pg456SignedMigration.save("scratch-restored.sha256",(DUMP_SHA+"\n").getBytes(StandardCharsets.US_ASCII));
  }
  static Connection openScratch() throws Exception {
    try(var credential=InspectorDbCredential.consume(Pg410KnownAuthRecovery.material(Path.of("/etc/schubert-nk/credentials/db-migration"),65536))) {
      char[] password=credential.copyPassword();var properties=new Properties();
      properties.setProperty("user","schubert_migration");properties.setProperty("connectTimeout","3");properties.setProperty("socketTimeout","5");
      try {
        properties.setProperty("password",new String(password));
        Connection db=DriverManager.getConnection("jdbc:postgresql://127.0.0.1:5432/"+SCRATCH,properties);
        try {
          try(var q=db.createStatement()) {
            q.setQueryTimeout(5);q.execute("SET ROLE nk_owner");
            try(var r=q.executeQuery("select current_user,session_user,current_database(),pg_is_in_recovery()")) {
              if(!r.next() || !"nk_owner".equals(r.getString(1)) || !"schubert_migration".equals(r.getString(2))
                  || !SCRATCH.equals(r.getString(3)) || r.getBoolean(4) || r.next())throw new IllegalStateException("fixed scratch identity");
            }
          }
          db.setReadOnly(true);return db;
        } catch(Exception failure) {db.close();throw failure;}
      } finally {Arrays.fill(password,'\0');properties.clear();}
    }
  }
  static void preservation(Connection db,Connection schema,Connection old) throws Exception {
    stage="INDEPENDENT_PRESERVATION";
    if(!Pg422SignedMigration.history(old).equals(Pg456SignedMigration.expected(Pg456SignedMigration.CANDIDATE,Pg456SignedMigration.OLD,25))
        || !Pg422SignedMigration.history(schema).equals(Pg456SignedMigration.expected(Pg456SignedMigration.CANDIDATE,Pg456SignedMigration.OLD,27)))
      throw new IllegalStateException("literal signed old25/current27 history differs");
    var rows=Pg407FailedRootRecovery.databaseRows(old);
    if(rows.size()!=251 || !rows.equals(Pg407FailedRootRecovery.databaseRows(db)))throw new IllegalStateException("all251 full14 rows differ");
    if(!Pg456SignedMigration.business(old).equals(Pg456SignedMigration.business(schema)))throw new IllegalStateException("all23 existing business row values differ");
    filesPreserved();Pg456SignedMigration.original(db);Pg456SignedMigration.postconditions(schema);
    // Independent known partially-privileged role rejects the former comma-list ANY oracle.
    try(var q=schema.createStatement();var r=q.executeQuery("select has_table_privilege('schubert_backup','schubert_web_session.web_receipt_references','SELECT,INSERT,DELETE'),has_table_privilege('schubert_backup','schubert_web_session.web_receipt_references','INSERT'),has_table_privilege('schubert_backup','schubert_web_session.web_receipt_references','DELETE')")) {
      if(!r.next() || !r.getBoolean(1) || r.getBoolean(2) || r.getBoolean(3) || r.next())throw new IllegalStateException("independent partial-role negative vector differs");
    }
    Pg387TrustedDeployment.terminalAll();
  }
  public static void main(String[] args) throws Exception {
    Thread.currentThread().setUncaughtExceptionHandler((t,e)-> {
      System.err.println("PG456_APPLIED_REFUSED stage="+stage+" type="+e.getClass().getName()+" diagnosticsRedacted=true preservationRetained=true");
      for(var frame:e.getStackTrace())if(frame.getClassName().equals("Pg456AppliedCompletion"))System.err.println("PG456_APPLIED_FRAME "+frame.getMethodName()+":"+frame.getLineNumber());
    });
    if(args.length!=3 || !args[0].equals("559bf7eacb401d6d07037dbdd295b32f174976a0")
        || !args[1].equals("21affa1850d60f3a7d54f5dbcc37e12c6460563865771fa49a52a433fe91b424")
        || !Set.of("verify","complete").contains(args[2])
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new IllegalArgumentException("one isolated applied candidate only");
    MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()-> {
      stage="M_TERMINAL";Pg387TrustedDeployment.requireNoUndeliveredWork();Pg387TrustedDeployment.terminalAll();
      if(!Pg410KnownAuthRecovery.show(InspectorUnitSnapshot.Target.MORNING).snapshot().quiescent())throw new IllegalStateException("Morning not terminal");
      Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice/schubert-nk-morning-controller.service"));
      return StartupAdmissionFile.create().tryExclusive(admission->Pg387TrustedDeployment.checked(()-> {
        stage="A_OLD_NEW_BOM";Pg387TrustedDeployment.terminalAll();
        Pg387TrustedDeployment.LABEL="PG430";Pg387TrustedDeployment.STEM="pg430";Pg387TrustedDeployment.SOURCE=Pg456SignedMigration.OLD_SOURCE;
        Pg387TrustedDeployment.RELEASE=Pg456SignedMigration.OLD;Pg387TrustedDeployment.expectedSchema("025");
        var prior=Pg387TrustedDeployment.verify();
        if(!prior.manifestSha256().equals(Pg456SignedMigration.OLD_DIGEST)
            || !Arrays.equals(prior.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current")))
            || !Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg456SignedMigration.OLD))throw new IllegalStateException("old approval/current required");
        Pg456SignedMigration.configure(args[0]);Pg387TrustedDeployment.freezeCandidate();var nextApproval=Pg387TrustedDeployment.verify();
        if(!nextApproval.manifestSha256().equals(args[1]))throw new IllegalStateException("fixed signed digest required");
        try(var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()) {
          stage="DB_OWNER";db.setAutoCommit(false);
          try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")) {
            if(!r.next() || !r.getBoolean(1) || r.next())throw new IllegalStateException("dedicated DB lock unavailable");
          }
          Pg456SignedMigration.original(db);filesPreserved();Pg456SignedMigration.postconditions(schema);
          byte[] before=privateBytes(SAVE.resolve("backup-profile-before.json"),"1de2865105e8f291fc62ca23942fd91efbd04757f8f8d8d7ddb5cae95537c053",0100600);
          byte[] profile=Files.readAllBytes(Pg456SignedMigration.CANDIDATE.resolve("config/effective/backup-profile.json"));
          if(!Arrays.equals(before,Pg410KnownAuthRecovery.material(Pg456SignedMigration.PROFILE,4096)) || !Pg456SignedMigration.schemaOnly(before,profile))throw new IllegalStateException("saved untouched profile delta differs");
          stage="SCRATCH_RESTORE";scratch(schema);
          try(var old=openScratch()) {
            preservation(db,schema,old);
            System.out.println("PG456_APPLIED_VERIFIED old25Clone=true current27=true full251Rows14Columns=true all23BusinessTables=true fullOriginalBackupMetadataBytes=true postconditions11=true partialRoleRejected=true productionDdlRepeated=0 permitsIssued=0");
            if(args[2].equals("complete")) {
              stage="CADDY_PLACEMENT";Pg456SignedMigration.caddy();
              stage="PROFILE_ACTIVATE";Pg456SignedMigration.replace(Pg456SignedMigration.PROFILE,profile,Math.toIntExact(new FixedServiceIdentity().configurationGroup()),"rw-r-----");
              Pg387TrustedDeployment.activate(nextApproval);preservation(db,schema,old);
              if(!Arrays.equals(profile,Files.readAllBytes(Pg456SignedMigration.PROFILE)))throw new IllegalStateException("profile readback");
              System.out.println("PG456_APPLIED_COMPLETED source="+args[0]+" schema027=true currentAndApproval=true CaddySignedPlacement=true originalStillPending=true allDataPreserved=true permitsIssued=0 businessReady=false");
            }
          }
          db.rollback();
        }
        return Boolean.TRUE;
      })).orElseThrow();
    })).orElseThrow();
  }
}
