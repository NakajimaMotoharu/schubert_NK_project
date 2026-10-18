package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClient;
import dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeException;
import dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessClient;
import dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessException;
import dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClient;
import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.InspectorUnitProbe;
import dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchRunRepository;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.CleanupDatabaseSession;
import dev.codex.schubert.nk.batch.repository.ExpiryAuditRepository;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Genuine fixed Expiry child, no Backup-dependent preflight or synthesized purge. SSC111/SS341§9.
 */
@NullMarked
final class CleanupExpiryExecution {
  private CleanupExpiryExecution() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SS343 fixed private Expiry Unit credential directory; EMAIN native acceptance")
  static int execute() throws IOException {
    var context = RootStartupContext.create();
    var expected = context.capture(RootStartupContext.Service.EXPIRY);
    var release = RootReleaseAdmission.create(context, expected);
    Path fixed = Path.of("/run/credentials/schubert-nk-expiry-cleanup.service");
    require(ServiceCredentialLocation.read(System.getenv()).directory().equals(fixed));
    var credentialCalls = LinuxDirectoryCalls.create();
    return ResourceScope.<OwnedTransferDirectory, Integer, IOException>acquire(
        () -> OwnedTransferDirectory.open(credentialCalls, fixed),
        OwnedTransferDirectory::close,
        credentials -> {
          var reader = new RootBatchCredentialReader(credentials, LinuxInodeSecurity.create());
          var owner = reader.readMaintenanceOwner();
          var request = reader.readExpiryRequest();
          requireOwner(owner, request);
          var parents = owner.parentsGuard();
          MaintenanceOwnerFrame.Guard guard =
              () -> {
                parents.check();
                require(reader.readMaintenanceOwner().equals(owner));
                require(reader.readExpiryRequest().equals(request));
                verify(context, expected, request);
                return parents.remainingNanos();
              };
          guard.check(); // Before database password, connection or MQ credentials.
          var database =
              CleanupDatabaseSession.forExpiry(
                  "jdbc:postgresql://127.0.0.1:5432/schubert_nk",
                  context,
                  expected,
                  release,
                  guard);
          return database.execute(
              reader.read(),
              connection ->
                  ArtemisManagementReadinessClient.withParentDeadline(
                      guard, () -> mq(connection, reader, request, guard)));
        });
  }

  private static int mq(
      Connection connection,
      RootBatchCredentialReader reader,
      CleanupWorkerRequest.Expiry request,
      MaintenanceOwnerFrame.Guard guard)
      throws IOException {
    guard.check();
    try (var maintenancePassword = reader.readMaintenanceMq();
        var opsPassword = reader.readOpsMq()) {
      long timeout = mqTimeoutMillis(guard);
      char[] maintenance = maintenancePassword.copyPassword();
      char[] ops = opsPassword.copyPassword();
      try (var locator =
          new org.apache.activemq.artemis.core.client.impl.ServerLocatorImpl(
              false,
              new org.apache.activemq.artemis.api.core.TransportConfiguration(
                  org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory.class
                      .getName(),
                  Map.of(
                      "host",
                      "127.0.0.1",
                      "port",
                      61616,
                      org.apache.activemq.artemis.core.remoting.impl.netty.TransportConstants
                          .NETTY_CONNECT_TIMEOUT,
                      Math.toIntExact(timeout))))) {
        locator
            .setCallTimeout(timeout)
            .setCallFailoverTimeout(timeout)
            .setInitialConnectAttempts(1)
            .setReconnectAttempts(0);
        // Fixed 2.56 implementation narrows createSessionFactory to ActiveMQException:
        // never catch/normalize arbitrary RuntimeException from the broad public interface.
        try (var factory =
                Objects.requireNonNull(locator.createSessionFactory(), "owned Expiry factory");
            var maintenanceSession =
                factory.createSession(
                    "schubert_maintenance", new String(maintenance), false, true, true, false, 0);
            var opsSession =
                factory.createSession(
                    "schubert_ops", new String(ops), false, true, true, false, 0)) {
          Arrays.fill(maintenance, '\0');
          Arrays.fill(ops, '\0');
          maintenanceSession.start();
          opsSession.start();
          var health = new ArtemisStartupObservation();
          var purge = new ArtemisExpiryPurgeClient();
          return executeAuthenticated(
              connection,
              request,
              guard,
              new ExpiryWork() {
                @Override
                public boolean healthy() {
                  return health.inspect(opsSession).get("nk.expiry")
                      != ArtemisQueuePressureClient.Pressure.CRITICAL;
                }

                @Override
                public ArtemisExpiryPurgeClient.Observation observe(BatchRun run) {
                  return purge.observe(maintenanceSession, run);
                }

                @Override
                public ArtemisExpiryPurgeClient.Result purge(
                    BatchRun run, ArtemisExpiryPurgeClient.Observation observed) {
                  return purge.purgeObserved(maintenanceSession, run, observed);
                }

                @Override
                public Instant now() {
                  return Instant.now().truncatedTo(ChronoUnit.MICROS);
                }
              });
        }
      } finally {
        Arrays.fill(maintenance, '\0');
        Arrays.fill(ops, '\0');
      }
    } catch (SQLException | ActiveMQException failure) {
      throw new IOException("Expiry execution unavailable");
    }
  }

  /** PG-D404: data-only result work; confers no OS, credential or parent admission. */
  interface ExpiryWork {
    boolean healthy();

    ArtemisExpiryPurgeClient.Observation observe(BatchRun run);

    ArtemisExpiryPurgeClient.Result purge(
        BatchRun run, ArtemisExpiryPurgeClient.Observation observed);

    Instant now();
  }

  /** PT-OPS-EXP711001..008: borrowed authenticated DB/MQ result transaction contract. */
  static int executeAuthenticated(
      @Nullable Connection connection,
      CleanupWorkerRequest.@Nullable Expiry request,
      MaintenanceOwnerFrame.@Nullable Guard guard,
      @Nullable ExpiryWork work)
      throws IOException, SQLException {
    if (connection == null || request == null || guard == null || work == null)
      throw new IllegalArgumentException("Expiry result contract required");
    guard.check();
    var mutation = new dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard(guard);
    work.healthy(); // Actual authenticated Ops gate before observation/purge.
    var observed = work.observe(request.handle().run());
    guard.check();
    var audit = new ExpiryAuditRepository(connection);
    if (request.skipped()) {
      connection.setAutoCommit(false);
      mutation.bind(connection);
      verifyPriorExpiry(connection, request, observed.selectedCount());
      connection.rollback();
      connection.setAutoCommit(true);
      guard.check();
      require(work.healthy());
      return 0;
    }
    connection.setAutoCommit(false);
    mutation.bind(connection);
    var stage =
        audit.stage(
            request.handle(),
            observed.beforeCount(),
            observed.selectedCount(),
            observed.estimatedSelectedBytes());
    guard.check();
    connection.commit();
    guard.check();
    connection.setAutoCommit(true);
    connection.setAutoCommit(false);
    mutation.bind(connection);
    require(
        audit
            .read(request.handle())
            .equals(
                Optional.of(
                    new ExpiryAuditRepository.Snapshot(
                        "RUNNING",
                        stage.cutoff(),
                        stage.before(),
                        null,
                        stage.target(),
                        0,
                        0,
                        stage.estimatedBytes(),
                        null,
                        null,
                        null))));
    connection.rollback();
    connection.setAutoCommit(true);
    guard.check();
    @Nullable Long after = null;
    boolean purgeSucceeded = false;
    try {
      guard.check();
      var actual = work.purge(request.handle().run(), observed);
      guard.check();
      after = actual.afterCount();
      purgeSucceeded = true;
    } catch (ArtemisExpiryPurgeException actualFailure) {
      // Real attempted purge. No fabricated after=0/before and no unexecuted FAILED.
    }
    boolean healthy = false;
    try {
      healthy = work.healthy();
    } catch (ArtemisManagementReadinessException actualHealthFailure) {
      /* Actual Ops failure blocks startup. */
    }
    BatchStepResult.Status status =
        healthy
            ? (purgeSucceeded ? BatchStepResult.Status.SUCCESS : BatchStepResult.Status.WARNING)
            : BatchStepResult.Status.FAILED;
    BatchStepResult.Reason reason =
        !healthy
            ? BatchStepResult.Reason.SAFETY_FAILURE
            : purgeSucceeded ? BatchStepResult.Reason.NONE : BatchStepResult.Reason.COMMAND_FAILURE;
    long removed = after == null ? 0 : stage.before() - after;
    var result =
        new BatchStepResult(
            status,
            stage.target(),
            removed,
            purgeSucceeded ? 0 : stage.target(),
            stage.estimatedBytes(),
            reason);
    Instant ended = work.now();
    guard.check();
    connection.setAutoCommit(false);
    mutation.bind(connection);
    audit.finish(request.handle(), stage, ended, after, result);
    guard.check();
    connection.commit();
    guard.check();
    connection.setAutoCommit(true);
    connection.setAutoCommit(false);
    mutation.bind(connection);
    require(
        audit
            .read(request.handle())
            .equals(
                Optional.of(
                    new ExpiryAuditRepository.Snapshot(
                        status.name(),
                        stage.cutoff(),
                        stage.before(),
                        after,
                        result.target(),
                        result.success(),
                        result.failure(),
                        result.bytes(),
                        ended,
                        reason.code(),
                        reason.summary()))));
    connection.rollback();
    connection.setAutoCommit(true);
    guard.check();
    return status == BatchStepResult.Status.SUCCESS
        ? 0
        : status == BatchStepResult.Status.WARNING ? 10 : 30;
  }

  /** Closed correlation only; actual parent/kernel/current authentication is mandatory outside. */
  static void requireOwner(MaintenanceOwnerFrame owner, CleanupWorkerRequest.Expiry request)
      throws IOException {
    Objects.requireNonNull(owner, "actual Morning owner");
    Objects.requireNonNull(request, "actual Expiry request");
    require(
        owner.cleanup().isEmpty()
            && owner.boot().equals(request.boot())
            && owner.run().equals(request.run())
            && owner.activation().equals(request.activation())
            && owner.cutoff().equals(request.cutoff())
            && owner.epoch().equals(request.epoch()));
  }

  /** Whole seconds are rounded down; never grant a fresh per-phase five-second budget. */
  static long mqTimeoutMillis(MaintenanceOwnerFrame.Guard owner) throws IOException {
    return Objects.requireNonNull(owner, "actual parent deadline").queryTimeoutSeconds() * 1000L;
  }

  /**
   * SSC117/BUG351: current SKIP and immutable original audit are separately read in the caller tx.
   */
  static void verifyPriorExpiry(
      Connection connection, CleanupWorkerRequest.Expiry request, long selectedCount)
      throws IOException {
    Objects.requireNonNull(connection, "owned Expiry connection");
    Objects.requireNonNull(request, "bound Expiry request");
    require(request.skipped() && selectedCount == 0);
    new BatchRunRepository(connection).verifyAlreadySuccessful(request.handle());
    var existing =
        new ExpiryAuditRepository(connection)
            .read(request.priorHandle())
            .orElseThrow(BatchRepositoryException::new);
    var reference = request.prior().orElseThrow();
    verifyPriorAudit(reference, existing);
  }

  /** SSC302/PT-OPS-EXPIRY-AUDIT-SSC302001..014: data comparison, never DB authority. */
  static void verifyPriorAudit(
      CleanupWorkerRequest.Expiry.PriorExpiry reference, ExpiryAuditRepository.Snapshot existing)
      throws IOException {
    Objects.requireNonNull(reference, "retained Expiry reference");
    Objects.requireNonNull(existing, "retained Expiry audit");
    @Nullable Long before = existing.before();
    @Nullable Long after = existing.after();
    require(
        "SUCCESS".equals(existing.status())
            && reference.ended().equals(existing.ended())
            && reference.cutoff().minus(7, ChronoUnit.DAYS).equals(existing.cutoff())
            && before != null
            && after != null
            && before >= after
            && before - after == existing.success()
            && existing.success() == existing.target()
            && existing.failure() == 0
            && existing.errorCode() == null
            && existing.errorSummary() == null);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed original/current paths, no caller-selected namespace")
  private static void verify(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      CleanupWorkerRequest.Expiry request)
      throws IOException {
    context.recheck(expected);
    require(request.boot().toString().equals(expected.boot()));
    MaintenanceRunFiles.observeHost(context, expected, request.original());
    if (request.prior().isPresent()) {
      var prior = request.prior().orElseThrow();
      var anchor =
          MaintenanceRunFiles.observeSuccessReferenceHost(
              context,
              expected,
              request.original(),
              prior.run(),
              Instant.now().truncatedTo(ChronoUnit.MICROS));
      require(anchor.equals(request.priorHandle().run()));
    }
    var startupCalls = LinuxHostDirectoryCalls.create();
    Path startupPath = Path.of("/run/schubert-nk/startup");
    ResourceScope.<OwnedTransferDirectory, Boolean, IOException>acquire(
        () -> OwnedTransferDirectory.open(startupCalls, startupPath),
        OwnedTransferDirectory::close,
        startup -> {
          var current = new StartupPermitFiles(startup, LinuxInodeSecurity.create()).current();
          require(
              current.state() == StartupPermitRecords.State.INVALID
                  && current.boot().equals(request.boot())
                  && current.epoch().equals(request.epoch())
                  && current.activation().equals(request.original()));
          return Boolean.TRUE;
        });
    require(
        InspectorUnitProbe.forTarget(InspectorUnitSnapshot.Target.ARTEMIS)
            .read()
            .brokerRunningInvocation(request.brokerInvocation()));
    context.recheck(expected);
  }
}
