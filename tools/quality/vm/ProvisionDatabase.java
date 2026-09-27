import java.nio.file.*;
import java.nio.file.attribute.*;
import java.security.*;
import java.util.*;
import org.flywaydb.core.Flyway;

/** Private PGPT VM only; executes committed SQL through dedicated migration identity. */
public final class ProvisionDatabase {
  static final Path PASSWORD = Path.of("/etc/schubert-nk/credentials/db-migration");
  public static void main(String[] args) throws Exception {
    if (args.length != 1 || !Set.of("prepare", "migrate").contains(args[0])
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
            .equals("pgpt-r2-20260927-01") || !System.getProperty("user.name").equals("root"))
      throw new IllegalStateException("isolated root fixture required");
    if (args[0].equals("prepare")) {
      if (Files.exists(PASSWORD)) throw new IllegalStateException("credential already exists");
      byte[] bytes = new byte[32]; new SecureRandom().nextBytes(bytes);
      String password;
      try { password = HexFormat.of().formatHex(bytes) + "\n"; }
      finally { Arrays.fill(bytes, (byte)0); }
      var permissions = PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------"));
      Files.createFile(PASSWORD, permissions); Files.writeString(PASSWORD, password);
      var server = Path.of("/var/lib/postgresql/pgpt-passwords/db-migration");
      Files.createFile(server, permissions); Files.writeString(server, password);
      Files.setOwner(server, server.getFileSystem().getUserPrincipalLookupService().lookupPrincipalByName("postgres"));
      System.out.println("PGPT_VM_MIGRATION_CREDENTIAL_PREPARED valuesPrinted=false");
      return;
    }
    var flyway = Flyway.configure()
        .dataSource("jdbc:postgresql://127.0.0.1:5432/schubert_nk", "schubert_migration",
            Files.readString(PASSWORD).trim())
        .defaultSchema("schubert_meta").schemas("schubert_meta").initSql("SET ROLE nk_owner")
        .locations("filesystem:/opt/pgpt-migrations")
        .validateOnMigrate(true).outOfOrder(false).baselineOnMigrate(false).cleanDisabled(true).load();
    int applied = flyway.migrate().migrationsExecuted;
    flyway.validate();
    var appliedVersions = Arrays.stream(flyway.info().applied())
        .filter(m -> m.getVersion() != null).map(m -> m.getVersion().toString()).toList();
    if (flyway.info().pending().length != 0 || !appliedVersions.equals(List.of(
        "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011",
        "012", "013", "014", "015", "016", "017", "018", "019", "020", "021", "022")))
      throw new AssertionError("22 committed migrations expected");
    System.out.println("PT-OPS-NATIVE-012 PASS dedicatedMigrationRole=true migrationsApplied=" + applied
        + " expectedVersions=22 validate=true pending=0 fullStartupGate=false");
  }
}
