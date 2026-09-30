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

  record Observations(
      ArtemisStartupObservation.Evidence values, BrokerJournalEvidence.Summary journal) {
    Observations {
      Objects.requireNonNull(values);
      Objects.requireNonNull(journal);
    }

    @Override
    public String toString() {
      return "BrokerObservations[actual=<redacted>]";
    }
  }

  /** Same callback owner; Live remains the OS guard, never a recursive DB guard. SSC128/130. */
  static final class Completion {
    private final MorningBrokerUnitCycle.Live live;
    private final Observations initial;
    private final MaintenanceOwnerFrame.Guard parent;
    private final MorningBrokerUnitCycle.ParentProof databaseProof;
    private final Path credentialPath;
    private final UUID boot;

    private Completion(
        MorningBrokerUnitCycle.Live live,
        Observations initial,
        MaintenanceOwnerFrame.Guard parent,
        MorningBrokerUnitCycle.ParentProof databaseProof,
        Path credentialPath,
        UUID boot) {
      this.live = Objects.requireNonNull(live);
      this.initial = Objects.requireNonNull(initial);
      this.parent = Objects.requireNonNull(parent);
      this.databaseProof = Objects.requireNonNull(databaseProof);
      this.credentialPath = Objects.requireNonNull(credentialPath);
      this.boot = Objects.requireNonNull(boot);
    }

    MorningBrokerUnitCycle.Live live() throws IOException {
      live.recheck();
      return live;
    }

    String invocation() throws IOException {
      live.recheck();
      return live.invocation();
    }

    void recheck() throws IOException {
      live.recheck();
    }

    Observations initial() throws IOException {
      live.recheck();
      return initial;
    }

    Observations observe() throws IOException {
      parent.check();
      live.recheck();
      databaseProof.verify();
      var credentials = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), credentialPath);
      return ResourceScope.use(
          credentials::close,
          () ->
              readObservations(
                  new RootBatchCredentialReader(credentials, LinuxInodeSecurity.create()),
                  parent,
                  live,
                  databaseProof,
                  boot));
    }

    @Override
    public String toString() {
      return "BrokerCompletion[actual=<redacted>]";
    }
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed same-owner current and Morning private credential copy")
  static Completion execute(
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
          // SSC128/BUG376: Live is also rechecked inside Session-owned read transactions.
          // Never start a recursive DB transaction through this borrowed OS/identity guard.
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
    database.recheckConsistent(state.activation().run());
    var credentials = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), credentialPath);
    return ResourceScope.use(
        credentials::close,
        () -> {
          var reader = new RootBatchCredentialReader(credentials, LinuxInodeSecurity.create());
          var cycle = MorningBrokerUnitCycle.create(context, expected, budget, parent::check);
          var observations = new ArrayList<Observations>();
          MorningBrokerUnitCycle.ParentProof databaseProof =
              () -> database.recheckConsistent(state.activation().run());
          var live =
              cycle.execute(
                  actual -> {
                    observations.add(
                        readObservations(reader, parent, actual, databaseProof, epoch.boot()));
                  });
          // BUG385: Cycle verifies readiness after start and again before intent retirement.
          // Keep both genuine snapshots; only its final verified observation is completion data.
          require(observations.size() == 2);
          return new Completion(
              live, observations.getLast(), parent, databaseProof, credentialPath, epoch.boot());
        });
  }

  private static Observations readObservations(
      RootBatchCredentialReader reader,
      MaintenanceOwnerFrame.Guard parent,
      MorningBrokerUnitCycle.Live live,
      MorningBrokerUnitCycle.ParentProof databaseProof,
      UUID boot)
      throws IOException {
    return ArtemisManagementReadinessClient.withParentDeadline(
        parent,
        () -> {
          var actual = observeOps(reader, parent, live, databaseProof);
          var journal = BrokerJournalEvidence.inspect(live, boot, parent);
          databaseProof.verify();
          return new Observations(actual, journal);
        });
  }

  private static ArtemisStartupObservation.Evidence observeOps(
      RootBatchCredentialReader reader,
      MaintenanceOwnerFrame.Guard parent,
      MorningBrokerUnitCycle.Live live,
      MorningBrokerUnitCycle.ParentProof databaseProof)
      throws IOException {
    // Startup/readiness may lag systemd Type=simple. Retry only genuine declared provider failure,
    // always under the existing absolute deadline. Unknown RuntimeException is not normal success.
    for (; ; ) {
      parent.check();
      live.recheck();
      databaseProof.verify();
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
            var observed = new ArtemisStartupObservation().inspectEvidence(session);
            require(
                observed.pressure().values().stream()
                    .noneMatch(
                        value -> value.state() == ArtemisQueuePressureClient.Pressure.CRITICAL));
            parent.check();
            live.recheck();
            databaseProof.verify();
            return observed;
          }
        } catch (ActiveMQException | ArtemisManagementReadinessException actualNotReady) {
          parent.check();
          live.recheck();
          databaseProof.verify();
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
