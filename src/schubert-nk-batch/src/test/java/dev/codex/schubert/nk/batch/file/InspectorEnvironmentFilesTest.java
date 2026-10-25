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
          "complete",
          f.files.executeOwned(
              RUN,
              retirement -> {
                var denied =
                    executor.submit(
                        () -> assertThrows(StorageIoException.class, retirement::retire));
                assertNotNull(assertDoesNotThrow(() -> denied.get(5, TimeUnit.SECONDS)));
                assertEquals(RUNTIME, Files.readString(f.target));
                assertEquals(0, f.count("unlink"));
                retirement.retire();
                assertFalse(Files.exists(f.target));
                return "complete";
              }));
      assertEquals(1, f.count("unlink"));
      f.released();
    }
  }

  @Test
  void nativeOwnedRetirementOccursBeforeCallbackIntentAndCannotEscape() throws Exception {
    InspectorEnvironmentFiles.Retirement[] saved = {null};
    try (var f = fixture()) {
      assertEquals(
          "complete",
          f.files.executeOwned(
              RUN,
              retirement -> {
                assertEquals(RUNTIME, Files.readString(f.target));
                saved[0] = retirement;
                retirement.retire();
                assertFalse(
                    Files.exists(f.target)); // The caller's intent may only be retired after this.
                assertThrows(StorageIoException.class, retirement::retire);
                return "complete";
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
      assertEquals(3, f.count("group"));
      assertFalse(Files.exists(f.target));
      assertEquals(CONFIG, Files.readString(f.staticFile));
      assertFalse(Files.exists(f.maintenance.resolve(RUN.id() + ".part")));
      f.released();
    }
    try (var f = fixture()) {
      Files.writeString(f.target, RUNTIME);
      assertEquals(7, (int) f.files.execute(RUN, () -> 7));
      assertEquals(0, f.count("create"));
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

                              closes[0] = f.count("close");
                              f.on(
                                  "close",
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
            assertEquals(closes[0] + 5, f.count("close"));
            assertEquals(RUNTIME, Files.readString(f.target));
            assertEquals(CONFIG, Files.readString(f.staticFile));
            assertEquals(0, f.count("unlink"));
            f.released();
          }
        }
    }
    for (String mode : List.of("io", "runtime", "null"))
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
                      if (mode.equals("runtime")) throw expected;
                      return null;
                    });
        if (mode.equals("io")) failure(operation);
        else if (mode.equals("runtime"))
          assertSame(expected, assertThrows(IllegalStateException.class, operation));
        else assertThrows(NullPointerException.class, operation);
        assertEquals(1, f.callbacks);
        assertEquals(RUNTIME, Files.readString(f.target));
        assertEquals(0, f.count("unlink"));
        f.released();
      }
  }

  @Test
  void namespaceAndStaticIdentity() throws Exception {
    for (int at : List.of(2, 3))
      for (String role : List.of("etc", "config", "runtime", "app", "maintenance", "static"))
        try (var f = fixture()) {
          f.on("group", at, () -> f.replace(role));
          failure(() -> f.files.execute(RUN, f::callback));
          assertEquals(at == 2 ? 0 : 1, f.callbacks);
          assertEquals(0, f.count("unlink"));
          f.released();
        }
    for (int at : List.of(2, 3))
      try (var f = fixture()) {
        f.on("group", at, () -> f.group = 2001);
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(at == 2 ? 0 : 1, f.callbacks);
        assertEquals(RUNTIME, Files.readString(f.target));
      }
    for (int at : List.of(2, 3))
      try (var f = fixture()) {
        f.on("group", at, () -> Files.writeString(f.staticFile, CONFIG.replace("v1,v2", "v3,v4")));
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(at == 2 ? 0 : 1, f.callbacks);
        assertEquals(CONFIG.replace("v1,v2", "v3,v4"), Files.readString(f.staticFile));
      }
    try (var f = fixture()) {
      f.on("attributes", 7, () -> f.replace("static"));
      failure(() -> f.files.execute(RUN, f::callback));
      assertEquals(0, f.callbacks);
      assertEquals(0, f.count("create"));
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
    for (String role : List.of("etc", "config", "runtime", "app", "maintenance", "static")) {
      for (String key :
          List.of("mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime"))
        for (Object invalid : Arrays.asList(null, "wrong type"))
          try (var f = fixture()) {
            f.change =
                (observed, values) -> {
                  if (role.equals(observed)) values.put(key, invalid);
                };
            failure(() -> f.files.execute(RUN, f::callback));
            assertEquals(0, f.callbacks);
            assertEquals(0, f.count("create"));
          }
      for (String key : List.of("mode", "uid", "gid", "nlink", "size"))
        try (var f = fixture()) {
          f.change =
              (observed, values) -> {
                if (role.equals(observed))
                  values.put(
                      key,
                      key.equals("size")
                          ? (Object) (-1L)
                          : key.equals("nlink") && !role.equals("static") ? 1 : 99);
              };
          failure(() -> f.files.execute(RUN, f::callback));
          assertEquals(0, f.callbacks);
          assertEquals(0, f.count("create"));
        }
      for (String wrong :
          List.of("nullAttributes", "nullFilesystem", "filesystem", "nullAcl", "acl"))
        try (var f = fixture()) {
          f.badRole = role;
          f.invalid = wrong;
          failure(() -> f.files.execute(RUN, f::callback));
          assertEquals(0, f.callbacks);
        }
    }
    for (String role : List.of("config", "app", "maintenance", "static"))
      try (var f = fixture()) {
        f.change =
            (observed, values) -> {
              if (role.equals(observed)) values.put("dev", 99L);
            };
        failure(() -> f.files.execute(RUN, f::callback));
        assertEquals(0, f.callbacks);
      }
    for (String role : List.of("runtime", "app", "maintenance"))
      try (var f = fixture()) {
        f.badRole = role;
        f.invalid = "readonly";
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
              Map.entry("group", 3),
              Map.entry("openRoot", 6),
              Map.entry("openDirectory", directoryOpens),
              Map.entry("openEntry", 26),
              Map.entry("create", 1),
              Map.entry("close", 6 + directoryOpens + 26),
              Map.entry("publish", 1),
              Map.entry("unlink", 1),
              Map.entry("sync", 2),
              Map.entry("attributes", 70),
              Map.entry("acl", 70),
              Map.entry("filesystem", 70),
              Map.entry("readonly", 70),
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
        f.on("group", position, () -> Thread.currentThread().interrupt());
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
      f.on("close", 6 + directoryOpens + 26, () -> Thread.currentThread().interrupt());
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
                    f.fail = "attributes";
                    f.failAt = f.count("attributes") + 1;
                    return 1;
                  }));
      assertEquals(1, f.callbacks);
      assertEquals(0, f.count("unlink"));
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
      assertEquals(0, f.count("unlink"));
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
      assertEquals(32, f.count("create"));
      assertEquals(32, f.count("unlink"));
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
      etc = base.resolve("etc");
      config = etc.resolve("schubert-nk");
      runtime = base.resolve("run");
      app = runtime.resolve("schubert-nk");
      maintenance = app.resolve("maintenance");
      staticFile = config.resolve(NAME);
      target = maintenance.resolve(NAME);
      Files.createDirectories(config);
      Files.createDirectories(maintenance);
      Files.writeString(staticFile, CONFIG);
      for (String role : List.of("etc", "config", "runtime", "app", "maintenance", "static"))
        originalRoles.put((Long) Files.getAttribute(path(role), "unix:ino"), role);
      DirectoryCalls delegate = LinuxDirectoryCalls.create();
      calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    String point = name.equals("createPrivateFile") ? "create" : name;
                    if (!name.equals("close")) point(point);
                    Object value;
                    try {
                      value = method.invoke(delegate, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (Set.of("openRoot", "openDirectory", "openEntry", "createPrivateFile")
                        .contains(name)) assertTrue(live.add((Integer) value));
                    if (name.equals("close")) {
                      assertTrue(live.remove((Integer) args[0]));
                      point("close");
                      if (rawCloses)
                        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                    }
                    return value;
                  });
      files = new InspectorEnvironmentFiles(etc, runtime, calls, this, this::group, this);
    }

    Path path(String role) {
      return switch (role) {
        case "etc" -> etc;
        case "config" -> config;
        case "runtime" -> runtime;
        case "app" -> app;
        case "maintenance" -> maintenance;
        case "static" -> staticFile;
        default -> throw new AssertionError(role);
      };
    }

    int callback() throws IOException {
      callbacks++;
      assertEquals(RUNTIME, Files.readString(target));
      return 1;
    }

    long group() throws IOException {
      point("group");
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
      if (role.equals("static")) Files.writeString(staticFile, CONFIG);
      else if (role.equals("etc") || role.equals("config")) {
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
      if (resolved.equals(etc)) return "etc";
      if (resolved.equals(config)) return "config";
      if (resolved.equals(runtime)) return "runtime";
      if (resolved.equals(app)) return "app";
      if (resolved.equals(maintenance)) return "maintenance";
      return resolved.startsWith(config) ? "static" : "runfile";
    }

    boolean selected(Path held) throws IOException {
      return badRole.equals(role(held));
    }

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      point("attributes");
      String role = role(held);
      if (invalid.equals("nullAttributes") && selected(held)) return null;
      var values = new HashMap<>(nativeIo.attributes(held));
      int permission =
          switch (role) {
            case "etc", "runtime", "app" -> 0755;
            case "config" -> 0750;
            case "maintenance" -> 0700;
            case "static" -> 0640;
            default -> 0600;
          };
      int type = (Integer) values.get("mode") & 0170000;
      values.put("mode", type | permission);
      values.put("uid", 0);
      values.put("gid", role.equals("config") || role.equals("static") ? 2000 : 0);
      values.put(
          "dev", role.equals("etc") || role.equals("config") || role.equals("static") ? 10L : 20L);
      change.accept(role, values);
      return values;
    }

    @Override
    public String filesystem(Path held) throws IOException {
      point("filesystem");
      assertNotNull(nativeIo.filesystem(held));
      if (selected(held)) {
        if (invalid.equals("nullFilesystem")) return null;
        if (invalid.equals("filesystem")) return "nfs";
      }
      String role = role(held);
      return Set.of("etc", "config", "static").contains(role) ? "ext4" : "tmpfs";
    }

    @Override
    public byte[] accessAcl(Path held, int max) throws StorageIoException {
      point("acl");
      assertEquals(44, max);
      try {
        if (selected(held)) {
          if (invalid.equals("nullAcl")) return null;
          if (invalid.equals("acl")) return new byte[] {2, 0, 0, 0};
        }
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      return new byte[0];
    }

    @Override
    public boolean readOnlyFilesystem(Path held) throws StorageIoException {
      point("readonly");
      try {
        return (selected(held) && invalid.equals("readonly"))
            || (staticReadonly && Set.of("etc", "config", "static").contains(role(held)));
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
          throw new AssertionError("readonly");
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
