package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.web.bootstrap.WebDependencyReadiness;
import dev.codex.schubert.nk.web.messaging.WebBrokerContexts;
import jakarta.jms.JMSContext;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.net.ServerSocket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-JMS-WEB-003: Web five-ID synthetic credential and isolated real TCP broker only. */
final class WebBrokerContextsCredentialTest {
  @TempDir Path temporary;

  @Test
  void native316LoadedSyntheticCredentialBuildsFactoryWithoutOpeningContext() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.WEB);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var reader =
          new ServiceCredentialReader(
              fixture.held,
              new InspectorCredentialLoaderTest.TestSecurity(io),
              ServiceConfigFiles.Service.WEB,
              io);
      try (var credentials = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.WEB);
          var owner =
              WebBrokerContexts.createRetainingUnknown(credentials, "tcp://127.0.0.1:61616")) {
        assertNotNull(owner.contexts());
      }
      ServiceCredentialSetTest.assertCleared(io);
    }
  }

  @Test
  void loadedWebRoleOpensRealBrokerAndOuterReplyProbeClosesBorrowedContext() throws Exception {
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
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.WEB);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var reader =
          new ServiceCredentialReader(
              fixture.held,
              new InspectorCredentialLoaderTest.TestSecurity(io),
              ServiceConfigFiles.Service.WEB,
              io);
      try (var credentials = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.WEB);
          var owner = WebBrokerContexts.create(credentials, "tcp://127.0.0.1:" + port)) {
        assertDoesNotThrow(
            () -> new WebDependencyReadiness(validDatabase(), owner.contexts()).verify());
        try (var context = owner.contexts().open()) {
          assertEquals(JMSContext.SESSION_TRANSACTED, context.getSessionMode());
        }
        assertEquals(
            0,
            broker
                .getActiveMQServer()
                .locateQueue(
                    org.apache.activemq.artemis.api.core.SimpleString.of("nk.sync.reply.web.q"))
                .getConsumerCount());
      }
      ServiceCredentialSetTest.assertCleared(io);
    } finally {
      broker.stop();
    }
  }

  private static DataSource validDatabase() {
    var connection =
        (Connection)
            Proxy.newProxyInstance(
                Connection.class.getClassLoader(),
                new Class<?>[] {Connection.class},
                (ignored, method, arguments) ->
                    switch (method.getName()) {
                      case "isValid" -> {
                        assertEquals(2, arguments[0]);
                        yield true;
                      }
                      case "close" -> null;
                      default -> throw new AssertionError(method.getName());
                    });
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (ignored, method, arguments) -> {
              if (method.getName().equals("getConnection")) return connection;
              throw new AssertionError(method.getName());
            });
  }
}
