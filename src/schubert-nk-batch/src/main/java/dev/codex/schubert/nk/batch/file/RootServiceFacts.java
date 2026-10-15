package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfig;
import dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSource;
import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessException;
import dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClient;
import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfig;
import java.io.IOException;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.jspecify.annotations.NullMarked;

/** Actual service Root inputs, all secret/JDBC/JMS owners close before return. SSC137/PT297. */
@NullMarked
final class RootServiceFacts {
  record Facts(RootReleaseAdmission.EffectiveConfigurations configurations, String rootsSha256) {
    Facts {
      Objects.requireNonNull(configurations);
      Objects.requireNonNull(rootsSha256);
    }

    @Override
    public String toString() {
      return "RootServiceFacts[public=<redacted>]";
    }
  }

  private RootServiceFacts() {}

  static Facts inspect(
      RootStartupContext root,
      RootStartupContext.Snapshot self,
      ServiceConfigFiles.Service service,
      RootCurrentPermitPreflight.Observed issued,
      MaintenanceOwnerFrame owner,
      RootReleaseAdmission release)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(self);
    Objects.requireNonNull(service);
    Objects.requireNonNull(issued);
    Objects.requireNonNull(owner);
    Objects.requireNonNull(release);
    require(
        self.service()
            == (service == ServiceConfigFiles.Service.API
                ? RootStartupContext.Service.API
                : RootStartupContext.Service.WEB));
    root.recheck(self);
    owner.parentsGuard().check();
    var config = release.inspectServiceConfigurations();
    require(
        config.apiSha256().equals(issued.permit().apiConfigDigest())
            && config.webSha256().equals(issued.permit().webConfigDigest()));
    var roots = MorningStartupRoots.createService(root, self, config.roots());
    var observedRoots = roots.capture();
    String rootsSha = observedRoots.sha256Issued(issued.permit());
    require(rootsSha.equals(issued.permit().rootsDigest()));
    String url;
    try {
      url =
          service == ServiceConfigFiles.Service.API
              ? ApiNonSecretConfig.parse(
                      config.apiYaml().commonYaml(), config.apiYaml().serviceYaml())
                  .value("nk.db.url")
              : WebNonSecretConfig.parse(
                      config.webYaml().commonYaml(), config.webYaml().serviceYaml())
                  .value("nk.db.url");
    } catch (java.security.NoSuchAlgorithmException known) {
      throw new IOException("root service configuration unavailable");
    }
    RootServiceCredentialSource.execute(
        root,
        self,
        (database, ops) -> {
          owner.parentsGuard().check();
          root.recheck(self);
          try (var source = new ServiceDatabaseSource(service, url, database.copyPassword());
              var connection = source.getConnection()) {
            var actual = release.inspectServiceDatabase(connection, self);
            require(actual.contents().sha256().equals(issued.permit().releaseDigest()));
            observeOps(root, self, issued.permit(), owner, ops);
            var after = release.inspectServiceDatabase(connection, self);
            require(actual.equals(after));
          } catch (SQLException known) {
            throw new IOException("root service database unavailable");
          }
          owner.parentsGuard().check();
          root.recheck(self);
          return Boolean.TRUE;
        });
    roots.recheck(observedRoots);
    release.recheckServiceConfigurations(config);
    require(owner.equals(RootStartupPending.observe(root, self, issued)));
    root.recheck(self);
    return new Facts(config, rootsSha);
  }

  private static void observeOps(
      RootStartupContext root,
      RootStartupContext.Snapshot self,
      StartupPermitRecords.Permit permit,
      MaintenanceOwnerFrame owner,
      InspectorDbCredential ops)
      throws IOException {
    var identity = new FixedServiceIdentity().resolveArtemis();
    var child = new ChildStartupContext();
    owner.parentsGuard().check();
    root.recheck(self);
    var before = child.verifyBroker(permit.boot(), permit.brokerInvocation(), identity);
    long timeout = CleanupExpiryExecution.mqTimeoutMillis(owner.parentsGuard());
    char[] password = ops.copyPassword();
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
      try (var factory = Objects.requireNonNull(locator.createSessionFactory());
          var session =
              factory.createSession(
                  "schubert_ops", new String(password), false, true, true, false, 0)) {
        Arrays.fill(password, '\0');
        session.start();
        var evidence = new ArtemisStartupObservation().inspectEvidence(session);
        require(
            evidence.pressure().values().stream()
                .noneMatch(v -> v.state() == ArtemisQueuePressureClient.Pressure.CRITICAL));
        require(
            before.equals(child.verifyBroker(permit.boot(), permit.brokerInvocation(), identity)));
        owner.parentsGuard().check();
        root.recheck(self);
      }
    } catch (ActiveMQException | ArtemisManagementReadinessException known) {
      throw new IOException("root service Ops unavailable");
    } finally {
      Arrays.fill(password, '\0');
    }
    require(before.equals(child.verifyBroker(permit.boot(), permit.brokerInvocation(), identity)));
    owner.parentsGuard().check();
    root.recheck(self);
  }
}
