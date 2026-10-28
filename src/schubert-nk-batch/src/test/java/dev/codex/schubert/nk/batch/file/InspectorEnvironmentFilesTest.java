package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/**
 * OPS-009/UI251/SS343 6.12; PG-D-155; NS001..008; real isolated namespace, synthetic root/GID/FS.
 */
final class InspectorEnvironmentFilesTest {
  private static final String FIXTURE_COMPLETE_575951DB = "complete";
  private static final String FIXTURE_UNLINK_04963CA9 = "unlink";
  private static final String FIXTURE_GROUP_654E1E20 = "group";
  private static final String FIXTURE_CREATE_5498A731 = "create";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_RUNTIME_2D52CD90 = "runtime";
  private static final String FIXTURE_ETC_9F5F0C94 = "etc";
  private static final String FIXTURE_CONFIG_48882AB4 = "config";
  private static final String FIXTURE_APP_4E5EF144 = "app";
  private static final String FIXTURE_MAINTENANCE_9CE8617E = "maintenance";
  private static final String FIXTURE_STATIC_0105CCA0 = "static";
  private static final String FIXTURE_ATTRIBUTES_D300E055 = "attributes";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_FILESYSTEM_909B3E41 = "filesystem";
  private static final String FIXTURE_ACL_43B23946 = "acl";
  private static final String FIXTURE_READONLY_C4A495E7 = "readonly";
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("00000000-0000-0000-0000-000000000155"),
          Instant.parse("2026-09-12T00:00:00Z"));
  private static final String CONFIG =
      "NK_INSPECTOR_DB_URL=jdbc:postgresql://127.0.0.1:5432/schubert_nk\nNK_INSPECTOR_FINGERPRINT_VERSIONS=v1,v2\n";
  private static final String RUNTIME =
      "NK_INSPECTOR_RUN_ID=00000000-0000-0000-0000-000000000155\nNK_INSPECTOR_CUTOFF=2026-09-12T00:00:00Z\n";
  private static final String NAME = "inbox-inspector.env";
  @TempDir Path temporary;

  @Test
  void inspector919001ForeignThreadCannotRetireOwnedEnvironment() throws Exception {
    try (var f = fixture();
        var executor = Executors.newSingleThreadExecutor()) {
      assertEquals(
          FIXTURE_COMPLETE_575951DB,
          f.files.executeOwned(
              RUN,
              retirement -> {
                var denied =
                    executor.submit(
                        () -> assertThrows(StorageIoException.class, retirement::retire));
                assertNotNull(assertDoesNotThrow(() -> denied.get(5, TimeUnit.SECONDS)));
                assertEquals(RUNTIME, Files.readString(f.target));
                assertEquals(0, f.count(FIXTURE_UNLINK_04963CA9));
                retirement.retire();
                assertFalse(Files.exists(f.target));
                return FIXTURE_COMPLETE_575951DB;
              }));
      assertEquals(1, f.count(FIXTURE_UNLINK_04963CA9));
      f.released();
    }
  }

  @Test
  void nativeOwnedRetirementOccursBeforeCallbackIntentAndCannotEscape() throws Exception {
    InspectorEnvironmentFiles.Retirement[] saved = {null};
    try (var f = fixture()) {
      assertEquals(
          FIXTURE_COMPLETE_575951DB,
          f.files.executeOwned(
              RUN,
              retirement -> {
                assertEquals(RUNTIME, Files.readString(f.target));
                saved[0] = retirement;
                retirement.retire();
                assertFalse(
                    Files.exists(f.target)); // The caller's intent may only be retired after this.
                assertThrows(StorageIoException.class, retirement::retire);
                return FIXTURE_COMPLETE_575951DB;
              }));
      assertThrows(StorageIoException.class, saved[0]::retire);
      f.released();
    }
    for (String existing : List.of(NAME, RUN.id() + ".part"))
      try (var f = fixture()) {
        Files.writeString(f.maintenance.resolve(existing), existing.equals(NAME) ? RUNTIME : "old");
        assertThrows(
            StorageIoException.class,
            () ->
                f.files.executeOwned(
                    RUN,
                    retirement -> {
                      fail("old namespace must not call child");
                      return "bad";
                    }));
        assertTrue(Files.exists(f.maintenance.resolve(existing)));
        f.released();
      }
    try (var f = fixture()) {
      assertThrows(
          StorageIoException.class, () -> f.files.executeOwned(RUN, retirement -> "not-retired"));
      assertEquals(RUNTIME, Files.readString(f.target));
      f.released();
    }
  }

  @Test
  void prepareCallbackRetire() throws Exception {
    try (var f = fixture()) {
      assertEquals(
          "terminal",
          f.files.execute(
              RUN,
              () -> {
                f.callbacks++;
                assertEquals(RUNTIME, Files.readString(f.target));
                assertEquals(CONFIG, Files.readString(f.staticFile));
                assertEquals(0100600, Files.getAttribute(f.target, "unix:mode"));
                assertEquals(5, f.live.size());
                return "terminal";
              }));
      assertEquals(1, f.callbacks);
      assertEquals(3, f.count(FIXTURE_GROUP_654E1E20));
      assertFalse(Files.exists(f.target));
      assertEquals(CONFIG, Files.readString(f.staticFile));
      assertFalse(Files.exists(f.maintenance.resolve(RUN.id() + ".part")));
      f.released();
    }
    try (var f = fixture()) {
      Files.writeString(f.target, RUNTIME);
      assertEquals(7, (int) f.files.execute(RUN, () -> 7));
      assertEquals(0, f.count(FIXTURE_CREATE_5498A731));
      assertFalse(Files.exists(f.target));
    }
  }

  private static void throwCompound(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static void assertCompound(Throwable expected, Throwable actual, boolean known) {
    assertSame(expected, actual);
    assertEquals(known ? 0 : 1, actual.getSuppressed().length);
    if (!known) {
      var fixed = assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
      assertEquals(StorageIoException.Reason.UNAVAILABLE, fixed.reason());
      assertNull(fixed.getCause());
      assertEquals(0, fixed.getSuppressed().length);
    }
  }

  @Test
  void callbackFailureRetention() throws Exception {

    // PG172/SSC063, BUG195/YKT154; close offsets independently follow reverse acquisition.
    for (int position = 1; position <= 5; position++) {
      int offset = position;
      for (boolean known : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("synthetic compound"),
                new NullPointerException("synthetic compound"),
                new AssertionError("synthetic compound"))) {
          try (var f = fixture()) {
            int[] closes = {0};
            int[] injected = {0};
            int[] callbacks = {0};

            Throwable actual =
                assertThrows(
                    unknown.getClass(),
                    () ->
                        f.files.execute(
                            RUN,
                            () -> {
                              callbacks[0]++;

                              closes[0] = f.count(FIXTURE_CLOSE_97959247);
                              f.on(
                                  FIXTURE_CLOSE_97959247,
                                  closes[0] + offset,
                                  () -> {
                                    injected[0]++;
                                    throwCompound(unknown);
                                  });
                              if (known) throw new IOException("synthetic primary");
                              throwCompound(unknown);
                              return true;
                            }));
            assertCompound(unknown, actual, known);
            assertEquals(1, injected[0]);
            assertEquals(1, callbacks[0]);
            assertEquals(closes[0] + 5, f.count(FIXTURE_CLOSE_97959247));
            assertEquals(RUNTIME, Files.readString(f.target));
            assertEquals(CONFIG, Files.readString(f.staticFile));
            assertEquals(0, f.count(FIXTURE_UNLINK_04963CA9));
            f.released();
          }
        }
    }
    for (String mode : List.of("io", FIXTURE_RUNTIME_2D52CD90, "null"))
      try (var f = fixture()) {
        var expected = new IllegalStateException("synthetic callback failure");
        Executable operation =
            () ->
                f.files.execute(
                    RUN,
                    () -> {
                      f.callbacks++;
                      assertEquals(RUNTIME, Files.readString(f.target));
                      if (mode.equals("io")) throw new IOException("synthetic raw child detail");
                      if (mode.equals(FIXTURE_RUNTIME_2D52CD90)) throw expected;
                      return null;
                    });
        if (mode.equals("io")) failure(operation);
        else if (mode.equals(FIXTURE_RUNTIME_2D52CD90))
          assertSame(expected, assertThrows(IllegalStateException.class, operation));
        else assertThrows(NullPointerException.class, operation);
        assertEquals(1, f.callbacks);
        assertEquals(RUNTIME, Files.readString(f.target));
        assertEquals(0, f.count(FIXTURE_UNLINK_04963CA9));
        f.released();
      }
  }

  @Test
  void namespaceAndStaticIdentity() throws Exception {
    for (int at : List.of(2, 3))
      for (String role :
          List.of(
              FIXTURE_ETC_9F5F0C94,
              FIXTURE_CONFIG_48882AB4,
              FIXTURE_RUNTIME_2D52CD90,
              FIXTURE_APP_4E5EF144,
              FIXTURE_MAINTENANCE_9CE8617E,
              FIXTURE_STATIC_0105CCA0))
        try (var f = fixture()) {
          f.on(FIXTURE_GROUP_654E1E20, at, () -> f.replace(role));
          failure(() -> f.files.execute(RUN, f::callback));
          assertEquals(at == 2 ? 0 : 1, f.callbacks);
          assertEquals(0, f.count(FIXTURE_UNLINK_04963CA9));
          f.released();
        }
    for (int at : List.of(2, 3))
      try (var f = fixture()) {
        f.on(FIXTURE_GROUP_654E1E20, at, () -> f.group = 2001);
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(at == 2 ? 0 : 1, f.callbacks);
        assertEquals(RUNTIME, Files.readString(f.target));
      }
    for (int at : List.of(2, 3))
      try (var f = fixture()) {
        f.on(
            FIXTURE_GROUP_654E1E20,
            at,
            () -> Files.writeString(f.staticFile, CONFIG.replace("v1,v2", "v3,v4")));
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(at == 2 ? 0 : 1, f.callbacks);
        assertEquals(CONFIG.replace("v1,v2", "v3,v4"), Files.readString(f.staticFile));
      }
    try (var f = fixture()) {
      f.on(FIXTURE_ATTRIBUTES_D300E055, 7, () -> f.replace(FIXTURE_STATIC_0105CCA0));
      failure(() -> f.files.execute(RUN, f::callback));
      assertEquals(0, f.callbacks);
      assertEquals(0, f.count(FIXTURE_CREATE_5498A731));
    }
  }

  @Test
  void permissionsAndAccounts() throws Exception {
    for (long group : new long[] {0, -1, 4294967296L})
      try (var f = fixture()) {
        f.group = group;
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(0, f.count("openRoot"));
      }
    for (String role :
        List.of(
            FIXTURE_ETC_9F5F0C94,
            FIXTURE_CONFIG_48882AB4,
            FIXTURE_RUNTIME_2D52CD90,
            FIXTURE_APP_4E5EF144,
            FIXTURE_MAINTENANCE_9CE8617E,
            FIXTURE_STATIC_0105CCA0)) {
      for (String key :
          List.of(
              FIXTURE_MODE_B6D5C2C3,
              "uid",
              "gid",
              "nlink",
              "size",
              "dev",
              "ino",
              "lastModifiedTime",
              "ctime"))
        for (Object invalid : Arrays.asList(null, "wrong type"))
          try (var f = fixture()) {
            f.change =
                (observed, values) -> {
                  if (role.equals(observed)) values.put(key, invalid);
                };
            failure(() -> f.files.execute(RUN, f::callback));
            assertEquals(0, f.callbacks);
            assertEquals(0, f.count(FIXTURE_CREATE_5498A731));
          }
      for (String key : List.of(FIXTURE_MODE_B6D5C2C3, "uid", "gid", "nlink", "size"))
        try (var f = fixture()) {
          f.change =
              (observed, values) -> {
                if (role.equals(observed))
                  values.put(
                      key,
                      key.equals("size")
                          ? (Object) (-1L)
                          : key.equals("nlink") && !role.equals(FIXTURE_STATIC_0105CCA0) ? 1 : 99);
              };
          failure(() -> f.files.execute(RUN, f::callback));
          assertEquals(0, f.callbacks);
          assertEquals(0, f.count(FIXTURE_CREATE_5498A731));
        }
      for (String wrong :
          List.of(
              "nullAttributes",
              "nullFilesystem",
              FIXTURE_FILESYSTEM_909B3E41,
              "nullAcl",
              FIXTURE_ACL_43B23946))
        try (var f = fixture()) {
          f.badRole = role;
          f.invalid = wrong;
          failure(() -> f.files.execute(RUN, f::callback));
          assertEquals(0, f.callbacks);
        }
    }
    for (String role :
        List.of(
            FIXTURE_CONFIG_48882AB4,
            FIXTURE_APP_4E5EF144,
            FIXTURE_MAINTENANCE_9CE8617E,
            FIXTURE_STATIC_0105CCA0))
      try (var f = fixture()) {
        f.change =
            (observed, values) -> {
              if (role.equals(observed)) values.put("dev", 99L);
            };
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(0, f.callbacks);
      }
    for (String role :
        List.of(FIXTURE_RUNTIME_2D52CD90, FIXTURE_APP_4E5EF144, FIXTURE_MAINTENANCE_9CE8617E))
      try (var f = fixture()) {
        f.badRole = role;
        f.invalid = FIXTURE_READONLY_C4A495E7;
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(0, f.callbacks);
      }
    try (var f = fixture()) {
      f.staticReadonly = true;
      assertEquals(1, (int) f.files.execute(RUN, () -> 1));
    }
  }

  @Test
  void allOpenCloseFailures() throws Exception {
    Map<String, Integer> expected;
    try (var f = fixture()) {
      f.files.execute(RUN, f::callback);
      // Three scopes each open /etc->config and /run->app->maintenance. Path depth is fixture
      // input, not a production-derived expected count; every acquired native FD closes once.
      int directoryOpens = 3 * (f.etc.getNameCount() + f.runtime.getNameCount() + 3);
      expected =
          Map.ofEntries(
              Map.entry(FIXTURE_GROUP_654E1E20, 3),
              Map.entry("openRoot", 6),
              Map.entry("openDirectory", directoryOpens),
              Map.entry("openEntry", 26),
              Map.entry(FIXTURE_CREATE_5498A731, 1),
              Map.entry(FIXTURE_CLOSE_97959247, 6 + directoryOpens + 26),
              Map.entry("publish", 1),
              Map.entry(FIXTURE_UNLINK_04963CA9, 1),
              Map.entry("sync", 2),
              Map.entry(FIXTURE_ATTRIBUTES_D300E055, 70),
              Map.entry(FIXTURE_ACL_43B23946, 70),
              Map.entry(FIXTURE_FILESYSTEM_909B3E41, 70),
              Map.entry(FIXTURE_READONLY_C4A495E7, 70),
              Map.entry("openRead", 8),
              Map.entry("readSize", 16),
              Map.entry("read", 16),
              Map.entry("readClose", 8),
              Map.entry("openWriter", 1),
              Map.entry("writeSize", 2),
              Map.entry("write", 1),
              Map.entry("force", 1),
              Map.entry("writerClose", 1));
      assertEquals(expected, f.counts);
      f.released();
    }
    for (var entry : expected.entrySet())
      for (int at = 1; at <= entry.getValue(); at++)
        try (var f = fixture()) {
          f.fail = entry.getKey();
          f.failAt = at;
          failure(() -> f.files.execute(RUN, f::callback));
          assertTrue(f.triggered, entry.getKey() + " at " + at);
          f.released();
          assertTrue(f.callbacks <= 1);
        }
    try (var f = fixture()) {
      failure(
          () ->
              f.files.execute(
                  RUN,
                  () -> {
                    f.rawCloses = true;
                    throw new IOException("synthetic callback diagnostics");
                  }));
      f.released();
    }
  }

  @Test
  void lateFailureAndInterruption() throws Exception {
    try (var f = fixture()) {
      Thread.currentThread().interrupt();
      try {
        failure(() -> f.files.execute(RUN, f::callback));
        assertTrue(Thread.currentThread().isInterrupted());
        assertTrue(f.counts.isEmpty());
      } finally {
        Thread.interrupted();
      }
    }
    for (int position : List.of(2, 3))
      try (var f = fixture()) {
        f.on(FIXTURE_GROUP_654E1E20, position, () -> Thread.currentThread().interrupt());
        try {
          failure(() -> f.files.execute(RUN, f::callback));
          assertTrue(Thread.currentThread().isInterrupted());
          f.released();
        } finally {
          Thread.interrupted();
        }
      }
    try (var f = fixture()) {
      int directoryOpens = 3 * (f.etc.getNameCount() + f.runtime.getNameCount() + 3);
      f.on(
          FIXTURE_CLOSE_97959247,
          6 + directoryOpens + 26,
          () -> Thread.currentThread().interrupt());
      try {
        failure(() -> f.files.execute(RUN, f::callback));
        assertTrue(Thread.currentThread().isInterrupted());
        assertEquals(1, f.callbacks);
        assertFalse(Files.exists(f.target));
        f.released();
      } finally {
        Thread.interrupted();
      }
    }
    try (var f = fixture()) {
      failure(
          () ->
              f.files.execute(
                  RUN,
                  () -> {
                    f.callbacks++;
                    Files.writeString(f.target, RUNTIME.replace("00:00:00Z", "00:00:01Z"));
                    // Conversion is not allowed: the runtime byte parser raises its fixed
                    // configuration error.
                    f.fail = FIXTURE_ATTRIBUTES_D300E055;
                    f.failAt = f.count(FIXTURE_ATTRIBUTES_D300E055) + 1;
                    return 1;
                  }));
      assertEquals(1, f.callbacks);
      assertEquals(0, f.count(FIXTURE_UNLINK_04963CA9));
    }
    try (var f = fixture()) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              f.files.execute(
                  RUN,
                  () -> {
                    Files.writeString(f.target, RUNTIME.replace("00:00:00Z", "00:00:01Z"));
                    return 1;
                  }));
      assertEquals(0, f.count(FIXTURE_UNLINK_04963CA9));
      assertTrue(Files.exists(f.target));
    }
  }

  @Test
  void concurrentScopes() throws Exception {
    try (var f = fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      AtomicInteger active = new AtomicInteger();
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < 32; index++) {
        int input = index;
        futures.add(
            executor.submit(
                () ->
                    f.files.execute(
                        RUN,
                        () -> {
                          assertEquals(1, active.incrementAndGet());
                          try {
                            assertEquals(RUNTIME, Files.readString(f.target));
                            return input;
                          } finally {
                            active.decrementAndGet();
                          }
                        })));
      }
      for (int index = 0; index < futures.size(); index++)
        assertEquals(index, futures.get(index).get(10, TimeUnit.SECONDS));
      assertEquals(32, f.count(FIXTURE_CREATE_5498A731));
      assertEquals(32, f.count(FIXTURE_UNLINK_04963CA9));
      assertFalse(Files.exists(f.target));
      f.released();
    }
  }

  @Test
  void constructorAndFactory() throws Exception {
    try (var f = fixture()) {
      assertThrows(
          NullPointerException.class,
          () -> new InspectorEnvironmentFiles(null, f.runtime, f.calls, f, f::group, f));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorEnvironmentFiles(f.etc, null, f.calls, f, f::group, f));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorEnvironmentFiles(f.etc, f.runtime, null, f, f::group, f));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorEnvironmentFiles(f.etc, f.runtime, f.calls, null, f::group, f));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorEnvironmentFiles(f.etc, f.runtime, f.calls, f, null, f));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorEnvironmentFiles(f.etc, f.runtime, f.calls, f, f::group, null));
      for (Path path : List.of(Path.of("relative"), Path.of("/"), f.etc.resolve("../etc"))) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new InspectorEnvironmentFiles(path, f.runtime, f.calls, f, f::group, f));
        assertThrows(
            IllegalArgumentException.class,
            () -> new InspectorEnvironmentFiles(f.etc, path, f.calls, f, f::group, f));
      }
      assertThrows(NullPointerException.class, () -> f.files.execute(null, () -> 1));
      assertThrows(NullPointerException.class, () -> f.files.execute(RUN, null));
      assertTrue(f.counts.isEmpty());
      f.uid = 1;
      failure(() -> f.files.execute(RUN, f::callback));
      assertTrue(f.counts.isEmpty());
      assertNotEquals(0, LinuxInodeSecurity.create().effectiveUid(), "unprivileged PG/PT host");
      failure(
          () -> InspectorEnvironmentFiles.create().execute(RUN, () -> fail("no root admission")));
    }
  }

  private Fixture fixture() throws Exception {
    return new Fixture(Files.createTempDirectory(temporary, "namespace-"));
  }

  private static void failure(Executable operation) {
    var ex = assertThrows(StorageIoException.class, operation);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, ex.reason());
    assertEquals("transfer storage operation failed", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
  }

  @FunctionalInterface
  interface Action {
    void execute() throws IOException;
  }

  private static final class Fixture
      implements AutoCloseable, InodeSecurityCalls, InspectorEnvironmentPublisher.Io {
    final Path base;
    final Path etc;
    final Path config;
    final Path runtime;
    final Path app;
    final Path maintenance;
    final Path staticFile;
    final Path target;
    final DirectoryCalls calls;
    final InspectorEnvironmentFiles files;
    final InspectorEnvironmentPublisher.NioIo nativeIo = new InspectorEnvironmentPublisher.NioIo();
    final Set<Integer> live = ConcurrentHashMap.newKeySet();
    final Map<Long, String> originalRoles = new HashMap<>();
    final Map<String, Integer> counts = new ConcurrentHashMap<>();
    long uid;
    long group = 2000;
    int readers;
    int writers;
    int callbacks;
    int failAt = 1;
    int hookAt = 1;
    String fail = "";
    String hookName = "";
    String invalid = "";
    String badRole = "";
    boolean triggered;
    boolean rawCloses;
    boolean staticReadonly;
    Action hook = () -> {};
    BiConsumer<String, Map<String, Object>> change = (role, values) -> {};

    Fixture(Path base) throws Exception {
      this.base = base;
      etc = base.resolve(FIXTURE_ETC_9F5F0C94);
      config = etc.resolve("schubert-nk");
      runtime = base.resolve("run");
      app = runtime.resolve("schubert-nk");
      maintenance = app.resolve(FIXTURE_MAINTENANCE_9CE8617E);
      staticFile = config.resolve(NAME);
      target = maintenance.resolve(NAME);
      Files.createDirectories(config);
      Files.createDirectories(maintenance);
      Files.writeString(staticFile, CONFIG);
      for (String role :
          List.of(
              FIXTURE_ETC_9F5F0C94,
              FIXTURE_CONFIG_48882AB4,
              FIXTURE_RUNTIME_2D52CD90,
              FIXTURE_APP_4E5EF144,
              FIXTURE_MAINTENANCE_9CE8617E,
              FIXTURE_STATIC_0105CCA0))
        originalRoles.put((Long) Files.getAttribute(path(role), "unix:ino"), role);
      DirectoryCalls delegate = LinuxDirectoryCalls.create();
      calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    String point =
                        name.equals("createPrivateFile") ? FIXTURE_CREATE_5498A731 : name;
                    if (!name.equals(FIXTURE_CLOSE_97959247)) point(point);
                    Object value;
                    try {
                      value = method.invoke(delegate, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (Set.of("openRoot", "openDirectory", "openEntry", "createPrivateFile")
                        .contains(name)) assertTrue(live.add((Integer) value));
                    if (name.equals(FIXTURE_CLOSE_97959247)) {
                      assertTrue(live.remove((Integer) args[0]));
                      point(FIXTURE_CLOSE_97959247);
                      if (rawCloses)
                        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                    }
                    return value;
                  });
      files = new InspectorEnvironmentFiles(etc, runtime, calls, this, this::group, this);
    }

    Path path(String role) {
      return switch (role) {
        case FIXTURE_ETC_9F5F0C94 -> etc;
        case FIXTURE_CONFIG_48882AB4 -> config;
        case FIXTURE_RUNTIME_2D52CD90 -> runtime;
        case FIXTURE_APP_4E5EF144 -> app;
        case FIXTURE_MAINTENANCE_9CE8617E -> maintenance;
        case FIXTURE_STATIC_0105CCA0 -> staticFile;
        default -> throw new AssertionError(role);
      };
    }

    int callback() throws IOException {
      callbacks++;
      assertEquals(RUNTIME, Files.readString(target));
      return 1;
    }

    long group() throws IOException {
      point(FIXTURE_GROUP_654E1E20);
      return group;
    }

    int count(String name) {
      return counts.getOrDefault(name, 0);
    }

    void on(String name, int at, Action action) {
      hookName = name;
      hookAt = at;
      hook = action;
    }

    void point(String name) throws StorageIoException {
      int at = counts.merge(name, 1, Integer::sum);
      if (hookName.equals(name) && hookAt == at) {
        try {
          hook.execute();
        } catch (IOException failure) {
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        }
      }
      if (name.equals(fail) && failAt == at) {
        triggered = true;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    void replace(String role) throws IOException {
      Path old = path(role);
      Files.move(old, old.resolveSibling(old.getFileName() + "-saved"));
      if (role.equals(FIXTURE_STATIC_0105CCA0)) Files.writeString(staticFile, CONFIG);
      else if (role.equals(FIXTURE_ETC_9F5F0C94) || role.equals(FIXTURE_CONFIG_48882AB4)) {
        Files.createDirectories(config);
        Files.writeString(staticFile, CONFIG);
      } else {
        Files.createDirectories(maintenance);
        Files.writeString(target, RUNTIME);
      }
    }

    String role(Path held) throws IOException {
      var values = nativeIo.attributes(held);
      String original = originalRoles.get((Long) values.get("ino"));
      if (original != null) return original;
      Path resolved = held.toRealPath();
      if (resolved.equals(etc)) return FIXTURE_ETC_9F5F0C94;
      if (resolved.equals(config)) return FIXTURE_CONFIG_48882AB4;
      if (resolved.equals(runtime)) return FIXTURE_RUNTIME_2D52CD90;
      if (resolved.equals(app)) return FIXTURE_APP_4E5EF144;
      if (resolved.equals(maintenance)) return FIXTURE_MAINTENANCE_9CE8617E;
      return resolved.startsWith(config) ? FIXTURE_STATIC_0105CCA0 : "runfile";
    }

    boolean selected(Path held) throws IOException {
      return badRole.equals(role(held));
    }

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      point(FIXTURE_ATTRIBUTES_D300E055);
      String role = role(held);
      if (invalid.equals("nullAttributes") && selected(held)) return null;
      var values = new HashMap<>(nativeIo.attributes(held));
      int permission =
          switch (role) {
            case FIXTURE_ETC_9F5F0C94, FIXTURE_RUNTIME_2D52CD90, FIXTURE_APP_4E5EF144 -> 0755;
            case FIXTURE_CONFIG_48882AB4 -> 0750;
            case FIXTURE_MAINTENANCE_9CE8617E -> 0700;
            case FIXTURE_STATIC_0105CCA0 -> 0640;
            default -> 0600;
          };
      int type = (Integer) values.get(FIXTURE_MODE_B6D5C2C3) & 0170000;
      values.put(FIXTURE_MODE_B6D5C2C3, type | permission);
      values.put("uid", 0);
      values.put(
          "gid",
          role.equals(FIXTURE_CONFIG_48882AB4) || role.equals(FIXTURE_STATIC_0105CCA0) ? 2000 : 0);
      values.put(
          "dev",
          role.equals(FIXTURE_ETC_9F5F0C94)
                  || role.equals(FIXTURE_CONFIG_48882AB4)
                  || role.equals(FIXTURE_STATIC_0105CCA0)
              ? 10L
              : 20L);
      change.accept(role, values);
      return values;
    }

    @Override
    public String filesystem(Path held) throws IOException {
      point(FIXTURE_FILESYSTEM_909B3E41);
      assertNotNull(nativeIo.filesystem(held));
      if (selected(held)) {
        if (invalid.equals("nullFilesystem")) return null;
        if (invalid.equals(FIXTURE_FILESYSTEM_909B3E41)) return "nfs";
      }
      String role = role(held);
      return Set.of(FIXTURE_ETC_9F5F0C94, FIXTURE_CONFIG_48882AB4, FIXTURE_STATIC_0105CCA0)
              .contains(role)
          ? "ext4"
          : "tmpfs";
    }

    @Override
    public byte[] accessAcl(Path held, int max) throws StorageIoException {
      point(FIXTURE_ACL_43B23946);
      assertEquals(44, max);
      try {
        if (selected(held)) {
          if (invalid.equals("nullAcl")) return null;
          if (invalid.equals(FIXTURE_ACL_43B23946)) return new byte[] {2, 0, 0, 0};
        }
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      return new byte[0];
    }

    @Override
    public boolean readOnlyFilesystem(Path held) throws StorageIoException {
      point(FIXTURE_READONLY_C4A495E7);
      try {
        return (selected(held) && invalid.equals(FIXTURE_READONLY_C4A495E7))
            || (staticReadonly
                && Set.of(FIXTURE_ETC_9F5F0C94, FIXTURE_CONFIG_48882AB4, FIXTURE_STATIC_0105CCA0)
                    .contains(role(held)));
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      point("openRead");
      var channel = nativeIo.open(held);
      readers++;
      return new SeekableByteChannel() {
        @Override
        public int read(ByteBuffer bytes) throws IOException {
          point("read");
          return channel.read(bytes);
        }

        @Override
        public long size() throws IOException {
          point("readSize");
          return channel.size();
        }

        @Override
        public void close() throws IOException {
          channel.close();
          readers--;
          point("readClose");
        }

        @Override
        public boolean isOpen() {
          return channel.isOpen();
        }

        @Override
        public int write(ByteBuffer bytes) {
          throw new AssertionError(FIXTURE_READONLY_C4A495E7);
        }

        @Override
        public long position() {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel position(long value) {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel truncate(long value) {
          throw new AssertionError("no truncate");
        }
      };
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path held) throws IOException {
      point("openWriter");
      var writer = nativeIo.openWriter(held);
      writers++;
      return new InspectorEnvironmentPublisher.Writer() {
        @Override
        public int write(ByteBuffer bytes) throws IOException {
          point("write");
          return writer.write(bytes);
        }

        @Override
        public long size() throws IOException {
          point("writeSize");
          return writer.size();
        }

        @Override
        public void force() throws IOException {
          point("force");
          writer.force();
        }

        @Override
        public void close() throws IOException {
          writer.close();
          writers--;
          point("writerClose");
        }
      };
    }

    void released() {
      assertTrue(live.isEmpty());
      assertEquals(0, readers);
      assertEquals(0, writers);
    }

    @Override
    public void close() {
      released();
    }
  }
}
