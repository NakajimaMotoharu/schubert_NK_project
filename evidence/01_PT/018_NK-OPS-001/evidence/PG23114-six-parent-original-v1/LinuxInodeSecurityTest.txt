package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.foreign.Linker;
import java.lang.foreign.MemoryLayout;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-121..128; public temporary metadata only, independent Linux UAPI golden. */
final class LinuxInodeSecurityTest {
  private static final String PUBLIC_ENTRY = "public";
  private static final String LINUX_OS = "Linux";
  private static final String AMD64_ARCH = "amd64";
  private static final int ENODATA_ERRNO = 61;
  private static final Path CAPABILITY = Path.of("/proc/self/fd/7");
  private static final long ERRNO =
      Linker.Option.captureStateLayout().byteOffset(MemoryLayout.PathElement.groupElement("errno"));
  @TempDir Path root;

  @Test
  void actualAclAndUid() throws Exception {
    InodeSecurityCalls nativeCalls = LinuxInodeSecurity.create();
    assertEquals(
        Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid")),
        nativeCalls.effectiveUid());
    Path file = Files.write(root.resolve(PUBLIC_ENTRY), new byte[] {7});
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      held.atExistingEntryHandle(
          PUBLIC_ENTRY,
          path -> {
            assertArrayEquals(new byte[0], nativeCalls.accessAcl(path, 44));
            return true;
          });
      setAcl(file, 12345);
      held.atExistingEntryHandle(
          PUBLIC_ENTRY,
          path -> {
            byte[] first = nativeCalls.accessAcl(path, 44);
            assertArrayEquals(golden(12345), first);
            Arrays.fill(first, (byte) 0);
            assertArrayEquals(golden(12345), nativeCalls.accessAcl(path, 65536));
            failure(() -> nativeCalls.accessAcl(path, 43)); // real ERANGE, never truncates
            return true;
          });
    }
  }

  @Test
  void filesystemFlagsAndFailures() throws Exception {
    var nativeCalls = LinuxInodeSecurity.create();
    boolean expected = Files.getFileStore(root).isReadOnly();
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      held.atDirectory(
          path -> {
            assertEquals(expected, nativeCalls.readOnlyFilesystem(path));
            return true;
          });
    }
    for (long flag : new long[] {0, 1, 2, 3, 0x80000000L, Long.MIN_VALUE, -1}) {
      var calls =
          new LinuxInodeSecurity(
              noAcl(ENODATA_ERRNO),
              (state, path, value) -> {
                assertEquals(112, value.byteSize());
                assertEquals("/proc/self/fd/7", path.getString(0));
                value.set(ValueLayout.JAVA_LONG, 72, flag);
                return 0;
              },
              () -> 1000);
      assertEquals((flag & 1L) == 1L, calls.readOnlyFilesystem(CAPABILITY));
    }
    for (int result : new int[] {-1, 1, Integer.MIN_VALUE})
      failure(
          () ->
              new LinuxInodeSecurity(noAcl(ENODATA_ERRNO), (s, p, v) -> result, () -> 1000)
                  .readOnlyFilesystem(CAPABILITY));
  }

  @Test
  void heldElfCapabilityAbsenceRequiresExactEnodataAndNativeHeldFile() throws Exception {
    for (int errno : new int[] {ENODATA_ERRNO, 95, 1, 5, 34}) {
      var calls =
          new LinuxInodeSecurity(
              (state, path, name, value, limit) -> {
                assertEquals("security.capability", name.getString(0));
                assertEquals(24, limit);
                state.set(ValueLayout.JAVA_INT, ERRNO, errno);
                return -1;
              },
              (s, p, v) -> 0,
              () -> 0);
      if (errno == ENODATA_ERRNO) calls.requireNoFileCapabilities(CAPABILITY);
      else failure(() -> calls.requireNoFileCapabilities(CAPABILITY));
    }
    for (int returned : new int[] {0, 1, 24, 25, -2}) {
      var calls = new LinuxInodeSecurity((s, p, n, v, l) -> returned, (s, p, v) -> 0, () -> 0);
      failure(() -> calls.requireNoFileCapabilities(CAPABILITY));
    }
    var actual = LinuxInodeSecurity.create();
    assertThrows(NullPointerException.class, () -> actual.requireNoFileCapabilities(null));
    assertThrows(IllegalArgumentException.class, () -> actual.requireNoFileCapabilities(root));
    Files.writeString(root.resolve("public-elf-fixture"), "PUBLIC");
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      held.atExistingEntryHandle(
          "public-elf-fixture",
          path -> {
            actual.requireNoFileCapabilities(path);
            return Boolean.TRUE;
          });
    }
  }

  @Test
  void aclReturnAndErrnoBoundaries() throws Exception {
    for (int size : new int[] {1, 44, 65536}) {
      var calls =
          new LinuxInodeSecurity(
              (state, path, name, value, limit) -> {
                assertEquals("/proc/self/fd/7", path.getString(0));
                assertEquals("system.posix_acl_access", name.getString(0));
                assertEquals(size, limit);
                assertEquals(size, value.byteSize());
                value.fill((byte) 0x5a);
                return size;
              },
              (s, p, v) -> 0,
              () -> 1000);
      byte[] expected = new byte[size];
      Arrays.fill(expected, (byte) 0x5a);
      assertArrayEquals(expected, calls.accessAcl(CAPABILITY, size));
    }
    for (long size : new long[] {-2, 0, 45, Long.MAX_VALUE})
      failure(
          () ->
              new LinuxInodeSecurity((s, p, n, v, l) -> size, (s, p, v) -> 0, () -> 0)
                  .accessAcl(CAPABILITY, 44));
    for (int errno : new int[] {0, 1, 2, 5, 9, 13, 34, ENODATA_ERRNO, 95, Integer.MAX_VALUE}) {
      var calls = new LinuxInodeSecurity(noAcl(errno), (s, p, v) -> 0, () -> 0);
      if (errno == ENODATA_ERRNO || errno == 95)
        assertArrayEquals(new byte[0], calls.accessAcl(CAPABILITY, 44));
      else failure(() -> calls.accessAcl(CAPABILITY, 44));
    }
  }

  @Test
  void canonicalCapabilityAndBounds() throws Exception {
    var calls = new LinuxInodeSecurity(noAcl(ENODATA_ERRNO), (s, p, v) -> 0, () -> 0);
    for (String name :
        List.of(
            "",
            ".",
            "/tmp/value",
            "proc/self/fd/7",
            "/proc/1/fd/7",
            "/proc/self/fd/-1",
            "/proc/self/fd/01",
            "/proc/self/fd/+1",
            "/proc/self/fd/1/child",
            "/proc/self/fd/2147483648",
            "/proc/self/fd/9999999999",
            "/proc/self/fd/10000000000",
            "/proc/self/fd/1/../2",
            "/proc/self/fd/١")) {
      var path = Path.of(name);
      var first = assertThrows(IllegalArgumentException.class, () -> calls.accessAcl(path, 44));
      assertEquals("invalid held inode capability", first.getMessage());
      assertThrows(IllegalArgumentException.class, () -> calls.readOnlyFilesystem(path));
    }
    for (String name : List.of("0", "1", "2147483647")) {
      var path = Path.of("/proc/self/fd/" + name);
      assertArrayEquals(new byte[0], calls.accessAcl(path, 1));
      assertFalse(calls.readOnlyFilesystem(path));
    }
    for (int limit : new int[] {Integer.MIN_VALUE, -1, 0, 65537, Integer.MAX_VALUE}) {
      var error =
          assertThrows(IllegalArgumentException.class, () -> calls.accessAcl(CAPABILITY, limit));
      assertEquals("invalid access ACL size limit", error.getMessage());
    }
    assertThrows(NullPointerException.class, () -> calls.accessAcl(null, 44));
    assertThrows(NullPointerException.class, () -> calls.readOnlyFilesystem(null));
  }

  @Test
  void platformAndSymbolAdmission() throws java.io.IOException {
    long expectedUid = Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid"));
    assertEquals(expectedUid, LinuxInodeSecurity.create().effectiveUid());
    SymbolLookup real = Linker.nativeLinker().defaultLookup();
    for (String arch : List.of(AMD64_ARCH, "x86_64", "aarch64"))
      assertEquals(expectedUid, LinuxInodeSecurity.create(LINUX_OS, arch, real).effectiveUid());
    for (String os : List.of("", "Windows", "linux", "Mac OS X"))
      platformFailure(() -> LinuxInodeSecurity.create(os, AMD64_ARCH, real));
    for (String arch : List.of("", "x86", "arm", "sparc"))
      platformFailure(() -> LinuxInodeSecurity.create(LINUX_OS, arch, real));
    for (String missing : List.of("gnu_get_libc_version", "getxattr", "statvfs", "geteuid"))
      platformFailure(
          () ->
              LinuxInodeSecurity.create(
                  LINUX_OS,
                  AMD64_ARCH,
                  name -> name.equals(missing) ? Optional.empty() : real.find(name)));
    assertThrows(
        NullPointerException.class, () -> LinuxInodeSecurity.create(null, AMD64_ARCH, real));
    assertThrows(NullPointerException.class, () -> LinuxInodeSecurity.create(LINUX_OS, null, real));
    assertThrows(
        NullPointerException.class, () -> LinuxInodeSecurity.create(LINUX_OS, AMD64_ARCH, null));
  }

  @Test
  void heldInodeSurvivesReplacement() throws Exception {
    var calls = LinuxInodeSecurity.create();
    Path original = Files.write(root.resolve(PUBLIC_ENTRY), new byte[] {1});
    Path replacement = Files.write(root.resolve("replacement"), new byte[] {2});
    setAcl(original, 12345);
    setAcl(replacement, 12346);
    var closedCapability = new AtomicReference<Path>();
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      held.atExistingEntryHandle(
          PUBLIC_ENTRY,
          path -> {
            assertArrayEquals(golden(12345), calls.accessAcl(path, 44));
            Files.move(original, root.resolve("retired"));
            Files.move(replacement, original);
            assertArrayEquals(golden(12345), calls.accessAcl(path, 44));
            closedCapability.set(
                path); // test-only negative lifetime probe, never production export
            return true;
          });
      failure(() -> calls.accessAcl(closedCapability.get(), 44));
      held.atExistingEntryHandle(
          PUBLIC_ENTRY,
          path -> {
            assertArrayEquals(golden(12346), calls.accessAcl(path, 44));
            return true;
          });
    }
  }

  @Test
  void concurrentReadsStayIndependent() throws Exception {
    var calls = LinuxInodeSecurity.create();
    var directories = LinuxDirectoryCalls.create();
    Path file = Files.write(root.resolve(PUBLIC_ENTRY), new byte[] {1});
    setAcl(file, 12345);
    long expectedUid = Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid"));
    boolean readonly = Files.getFileStore(root).isReadOnly();
    try (var pool = Executors.newFixedThreadPool(12)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++)
        tasks.add(
            () -> {
              try (var held = OwnedTransferDirectory.open(directories, root)) {
                return held.atExistingEntryHandle(
                    PUBLIC_ENTRY,
                    path -> {
                      assertArrayEquals(golden(12345), calls.accessAcl(path, 44));
                      assertEquals(readonly, calls.readOnlyFilesystem(path));
                      assertEquals(expectedUid, calls.effectiveUid());
                      return true;
                    });
              }
            });
      for (var result : pool.invokeAll(tasks, 30, TimeUnit.SECONDS))
        assertTrue(result.get(5, TimeUnit.SECONDS));
    }
  }

  @Test
  void interfacesAndRedaction() {
    LinuxInodeSecurity.StatvfsCall stat = (s, p, v) -> 0;
    assertThrows(NullPointerException.class, () -> new LinuxInodeSecurity(null, stat, () -> 0));
    assertThrows(
        NullPointerException.class,
        () -> new LinuxInodeSecurity(noAcl(ENODATA_ERRNO), null, () -> 0));
    assertThrows(
        NullPointerException.class, () -> new LinuxInodeSecurity(noAcl(ENODATA_ERRNO), stat, null));
    for (int uid : new int[] {0, 1, 1000, Integer.MAX_VALUE, Integer.MIN_VALUE, -2, -1}) {
      InodeSecurityCalls calls = new LinuxInodeSecurity(noAcl(ENODATA_ERRNO), stat, () -> uid);
      assertEquals(uid & 0xffff_ffffL, calls.effectiveUid());
    }
    InodeSecurityCalls real = LinuxInodeSecurity.create();
    Path missing = Path.of("/proc/self/fd/2147483647");
    failure(() -> real.accessAcl(missing, 44));
    failure(() -> real.readOnlyFilesystem(missing));
  }

  private static LinuxInodeSecurity.GetXattrCall noAcl(int errno) {
    return (state, path, name, value, limit) -> {
      state.set(ValueLayout.JAVA_INT, ERRNO, errno);
      return -1;
    };
  }

  private static byte[] golden(int uid) {
    byte[] result =
        HexFormat.of()
            .parseHex(
                "0200000001000400ffffffff020004000000000004000000ffffffff10000400ffffffff20000000ffffffff");
    for (int i = 0; i < 4; i++) result[16 + i] = (byte) (uid >>> (8 * i));
    return result;
  }

  private static void setAcl(Path file, int uid) throws Exception {
    Process process =
        new ProcessBuilder(
                "/usr/bin/setfacl",
                "--set=u::r--,u:" + uid + ":r--,g::---,m::r--,o::---",
                "--",
                file.toString())
            .redirectErrorStream(true)
            .start();
    try {
      assertTrue(process.waitFor(5, TimeUnit.SECONDS));
      assertEquals(0, process.exitValue());
      assertEquals("", new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8));
    } finally {
      process.destroyForcibly();
    }
  }

  private static void failure(Executable action) {
    var error = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason());
    assertEquals("transfer storage operation failed", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static void platformFailure(Executable action) {
    var error = assertThrows(IllegalStateException.class, action);
    assertEquals("native inode security is unavailable", error.getMessage());
    assertNull(error.getCause());
  }
}
