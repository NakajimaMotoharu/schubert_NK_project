import com.zaxxer.hikari.HikariDataSource;
import dev.codex.schubert.nk.api.bootstrap.ApiJdbcPool;
import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import dev.codex.schubert.nk.web.bootstrap.WebJdbcPool;
import java.io.IOException;
import java.sql.SQLException;
import java.util.concurrent.atomic.AtomicReference;

/**
 * PT-OPS-NATIVE-001/002. External test-only systemd/LoadCredential/SCRAM probe.
 * Calls actual Production scope and actual API/Web pool factories; NOT a Production service,
 * readiness bypass, fixture NK capture or CHR acceptance. Independent SS331 role/SS342 pool oracle.
 * SYS-002/004,DAT-001; UI212/243/253; SS331/342/343; SSC084; PG290; 471 D01/02.
 */
public final class NativeResourceProbe {
  public static void main(String[] args) throws IOException {
    if (args.length != 1) throw new IllegalArgumentException("probe service required");
    var service = switch (args[0]) {
      case "api" -> ServiceConfigFiles.Service.API;
      case "web" -> ServiceConfigFiles.Service.WEB;
      default -> throw new IllegalArgumentException("probe service invalid");
    };
    String expectedRole = service == ServiceConfigFiles.Service.API
        ? "schubert_app" : "schubert_web_session";
    int max = service == ServiceConfigFiles.Service.API ? 8 : 2;
    int min = service == ServiceConfigFiles.Service.API ? 2 : 1;
    var poolRef = new AtomicReference<HikariDataSource>();
    var credentialsRef = new AtomicReference<ServiceCredentialSet>();
    var inputs = new ServiceProcessResources.Inputs(service,
        ServiceCredentialLocation.read(System.getenv()), "jdbc:postgresql://127.0.0.1:5432/schubert_nk");
    new ServiceProcessResources(inputs, source -> {
      HikariDataSource pool = service == ServiceConfigFiles.Service.API
          ? new ApiJdbcPool().open(source) : new WebJdbcPool().open(source);
      poolRef.set(pool);
      return pool;
    }).execute((pool, credentials) -> {
      credentialsRef.set(credentials);
      if (poolRef.get().getMaximumPoolSize() != max || poolRef.get().getMinimumIdle() != min)
        throw new AssertionError("pool ceiling mismatch");
      try (var connection = pool.getConnection(); var statement = connection.createStatement();
          var rows = statement.executeQuery("select current_user::text, current_database()::text, pg_is_in_recovery()")) {
        if (!rows.next() || !expectedRole.equals(rows.getString(1))
            || !"schubert_nk".equals(rows.getString(2)) || rows.getBoolean(3) || rows.next())
          throw new AssertionError("database identity mismatch");
      } catch (SQLException failure) { throw new IOException("probe DB query unavailable"); }
      for (var id : ServiceCredentialId.forService(service)) {
        if (id.kind() == ServiceCredentialId.Kind.KEY && !"v1".equals(credentials.version(id)))
          throw new AssertionError("key version mismatch");
      }
    });
    if (!poolRef.get().isClosed()) throw new AssertionError("pool not closed");
    boolean cleared = false;
    try { credentialsRef.get().copyPassword(ServiceCredentialId.forService(service).getFirst()); }
    catch (IllegalStateException expected) { cleared = true; }
    if (!cleared) throw new AssertionError("credential handle still available");
    System.out.println("PT-OPS-NATIVE-" + (service == ServiceConfigFiles.Service.API ? "001" : "002")
        + " PASS role=" + expectedRole + " pool.max=" + max + " pool.min=" + min
        + " materials=5 pool.closed=true credential.closed=true productionService=false");
  }
}
