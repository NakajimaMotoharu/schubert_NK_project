package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.messaging.config.ApiBrokerContexts;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import jakarta.jms.JMSContext;
import java.io.InputStream;
import java.net.ServerSocket;
import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-024-G/H: loaded five-ID API credential scope with isolated loopback broker. */
final class ApiBrokerContextsCredentialTest {
  @TempDir Path temporary;

  @Test
  void admittedApiCredentialSetCreatesTwoConfiguredFactoriesWithoutOpeningContext()
      throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var reader =
          new ServiceCredentialReader(
              fixture.held,
              new InspectorCredentialLoaderTest.TestSecurity(io),
              ServiceConfigFiles.Service.API,
              io);
      try (var credentials = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.API)) {
        assertThrows(
            IllegalArgumentException.class,
            () -> ApiBrokerContexts.create(credentials, "tcp://0.0.0.0:61616"));
        try (var owner = ApiBrokerContexts.create(credentials, "tcp://127.0.0.1:61616")) {
          assertNotNull(owner.sync());
          assertNotNull(owner.webLog());
        }
        try (var owner =
            ApiBrokerContexts.createRetainingUnknown(credentials, "tcp://127.0.0.1:61616")) {
          assertNotNull(owner.sync());
          assertNotNull(owner.webLog());
          assertNotNull(owner.async());
        }
      }
      ServiceCredentialSetTest.assertCleared(io);
    }
  }

  @Test
  void loadedApiCredentialOpensBothProfilesAgainstIsolatedRealBroker() throws Exception {
    int port;
    try (var reservation = new ServerSocket(0)) {
      port = reservation.getLocalPort();
    }
    Configuration config;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      config = new FileConfigurationParser().parseMainConfig(input);
    }
    Path brokerRoot = Files.createDirectory(temporary.resolve("broker"));
    config
        .setPagingDirectory(brokerRoot.resolve("paging").toString())
        .setBindingsDirectory(brokerRoot.resolve("bindings").toString())
        .setJournalDirectory(brokerRoot.resolve("journal").toString())
        .setLargeMessagesDirectory(brokerRoot.resolve("large-messages").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "tcp://127.0.0.1:" + port);
    var broker = new EmbeddedActiveMQ().setConfiguration(config).start();
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var reader =
          new ServiceCredentialReader(
              fixture.held,
              new InspectorCredentialLoaderTest.TestSecurity(io),
              ServiceConfigFiles.Service.API,
              io);
      try (var credentials = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.API);
          var owner = ApiBrokerContexts.create(credentials, "tcp://127.0.0.1:" + port)) {
        try (var sync = owner.sync().get();
            var webLog = owner.webLog().get()) {
          assertEquals(JMSContext.SESSION_TRANSACTED, sync.getSessionMode());
          assertEquals(JMSContext.SESSION_TRANSACTED, webLog.getSessionMode());
        }
      }
      ServiceCredentialSetTest.assertCleared(io);
    } finally {
      broker.stop();
    }
  }
}
