package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.IntConsumer;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent metadata matrices plus actual NOFOLLOW/flock; synthetic root/tmpfs admission. */
final class StartupAdmissionFileTest {
  private static final String FIXTURE_SERVICE_3E9B10A4 = "service";
  private static final String FIXTURE_FILE_BFDDE6F5 = "file";
  private static final String FIXTURE_INO_4BE7C1E0 = "ino";
  private static final String FIXTURE_DEV_8A17302D = "dev";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_OTHER_LOCK_7F80A9E4 = "other.lock";
  private static final String FIXTURE_UNIX_MODE_18F40B0C = "unix:mode";
  private static final String FIXTURE_NO_MUTATION_68019DA1 = "no mutation";
  @TempDir Path base;

  @Test
  void actualBorrowedAdmissionCarriesItsVerifiedFileIdentityNotAClaim() throws Exception {
    var f = fixture();
    long device = (Long) Files.getAttribute(f.file, "unix:dev");
    long inode = (Long) Files.getAttribute(f.file, "unix:ino");
    assertEquals(
        Optional.of(19),
        f.adapter()
            .tryExclusiveObserved(
                admission -> {
                  assertTrue(admission.descriptor() >= 128 && admission.descriptor() <= 65535);
                  assertEquals(device, admission.device());
                  assertEquals(inode, admission.inode());
                  assertTrue(f.owned.isEmpty());
                  assertEquals(20, assertDoesNotThrow(() -> external(f.file)));
                  return 19;
                }));
    assertEquals(0, external(f.file));
    assertTrue(f.owned.isEmpty());
    assertThrows(NullPointerException.class, () -> f.adapter().tryExclusiveObserved(null));
  }

  @Test
  void admissionLock001TwoViewsSameOfdAndReadonlyPrivate() throws Exception {
    var f = fixture();
    assertEquals(
        Optional.of(17),
        f.adapter()
            .tryExclusive(
                fd -> {
                  assertTrue(fd >= 128 && fd <= 65535);
                  assertTrue(
                      f.owned.isEmpty(),
                      "BUG-265: all observation FDs close before target callback");
                  assertEquals(20, assertDoesNotThrow(() -> external(f.file)));
                  assertEquals(0, f.privateReadonlyCalls.get());
                  return 17;
                }));
    assertEquals(0, external(f.file));
    assertEquals(0, f.owned.size());
    assertEquals(9, f.hostReadonlyCalls.get()); // host initial/before/after: three inodes each
    assertEquals(Optional.of(18), f.adapter().tryExclusive(fd -> 18));
  }

  @Test
  void admissionLock002ContentionAndCrossViewMismatch() throws Exception {
    var f = fixture();
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), f.app)) {
      directory.atExistingEntryHandle(
          "startup-admission.lock",
          held ->
              LinuxFileLock.create()
                  .tryExclusive(
                      held,
                      () -> {
                        assertEquals(Optional.empty(), f.adapter().tryExclusive(fd -> fail()));
                        return 1;
                      }));
    }
    assertEquals(0, f.owned.size());
    var different = fixture();
    different.separate = true;
    // Synthetic equal metadata cannot conceal two actual lock inodes: private OFD acquires.
    rejected(different);
    var mismatch = fixture();
    mismatch.change =
        (view, role, m) -> {
          if (view.equals(FIXTURE_SERVICE_3E9B10A4) && role.equals(FIXTURE_FILE_BFDDE6F5))
            m.put(FIXTURE_INO_4BE7C1E0, (Long) m.get(FIXTURE_INO_4BE7C1E0) + 1);
          return m;
        };
    rejected(mismatch);
    var device = fixture();
    device.change =
        (view, role, m) -> {
          if (role.equals(FIXTURE_FILE_BFDDE6F5))
            m.put(FIXTURE_DEV_8A17302D, (Long) m.get(FIXTURE_DEV_8A17302D) + 1);
          return m;
        };
    rejected(device);
    var app = fixture();
    app.change =
        (view, role, m) -> {
          if (role.equals("app"))
            m.put(FIXTURE_DEV_8A17302D, (Long) m.get(FIXTURE_DEV_8A17302D) + 1);
          return m;
        };
    rejected(app);
  }

  @Test
  void admissionLock003EveryTypedMetadataAndBoundaryRejected() throws Exception {
    for (String role : List.of("run", "app", FIXTURE_FILE_BFDDE6F5)) {
      for (String key :
          List.of(
              FIXTURE_MODE_B6D5C2C3,
              "uid",
              "gid",
              "nlink",
              "size",
              FIXTURE_DEV_8A17302D,
              FIXTURE_INO_4BE7C1E0)) {
        for (boolean missing : List.of(false, true)) {
          var f = fixture();
          f.change =
              (view, r, m) -> {
                if (r.equals(role)) {
                  if (missing) m.remove(key);
                  else m.put(key, "bad");
                }
                return m;
              };
          rejected(f);
        }
      }
      var absent = fixture();
      absent.change = (view, r, m) -> r.equals(role) ? null : m;
      rejected(absent);
      for (var entry :
          Map.<String, Object>of(
                  "uid",
                  1,
                  "gid",
                  1,
                  FIXTURE_MODE_B6D5C2C3,
                  0,
                  "nlink",
                  role.equals(FIXTURE_FILE_BFDDE6F5) ? 2 : 1,
                  "size",
                  role.equals(FIXTURE_FILE_BFDDE6F5) ? 1L : -1L)
              .entrySet()) {
        var f = fixture();
        f.change =
            (view, r, m) -> {
              if (r.equals(role)) m.put(entry.getKey(), entry.getValue());
              return m;
            };
        rejected(f);
      }
      for (String type : List.of("ext4", "proc", "")) {
        var f = fixture();
        f.type = type;
        rejected(f);
      }
      var noType = fixture();
      noType.type = null;
      rejected(noType);
      var acl = fixture();
      acl.acl = true;
      rejected(acl);
      var ro = fixture();
      ro.hostReadOnly = true;
      rejected(ro);
    }
    for (long uid : List.of(-1L, 1L, 1000L)) {
      var f = fixture();
      f.uid = uid;
      rejected(f);
      assertEquals(0, f.opened.get());
    }
  }

  @Test
  void admissionLock004PhysicalSymlinkReplacementAndNoRepair() throws Exception {
    var symbolic = fixture();
    Files.delete(symbolic.file);
    Files.createSymbolicLink(symbolic.file, Path.of(FIXTURE_OTHER_LOCK_7F80A9E4));
    rejected(symbolic);
    var replaced = fixture();
    Path old = replaced.app.resolve("old.lock");
    unavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                replaced
                    .adapter()
                    .tryExclusive(
                        fd -> {
                          Files.move(replaced.file, old);
                          Files.createFile(replaced.file);
                          Files.setAttribute(replaced.file, FIXTURE_UNIX_MODE_18F40B0C, 0600);
                          return 1;
                        })));
    assertEquals(0, external(old));
    assertEquals(0, replaced.owned.size());
    var directory = fixture();
    Files.delete(directory.file);
    Files.createDirectory(directory.file);
    rejected(directory);
    var linked = fixture();
    Files.createLink(linked.app.resolve("link.lock"), linked.file);
    rejected(linked);
    var absent = fixture();
    Files.delete(absent.file);
    rejected(absent);
    assertFalse(Files.exists(absent.file));
  }

  @Test
  void admissionLock005AllIoAndCloseFaultsReleaseEveryOwner() throws Exception {
    var baseline = fixture();
    int[] bodyOpen = {0};
    int[] bodyClose = {0};
    assertEquals(
        Optional.of(1),
        baseline
            .adapter()
            .tryExclusive(
                fd -> {
                  bodyOpen[0] = baseline.opened.get();
                  bodyClose[0] = baseline.closed.get();
                  assertTrue(baseline.owned.isEmpty());
                  return 1;
                }));
    int calls = baseline.opened.get();
    assertTrue(calls > 0);
    for (int position = 1; position <= calls; position++) {
      var opened = fixture();
      opened.openFailure = position;
      int[] openCallbacks = {0};
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> opened.adapter().tryExclusive(fd -> ++openCallbacks[0])));
      assertEquals(position <= bodyOpen[0] ? 0 : 1, openCallbacks[0]);
      assertTrue(opened.owned.isEmpty());
      var negative = fixture();
      negative.negativeResult = position;
      int[] negativeCallbacks = {0};
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> negative.adapter().tryExclusive(fd -> ++negativeCallbacks[0])));
      assertEquals(position <= bodyOpen[0] ? 0 : 1, negativeCallbacks[0]);
      assertTrue(negative.owned.isEmpty());
      var closed = fixture();
      closed.closeFailure = position;
      int[] closeCallbacks = {0};
      unavailable(
          assertThrows(
              StorageIoException.class,
              () -> closed.adapter().tryExclusive(fd -> ++closeCallbacks[0])));
      assertEquals(position <= bodyClose[0] ? 0 : 1, closeCallbacks[0]);
      assertTrue(closed.owned.isEmpty());
    }
    for (String fault : List.of("attrs", "type", "acl", "readonly")) {
      var f = fixture();
      f.fault = fault;
      rejected(f);
    }
    var known = fixture();
    unavailable(
        assertThrows(
            StorageIoException.class,
            () ->
                known
                    .adapter()
                    .tryExclusive(
                        fd -> {
                          throw new IOException("SECRET_CANARY");
                        })));
    assertTrue(known.owned.isEmpty());
    for (Throwable unknown :
        List.of(new IllegalStateException("synthetic"), new AssertionError("synthetic"))) {
      var f = fixture();
      assertSame(
          unknown,
          assertThrows(
              unknown.getClass(),
              () ->
                  f.adapter()
                      .tryExclusive(
                          fd -> {
                            raise(unknown);
                            return 1;
                          })));
      assertTrue(f.owned.isEmpty());
    }
    var empty = fixture();
    assertThrows(NullPointerException.class, () -> empty.adapter().tryExclusive(fd -> null));
    assertTrue(empty.owned.isEmpty());
  }

  @Test
  void admissionLock006CompoundUnknownCleanupIsNeverDowngraded() throws Exception {
    for (boolean knownBody : List.of(false, true)) {
      for (boolean fatalClose : List.of(false, true)) {
        var f = fixture();
        var body = new IllegalStateException("body");
        Throwable cleanup =
            fatalClose ? new AssertionError("close") : new IllegalStateException("close");
        Throwable expected = knownBody ? cleanup : body;
        f.afterClose =
            count -> {
              if (count == 1) raise(cleanup);
            };
        if (knownBody) f.fault = "attrs";
        else
          f.change =
              (view, role, values) -> {
                throw body;
              };
        Throwable actual =
            assertThrows(
                expected.getClass(),
                () ->
                    f.adapter()
                        .tryExclusive(fd -> fail("admission fault must not reach callback")));
        assertSame(expected, actual);
        assertTrue(f.owned.isEmpty());
        assertEquals(0, external(f.file));
      }
    }
  }

  @Test
  void admissionLock007ConcurrentSingleWinnerAndReusableAfterRelease() throws Exception {
    var f = fixture();
    var barrier = new CyclicBarrier(8);
    var rejected = new CountDownLatch(7);
    var callbacks = new AtomicInteger();
    try (var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Callable<Optional<Integer>>>();
      for (int i = 0; i < 8; i++)
        tasks.add(
            () -> {
              barrier.await(10, TimeUnit.SECONDS);
              var result =
                  f.adapter()
                      .tryExclusive(
                          fd -> {
                            callbacks.incrementAndGet();
                            assertTrue(
                                assertDoesNotThrow(() -> rejected.await(10, TimeUnit.SECONDS)));
                            return 1;
                          });
              if (result.isEmpty()) rejected.countDown();
              return result;
            });
      int winners = 0;
      for (var done : executor.invokeAll(tasks)) if (done.get().isPresent()) winners++;
      assertEquals(1, winners);
    }
    assertEquals(1, callbacks.get());
    assertTrue(f.owned.isEmpty());
    assertEquals(Optional.of(2), f.adapter().tryExclusive(fd -> 2));
  }

  @Test
  void admissionLock008FactoryNullAndActualNioContracts() throws Exception {
    var f = fixture();
    var security = f.security();
    var locks = LinuxFileLock.create();
    var io = f.io();
    assertThrows(
        NullPointerException.class,
        () -> new StartupAdmissionFile(null, f.host, f.service, security, locks, io));
    assertThrows(
        NullPointerException.class,
        () -> new StartupAdmissionFile(f.runtime, null, f.service, security, locks, io));
    assertThrows(
        NullPointerException.class,
        () -> new StartupAdmissionFile(f.runtime, f.host, null, security, locks, io));
    assertThrows(
        NullPointerException.class,
        () -> new StartupAdmissionFile(f.runtime, f.host, f.service, null, locks, io));
    assertThrows(
        NullPointerException.class,
        () -> new StartupAdmissionFile(f.runtime, f.host, f.service, security, null, io));
    assertThrows(
        NullPointerException.class,
        () -> new StartupAdmissionFile(f.runtime, f.host, f.service, security, locks, null));
    for (Path invalid : List.of(Path.of("run"), Path.of("/"), Path.of("/run/../run")))
      assertThrows(
          IllegalArgumentException.class,
          () -> new StartupAdmissionFile(invalid, f.host, f.service, security, locks, io));
    assertThrows(NullPointerException.class, () -> f.adapter().tryExclusive(null));
    assertEquals(0, f.opened.get());
    assertNotEquals(0, LinuxInodeSecurity.create().effectiveUid());
    unavailable(
        assertThrows(
            StorageIoException.class, () -> StartupAdmissionFile.create().tryExclusive(fd -> 1)));
    var actual = new StartupAdmissionFile.NioIo();
    assertEquals(0100600, actual.attributes(f.file).get(FIXTURE_MODE_B6D5C2C3));
    assertEquals("tmpfs", actual.filesystemType(Path.of("/dev/shm")));
  }

  private Fixture fixture() throws IOException {
    return new Fixture(Files.createTempDirectory(base, "run-"));
  }

  private static void rejected(Fixture f) {
    var count = new AtomicInteger();
    unavailable(
        assertThrows(
            StorageIoException.class,
            () -> f.adapter().tryExclusive(fd -> count.incrementAndGet())));
    assertEquals(0, count.get());
    assertTrue(f.owned.isEmpty());
  }

  private static void unavailable(StorageIoException e) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, e.reason());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static void raise(Throwable e) {
    if (e instanceof RuntimeException r) throw r;
    throw (Error) e;
  }

  private static int external(Path path) throws Exception {
    var p =
        new ProcessBuilder("/usr/bin/flock", "-x", "-n", "-E", "20", path.toString(), "/bin/true")
            .start();
    try {
      assertTrue(p.waitFor(5, TimeUnit.SECONDS));
      return p.exitValue();
    } finally {
      if (p.isAlive()) p.destroy();
    }
  }

  @FunctionalInterface
  interface Change {
    @Nullable Map<String, Object> apply(String view, String role, Map<String, Object> values);
  }

  final class Fixture {
    final Path runtime;
    final Path app;
    final Path file;
    final long runInode;
    final long fileInode;
    final Map<Integer, String> owned = new ConcurrentHashMap<>();
    final AtomicInteger opened = new AtomicInteger();
    final AtomicInteger closed = new AtomicInteger();
    final AtomicInteger hostReadonlyCalls = new AtomicInteger();
    final AtomicInteger privateReadonlyCalls = new AtomicInteger();
    final Calls host = new Calls("host");
    final Calls service = new Calls(FIXTURE_SERVICE_3E9B10A4);
    volatile int openFailure;
    volatile int closeFailure;
    volatile int negativeResult;
    volatile long uid;
    volatile boolean separate;
    volatile boolean acl;
    volatile boolean hostReadOnly;
    @Nullable String type = "tmpfs";
    String fault = "";
    Change change = (v, r, m) -> m;
    IntConsumer afterClose = n -> {};

    Fixture(Path runtime) throws IOException {
      this.runtime = runtime;
      app = Files.createDirectory(runtime.resolve("schubert-nk"));
      file = Files.createFile(app.resolve("startup-admission.lock"));
      Files.createFile(app.resolve(FIXTURE_OTHER_LOCK_7F80A9E4));
      Files.setAttribute(runtime, FIXTURE_UNIX_MODE_18F40B0C, 0755);
      Files.setAttribute(app, FIXTURE_UNIX_MODE_18F40B0C, 0755);
      Files.setAttribute(file, FIXTURE_UNIX_MODE_18F40B0C, 0600);
      Files.setAttribute(
          app.resolve(FIXTURE_OTHER_LOCK_7F80A9E4), FIXTURE_UNIX_MODE_18F40B0C, 0600);
      runInode = (Long) Files.getAttribute(runtime, "unix:ino");
      fileInode = (Long) Files.getAttribute(file, "unix:ino");
    }

    String view(Path held) {
      return Objects.requireNonNull(owned.get(Integer.parseInt(held.toString().substring(14))));
    }

    String role(Path held) throws IOException {
      var m = Files.readAttributes(held, "unix:mode,ino");
      if (((Integer) m.get(FIXTURE_MODE_B6D5C2C3) & 0170000) != 040000)
        return FIXTURE_FILE_BFDDE6F5;
      return m.get(FIXTURE_INO_4BE7C1E0).equals(runInode) ? "run" : "app";
    }

    void failure(String name) throws IOException {
      if (fault.equals(name)) throw new IOException("SECRET_CANARY");
    }

    StartupAdmissionFile adapter() {
      return new StartupAdmissionFile(
          runtime, host, service, security(), LinuxFileLock.create(), io());
    }

    StartupAdmissionFile.Io io() {
      return new StartupAdmissionFile.Io() {
        @Override
        public @Nullable Map<String, Object> attributes(Path held) throws IOException {
          failure("attrs");
          var m = new HashMap<>(Files.readAttributes(held, "unix:mode,uid,gid,nlink,size,dev,ino"));
          m.put("uid", 0);
          m.put("gid", 0);
          if (separate
              && view(held).equals(FIXTURE_SERVICE_3E9B10A4)
              && role(held).equals(FIXTURE_FILE_BFDDE6F5)) m.put(FIXTURE_INO_4BE7C1E0, fileInode);
          return change.apply(view(held), role(held), m);
        }

        @Override
        public @Nullable String filesystemType(Path held) throws IOException {
          failure("type");
          return type;
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
        public boolean readOnlyFilesystem(Path held) throws StorageIoException {
          try {
            failure("readonly");
            if (view(held).equals("host")) {
              hostReadonlyCalls.incrementAndGet();
              return hostReadOnly;
            }
            privateReadonlyCalls.incrementAndGet();
            return true;
          } catch (IOException e) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }

        @Override
        public byte[] accessAcl(Path held, int max) throws StorageIoException {
          assertEquals(44, max);
          try {
            failure("acl");
            return acl ? new byte[] {1} : new byte[0];
          } catch (IOException e) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }
      };
    }

    final class Calls implements DirectoryCalls {
      final String name;
      final DirectoryCalls real = LinuxDirectoryCalls.create();

      Calls(String name) {
        this.name = name;
      }

      int open(Open action) throws StorageIoException {
        int position = opened.incrementAndGet();
        if (position == negativeResult) return -1;
        if (position == openFailure)
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        int fd = action.run();
        assertNull(owned.put(fd, name));
        return fd;
      }

      @Override
      public int openRoot() throws StorageIoException {
        return open(real::openRoot);
      }

      @Override
      public int openDirectory(int parent, String child) throws StorageIoException {
        return open(() -> real.openDirectory(parent, child));
      }

      @Override
      public int openEntry(int parent, String child) throws StorageIoException {
        return open(
            () ->
                real.openEntry(
                    parent,
                    separate
                            && name.equals(FIXTURE_SERVICE_3E9B10A4)
                            && child.equals("startup-admission.lock")
                        ? FIXTURE_OTHER_LOCK_7F80A9E4
                        : child));
      }

      @Override
      public void close(int fd) throws StorageIoException {
        assertEquals(name, owned.remove(fd));
        real.close(fd);
        int n = closed.incrementAndGet();
        afterClose.accept(n);
        if (n == closeFailure) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }

      @Override
      public int createFile(int parent, String child) {
        throw new AssertionError(FIXTURE_NO_MUTATION_68019DA1);
      }

      @Override
      public void createDirectory(int parent, String child) {
        throw new AssertionError(FIXTURE_NO_MUTATION_68019DA1);
      }

      @Override
      public void publish(int directory, String part, String ready) {
        throw new AssertionError(FIXTURE_NO_MUTATION_68019DA1);
      }

      @Override
      public void unlink(int directory, String child) {
        throw new AssertionError(FIXTURE_NO_MUTATION_68019DA1);
      }

      @Override
      public void sync(int directory) {
        throw new AssertionError(FIXTURE_NO_MUTATION_68019DA1);
      }
    }
  }

  @FunctionalInterface
  interface Open {
    int run() throws StorageIoException;
  }
}
