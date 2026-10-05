package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.api.application.admin.BootstrapAdminService;
import dev.codex.schubert.nk.api.application.admin.UserCommandMetadata;
import dev.codex.schubert.nk.api.file.InspectorCredentialException;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoader;
import dev.codex.schubert.nk.api.file.ServiceCredentialException;
import dev.codex.schubert.nk.api.file.ServiceCredentialReader;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Dedicated initial ADMIN oneshot, never an ordinary API startup/permit bypass. All IO stays within
 * fixed configuration, same held credential inode and admitted DB role. NK-ADM-001/NK-OPS-001;
 * AUT001002/DAT009/MON004/OPS009/UI225226242; SS343§8.2/SSC188; PT-ADM-BOOT007..008.
 */
@NullMarked
public final class BootstrapAdminMain {
  static final String UNIT = "schubert-nk-bootstrap-admin.service";
  private static final String CREDENTIAL_DIRECTORY = "/run/credentials/" + UNIT;

  public static void main(String[] arguments) {
    int status = 50;
    try {
      status = new BootstrapAdminMain().run(arguments, System.getenv());
    } catch (Throwable failure) {
      // Only a fixed diagnostic escapes, never JDBC/file/provider details or credentials.
      System.err.println("Initial ADMIN bootstrap failed");
    }
    System.err.println("Initial ADMIN bootstrap finished");
    System.exit(status);
  }

  int run(String[] arguments, Map<String, String> environment)
      throws IOException,
          SQLException,
          InspectorCredentialException,
          ServiceCredentialException,
          java.security.NoSuchAlgorithmException {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(environment, "environment");
    if (arguments.length != 0) return 70;
    Path credentialRoot;
    try {
      credentialRoot = ServiceCredentialLocation.read(environment).directory();
      if (!credentialRoot.toString().equals(CREDENTIAL_DIRECTORY)) return 70;
    } catch (IllegalArgumentException invalid) {
      return 70;
    }
    var context = new ChildStartupContext();
    var identity = new FixedServiceIdentity().resolve(ServiceConfigFiles.Service.API);
    var before = context.capture();
    requireActor(before, identity);
    var config = new ApiConfigurationLoader(ServiceConfigFiles.production(), environment).load();
    var security = LinuxInodeSecurity.create();
    int status;
    try (var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), credentialRoot)) {
      var reader = new InspectorCredentialLoader(root, security);
      var database = new ServiceCredentialReader(root, security, ServiceConfigFiles.Service.API);
      try (var username = reader.readBootstrapUsername();
          var password = reader.readBootstrapPassword();
          var dbPassword = database.readPassword(ServiceCredentialId.DB_API)) {
        char[] name = username.copyPassword();
        try (var source =
                new ServiceDatabaseSource(
                    ServiceConfigFiles.Service.API,
                    config.value("nk.db.url"),
                    dbPassword.copyPassword());
            var connection = source.getConnection()) {
          requireSame(before, context.capture(), identity);
          status = createAndCommit(connection, new String(name), password.copyPassword());
          requireSame(before, context.capture(), identity);
        } finally {
          Arrays.fill(name, '\0');
        }
      }
    }
    // Do not announce normal 0/20 before every owned resource has actually returned.
    requireSame(before, context.capture(), identity);
    return status;
  }

  static int createAndCommit(Connection connection, String username, char[] password)
      throws SQLException {
    Objects.requireNonNull(password, "password");
    try {
      Objects.requireNonNull(connection, "connection");
      connection.setAutoCommit(false);
      connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      var metadata = new UserCommandMetadata(UUID.randomUUID(), UUID.randomUUID(), Instant.now());
      var outcome = new BootstrapAdminService().create(connection, username, password, metadata);
      connection.commit();
      return outcome == BootstrapAdminService.Outcome.CREATED ? 0 : 20;
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  static void requireActor(ChildStartupContext.Observed actor, FixedServiceIdentity.Value fixed)
      throws IOException {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(fixed, "fixed identity");
    if (actor.uid() != fixed.uid()
        || actor.gid() != fixed.gid()
        || !actor.groups().equals(fixed.groups())
        || !actor.zeroCapabilities()
        || !actor.noNewPrivileges()
        || !actor.cgroup().equals("0::/system.slice/" + UNIT + "\n"))
      throw new IOException("bootstrap Unit actor unavailable");
  }

  static void requireSame(
      ChildStartupContext.Observed before,
      ChildStartupContext.Observed after,
      FixedServiceIdentity.Value fixed)
      throws IOException {
    requireActor(after, fixed);
    if (!before.equals(after)) throw new IOException("bootstrap Unit generation unavailable");
  }
}
