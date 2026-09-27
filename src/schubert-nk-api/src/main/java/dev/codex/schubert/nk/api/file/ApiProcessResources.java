package dev.codex.schubert.nk.api.file;

import com.zaxxer.hikari.HikariDataSource;
import dev.codex.schubert.nk.api.bootstrap.ApiJdbcPool;
import dev.codex.schubert.nk.api.bootstrap.ApiStartupInputs;
import dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSource;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Objects;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;

/**
 * Operation-owned API credential root/material/source/pool, not full process readiness. All
 * dependencies passed to the operation are borrowed only until it returns. Startup/DB/JMS/root
 * admission must still precede receive groups; no fixture/management credential is selected here.
 * NK-OPS-001; SYS-002/004,DAT-001; UI212/243/253; SS311/342/343/SSC081/082/084;
 * PG288/PT-OPS-API-RES-001..006; 471 D01/02/05.
 */
@NullMarked
public final class ApiProcessResources {
  private final ApiStartupInputs.Values inputs;
  private final DirectoryCalls directories;
  private final InodeSecurityCalls security;
  private final InspectorCredentialLoader.Io io;
  private final SourceFactory sources;
  private final PoolFactory pools;

  @FunctionalInterface
  interface SourceFactory {
    ServiceDatabaseSource open(String url, char[] ownedPassword);
  }

  @FunctionalInterface
  interface PoolFactory {
    HikariDataSource open(DataSource source);
  }

  @FunctionalInterface
  public interface Operation {
    void run(DataSource pool, ServiceCredentialSet credentials) throws IOException;
  }

  public ApiProcessResources(ApiStartupInputs.Values inputs) {
    this(
        Objects.requireNonNull(inputs, "startup inputs"),
        LinuxDirectoryCalls.create(),
        LinuxInodeSecurity.create(),
        new InspectorCredentialLoader.NioIo());
  }

  ApiProcessResources(
      ApiStartupInputs.Values inputs,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      InspectorCredentialLoader.Io io) {
    this(
        inputs,
        directories,
        security,
        io,
        (url, password) -> new ServiceDatabaseSource(ServiceConfigFiles.Service.API, url, password),
        source -> new ApiJdbcPool().open(source));
  }

  ApiProcessResources(
      ApiStartupInputs.Values inputs,
      DirectoryCalls directories,
      InodeSecurityCalls security,
      InspectorCredentialLoader.Io io,
      SourceFactory sources,
      PoolFactory pools) {
    this.inputs = Objects.requireNonNull(inputs, "startup inputs");
    this.directories = Objects.requireNonNull(directories, "directory calls");
    this.security = Objects.requireNonNull(security, "inode security");
    this.io = Objects.requireNonNull(io, "credential IO");
    this.sources = Objects.requireNonNull(sources, "database source factory");
    this.pools = Objects.requireNonNull(pools, "database pool factory");
  }

  public void execute(Operation operation) throws StorageIoException {
    Objects.requireNonNull(operation, "startup operation");
    var root = OwnedTransferDirectory.open(directories, inputs.credentials().directory());
    ResourceScope.use(
        root::close,
        () -> {
          var reader =
              new ServiceCredentialReader(root, security, ServiceConfigFiles.Service.API, io);
          var credentials = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.API);
          return ResourceScope.use(credentials::close, () -> withDatabase(credentials, operation));
        });
  }

  private Boolean withDatabase(ServiceCredentialSet credentials, Operation operation)
      throws StorageIoException {
    char[] password = credentials.copyPassword(ServiceCredentialId.DB_API);
    ServiceDatabaseSource source;
    try {
      source =
          Objects.requireNonNull(
              sources.open(inputs.config().value("nk.db.url"), password), "database source");
    } finally {
      Arrays.fill(password, '\0');
    }
    return ResourceScope.use(
        source::close,
        () -> {
          HikariDataSource pool = Objects.requireNonNull(pools.open(source), "database pool");
          return ResourceScope.use(
              pool::close,
              () -> {
                operation.run(pool, credentials);
                return Boolean.TRUE;
              });
        });
  }
}
