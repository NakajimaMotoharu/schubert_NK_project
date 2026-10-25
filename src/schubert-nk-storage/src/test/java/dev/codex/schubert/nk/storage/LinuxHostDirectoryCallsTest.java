package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Fixed kernel anchor, read-only capability delegation, independent call-order oracle. */
final class LinuxHostDirectoryCallsTest {
  @Test
  void opsHost001FixedKernelAnchorAndNativeFlags() throws Exception {
    var fixture = new Fixture();
    assertEquals(17, fixture.calls().openRoot());
    assertEquals(List.of("uid", "open:/proc/1/root:589824:0"), fixture.events);
    assertFalse(Objects.requireNonNull(fixture.pointer).scope().isAlive());
  }

  @Test
  void opsHost002NoFollowChildrenAndOwnedCloseForwardOnly() throws Exception {
    var fixture = new Fixture();
    var calls = fixture.calls();
    assertEquals(18, calls.openDirectory(17, "run"));
    assertEquals(19, calls.openEntry(18, "startup-admission.lock"));
    calls.close(19);
    calls.close(18);
    calls.close(17);
    assertEquals(
        List.of(
            "directory:17:run",
            "entry:18:startup-admission.lock",
            "close:19",
            "close:18",
            "close:17"),
        fixture.events);
  }

  @Test
  void opsHost003EveryMutationRefusedWithoutDelegation() {
    var fixture = new Fixture();
    var calls = fixture.calls();
    unavailable(assertThrows(StorageIoException.class, () -> calls.createFile(17, "file")));
    unavailable(assertThrows(StorageIoException.class, () -> calls.createPrivateFile(17, "file")));
    unavailable(
        assertThrows(StorageIoException.class, () -> calls.createDirectory(17, "directory")));
    unavailable(
        assertThrows(
            StorageIoException.class, () -> calls.createPrivateDirectory(17, "directory")));
    unavailable(assertThrows(StorageIoException.class, () -> calls.publish(17, "part", "ready")));
    unavailable(assertThrows(StorageIoException.class, () -> calls.unlink(17, "file")));
    unavailable(assertThrows(StorageIoException.class, () -> calls.sync(17)));
    assertTrue(fixture.events.isEmpty());
  }

  @Test
  void opsHost004UidGateAndNativeFailureNeverFallBack() {
    for (long uid : List.of(-1L, 1L, 1000L, 65534L, Long.MAX_VALUE)) {
      var fixture = new Fixture();
      fixture.uid = uid;
      unavailable(assertThrows(StorageIoException.class, () -> fixture.calls().openRoot()));
      assertEquals(List.of("uid"), fixture.events);
    }
    var fixture = new Fixture();
    fixture.openResult = -1;
    unavailable(assertThrows(StorageIoException.class, () -> fixture.calls().openRoot()));
    assertEquals(List.of("uid", "open:/proc/1/root:589824:0"), fixture.events);
    assertFalse(Objects.requireNonNull(fixture.pointer).scope().isAlive());
  }

  @Test
  void opsHost005UnknownFailuresKeepIdentityAndArenaClosed() {
    for (Throwable unknown :
        List.of(
            new IllegalStateException("public unknown"), new AssertionError("public unknown"))) {
      var fixture = new Fixture();
      fixture.unknown = unknown;
      assertSame(unknown, assertThrows(unknown.getClass(), () -> fixture.calls().openRoot()));
      assertFalse(Objects.requireNonNull(fixture.pointer).scope().isAlive());
      assertEquals(0, unknown.getSuppressed().length);
    }
  }

  @Test
  void opsHost006NullPlatformAndSymbolContracts() {
    var fixture = new Fixture();
    LinuxHostDirectoryCalls.OpenCall open = (p, f, m) -> 17;
    assertThrows(
        NullPointerException.class,
        () -> new LinuxHostDirectoryCalls(null, fixture.security(), open));
    assertThrows(
        NullPointerException.class, () -> new LinuxHostDirectoryCalls(fixture, null, open));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxHostDirectoryCalls(fixture, fixture.security(), null));
    var symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(
        NullPointerException.class, () -> LinuxHostDirectoryCalls.create(null, "amd64", symbols));
    assertThrows(
        NullPointerException.class, () -> LinuxHostDirectoryCalls.create("Linux", null, symbols));
    assertThrows(
        NullPointerException.class, () -> LinuxHostDirectoryCalls.create("Linux", "amd64", null));
    for (String os : List.of("Windows", "linux", ""))
      assertThrows(
          IllegalStateException.class, () -> LinuxHostDirectoryCalls.create(os, "amd64", symbols));
    assertThrows(
        IllegalStateException.class,
        () -> LinuxHostDirectoryCalls.create("Linux", "unknown", symbols));
    assertThrows(
        IllegalStateException.class,
        () ->
            LinuxHostDirectoryCalls.create(
                "Linux",
                "amd64",
                name -> name.equals("open") ? Optional.empty() : symbols.find(name)));
    for (String arch : List.of("amd64", "x86_64", "aarch64"))
      assertNotNull(LinuxHostDirectoryCalls.create("Linux", arch, symbols));
    assertTrue(fixture.events.isEmpty());
  }

  @Test
  void opsHost007ActualOrdinaryUidCannotOpenHostAnchor() {
    assertNotEquals(
        0L, LinuxInodeSecurity.create().effectiveUid(), "host PT requires ordinary UID");
    unavailable(
        assertThrows(StorageIoException.class, () -> LinuxHostDirectoryCalls.create().openRoot()));
  }

  @Test
  void opsHost008ConcurrentScopesKeepOnlyOwnPointers() throws Exception {
    try (var executor = Executors.newFixedThreadPool(8)) {
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 32; i++)
        work.add(
            () -> {
              var fixture = new Fixture();
              assertEquals(17, fixture.calls().openRoot());
              assertFalse(Objects.requireNonNull(fixture.pointer).scope().isAlive());
              return true;
            });
      for (var result : executor.invokeAll(work)) assertTrue(result.get(5, TimeUnit.SECONDS));
    }
  }

  private static void unavailable(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture implements DirectoryCalls {
    final List<String> events = new ArrayList<>();
    long uid = 0;
    int openResult = 17;
    MemorySegment pointer;
    Throwable unknown;

    InodeSecurityCalls security() {
      return new InodeSecurityCalls() {
        @Override
        public long effectiveUid() {
          events.add("uid");
          return uid;
        }

        @Override
        public byte[] accessAcl(Path p, int max) {
          throw new AssertionError("unused security port");
        }

        @Override
        public boolean readOnlyFilesystem(Path p) {
          throw new AssertionError("unused security port");
        }
      };
    }

    LinuxHostDirectoryCalls calls() {
      return new LinuxHostDirectoryCalls(
          this,
          security(),
          (p, f, m) -> {
            pointer = p;
            events.add("open:" + p.getString(0) + ":" + f + ":" + m);
            if (unknown instanceof RuntimeException failure) throw failure;
            if (unknown instanceof Error failure) throw failure;
            return openResult;
          });
    }

    @Override
    public int openRoot() {
      throw new AssertionError("no private namespace fallback");
    }

    @Override
    public int openDirectory(int fd, String n) {
      events.add("directory:" + fd + ":" + n);
      return 18;
    }

    @Override
    public int openEntry(int fd, String n) {
      events.add("entry:" + fd + ":" + n);
      return 19;
    }

    @Override
    public void close(int fd) {
      events.add("close:" + fd);
    }

    @Override
    public int createFile(int fd, String n) {
      throw new AssertionError("no mutation");
    }

    @Override
    public void createDirectory(int fd, String n) {
      throw new AssertionError("no mutation");
    }

    @Override
    public void publish(int fd, String p, String r) {
      throw new AssertionError("no mutation");
    }

    @Override
    public void unlink(int fd, String n) {
      throw new AssertionError("no mutation");
    }

    @Override
    public void sync(int fd) {
      throw new AssertionError("no mutation");
    }
  }
}
