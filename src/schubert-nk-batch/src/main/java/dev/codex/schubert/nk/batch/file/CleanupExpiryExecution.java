package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.mq.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.*;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.apache.activemq.artemis.api.core.client.*;
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
    var credentials = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), fixed);
    return ResourceScope.use(
        credentials::close,
        () -> {
          var reader = new RootBatchCredentialReader(credentials, LinuxInodeSecurity.create());
          var request = reader.readExpiryRequest();
          verify(context, expected, request);
          var database =
              CleanupDatabaseSession.forExpiry(
                  "jdbc:postgresql://127.0.0.1:5432/schubert_nk", context, expected, release);
          return database.execute(
              reader.read(), connection -> mq(connection, reader, context, expected, request));
        });
  }

  private static int mq(
      Connection connection,
      RootBatchCredentialReader reader,
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      CleanupWorkerRequest.Expiry request)
      throws IOException {
    try (var maintenancePassword = reader.readMaintenanceMq();
        var opsPassword = reader.readOpsMq()) {
      char[] maintenance = maintenancePassword.copyPassword(), ops = opsPassword.copyPassword();
      try (var locator =
          new org.apache.activemq.artemis.core.client.impl.ServerLocatorImpl(
              false,
              new org.apache.activemq.artemis.api.core.TransportConfiguration(
                  org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory.class
                      .getName(),
                  Map.of("host", "127.0.0.1", "port", 61616)))) {
        locator
            .setCallTimeout(5000)
            .setCallFailoverTimeout(5000)
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
          health.inspect(opsSession); // Actual authenticated Ops gate before observation/purge.
          var purge = new ArtemisExpiryPurgeClient();
          var observed = purge.observe(maintenanceSession, request.handle().run());
          verify(context, expected, request);
          var audit = new ExpiryAuditRepository(connection);
          if (request.skipped()) {
            connection.setAutoCommit(false);
            verifyPriorExpiry(connection, request, observed.selectedCount());
            connection.rollback();
            connection.setAutoCommit(true);
            verify(context, expected, request);
            require(
                health.inspect(opsSession).get("nk.expiry")
                    != ArtemisQueuePressureClient.Pressure.CRITICAL);
            return 0;
          }
          connection.setAutoCommit(false);
          var stage =
              audit.stage(
                  request.handle(),
                  observed.beforeCount(),
                  observed.selectedCount(),
                  observed.estimatedSelectedBytes());
          connection.commit();
          connection.setAutoCommit(true);
          connection.setAutoCommit(false);
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
          verify(context, expected, request);
          @Nullable Long after = null;
          boolean purgeSucceeded = false;
          try {
            var actual = purge.purgeObserved(maintenanceSession, request.handle().run(), observed);
            after = actual.afterCount();
            purgeSucceeded = true;
          } catch (ArtemisExpiryPurgeException actualFailure) {
            // Real attempted purge. No fabricated after=0/before and no unexecuted FAILED.
          }
          boolean healthy = false;
          try {
            healthy =
                health.inspect(opsSession).get("nk.expiry")
                    != ArtemisQueuePressureClient.Pressure.CRITICAL;
          } catch (ArtemisManagementReadinessException actualHealthFailure) {
            /* Actual Ops failure blocks startup. */
          }
          BatchStepResult.Status status =
              healthy
                  ? (purgeSucceeded
                      ? BatchStepResult.Status.SUCCESS
                      : BatchStepResult.Status.WARNING)
                  : BatchStepResult.Status.FAILED;
          BatchStepResult.Reason reason =
              !healthy
                  ? BatchStepResult.Reason.SAFETY_FAILURE
                  : purgeSucceeded
                      ? BatchStepResult.Reason.NONE
                      : BatchStepResult.Reason.COMMAND_FAILURE;
          long removed = after == null ? 0 : stage.before() - after;
          var result =
              new BatchStepResult(
                  status,
                  stage.target(),
                  removed,
                  purgeSucceeded ? 0 : stage.target(),
                  stage.estimatedBytes(),
                  reason);
          Instant ended = Instant.now().truncatedTo(ChronoUnit.MICROS);
          verify(context, expected, request);
          connection.setAutoCommit(false);
          audit.finish(request.handle(), stage, ended, after, result);
          connection.commit();
          connection.setAutoCommit(true);
          connection.setAutoCommit(false);
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
          verify(context, expected, request);
          return status == BatchStepResult.Status.SUCCESS
              ? 0
              : status == BatchStepResult.Status.WARNING ? 10 : 30;
        }
      } finally {
        Arrays.fill(maintenance, '\0');
        Arrays.fill(ops, '\0');
      }
    } catch (SQLException | ActiveMQException failure) {
      throw new IOException("Expiry execution unavailable");
    }
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
    @Nullable Long before = existing.before(), after = existing.after();
    require(
        "SUCCESS".equals(existing.status())
            && reference.ended().equals(existing.ended())
            && request.cutoff().minus(7, ChronoUnit.DAYS).equals(existing.cutoff())
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
    var startup =
        OwnedTransferDirectory.open(
            LinuxDirectoryCalls.create(), Path.of("/run/schubert-nk/startup"));
    ResourceScope.use(
        startup::close,
        () -> {
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
            .runningInvocation(request.brokerInvocation()));
    context.recheck(expected);
  }
}
