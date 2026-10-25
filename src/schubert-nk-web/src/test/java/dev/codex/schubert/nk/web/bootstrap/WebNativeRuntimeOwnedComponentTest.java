package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.api.file.WebNativeRuntimeCredentialFixture;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptor;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** WEBOWN327001..007 / SS313343354. Own DB/JMS/HTTP/FDs, not native Root admission. */
final class WebNativeRuntimeOwnedComponentTest {
  @TempDir Path temporary;

  @Test
  void webown327001StartedHandlesRemainOwnedUntilIdempotentClose() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      fixture.withKeys(
          keys -> {
            var owner = fixture.owner(keys);
            try {
              assertFalse(owner.healthy());
              assertFalse(owner.ready());
              owner.start();
              assertTrue(owner.healthy());
              assertTrue(owner.ready());
              assertEquals(1, fixture.promotions.get());
              assertEquals(2, fixture.live.size());
              assertEquals(2, fixture.verified.get());
              assertThrows(IOException.class, owner::start);
              assertEquals(1, fixture.directoryAcquisitions.get());
              assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
            } finally {
              owner.close();
            }
            assertFalse(owner.healthy());
            assertFalse(owner.ready());
            assertTrue(fixture.live.isEmpty());
            int closed = fixture.closes.get();
            owner.close();
            assertEquals(closed, fixture.closes.get());
            assertEquals(1, fixture.promotions.get());
            assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
            try (var connection = fixture.database.web()) {
              assertTrue(connection.isValid(2));
            }
          });
    }
  }

  @Test
  void webown327002VerificationFailureKeepsCapturedOwnerAndOriginalThrowable() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      fixture.withKeys(
          keys -> {
            Throwable[] failures = {
              new IOException("synthetic IO"),
              new IllegalStateException("synthetic runtime"),
              new LinkageError("synthetic fatal"),
              null,
              null,
              null,
              null
            };
            for (int index = 0; index < failures.length; index++) {
              int mode = index;
              Throwable primary = failures[index];
              fixture.verified.set(0);
              fixture.verification =
                  entry -> {
                    if (mode >= 5 && fixture.verified.get() == 0) return fixture.verifyOwn(entry);
                    if (primary instanceof IOException io) throw io;
                    if (primary instanceof RuntimeException runtime) throw runtime;
                    if (primary instanceof Error fatal) throw fatal;
                    return mode == 3 || mode == 5 ? null : Boolean.FALSE;
                  };
              var owner = fixture.owner(keys);
              try {
                Throwable observed = assertThrows(Throwable.class, owner::start);
                if (primary != null) assertSame(primary, observed);
                else {
                  assertInstanceOf(IOException.class, observed);
                  assertEquals("Web directory proof unavailable", observed.getMessage());
                }
                assertEquals(mode >= 5 ? 2 : 1, fixture.live.size());
                assertFalse(owner.ready());
                assertEquals(0, fixture.promotions.get());
              } finally {
                owner.close();
              }
              assertTrue(fixture.live.isEmpty());
              assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
            }
          });
    }
  }

  @Test
  void webown327003ReadyFailureNeverPromotesAndCloseReleasesKnownComponents() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      fixture.withKeys(
          keys -> {
            var primary = new IOException("synthetic Ready failure");
            fixture.releaseFailure = primary;
            var owner = fixture.owner(keys);
            try {
              assertSame(primary, assertThrows(IOException.class, owner::start));
              assertFalse(owner.ready());
              assertEquals(1, fixture.promotions.get());
              assertEquals(2, fixture.live.size());
            } finally {
              owner.close();
            }
            assertFalse(owner.healthy());
            assertTrue(fixture.live.isEmpty());
            assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
          });
    }
  }

  @Test
  void webown327004CloseCannotEnterWhileStartOwnsPrivateMonitor() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      fixture.withKeys(
          keys -> {
            var owner = fixture.owner(keys);
            var attempted = new CountDownLatch(1);
            var failure = new AtomicReference<Throwable>();
            var closer =
                new Thread(
                    () -> {
                      attempted.countDown();
                      try {
                        owner.close();
                      } catch (Throwable problem) {
                        failure.set(problem);
                      }
                    },
                    "own-component-close");
            fixture.verification =
                entry -> {
                  if (fixture.verified.get() == 0) {
                    closer.start();
                    try {
                      assertTrue(attempted.await(5, TimeUnit.SECONDS));
                      long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
                      while (closer.getState() != Thread.State.BLOCKED
                          && System.nanoTime() < deadline) Thread.onSpinWait();
                      assertEquals(Thread.State.BLOCKED, closer.getState());
                      assertEquals(1, fixture.live.size());
                    } catch (InterruptedException interrupted) {
                      Thread.currentThread().interrupt();
                      throw new IOException("own fixture interrupted", interrupted);
                    }
                  }
                  return fixture.verifyOwn(entry);
                };
            try {
              owner.start();
              closer.join(TimeUnit.SECONDS.toMillis(20));
              assertFalse(closer.isAlive());
              assertNull(failure.get());
              assertTrue(fixture.live.isEmpty());
              assertFalse(owner.ready());
              assertFalse(owner.healthy());
              assertEquals(1, fixture.promotions.get());
            } finally {
              owner.close();
              if (closer.isAlive()) closer.join(TimeUnit.SECONDS.toMillis(20));
            }
          });
    }
  }

  @Test
  void webown327005NullPortsFailBeforeAnyDirectoryAcquisition() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      fixture.withKeys(
          keys -> {
            var config = fixture.config();
            assertThrows(
                NullPointerException.class,
                () ->
                    new WebNativeRuntime(
                        fixture.source(),
                        keys,
                        config,
                        fixture.ready(),
                        () -> false,
                        null,
                        fixture::path,
                        (c, k) -> 0,
                        fixture::verifyOwn));
            assertThrows(
                NullPointerException.class,
                () ->
                    new WebNativeRuntime(
                        fixture.source(),
                        keys,
                        config,
                        fixture.ready(),
                        () -> false,
                        fixture::directories,
                        null,
                        (c, k) -> 0,
                        fixture::verifyOwn));
            assertThrows(
                NullPointerException.class,
                () ->
                    new WebNativeRuntime(
                        fixture.source(),
                        keys,
                        config,
                        fixture.ready(),
                        () -> false,
                        fixture::directories,
                        fixture::path,
                        null,
                        fixture::verifyOwn));
            assertThrows(
                NullPointerException.class,
                () ->
                    new WebNativeRuntime(
                        fixture.source(),
                        keys,
                        config,
                        fixture.ready(),
                        () -> false,
                        fixture::directories,
                        fixture::path,
                        (c, k) -> 0,
                        null));
            assertEquals(0, fixture.directoryAcquisitions.get());
            var owner =
                new WebNativeRuntime(
                    fixture.source(),
                    keys,
                    config,
                    fixture.ready(),
                    () -> false,
                    () -> null,
                    fixture::path,
                    (c, k) -> 0,
                    fixture::verifyOwn);
            try {
              assertThrows(NullPointerException.class, owner::start);
            } finally {
              owner.close();
            }
            var acquireFailure = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
            var failed =
                new WebNativeRuntime(
                    fixture.source(),
                    keys,
                    config,
                    fixture.ready(),
                    () -> false,
                    () -> {
                      throw acquireFailure;
                    },
                    fixture::path,
                    (c, k) -> 0,
                    fixture::verifyOwn);
            try {
              assertSame(acquireFailure, assertThrows(StorageIoException.class, failed::start));
            } finally {
              failed.close();
            }
            assertTrue(fixture.live.isEmpty());
            assertEquals(0, fixture.promotions.get());
            assertEquals("v", keys.version(ServiceCredentialId.WEB_SESSION_AES_CURRENT));
          });
    }
  }

  @Test
  void webown327006OuterStoppingCannotPublishReady() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      fixture.withKeys(
          keys -> {
            fixture.stopping.set(true);
            var owner = fixture.owner(keys);
            try {
              assertEquals(
                  "Web readiness unavailable",
                  assertThrows(IOException.class, owner::start).getMessage());
              assertFalse(owner.ready());
              assertFalse(owner.healthy());
              assertEquals(0, fixture.promotions.get());
            } finally {
              owner.close();
            }
            assertTrue(fixture.live.isEmpty());
            assertThrows(IOException.class, owner::start);
          });
    }
  }

  @Test
  void webown327007NativeBindingsUseFixedLiteralsAndVerifyOwnMetadata() throws Exception {
    var config = WebNonSecretConfig.parse("", "");
    assertEquals(Path.of("/run/schubert-nk/web"), WebNativeRuntime.nativePath(config, "runtime"));
    assertEquals(
        Path.of("/srv/schubert-nk/data/transfer"),
        WebNativeRuntime.nativePath(config, "nk.web.storage.transfer-root"));
    assertEquals(
        Path.of("/srv/schubert-nk/data/assets"),
        WebNativeRuntime.nativePath(config, "nk.web.storage.asset-root"));
    assertEquals(8080, WebNativeRuntime.nativePort(config, "nk.web.http.port"));
    assertEquals(8081, WebNativeRuntime.nativePort(config, "nk.web.management.port"));
    assertThrows(
        IllegalArgumentException.class, () -> WebNativeRuntime.nativePath(config, "unknown"));
    assertThrows(
        IllegalArgumentException.class, () -> WebNativeRuntime.nativePort(config, "unknown"));
    assertThrows(NullPointerException.class, () -> WebNativeRuntime.nativePath(null, "runtime"));
    assertThrows(NullPointerException.class, () -> WebNativeRuntime.nativePath(config, null));
    assertThrows(
        NullPointerException.class, () -> WebNativeRuntime.nativePort(null, "nk.web.http.port"));
    assertThrows(NullPointerException.class, () -> WebNativeRuntime.nativePort(config, null));
    Path own = Files.createDirectory(temporary.resolve("own"));
    Files.setPosixFilePermissions(own, PosixFilePermissions.fromString("rwxr-x---"));
    var attributes = Files.readAttributes(own, PosixFileAttributes.class);
    var identity = new StorageIdentity(attributes.owner().getName(), attributes.group().getName());
    try (var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), own)) {
      assertEquals(Boolean.TRUE, WebNativeRuntime.nativeVerify(Map.entry(root, identity)));
      String other = identity.owner().equals("not-owner") ? "other-owner" : "not-owner";
      assertThrows(
          StorageIoException.class,
          () ->
              WebNativeRuntime.nativeVerify(
                  Map.entry(root, new StorageIdentity(other, identity.group()))));
      Files.setPosixFilePermissions(own, PosixFilePermissions.fromString("rwx------"));
      assertThrows(
          StorageIoException.class, () -> WebNativeRuntime.nativeVerify(Map.entry(root, identity)));
    }
    assertThrows(NullPointerException.class, () -> WebNativeRuntime.nativeVerify(null));
    assertThrows(
        NullPointerException.class,
        () ->
            WebNativeRuntime.nativeVerify(
                new java.util.AbstractMap.SimpleImmutableEntry<>(null, identity)));
  }

  private static final class Fixture implements AutoCloseable {
    final Path root;
    final WebLogDatabaseFixture database;
    final EmbeddedActiveMQ broker;
    final int brokerPort;
    final Set<Integer> live = ConcurrentHashMap.newKeySet();
    final AtomicInteger closes = new AtomicInteger();
    final AtomicInteger directoryAcquisitions = new AtomicInteger();
    final AtomicInteger verified = new AtomicInteger();
    final AtomicInteger promotions = new AtomicInteger();
    final AtomicBoolean stopping = new AtomicBoolean();
    IOException releaseFailure;
    ResourceScope.OwnedAction<Map.Entry<OwnedTransferDirectory, StorageIdentity>, Boolean>
        verification = this::verifyOwn;

    Fixture(Path root) throws Exception {
      this.root = root;
      // Validate the exact shared fixture format before creating any external owned resource.
      assertEquals("tcp://127.0.0.1:1", configAtPort(1).value("nk.mq.url"));
      for (String name : new String[] {"runtime", "transfer", "assets", "keys"})
        Files.createDirectory(root.resolve(name));
      database = new WebLogDatabaseFixture(Files.createDirectory(root.resolve("database")));
      broker = new EmbeddedActiveMQ();
      try {
        org.apache.activemq.artemis.core.config.Configuration configuration;
        try (var input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
          configuration = new FileConfigurationParser().parseMainConfig(input);
        }
        Path directory = Files.createDirectory(root.resolve("broker"));
        configuration
            .setPagingDirectory(directory.resolve("paging").toString())
            .setBindingsDirectory(directory.resolve("bindings").toString())
            .setJournalDirectory(directory.resolve("journal").toString())
            .setLargeMessagesDirectory(directory.resolve("large").toString())
            .setSecurityEnabled(false)
            .clearAcceptorConfigurations()
            .addAcceptorConfiguration("component", "tcp://127.0.0.1:0");
        broker.setConfiguration(configuration).start();
        brokerPort =
            ((NettyAcceptor)
                    broker.getActiveMQServer().getRemotingService().getAcceptor("component"))
                .getActualPort();
        assertTrue(brokerPort > 0);
      } catch (Throwable failure) {
        try {
          broker.stop();
        } catch (Throwable closing) {
          if (closing != failure) failure.addSuppressed(closing);
        }
        try {
          database.stop();
        } catch (Throwable closing) {
          if (closing != failure) failure.addSuppressed(closing);
        }
        throw failure;
      }
    }

    void withKeys(WebNativeRuntimeCredentialFixture.Action action) throws Exception {
      WebNativeRuntimeCredentialFixture.withKeys(root.resolve("keys"), action);
    }

    WebNonSecretConfig config() throws java.security.NoSuchAlgorithmException {
      return configAtPort(brokerPort);
    }

    private static WebNonSecretConfig configAtPort(int port)
        throws java.security.NoSuchAlgorithmException {
      return WebNonSecretConfig.parse("", "nk.mq.url: tcp://127.0.0.1:" + port + "\n");
    }

    DataSource source() {
      return (DataSource)
          Proxy.newProxyInstance(
              getClass().getClassLoader(),
              new Class<?>[] {DataSource.class},
              (proxy, method, args) -> {
                if (method.getName().equals("getConnection")) return database.web();
                throw new AssertionError("unexpected owned fixture DataSource operation");
              });
    }

    ServiceStartupAdmission.Ready ready() {
      return new ServiceStartupAdmission.Ready() {
        @Override
        public void release() throws IOException {
          promotions.incrementAndGet();
          if (releaseFailure != null) throw releaseFailure;
        }

        @Override
        public Map<String, String> information() {
          return Map.of(
              "commit",
              "0000000000000000000000000000000000000001",
              "app",
              "0.1.0-SNAPSHOT",
              "config",
              "1",
              "schema",
              "027",
              "protocol",
              "0.1.0-SNAPSHOT");
        }
      };
    }

    WebNativeRuntime owner(ServiceCredentialSet keys) throws Exception {
      return new WebNativeRuntime(
          source(),
          keys,
          config(),
          ready(),
          stopping::get,
          this::directories,
          this::path,
          (config, key) -> {
            assertTrue(Set.of("nk.web.http.port", "nk.web.management.port").contains(key));
            return 0;
          },
          entry -> verification.run(entry));
    }

    Path path(WebNonSecretConfig config, String key) {
      assertNotNull(config);
      return root.resolve(
          switch (key) {
            case "runtime" -> "runtime";
            case "nk.web.storage.transfer-root" -> "transfer";
            case "nk.web.storage.asset-root" -> "assets";
            default -> throw new AssertionError("unexpected component path");
          });
    }

    DirectoryCalls directories() throws StorageIoException {
      directoryAcquisitions.incrementAndGet();
      var delegate = LinuxDirectoryCalls.create();
      return (DirectoryCalls)
          Proxy.newProxyInstance(
              getClass().getClassLoader(),
              new Class<?>[] {DirectoryCalls.class},
              (proxy, method, args) -> {
                try {
                  Object result = method.invoke(delegate, args);
                  if (result instanceof Integer descriptor && descriptor >= 0)
                    assertTrue(live.add(descriptor));
                  return result;
                } catch (InvocationTargetException failure) {
                  throw failure.getCause();
                } finally {
                  if (method.getName().equals("close")) {
                    assertTrue(live.remove((Integer) args[0]));
                    closes.incrementAndGet();
                  }
                }
              });
    }

    Boolean verifyOwn(Map.Entry<OwnedTransferDirectory, StorageIdentity> entry) throws IOException {
      int index = verified.getAndIncrement();
      assertEquals(
          index == 0
              ? new StorageIdentity("schubert-api", "schubert-web")
              : new StorageIdentity("schubert-data", "schubert-read"),
          entry.getValue());
      boolean directory = entry.getKey().atDirectory(Files::isDirectory);
      assertTrue(directory);
      return Boolean.TRUE;
    }

    @Override
    public void close() throws IOException {
      Throwable failure = null;
      try {
        broker.stop();
      } catch (Throwable primary) {
        if (primary instanceof InterruptedException) Thread.currentThread().interrupt();
        failure = primary;
      }
      try {
        database.stop();
      } catch (Throwable secondary) {
        if (secondary instanceof InterruptedException) Thread.currentThread().interrupt();
        if (failure == null) failure = secondary;
        else if (secondary instanceof Error && !(failure instanceof Error)) {
          if (secondary != failure) secondary.addSuppressed(failure);
          failure = secondary;
        } else if (secondary != failure) failure.addSuppressed(secondary);
      }
      if (failure instanceof Error fatal) throw fatal;
      if (failure instanceof RuntimeException runtime) throw runtime;
      if (failure != null) throw new IOException("own component fixture stop unconfirmed", failure);
      assertTrue(live.isEmpty());
    }
  }
}
