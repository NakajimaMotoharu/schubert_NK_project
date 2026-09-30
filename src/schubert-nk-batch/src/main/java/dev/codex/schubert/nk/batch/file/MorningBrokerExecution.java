package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.mq.*;
import dev.codex.schubert.nk.batch.platform.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.*;
import java.io.IOException;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.jspecify.annotations.NullMarked;

/**
 * Same M/A/DB/original/INVALID owner: genuine Broker start + all Ops + fresh journal evidence.
 * NK-OPS-001 RD SYS004/MQ/OPS009 UI251/253 SS321/341/343 SSC125 BROKERSTART001..004. Successful
 * data observation is not issuer/API/Web or whole Morning acceptance.
 */
@NullMarked
final class MorningBrokerExecution {
  private MorningBrokerExecution() {}

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed same-owner current and Morning private credential copy")
  static MorningBrokerUnitCycle.Live execute(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MorningParentBudget budget,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database,
      StartupPermitRecords.Epoch epoch,
      MorningNewRunAdmission.OriginalProof original)
      throws IOException {
    require(
        expected.service() == RootStartupContext.Service.MORNING
            && epoch.state() == StartupPermitRecords.State.INVALID
            && epoch.activation().equals(state.activation())
            && expected.boot().equals(epoch.boot().toString()));
    Path startupPath = Path.of("/run/schubert-nk/startup");
    Path credentialPath = Path.of("/run/credentials/schubert-nk-morning-controller.service");
    require(ServiceCredentialLocation.read(System.getenv()).directory().equals(credentialPath));
    MaintenanceOwnerFrame.Guard parent =
        () -> {
          budget.requireWithin();
          context.recheck(expected);
          original.verify();
          database.recheckConsistent(state.activation().run());
          var startup = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), startupPath);
          ResourceScope.use(
              startup::close,
              () -> {
                require(
                    new StartupPermitFiles(startup, LinuxInodeSecurity.create())
                        .current()
                        .equals(epoch));
                return true;
              });
          context.recheck(expected);
          original.verify();
          return budget.remainingNanos();
        };
    parent.check();
    var credentials = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), credentialPath);
    return ResourceScope.use(
        credentials::close,
        () -> {
          var reader = new RootBatchCredentialReader(credentials, LinuxInodeSecurity.create());
          var cycle = MorningBrokerUnitCycle.create(context, expected, budget, parent::check);
          return cycle.execute(
              live ->
                  ArtemisManagementReadinessClient.withParentDeadline(
                      parent,
                      () -> {
                        observeOps(reader, parent, live);
                        BrokerJournalEvidence.inspect(live, epoch.boot(), parent);
                        return true;
                      }));
        });
  }

  private static void observeOps(
      RootBatchCredentialReader reader,
      MaintenanceOwnerFrame.Guard parent,
      MorningBrokerUnitCycle.Live live)
      throws IOException {
    // Startup/readiness may lag systemd Type=simple. Retry only genuine declared provider failure,
    // always under the existing absolute deadline. Unknown RuntimeException is not normal success.
    for (; ; ) {
      parent.check();
      live.recheck();
      try (var secret = reader.readOpsMq()) {
        long timeout = CleanupExpiryExecution.mqTimeoutMillis(parent);
        char[] password = secret.copyPassword();
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
          try (var factory =
                  Objects.requireNonNull(locator.createSessionFactory(), "owned Ops factory");
              var session =
                  factory.createSession(
                      "schubert_ops", new String(password), false, true, true, false, 0)) {
            Arrays.fill(password, '\0');
            parent.check();
            live.recheck();
            session.start();
            var observed = new ArtemisStartupObservation().inspect(session);
            require(
                observed.values().stream()
                    .noneMatch(value -> value == ArtemisQueuePressureClient.Pressure.CRITICAL));
            parent.check();
            live.recheck();
            return;
          }
        } catch (ActiveMQException | ArtemisManagementReadinessException actualNotReady) {
          parent.check();
          live.recheck();
        } finally {
          Arrays.fill(password, '\0');
        }
      }
      try {
        TimeUnit.MILLISECONDS.sleep(100);
      } catch (InterruptedException cancelled) {
        Thread.currentThread().interrupt();
        throw new IOException("Broker readiness unavailable");
      }
    }
  }
}
