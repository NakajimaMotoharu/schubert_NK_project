import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.SecureRandom;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** Isolated PGPT VM initial backup password only; never overwrite an existing credential/role. */
public final class ProvisionBackupDatabase {
  public static void main(String[] args) throws Exception {
    if(args.length!=0||!System.getProperty("user.name").equals("root")||
        !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new IllegalStateException("isolated root fixture required");
    Path target=Path.of("/etc/schubert-nk/credentials/backup-pgpass");
    if(Files.exists(target,LinkOption.NOFOLLOW_LINKS))throw new IllegalStateException("existing credential preserved");
    String query="SELECT rolpassword IS NULL AND rolcanlogin AND NOT rolsuper AND NOT rolcreaterole FROM pg_authid WHERE rolname='schubert_backup'";
    var check=new ProcessBuilder("/usr/bin/sudo","-u","postgres","/usr/bin/psql","-X","-A","-t","-c",query).redirectError(ProcessBuilder.Redirect.DISCARD).start();
    String result=new String(check.getInputStream().readAllBytes(),StandardCharsets.US_ASCII).trim();
    if(!check.waitFor(10,TimeUnit.SECONDS)||check.exitValue()!=0||!result.equals("t"))throw new IllegalStateException("initial role required");
    byte[] entropy=new byte[32];new SecureRandom().nextBytes(entropy);
    byte[] pgpass;
    String password;
    try {password=HexFormat.of().formatHex(entropy);pgpass=("127.0.0.1:5432:schubert_nk:schubert_backup:"+password+"\n").getBytes(StandardCharsets.US_ASCII);}
    finally {Arrays.fill(entropy,(byte)0);}
    try {
      Files.createFile(target,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
      Files.write(target,pgpass,StandardOpenOption.WRITE);
      String sql="SET log_statement='none';SET log_min_error_statement='panic';DO $$BEGIN IF EXISTS (SELECT 1 FROM pg_authid WHERE rolname='schubert_backup' AND rolpassword IS NULL) THEN ALTER ROLE schubert_backup PASSWORD '"+password+"';ELSE RAISE EXCEPTION 'initial role required';END IF;END$$;";
      var process=new ProcessBuilder("/usr/bin/sudo","-u","postgres","/usr/bin/psql","-X","-v","ON_ERROR_STOP=1")
          .redirectOutput(ProcessBuilder.Redirect.DISCARD).redirectError(ProcessBuilder.Redirect.DISCARD).start();
      byte[] command=sql.getBytes(StandardCharsets.US_ASCII);
      try(var stdin=process.getOutputStream()){stdin.write(command);}finally{Arrays.fill(command,(byte)0);}
      if(!process.waitFor(10,TimeUnit.SECONDS)||process.exitValue()!=0)throw new IllegalStateException("initial role update failed; preserved for inspection");
    } finally {Arrays.fill(pgpass,(byte)0);}
    System.out.println("PGPT_BACKUP_CREDENTIAL_PREPARED initialOnly=true valuesPrinted=false");
  }
}
