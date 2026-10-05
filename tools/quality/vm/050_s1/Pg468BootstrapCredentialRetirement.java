import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.bootstrap.*;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.sql.Connection;

/** BOOT008/SS3438.2: retire only two unused bootstrap sources after real reset/login.
 * Keep active service credentials, original DONE, complete DB, Backup and current intact.
 * Rename is recoverable; never starts a Unit, writes DB, issues a permit or deletes data.
 */
public final class Pg468BootstrapCredentialRetirement {
  static final Path CREDS=Path.of("/etc/schubert-nk/credentials");
  static final Path SAVE=Path.of("/var/lib/pgpt-s1-preservation/pg468-bootstrap-retired-v1");
  static final String UNIT="schubert-nk-bootstrap-admin.service";
  static final Set<String> SOURCES=Set.of("bootstrap-admin-username","bootstrap-admin-password");
  static void require(boolean value){if(!value)throw new IllegalStateException("fixed bootstrap retirement refused");}
  static boolean metadata(Map<String,Object> v){return v!=null && Integer.valueOf(0).equals(v.get("uid")) && Integer.valueOf(0).equals(v.get("gid")) && Integer.valueOf(0100400).equals(v.get("mode")) && Integer.valueOf(1).equals(v.get("nlink")) && v.get("size") instanceof Long n && n>0 && n<=128;}
  static void terminal()throws Exception{
    byte[] raw=Pg425KnownApiRecovery.command(new byte[0],"/usr/bin/systemctl","show",UNIT,"--property=LoadState,ActiveState,SubState,MainPID,ControlPID,Job,Restart,UnitFileState");
    var values=new HashMap<String,String>();
    for(String line:new String(raw,StandardCharsets.US_ASCII).split("\n")){int at=line.indexOf('=');require(at>0 && values.putIfAbsent(line.substring(0,at),line.substring(at+1))==null);}
    require(values.equals(Map.of("LoadState","loaded","ActiveState","inactive","SubState","dead","MainPID","0","ControlPID","0","Job","","Restart","no","UnitFileState","static")));
    Pg407FailedRootRecovery.checkTree(Path.of("/sys/fs/cgroup/system.slice",UNIT));
    require(!Files.exists(Path.of("/run/credentials",UNIT),LinkOption.NOFOLLOW_LINKS));
  }
  static String digest(Connection c)throws Exception{
    try(var q=c.createStatement()){q.setQueryTimeout(5);try(var r=q.executeQuery("select md5(coalesce(string_agg(row_to_json(t)::text,E'\\n' order by id),'')) from schubert.app_users t")){require(r.next());String value=r.getString(1);require(value!=null && value.matches("[0-9a-f]{32}") && !r.next());return value;}}
  }
  static String hash(Path p)throws Exception{byte[] b=Pg410KnownAuthRecovery.material(p,1048576);try{return Pg410KnownAuthRecovery.hash(b);}finally{Arrays.fill(b,(byte)0);}}
  static void retain(){System.err.println("PG468_BOOTSTRAP_RETIREMENT_UNKNOWN ownershipUnknown=true nextBootstrapIsolated=true automaticResume=false secretsPrinted=false");for(;;){try{Thread.sleep(1000);}catch(InterruptedException signal){Thread.interrupted();}}}
  public static void main(String[] args)throws Exception{
    Thread.currentThread().setUncaughtExceptionHandler((t,e)->System.err.println("PG468_BOOTSTRAP_RETIREMENT_REFUSED type="+e.getClass().getName()+" secretsPrinted=false"));
    require(args!=null && args.length==1 && args[0]!=null && Set.of("verify","retire").contains(args[0]));boolean verify=args[0].equals("verify");boolean[] mutated={false};
    require(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim().equals("e07aa706-1acd-4e65-b309-d7f330f79d54"));
    try{require(MaintenanceFileLock.create().tryExclusive(()->Pg387TrustedDeployment.checked(()->{
      try{return StartupAdmissionFile.create().tryExclusive(a->Pg387TrustedDeployment.checked(()->{
      Pg468CodeOnlyDeployment.configure("PG468",Pg468CompletedReadback.SOURCE,Path.of("/opt/schubert-nk/releases/0.1.0-PG468"));var approval=Pg387TrustedDeployment.verify();
      require(approval.manifestSha256().equals(Pg468CompletedReadback.DIGEST) && Arrays.equals(approval.encode(),Files.readAllBytes(Path.of("/etc/schubert-nk/release-approval/current"))) && Files.readSymbolicLink(Path.of("/opt/schubert-nk/current")).equals(Pg387TrustedDeployment.RELEASE));
      terminal();require(Arrays.equals(Files.readAllBytes(Pg387TrustedDeployment.RELEASE.resolve("systemd").resolve(UNIT)),Files.readAllBytes(Path.of("/etc/systemd/system",UNIT))));
      require(Files.readString(Path.of("/var/lib/pgpt-s1-preservation/pg468-bootstrap-existing-ref/complete.private")).contains("normalOwnedReturnAndExit20=true\n"));
      try(var db=Pg407FailedRootRecovery.openDatabase();var schema=Pg422SignedMigration.openSchema()){
        db.setReadOnly(true);db.setAutoCommit(false);schema.setReadOnly(true);schema.setAutoCommit(false);
        try(var q=db.createStatement();var r=q.executeQuery("select pg_catalog.pg_try_advisory_lock(71419602)")){require(r.next() && r.getBoolean(1) && !r.next());}
        try(var q=schema.createStatement();var r=q.executeQuery("select count(*) from schubert.app_users where username='pgpt_admin_467' and role='ADMIN' and status='ACTIVE' and version=1 and updated_by=id and password_changed_at>created_at")){require(r.next() && r.getLong(1)==1 && !r.next());}
        var original=Pg428ColdBootPreparation.original();var backup=Pg428ColdBootPreparation.backupSnapshot();var fixture=Pg428ColdBootPreparation.fixtureSnapshot();var rows=Pg407FailedRootRecovery.databaseRows(db);String user=digest(schema);require(rows.size()==351);
        var directory=Pg410KnownAuthRecovery.metadata(CREDS);require(Integer.valueOf(0).equals(directory.get("uid")) && (((Integer)directory.get("mode"))&0170000)==0040000 && (((Integer)directory.get("mode"))&0022)==0);
        var hashes=new TreeMap<String,String>();var metas=new TreeMap<String,Map<String,Object>>();try(var paths=Files.list(CREDS)){for(var p:paths.toList()){String name=p.getFileName().toString();hashes.put(name,hash(p));metas.put(name,Pg410KnownAuthRecovery.metadata(p));}}
        require(hashes.keySet().containsAll(SOURCES) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));for(String name:SOURCES)require(metadata(metas.get(name)));
        terminal();require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && user.equals(digest(schema)));
        if(!verify){
          Files.createDirectory(SAVE,java.nio.file.attribute.PosixFilePermissions.asFileAttribute(java.nio.file.attribute.PosixFilePermissions.fromString("rwx------")));Pg387TrustedDeployment.sync(SAVE.getParent());
          mutated[0]=true;
          for(String name:new String[]{"bootstrap-admin-password","bootstrap-admin-username"}){terminal();require(metadata(Pg410KnownAuthRecovery.metadata(CREDS.resolve(name))) && hashes.get(name).equals(hash(CREDS.resolve(name))));Files.move(CREDS.resolve(name),SAVE.resolve(name),StandardCopyOption.ATOMIC_MOVE);Pg387TrustedDeployment.sync(CREDS);Pg387TrustedDeployment.sync(SAVE);require(hashes.get(name).equals(hash(SAVE.resolve(name))) && metadata(Pg410KnownAuthRecovery.metadata(SAVE.resolve(name))) && !Files.exists(CREDS.resolve(name),LinkOption.NOFOLLOW_LINKS));}
        }
        for(var e:hashes.entrySet()){Path p=(!verify && SOURCES.contains(e.getKey())?SAVE:CREDS).resolve(e.getKey());require(e.getValue().equals(hash(p)));if(!SOURCES.contains(e.getKey()))require(metas.get(e.getKey()).equals(Pg410KnownAuthRecovery.metadata(p)));}
        terminal();require(original.equals(Pg428ColdBootPreparation.original()) && backup.equals(Pg428ColdBootPreparation.backupSnapshot()) && fixture.equals(Pg428ColdBootPreparation.fixtureSnapshot()) && rows.equals(Pg407FailedRootRecovery.databaseRows(db)) && user.equals(digest(schema)));db.rollback();schema.rollback();
      }catch(Exception|Error failure){if(mutated[0])retain();throw failure;}
      return Boolean.TRUE;
      })).orElseThrow();}catch(Exception|Error admissionUnknown){if(mutated[0]){System.err.println("PG468_BOOTSTRAP_RETIREMENT_POST_A_UNKNOWN M_RETAINED=true A_OWNERSHIP_NOT_INFERRED=true");retain();}throw admissionUnknown;}
    })).orElseThrow());}catch(Exception|Error maintenanceUnknown){if(mutated[0])retain();throw maintenanceUnknown;}
    if(!verify){Files.writeString(SAVE.resolve("complete.private"),"bootstrapSourcesRetiredRecoverably=true\nactiveServiceCredentialsPreserved=true\nall351OriginalBackupCurrentPreserved=true\nallNewOwnedScopesReturnedNormally=true\n",StandardOpenOption.CREATE_NEW);Files.setPosixFilePermissions(SAVE.resolve("complete.private"),java.nio.file.attribute.PosixFilePermissions.fromString("r--------"));try(var c=java.nio.channels.FileChannel.open(SAVE.resolve("complete.private"),StandardOpenOption.READ)){c.force(true);}Pg387TrustedDeployment.sync(SAVE);}
    System.out.println("PG468_BOOTSTRAP_RETIREMENT_"+(verify?"VERIFIED":"COMPLETED")+" sourceCount2=true activeCredentialsPreserved=true originalBackupDbCurrentPreserved=true recoverable=true newOwnedClosed=true starts0=true ddl0=true secretsPrinted=false");
  }
}
