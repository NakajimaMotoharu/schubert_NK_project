package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSource;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-API-RES-001..006. Real credential channels/PG/pool, explicitly synthetic OS admission. */
final class ServiceProcessResourcesTest {
  private static final String FIXTURE_UNTRUSTED_6FC6869D = "UNTRUSTED";
  @TempDir static Path temporary;
  private static ApiLogDatabaseFixture database;
  private static String url;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(Files.createDirectory(temporary.resolve("pg")));
    try (var admin = database.admin()) {
      url = admin.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  private static ServiceProcessResources.Inputs inputs(Path root) {
    return new ServiceProcessResources.Inputs(
        ServiceConfigFiles.Service.API,
        ServiceCredentialLocation.read(Map.of("CREDENTIALS_DIRECTORY", root.toString())),
        url);
  }

  @Test
  void opsApiRes001RealFiveMaterialsAndAdmittedPoolOwnedScope() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
      var io = new InspectorCredentialLoaderTest.TestIo();
      AtomicReference<HikariDataSource> poolRef = new AtomicReference<>();
      AtomicReference<ServiceCredentialSet> credentialsRef = new AtomicReference<>();
      var runtime =
          new ServiceProcessResources(
              inputs(fixture.root),
              LinuxDirectoryCalls.create(),
              new InspectorCredentialLoaderTest.TestSecurity(io),
              io,
              ServiceProcessResourcesTest::apiPool);
      runtime.executeRetainingUnknown(
          (pool, credentials) -> {
            poolRef.set((HikariDataSource) pool);
            credentialsRef.set(credentials);
            assertEquals(8, poolRef.get().getMaximumPoolSize());
            assertEquals(2, poolRef.get().getMinimumIdle());
            assertThrows(
                NullPointerException.class,
                () -> ServiceProcessResources.unassembledStartup().run(null, credentials));
            assertThrows(
                NullPointerException.class,
                () -> ServiceProcessResources.unassembledStartup().run(pool, null));
            try (var connection = pool.getConnection();
                var statement = connection.createStatement();
                var rows = statement.executeQuery("select current_user::text")) {
              assertTrue(rows.next());
              assertEquals("schubert_app", rows.getString(1));
              assertFalse(rows.next());
            } catch (SQLException failure) {
              throw new IOException("fixture query failed");
            }
            byte[] copy = credentials.copyKey(ServiceCredentialId.API_CONTEXT_AES_CURRENT);
            try {
              assertArrayEquals(new byte[32], copy);
            } finally {
              Arrays.fill(copy, (byte) 0);
            }
          });
      assertTrue(poolRef.get().isClosed());
      assertThrows(
          IllegalStateException.class,
          () -> credentialsRef.get().copyKey(ServiceCredentialId.API_CONTEXT_AES_CURRENT));
      ServiceCredentialSetTest.assertCleared(io);
      boolean directoryExists = fixture.held.atDirectory(path -> Files.isDirectory(path));
      assertTrue(directoryExists);
      // Valid acquired materials/pool must never make the unfinished native assembly accepting.
      // This tests the production refusal through the real owned scope, not a readiness fixture.
      assertThrows(
          StorageIoException.class,
          () -> runtime.execute(ServiceProcessResources.unassembledStartup()));
      ServiceCredentialSetTest.assertCleared(io);
    }
  }

  @Test
  void opsApiRes002CallbackAndPoolCloseCompoundFailuresDoNotReturnSuccess() throws Exception {
    for (Throwable body :
        List.of(
            new IOException(FIXTURE_UNTRUSTED_6FC6869D),
            new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D),
            new AssertionError(FIXTURE_UNTRUSTED_6FC6869D))) {
      for (Throwable cleanup :
          Arrays.asList(
              null,
              new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D),
              body instanceof IOException
                  ? new AssertionError(FIXTURE_UNTRUSTED_6FC6869D)
                  : body)) {
        try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
          ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
          var io = new InspectorCredentialLoaderTest.TestIo();
          AtomicReference<ServiceDatabaseSource> sourceRef = new AtomicReference<>();
          AtomicReference<ClosingPool> poolRef = new AtomicReference<>();
          AtomicReference<ServiceCredentialSet> credentialsRef = new AtomicReference<>();
          var runtime =
              new ServiceProcessResources(
                  inputs(fixture.root),
                  LinuxDirectoryCalls.create(),
                  new InspectorCredentialLoaderTest.TestSecurity(io),
                  io,
                  (target, password) -> {
                    var source =
                        new ServiceDatabaseSource(ServiceConfigFiles.Service.API, target, password);
                    sourceRef.set(source);
                    return source;
                  },
                  source -> {
                    var pool = new ClosingPool(apiPool(source), cleanup);
                    poolRef.set(pool);
                    return pool;
                  });
          var operation =
              (ServiceProcessResources.Operation)
                  (pool, credentials) -> {
                    credentialsRef.set(credentials);
                    if (body instanceof IOException known) throw known;
                    if (body instanceof RuntimeException unknown) throw unknown;
                    throw (Error) body;
                  };
          if (body instanceof IOException) {
            if (cleanup == null)
              assertThrows(StorageIoException.class, () -> runtime.execute(operation));
            else
              assertSame(
                  cleanup, assertThrows(cleanup.getClass(), () -> runtime.execute(operation)));
          } else assertSame(body, assertThrows(body.getClass(), () -> runtime.execute(operation)));
          assertTrue(poolRef.get().owned.isClosed());
          assertEquals(1, poolRef.get().closes.get());
          assertThrows(SQLException.class, sourceRef.get()::getConnection);
          assertThrows(
              IllegalStateException.class,
              () -> credentialsRef.get().copyPassword(ServiceCredentialId.DB_API));
          for (Throwable secondary : body.getSuppressed())
            assertFalse(secondary.toString().contains(FIXTURE_UNTRUSTED_6FC6869D));
          ServiceCredentialSetTest.assertCleared(io);
        }
      }
    }
  }

  @Test
  void opsApiRes003PartialAcquisitionFailureClearsPasswordAndMaterials() throws Exception {
    for (int stage = 0; stage < 4; stage++) {
      try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
        ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
        var io = new InspectorCredentialLoaderTest.TestIo();
        AtomicReference<char[]> copied = new AtomicReference<>();
        AtomicReference<ServiceDatabaseSource> sourceRef = new AtomicReference<>();
        int failureStage = stage;
        var runtime =
            new ServiceProcessResources(
                inputs(fixture.root),
                LinuxDirectoryCalls.create(),
                new InspectorCredentialLoaderTest.TestSecurity(io),
                io,
                (target, password) -> {
                  copied.set(password);
                  if (failureStage == 0)
                    throw new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D);
                  if (failureStage == 1) return null;
                  var source =
                      new ServiceDatabaseSource(ServiceConfigFiles.Service.API, target, password);
                  sourceRef.set(source);
                  return source;
                },
                source -> {
                  if (failureStage == 2)
                    throw new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D);
                  return null;
                });
        Class<? extends RuntimeException> expectedFailure =
            stage % 2 == 0 ? IllegalStateException.class : NullPointerException.class;
        assertThrows(
            expectedFailure, () -> runtime.execute((pool, credentials) -> fail("no callback")));
        assertArrayEquals(new char[copied.get().length], copied.get());
        if (stage >= 2) assertThrows(SQLException.class, sourceRef.get()::getConnection);
        ServiceCredentialSetTest.assertCleared(io);
      }
    }
  }

  @Test
  void opsApiRes004MissingMalformedAndAclFailureNeverCreatesDatabase() throws Exception {
    for (int stage = 0; stage < 3; stage++) {
      try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
        ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
        if (stage == 0) Files.delete(fixture.root.resolve("mq-api"));
        if (stage == 1) Files.writeString(fixture.root.resolve("mq-api"), "\n");
        var io = new InspectorCredentialLoaderTest.TestIo();
        if (stage == 2) io.rootChange = attributes -> attributes.put("uid", 2);
        var runtime =
            new ServiceProcessResources(
                inputs(fixture.root),
                LinuxDirectoryCalls.create(),
                new InspectorCredentialLoaderTest.TestSecurity(io),
                io,
                (target, password) -> {
                  throw new AssertionError("no source");
                },
                source -> {
                  throw new AssertionError("no pool");
                });
        assertThrows(
            StorageIoException.class,
            () -> runtime.execute((pool, credentials) -> fail("no callback")));
        ServiceCredentialSetTest.assertCleared(io);
      }
    }
  }

  @Test
  void opsApiRes005NullAndNativeFactoryBoundaries() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> new ServiceProcessResources(null, ServiceProcessResourcesTest::apiPool));
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      var values = inputs(fixture.root);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var calls = LinuxDirectoryCalls.create();
      var security = new InspectorCredentialLoaderTest.TestSecurity(io);
      var source =
          (ServiceProcessResources.SourceFactory)
              (target, password) ->
                  new ServiceDatabaseSource(ServiceConfigFiles.Service.API, target, password);
      var pool = (ServiceProcessResources.PoolFactory) admitted -> apiPool(admitted);
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources(null, calls, security, io, source, pool));
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources(values, null, security, io, source, pool));
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources(values, calls, null, io, source, pool));
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources(values, calls, security, null, source, pool));
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources(values, calls, security, io, null, pool));
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources(values, calls, security, io, source, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new ServiceProcessResources(values, ServiceProcessResourcesTest::apiPool)
                  .execute(null));
      // Real temp FS does NOT satisfy production credential policy. This proves refusal, not OS
      // admission.
      assertThrows(
          StorageIoException.class,
          () ->
              new ServiceProcessResources(values, ServiceProcessResourcesTest::apiPool)
                  .execute((p, c) -> fail("not admitted")));
    }
  }

  @Test
  void opsApiRes006IndependentConcurrentScopes() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary);
        var workers = Executors.newFixedThreadPool(4)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
      var values = inputs(fixture.root);
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 8; i++)
        work.add(
            () -> {
              var io = new InspectorCredentialLoaderTest.TestIo();
              new ServiceProcessResources(
                      values,
                      LinuxDirectoryCalls.create(),
                      new InspectorCredentialLoaderTest.TestSecurity(io),
                      io,
                      ServiceProcessResourcesTest::apiPool)
                  .execute(
                      (pool, credentials) -> {
                        try (var connection = pool.getConnection()) {
                          assertFalse(connection.isClosed());
                        } catch (SQLException failure) {
                          throw new IOException("fixture connection failed");
                        }
                      });
              ServiceCredentialSetTest.assertCleared(io);
              return true;
            });
      for (var done : workers.invokeAll(work)) assertTrue(done.get(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void opsWebRes001WebOnlyFiveMaterialsTechnicalRoleAndTwoConnectionCeiling() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.WEB);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var location =
          ServiceCredentialLocation.read(Map.of("CREDENTIALS_DIRECTORY", fixture.root.toString()));
      var values =
          new ServiceProcessResources.Inputs(ServiceConfigFiles.Service.WEB, location, url);
      assertEquals(ServiceConfigFiles.Service.WEB, values.service());
      assertEquals(location, values.credentials());
      assertEquals(url, values.databaseUrl());
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources.Inputs(null, location, url));
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources.Inputs(ServiceConfigFiles.Service.WEB, null, url));
      assertThrows(
          NullPointerException.class,
          () -> new ServiceProcessResources.Inputs(ServiceConfigFiles.Service.WEB, location, null));
      assertThrows(NullPointerException.class, () -> new ServiceProcessResources(values, null));
      AtomicReference<HikariDataSource> closed = new AtomicReference<>();
      new ServiceProcessResources(
              values,
              LinuxDirectoryCalls.create(),
              new InspectorCredentialLoaderTest.TestSecurity(io),
              io,
              admitted -> {
                var config = new HikariConfig();
                config.setDataSource(admitted);
                config.setMaximumPoolSize(2);
                config.setMinimumIdle(1);
                config.setConnectionTimeout(3000);
                var pool = new HikariDataSource(config);
                closed.set(pool);
                return pool;
              })
          .execute(
              (pool, credentials) -> {
                assertEquals(2, closed.get().getMaximumPoolSize());
                assertEquals(1, closed.get().getMinimumIdle());
                try (var connection = pool.getConnection();
                    var statement = connection.createStatement();
                    var rows = statement.executeQuery("select current_user::text")) {
                  assertTrue(rows.next());
                  assertEquals("schubert_web_session", rows.getString(1));
                  assertFalse(rows.next());
                } catch (SQLException failure) {
                  throw new IOException("fixture query failed");
                }
                assertThrows(
                    IllegalArgumentException.class,
                    () -> credentials.copyPassword(ServiceCredentialId.DB_API));
                byte[] key = credentials.copyKey(ServiceCredentialId.WEB_SESSION_AES_CURRENT);
                try {
                  assertArrayEquals(new byte[32], key);
                } finally {
                  Arrays.fill(key, (byte) 0);
                }
              });
      assertTrue(closed.get().isClosed());
      assertEquals(5, io.opens);
      assertEquals(5, io.closes);
      ServiceCredentialSetTest.assertCleared(io);
    }
  }

  private static HikariDataSource apiPool(javax.sql.DataSource source) {
    // Independent pool fixture. Production API/Web factories remain in their owning modules.
    var config = new HikariConfig();
    config.setDataSource(source);
    config.setMaximumPoolSize(8);
    config.setMinimumIdle(2);
    config.setConnectionTimeout(3000);
    return new HikariDataSource(config);
  }

  private static final class ClosingPool extends HikariDataSource {
    final HikariDataSource owned;
    final Throwable failure;
    final AtomicInteger closes = new AtomicInteger();

    ClosingPool(HikariDataSource owned, Throwable failure) {
      this.owned = owned;
      this.failure = failure;
    }

    @Override
    public Connection getConnection() throws SQLException {
      return owned.getConnection();
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      owned.close();
      if (failure instanceof RuntimeException unknown) throw unknown;
      if (failure instanceof Error fatal) throw fatal;
    }
  }
}
