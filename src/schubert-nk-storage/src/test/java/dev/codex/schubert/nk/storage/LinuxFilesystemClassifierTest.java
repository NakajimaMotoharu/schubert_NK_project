package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.foreign.Linker;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * SSC269 hand-written Linux magic/LP64 byte oracle, real retained FD and no classification cache.
 */
final class LinuxFilesystemClassifierTest {
  @TempDir Path root;

  @Test
  void fst005NativeUnknownFailurePreservesPrimaryAndClosesActualArena() {
    for (Throwable failure :
        new Throwable[] {
          new IllegalStateException("independent native failure"),
          new AssertionError("independent native fatal failure")
        }) {
      java.lang.foreign.MemorySegment[] retained = {null};
      var classifier =
          new LinuxFilesystemClassifier(
              (path, state) -> {
                retained[0] = state;
                assertTrue(state.scope().isAlive());
                if (failure instanceof RuntimeException runtime) throw runtime;
                throw (Error) failure;
              });
      assertSame(
          failure,
          assertThrows(
              failure.getClass(), () -> classifier.filesystem(Path.of("/proc/self/fd/42"))));
      assertNotNull(retained[0]);
      assertFalse(retained[0].scope().isAlive());
      assertThrows(IllegalStateException.class, () -> retained[0].get(ValueLayout.JAVA_LONG, 0));
    }
  }

  @Test
  void fst001IndependentMagicAndAbiEveryCallIsFresh() throws Exception {
    long[] magic = {0xEF53L};
    var calls = new AtomicInteger();
    var classifier =
        new LinuxFilesystemClassifier(
            (path, state) -> {
              assertEquals("/proc/self/fd/42", path.getString(0));
              assertEquals(120, state.byteSize());
              assertEquals(0, state.address() % 8);
              // Independent ABI vector: first long f_type, deliberately unrelated bsize/spares.
              state.set(ValueLayout.JAVA_LONG, 0, magic[0]);
              state.set(ValueLayout.JAVA_LONG, 8, 4096);
              state.set(ValueLayout.JAVA_LONG, 112, 0x01021994L);
              calls.incrementAndGet();
              return 0;
            });
    Map<Long, String> expected =
        Map.of(
            0xEF53L, "ext2/ext3/ext4",
            0x58465342L, "xfs",
            0x9123683EL, "btrfs",
            0x01021994L, "tmpfs");
    for (var entry : expected.entrySet()) {
      magic[0] = entry.getKey();
      assertEquals(entry.getValue(), classifier.filesystem(Path.of("/proc/self/fd/42")));
    }
    magic[0] = 0;
    assertEquals(
        StorageIoException.Reason.UNAVAILABLE,
        assertThrows(
                StorageIoException.class, () -> classifier.filesystem(Path.of("/proc/self/fd/42")))
            .reason());
    magic[0] = 0x01021994L;
    assertEquals("tmpfs", classifier.filesystem(Path.of("/proc/self/fd/42")));
    assertEquals(6, calls.get());
  }

  @Test
  void fst002FailedSyscallNullAndInvalidCapabilityNeverBecomeSuccess() {
    int[] code = {-1};
    var calls = new AtomicInteger();
    var classifier =
        new LinuxFilesystemClassifier(
            (path, state) -> {
              calls.incrementAndGet();
              state.set(ValueLayout.JAVA_LONG, 0, 0xEF53L);
              return code[0];
            });
    for (int failure : new int[] {-1, 1, Integer.MIN_VALUE, Integer.MAX_VALUE}) {
      code[0] = failure;
      assertThrows(
          StorageIoException.class, () -> classifier.filesystem(Path.of("/proc/self/fd/0")));
    }
    assertThrows(IllegalArgumentException.class, () -> classifier.filesystem(null));
    for (String invalid :
        new String[] {
          "",
          "/",
          "proc/self/fd/2",
          "/proc/self/fd/02",
          "/proc/self/fd/-1",
          "/proc/self/fd/2147483648",
          "/proc/self/fd/9999999999",
          "/proc/self/fd/10000000000",
          "/proc/self/fd/2/..",
          "/proc/1/fd/2",
          "/proc/self/fd/2/entry"
        }) {
      assertThrows(IllegalArgumentException.class, () -> classifier.filesystem(Path.of(invalid)));
    }
    assertEquals(4, calls.get());
  }

  @Test
  void fst003UnsupportedPlatformAndMissingSymbolsFailClosed() {
    SymbolLookup none = name -> Optional.empty();
    assertThrows(
        IllegalStateException.class,
        () -> LinuxFilesystemClassifier.create("Other", "amd64", none));
    assertThrows(
        IllegalStateException.class, () -> LinuxFilesystemClassifier.create("Linux", "x86", none));
    assertThrows(
        IllegalStateException.class,
        () -> LinuxFilesystemClassifier.create("Linux", "amd64", none));
    SymbolLookup gnuOnly =
        name ->
            name.equals("gnu_get_libc_version")
                ? Linker.nativeLinker().defaultLookup().find(name)
                : Optional.empty();
    assertThrows(
        IllegalStateException.class,
        () -> LinuxFilesystemClassifier.create("Linux", "x86_64", gnuOnly));
  }

  @Test
  void fst004RealRetainedFdIndependentJdkTypeAndReleasedFd() throws Exception {
    var classifier = LinuxFilesystemClassifier.create();
    String expected =
        switch (Files.getFileStore(root).type()) {
          case "ext2", "ext3", "ext4" -> "ext2/ext3/ext4";
          case "xfs" -> "xfs";
          case "btrfs" -> "btrfs";
          case "tmpfs" -> "tmpfs";
          default -> throw new AssertionError("PT needs a qualified local filesystem");
        };
    var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
    Path[] closed = {null};
    try (directory) {
      directory.atDirectory(
          p -> {
            closed[0] = p;
            assertEquals(expected, classifier.filesystem(p));
            return true;
          });
    }
    assertNotNull(closed[0]);
    assertThrows(StorageIoException.class, () -> classifier.filesystem(closed[0]));
  }
}
