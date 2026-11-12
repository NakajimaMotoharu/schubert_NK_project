package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.api.application.admin.BootstrapAdminService;
import dev.codex.schubert.nk.api.application.admin.UserCommandMetadata;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.InspectorCredentialException;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoader;
import dev.codex.schubert.nk.api.file.ServiceCredentialException;
import dev.codex.schubert.nk.api.file.ServiceCredentialReader;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageProfile;
import dev.codex.schubert.nk.bootstrap.FixedNativeCoverageTerminal;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.IntConsumer;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Dedicated initial ADMIN oneshot, never an ordinary API startup/permit bypass. All IO stays within
 * fixed configuration, same held credential inode and admitted DB role. NK-ADM-001/NK-OPS-001;
 * AUT001002/DAT009/MON004/OPS009/UI225226242; SS343§8.2/SSC188; PT-ADM-BOOT007..008.
 */
@NullMarked
public final class BootstrapAdminMain {
  static final String UNIT = "schubert-nk-bootstrap-admin.service";
  private static final String CREDENTIAL_DIRECTORY = "/run/credentials/" + UNIT;

  private final Map<String, String> environment;
  private final Operation operation;
  private final Capture capture;
  private final Capture closing;
  private final PrintStream diagnostics;
  private final IntConsumer termination;

  /** Java25 instance-main native binding; no configurable startup authority. SSC234. */
  public BootstrapAdminMain() {
    environment = System.getenv();
    operation = this::run;
    var measurement =
        new FixedNativeCoverageTerminal(
            FixedNativeCoverageProfile.TerminalRole.BOOTSTRAP, environment.get("INVOCATION_ID"));
    capture = measurement::terminal;
    closing = measurement::closing;
    diagnostics = System.err;
    termination = System::exit;
  }

  BootstrapAdminMain(
      @Nullable Map<String, String> environment,
      @Nullable Operation operation,
      @Nullable Capture capture,
      @Nullable Capture closing,
      @Nullable PrintStream diagnostics,
      @Nullable IntConsumer termination) {
    if (environment == null
        || operation == null
        || capture == null
        || closing == null
        || diagnostics == null
        || termination == null)
      throw new IllegalArgumentException("bootstrap main dependencies required");
    this.environment = Map.copyOf(environment);
    this.operation = operation;
    this.capture = capture;
    this.closing = closing;
    this.diagnostics = diagnostics;
    this.termination = termination;
  }

  public void main(String[] arguments) {
    int status = launch(arguments, environment, operation, capture, diagnostics);
    try {
      if (closing.run()) diagnostics.println("Bootstrap fixed PT native closing complete");
    } catch (Throwable failure) {
      diagnostics.println("Initial ADMIN bootstrap failed");
      status = 50;
    }
    termination.accept(status);
  }

  /** PG-D401: internal data/control-flow ports, never an OS admission or startup capability. */
  @FunctionalInterface
  interface Operation {
    int run(String[] arguments, Map<String, String> environment)
        throws IOException, SQLException, java.security.NoSuchAlgorithmException;
  }

  @FunctionalInterface
  interface Capture {
    boolean run() throws IOException;
  }

  /** PT-ADM-BOOT669001..005: fixed exit/diagnostic order with independent failure vectors. */
  static int launch(
      String @Nullable [] arguments,
      @Nullable Map<String, String> environment,
      @Nullable Operation operation,
      @Nullable Capture capture,
      @Nullable PrintStream diagnostics) {
    if (arguments == null
        || environment == null
        || operation == null
        || capture == null
        || diagnostics == null) throw new IllegalArgumentException("bootstrap entry required");
    int status = 50;
    try {
      status = operation.run(arguments, environment);
    } catch (Throwable failure) {
      // Only a fixed diagnostic escapes, never JDBC/file/provider details or credentials.
      diagnostics.println("Initial ADMIN bootstrap failed");
    }
    diagnostics.println("Initial ADMIN bootstrap finished");
    try {
      if (capture.run()) diagnostics.println("Bootstrap fixed PT native capture complete");
    } catch (Throwable failure) {
      diagnostics.println("Initial ADMIN bootstrap failed");
      status = 50;
    }
    return status;
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
      try {
        connection.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
        var metadata = new UserCommandMetadata(UUID.randomUUID(), UUID.randomUUID(), Instant.now());
        var outcome = new BootstrapAdminService().create(connection, username, password, metadata);
        connection.commit();
        return outcome == BootstrapAdminService.Outcome.CREATED ? 0 : 20;
      } catch (SQLException | RuntimeException | Error failure) {
        // BUG2697/YKT2371; SS343 SSC188/SS312: caller owns TX, outer TWR owns physical close.
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException | Error rollbackFailure) {
          TemporaryInfrastructureException.attachSecondary(failure, rollbackFailure);
        }
        throw failure;
      }
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
