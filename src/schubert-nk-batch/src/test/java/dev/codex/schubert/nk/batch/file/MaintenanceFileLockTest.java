package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxFileLock;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiFunction;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * NK-OPS-001/PT-OPS-LOCK-001..008; SS311/341/343; synthetic root metadata, real held inode/flock.
 */
final class MaintenanceFileLockTest {
  private static final String FIXTURE_RUN_5E87F618 = "run";
  private static final String FIXTURE_APP_4E5EF144 = "app";
  private static final String FIXTURE_FILE_BFDDE6F5 = "file";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  private static final String FIXTURE_INO_4BE7C1E0 = "ino";
  private static final String FIXTURE_UNIX_MODE_18F40B0C = "unix:mode";
  private static final String FIXTURE_ACL_43B23946 = "acl";
  @TempDir Path base;

  @Test
  void admittedRealLock() throws Exception {
    var f = fixture();
    assertEquals(
        Optional.of(17),
        f.lock()
            .tryExclusive(
                () -> {
                  assertEquals(20, assertDoesNotThrow(() -> external(f.file)));
                  return 17;
                }));
    assertEquals(0, external(f.file));
    assertEquals(Optional.of(18), f.lock().tryExclusive(() -> 18));
    assertEquals(0, Files.size(f.file));
    assertEquals(0, f.calls.outstanding.get());
    assertTrue(f.calls.opened.get() > 0);
  }

  @Test
  void contentionAndIndependentInvocations() throws Exception {
    var f = fixture();
    var adapter = f.lock();
    var barrier = new CyclicBarrier(32);
    var rejected = new CountDownLatch(31);
    var callbacks = new AtomicInteger();
    try (var pool = Executors.newFixedThreadPool(32)) {
      var tasks = new ArrayList<Callable<Optional<Integer>>>();
      for (int i = 0; i < 32; i++)
        tasks.add(
            () -> {
              barrier.await(10, TimeUnit.SECONDS);
              var result =
                  adapter.tryExclusive(
                      () -> {
                        callbacks.incrementAndGet();
                        assertTrue(assertDoesNotThrow(() -> rejected.await(10, TimeUnit.SECONDS)));
                        assertEquals(20, assertDoesNotThrow(() -> external(f.file)));
                        return 1;
                      });
              if (result.isEmpty()) rejected.countDown();
              return result;
            });
      int winners = 0;
      for (var done : pool.invokeAll(tasks))
        if (done.get(10, TimeUnit.SECONDS).isPresent()) winners++;
      assertEquals(1, winners);
    }
    assertEquals(1, callbacks.get());
    assertEquals(0, f.calls.outstanding.get());
    assertEquals(Optional.of(2), adapter.tryExclusive(() -> 2));
    try (var pool = Executors.newSingleThreadExecutor()) {
      var child =
          new ProcessBuilder(
                  "/usr/bin/flock",
                  "-x",
                  "-n",
                  "-E",
                  "20",
                  f.file.toString(),
                  "/bin/sh",
                  "-c",
                  "printf 'READY\\n'; read -r ignored || :")
              .start();
      try (var reader = child.inputReader();
          var writer = child.getOutputStream()) {
        try {
          assertEquals("READY", pool.submit(reader::readLine).get(5, TimeUnit.SECONDS));
          assertEquals(Optional.empty(), adapter.tryExclusive(callbacks::incrementAndGet));
          assertEquals(1, callbacks.get());
          writer.write('\n');
          writer.flush();
          assertTrue(child.waitFor(5, TimeUnit.SECONDS));
          assertEquals(0, child.exitValue());
        } finally {
          if (child.isAlive()) child.destroy();
        }
      }
    }
    assertEquals(Optional.of(3), adapter.tryExclusive(() -> 3));
    assertEquals(0, f.calls.outstanding.get());
  }

  @Test
  void rootAndFilesystemPolicy() throws Exception {
    for (long uid : List.of(1L, 1000L, -1L, 4294967295L)) {
      var f = fixture();
      f.uid = uid;
      rejected(f);
      assertEquals(0, f.calls.opened.get());
    }
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144, FIXTURE_FILE_BFDDE6F5)) {
      for (String key : List.of("uid", "gid"))
        for (int value : List.of(1, -1)) {
          var f = fixture();
          f.change = replace(role, key, value);
          rejected(f);
        }
      for (String type : Arrays.asList("nfs", "cifs", "overlay", "", null)) {
        var f = fixture();
        f.badRole = role;
        f.type = type;
        rejected(f);
      }
      var readonly = fixture();
      readonly.badRole = role;
      readonly.readOnly = true;
      rejected(readonly);
      var acl = fixture();
      acl.badRole = role;
      acl.acl = new byte[] {2, 0, 0, 0};
      rejected(acl);
    }
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144)) {
      for (int mode : List.of(040777, 040775, 040700, 0140755, 044755)) {
        var f = fixture();
        f.change = replace(role, FIXTURE_MODE_B6D5C2C3, mode);
        rejected(f);
      }
      for (int links : List.of(0, 1, -1)) {
        var f = fixture();
        f.change = replace(role, "nlink", links);
        rejected(f);
      }
      var f = fixture();
      f.change = replace(role, FIXTURE_SIZE_EB1E91E4, -1L);
      rejected(f);
    }
    for (String role : List.of(FIXTURE_APP_4E5EF144, FIXTURE_FILE_BFDDE6F5)) {
      var f = fixture();
      f.change = replace(role, "dev", Long.MAX_VALUE);
      rejected(f);
    }
  }

  @Test
  void inodeAndAttributePolicy() throws Exception {
    for (int mode : List.of(0100644, 0100400, 040600, 0120600, 0140600)) {
      var f = fixture();
      f.change = replace(FIXTURE_FILE_BFDDE6F5, FIXTURE_MODE_B6D5C2C3, mode);
      rejected(f);
    }
    for (int links : List.of(0, 2, -1)) {
      var f = fixture();
      f.change = replace(FIXTURE_FILE_BFDDE6F5, "nlink", links);
      rejected(f);
    }
    for (long size : List.of(-1L, 1L, Long.MAX_VALUE)) {
      var f = fixture();
      f.change = replace(FIXTURE_FILE_BFDDE6F5, FIXTURE_SIZE_EB1E91E4, size);
      rejected(f);
    }
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144, FIXTURE_FILE_BFDDE6F5)) {
      var absent = fixture();
      absent.change = (r, m) -> r.equals(role) ? null : m;
      rejected(absent);
      for (String key :
          List.of(
              FIXTURE_MODE_B6D5C2C3,
              "uid",
              "gid",
              "nlink",
              FIXTURE_SIZE_EB1E91E4,
              "dev",
              FIXTURE_INO_4BE7C1E0)) {
        for (Object value : Arrays.asList(null, "unknown")) {
          var f = fixture();
          f.change = replace(role, key, value);
          rejected(f);
        }
      }
    }
    for (String kind : List.of("symlink", "directory", "hardlink", "nonempty", "missing")) {
      var f = fixture();
      if (kind.equals("nonempty")) Files.write(f.file, new byte[] {1});
      else if (kind.equals("hardlink")) Files.createLink(f.app.resolve("alias"), f.file);
      else {
        Files.move(f.file, f.app.resolve("saved"));
        if (kind.equals("symlink")) Files.createSymbolicLink(f.file, Path.of("saved"));
        if (kind.equals("directory")) Files.createDirectory(f.file);
      }
      rejected(f);
    }
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144)) {
      var f = fixture();
      Path original = role.equals(FIXTURE_RUN_5E87F618) ? f.runtime : f.app;
      Path saved = original.resolveSibling(original.getFileName() + "-saved");
      Files.move(original, saved);
      Files.createSymbolicLink(original, saved);
      rejected(f);
    }
  }

  @Test
  void replacementAndPostconditions() throws Exception {
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144, FIXTURE_FILE_BFDDE6F5)) {
      var f = fixture();
      assertUnavailable(
          assertThrows(
              StorageIoException.class,
              () ->
                  f.lock()
                      .tryExclusive(
                          () -> {
                            Path path =
                                role.equals(FIXTURE_RUN_5E87F618)
                                    ? f.runtime
                                    : role.equals(FIXTURE_APP_4E5EF144) ? f.app : f.file;
                            Files.move(path, path.resolveSibling(path.getFileName() + "-saved"));
                            if (role.equals(FIXTURE_FILE_BFDDE6F5)) {
                              Files.createFile(path);
                              Files.setAttribute(path, FIXTURE_UNIX_MODE_18F40B0C, 0600);
                            } else {
                              Files.createDirectory(path);
                              Files.setAttribute(path, FIXTURE_UNIX_MODE_18F40B0C, 0755);
                            }
                            return 1;
                          })));
      assertEquals(0, f.calls.outstanding.get());
    }
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144, FIXTURE_FILE_BFDDE6F5))
      for (String change : List.of(FIXTURE_MODE_B6D5C2C3, FIXTURE_ACL_43B23946, "identity")) {
        var f = fixture();
        assertUnavailable(
            assertThrows(
                StorageIoException.class,
                () ->
                    f.lock()
                        .tryExclusive(
                            () -> {
                              if (change.equals(FIXTURE_ACL_43B23946)) {
                                f.badRole = role;
                                f.acl = new byte[] {1};
                              } else
                                f.change =
                                    replace(
                                        role,
                                        change.equals(FIXTURE_MODE_B6D5C2C3)
                                            ? FIXTURE_MODE_B6D5C2C3
                                            : FIXTURE_INO_4BE7C1E0,
                                        change.equals(FIXTURE_MODE_B6D5C2C3)
                                            ? (Object) Integer.valueOf(0777)
                                            : Long.valueOf(Long.MAX_VALUE));
                              return 1;
                            })));
        assertEquals(0, f.calls.outstanding.get());
        assertEquals(0, external(f.file));
      }
    // Changing identity during initial capture must fail the pre-callback re-open comparison.
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144, FIXTURE_FILE_BFDDE6F5)) {
      var f = fixture();
      var reads = new AtomicInteger();
      f.change =
          (r, m) -> {
            if (r.equals(role) && reads.incrementAndGet() > 1)
              m.put(FIXTURE_INO_4BE7C1E0, Long.MAX_VALUE);
            return m;
          };
      rejected(f);
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
  void ioAndCloseFailures() throws Exception {

    // PG172/SSC063, BUG195/YKT154; close offsets independently follow reverse acquisition.
    for (int position = 1; position <= 2; position++) {
      int offset = position + 1;
      for (boolean known : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("synthetic compound"),
                new NullPointerException("synthetic compound"),
                new AssertionError("synthetic compound"))) {
          var f = fixture();
          int[] closes = {0};
          int[] injected = {0};
          int[] callbacks = {0};

          Throwable actual =
              assertThrows(
                  unknown.getClass(),
                  () ->
                      f.lock()
                          .tryExclusive(
                              () -> {
                                callbacks[0]++;

                                closes[0] = f.calls.closed.get();
                                f.calls.afterClose =
                                    count -> {
                                      if (count == closes[0] + offset) {
                                        injected[0]++;
                                        throwCompound(unknown);
                                      }
                                    };
                                if (known) throw new IOException("synthetic primary");
                                throwCompound(unknown);
                                return true;
                              }));
          assertCompound(unknown, actual, known);
          assertEquals(1, injected[0]);
          assertEquals(1, callbacks[0]);
          assertEquals(closes[0] + 3, f.calls.closed.get());
          assertEquals(0, f.calls.outstanding.get());
          assertEquals(0, external(f.file));
          assertEquals(0L, Files.size(f.file));
        }
    }
    var baseline = fixture();
    assertEquals(Optional.of(1), baseline.lock().tryExclusive(() -> 1));
    int opens = 3 * (baseline.runtime.getNameCount() + 3);
    assertEquals(opens, baseline.calls.opened.get());
    for (int position = 1; position <= opens; position++) {
      var f = fixture();
      f.calls.openFailure = position;
      assertUnavailable(
          assertThrows(StorageIoException.class, () -> f.lock().tryExclusive(() -> 1)));
      assertEquals(0, f.calls.outstanding.get());
      assertEquals(0, external(f.file));
      var g = fixture();
      g.calls.closeFailure = position;
      assertUnavailable(
          assertThrows(StorageIoException.class, () -> g.lock().tryExclusive(() -> 1)));
      assertEquals(0, g.calls.outstanding.get());
      assertEquals(0, external(g.file));
    }
    for (String role : List.of(FIXTURE_RUN_5E87F618, FIXTURE_APP_4E5EF144, FIXTURE_FILE_BFDDE6F5))
      for (String fault : List.of("attrs", "type", "readonly", FIXTURE_ACL_43B23946)) {
        var f = fixture();
        f.badRole = role;
        f.fault = fault;
        rejected(f);
      }
    var f = fixture();
    assertUnavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                f.lock()
                    .tryExclusive(
                        () -> {
                          throw new IOException("SECRET_CANARY");
                        })));
    var runtime = new IllegalStateException("programming failure");
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () ->
                f.lock()
                    .tryExclusive(
                        () -> {
                          throw runtime;
                        })));
    assertThrows(NullPointerException.class, () -> f.lock().tryExclusive(() -> null));
    assertEquals(0, f.calls.outstanding.get());
    assertEquals(0, external(f.file));
    assertEquals(Optional.of(5), f.lock().tryExclusive(() -> 5));
  }

  @Test
  void constructorAndNativeBoundary() throws Exception {
    var repo = Path.of(System.getProperty("nk.pt.repository"));
    var source =
        Files.readString(
            repo.resolve(
                "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MaintenanceFileLock.java"));
    assertTrue(source.contains("Path.of(\"/run\")"));
    assertFalse(source.contains("public MaintenanceFileLock("));
    assertEquals(1, source.split("@SuppressFBWarnings", -1).length - 1);
    assertTrue(source.contains("value = \"DMI_HARDCODED_ABSOLUTE_FILENAME\""));
    assertTrue(source.contains("matchType = SuppressMatchType.EXACT"));
    var pom = Files.readString(repo.resolve("src/schubert-nk-batch/pom.xml"));
    assertTrue(
        pom.contains(
            "<artifactId>spotbugs-annotations</artifactId>\n      <version>4.10.4</version>\n      <scope>provided</scope>"));
    var f = fixture();
    var nativeLock = LinuxFileLock.create();
    var security = f.security();
    var io = f.io();
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceFileLock(null, f.calls, security, nativeLock, io));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceFileLock(f.runtime, null, security, nativeLock, io));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceFileLock(f.runtime, f.calls, null, nativeLock, io));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceFileLock(f.runtime, f.calls, security, null, io));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceFileLock(f.runtime, f.calls, security, nativeLock, null));
    for (Path path : List.of(Path.of(FIXTURE_RUN_5E87F618), Path.of("/"), Path.of("/run/../run")))
      assertThrows(
          IllegalArgumentException.class,
          () -> new MaintenanceFileLock(path, f.calls, security, nativeLock, io));
    assertThrows(NullPointerException.class, () -> f.lock().tryExclusive(null));
    assertEquals(0, f.calls.opened.get());
    assertNotEquals(
        0, LinuxInodeSecurity.create().effectiveUid(), "PT environment must be unprivileged");
    assertUnavailable(
        assertThrows(
            StorageIoException.class, () -> MaintenanceFileLock.create().tryExclusive(() -> 1)));
    var real = new MaintenanceFileLock.NioIo();
    assertEquals(0L, real.attributes(f.file).get(FIXTURE_SIZE_EB1E91E4));
    assertEquals(0100600, real.attributes(f.file).get(FIXTURE_MODE_B6D5C2C3));
    assertEquals("tmpfs", real.filesystemType(Path.of("/dev/shm")));
    assertEquals("sysfs", real.filesystemType(Path.of("/sys")));
    // BUG-141: native adapter oracle is independent kernel mount metadata, not a container default.
    var mounts = Files.readAllLines(Path.of("/proc/mounts"));
    for (String mount : List.of("/dev/shm", "/sys")) {
      var entries = mounts.stream().map(s -> s.split(" ")).filter(s -> s[1].equals(mount)).toList();
      assertEquals(1, entries.size());
      var options = Set.of(entries.getFirst()[3].split(","));
      assertTrue(options.contains("ro") ^ options.contains("rw"));
      try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), Path.of(mount))) {
        assertEquals(options.contains("ro"), held.atDirectory(real::readOnly));
      }
    }
  }

  @Test
  void fixedProvisioningContract() throws Exception {
    var repo = Path.of(System.getProperty("nk.pt.repository"));
    var lines =
        Files.readAllLines(repo.resolve("src/deployment/tmpfiles/schubert-nk-maintenance.conf"));
    assertEquals(
        List.of(
            "d! /run/schubert-nk 0755 root root -",
            "d! /run/schubert-nk/maintenance 0700 root root -",
            "d! /run/schubert-nk/startup 0700 root root -",
            "d! /run/schubert-nk/backup-request 0700 root root -",
            "d! /run/schubert-nk/cleanup-request 0700 root root -",
            "d! /run/schubert-nk/expiry-request 0700 root root -",
            "f! /run/schubert-nk/maintenance.lock 0600 root root -",
            "f! /run/schubert-nk/startup-admission.lock 0600 root root -"),
        lines.stream().filter(s -> !s.isBlank() && !s.startsWith("#")).toList());
    var f = fixture();
    assertEquals(Optional.of(1), f.lock().tryExclusive(() -> 1));
    // Probe mutation methods throw, so any create/chmod/delete repair would fail this test.
    assertEquals(0, Files.size(f.file));
    assertEquals(0100600, Files.getAttribute(f.file, FIXTURE_UNIX_MODE_18F40B0C));
  }

  /** SSC109/BUG327, PT-OPS-MNAMESPACE001: independent private/host mount flags. */
  @Test
  void dualViewKeepsMutationWritableAndHostIdentity() throws Exception {
    for (String condition : List.of("shared-ro", "host-ro", "app-ro", "file-ro", "drift")) {
      var f = fixture();
      var host = new Calls();
      var delegate = f.io();
      var io =
          new MaintenanceFileLock.Io() {
            boolean isHost(Path held) {
              return host.held.contains(Integer.parseInt(held.getFileName().toString()));
            }

            public Map<String, Object> attributes(Path held) throws IOException {
              var result = delegate.attributes(held);
              if (condition.equals("drift") && isHost(held))
                result.put(FIXTURE_INO_4BE7C1E0, Long.MAX_VALUE);
              return result;
            }

            public String filesystemType(Path held) throws IOException {
              return delegate.filesystemType(held);
            }

            public boolean readOnly(Path held) throws IOException {
              if (isHost(held)) return condition.equals("host-ro");
              String role = f.role(held);
              return role.equals(FIXTURE_RUN_5E87F618) || condition.equals(role + "-ro");
            }
          };
      var adapter =
          new MaintenanceFileLock(
              f.runtime, f.calls, f.security(), LinuxFileLock.create(), io, Optional.of(host));
      var invoked = new AtomicInteger();
      if (condition.equals("shared-ro")) {
        assertEquals(Optional.of(1), adapter.tryExclusive(invoked::incrementAndGet));
        assertEquals(1, invoked.get());
      } else {
        assertUnavailable(
            assertThrows(
                StorageIoException.class, () -> adapter.tryExclusive(invoked::incrementAndGet)));
        assertEquals(0, invoked.get());
      }
      assertEquals(0, host.outstanding.get());
      assertEquals(0, f.calls.outstanding.get());
      assertEquals(0, external(f.file));
    }
  }

  private Fixture fixture() throws IOException {
    return new Fixture(Files.createTempDirectory(base, "runtime-"));
  }

  private static BiFunction<String, Map<String, Object>, Map<String, Object>> replace(
      String role, String key, Object value) {
    return (r, m) -> {
      if (r.equals(role)) m.put(key, value);
      return m;
    };
  }

  private static void rejected(Fixture f) {
    var calls = new AtomicInteger();
    assertUnavailable(
        assertThrows(
            StorageIoException.class, () -> f.lock().tryExclusive(calls::incrementAndGet)));
    assertEquals(0, calls.get());
    assertEquals(0, f.calls.outstanding.get());
  }

  private static void assertUnavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static int external(Path file) throws Exception {
    var child =
        new ProcessBuilder("/usr/bin/flock", "-x", "-n", "-E", "20", file.toString(), "/bin/true")
            .start();
    try {
      assertTrue(child.waitFor(5, TimeUnit.SECONDS));
      return child.exitValue();
    } finally {
      if (child.isAlive()) child.destroy();
    }
  }

  private static final class Fixture {
    final Path runtime;
    final Path app;
    final Path file;
    final long runInode;
    final Calls calls = new Calls();
    long uid = 0;
    String badRole = "";
    String fault = "";
    String type = "tmpfs";
    boolean readOnly;
    byte[] acl = new byte[0];
    BiFunction<String, Map<String, Object>, Map<String, Object>> change = (r, m) -> m;

    Fixture(Path runtime) throws IOException {
      this.runtime = runtime;
      app = Files.createDirectory(runtime.resolve("schubert-nk"));
      file = Files.createFile(app.resolve("maintenance.lock"));
      Files.setAttribute(runtime, FIXTURE_UNIX_MODE_18F40B0C, 0755);
      Files.setAttribute(app, FIXTURE_UNIX_MODE_18F40B0C, 0755);
      Files.setAttribute(file, FIXTURE_UNIX_MODE_18F40B0C, 0600);
      runInode = (Long) Files.getAttribute(runtime, "unix:ino");
    }

    String role(Path held) throws IOException {
      var attrs = Files.readAttributes(held, "unix:mode,ino");
      if (((Integer) attrs.get(FIXTURE_MODE_B6D5C2C3) & 0170000) != 040000)
        return FIXTURE_FILE_BFDDE6F5;
      return attrs.get(FIXTURE_INO_4BE7C1E0).equals(runInode)
          ? FIXTURE_RUN_5E87F618
          : FIXTURE_APP_4E5EF144;
    }

    void fault(Path held, String operation) throws IOException {
      if (badRole.equals(role(held)) && fault.equals(operation))
        throw new IOException("SECRET_CANARY");
    }

    MaintenanceFileLock lock() {
      return new MaintenanceFileLock(runtime, calls, security(), LinuxFileLock.create(), io());
    }

    MaintenanceFileLock.Io io() {
      return new MaintenanceFileLock.Io() {
        @Override
        public Map<String, Object> attributes(Path held) throws IOException {
          fault(held, "attrs");
          var m = new HashMap<>(Files.readAttributes(held, "unix:mode,uid,gid,nlink,size,dev,ino"));
          m.put("uid", 0);
          m.put("gid", 0);
          return change.apply(role(held), m);
        }

        @Override
        public String filesystemType(Path held) throws IOException {
          fault(held, "type");
          return badRole.equals(role(held)) ? type : "tmpfs";
        }

        @Override
        public boolean readOnly(Path held) throws IOException {
          fault(held, "readonly");
          return badRole.equals(role(held)) && readOnly;
        }
      };
    }

    InodeSecurityCalls security() {
      return new InodeSecurityCalls() {
        @Override
        public long effectiveUid() {
          return uid;
        }

        @Override
        public boolean readOnlyFilesystem(Path held) {
          throw new AssertionError("NIO owns FS metadata");
        }

        @Override
        public byte[] accessAcl(Path held, int maximum) throws StorageIoException {
          assertEquals(44, maximum);
          try {
            fault(held, FIXTURE_ACL_43B23946);
            return badRole.equals(role(held)) ? acl : new byte[0];
          } catch (IOException e) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }
      };
    }
  }

  private static final class Calls implements DirectoryCalls {
    final DirectoryCalls real = LinuxDirectoryCalls.create();
    final AtomicInteger opened = new AtomicInteger();
    final AtomicInteger closed = new AtomicInteger();
    final AtomicInteger outstanding = new AtomicInteger();
    int openFailure;
    int closeFailure;
    java.util.function.IntConsumer afterClose = count -> {};
    final Set<Integer> held = ConcurrentHashMap.newKeySet();

    private int open(Open action) throws StorageIoException {
      if (opened.incrementAndGet() == openFailure)
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      int fd = action.execute();
      held.add(fd);
      outstanding.incrementAndGet();
      return fd;
    }

    @Override
    public int openRoot() throws StorageIoException {
      return open(real::openRoot);
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      return open(() -> real.openDirectory(parent, name));
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      return open(() -> real.openEntry(parent, name));
    }

    @Override
    public void close(int fd) throws StorageIoException {
      real.close(fd);
      held.remove(fd);
      outstanding.decrementAndGet();
      int count = closed.incrementAndGet();
      afterClose.accept(count);
      if (count == closeFailure)
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }

    @Override
    public int createFile(int parent, String name) {
      throw new AssertionError("no create");
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw new AssertionError("no create");
    }

    @Override
    public void publish(int fd, String from, String to) {
      throw new AssertionError("no publish");
    }

    @Override
    public void unlink(int fd, String name) {
      throw new AssertionError("no unlink");
    }

    @Override
    public void sync(int fd) {
      throw new AssertionError("no write");
    }

    interface Open {
      int execute() throws StorageIoException;
    }
  }
}
