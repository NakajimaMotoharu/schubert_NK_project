package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS333§12/SSC118; NK-OPS-001/1483, public own bytes and read-only fault inputs. */
final class TransferIoBoundaryTest {
  @TempDir Path temporary;
  private static final Instant CUTOFF = Instant.parse("2026-09-30T00:00:00Z");
  private static final String NAME = "11111111-2222-4333-8444-555555555555.part";

  /** PT-OPS-TRANSFER-IO-001: ASCII width and Gregorian leap rules remain independent. */
  @Test
  void transferIo001GrammarAndLeapDatesKeepAllInvalidEntries() throws Exception {
    try (var f = new Fixture(temporary, false)) {
      var invalid = List.of("100000101", "+0010101", "２０２６０９２９", "2026092", "19000229");
      for (String name : invalid) directory(f.path.resolve(name));
      for (String name : List.of("20000229", "20240229")) directory(f.path.resolve(name));
      outcome(
          f.subject(f).execute(CUTOFF), 0, 0, 0, 5, 0, BatchStepResult.Reason.PROTECTED_RECORDS);
      for (String name : invalid) assertTrue(Files.isDirectory(f.path.resolve(name)));
      for (String name : List.of("20000229", "20240229"))
        assertFalse(Files.exists(f.path.resolve(name)));
      assertEquals(0, f.unlinks);
      assertEquals(2, f.removes);
      f.borrowed();
      assertTrue(Files.isDirectory(f.path));
    }
  }

  /** PT-OPS-TRANSFER-IO-002: malformed root metadata never reaches deletion. */
  @Test
  void transferIo002RootMetadataAndFilesystemFailuresPreserveEveryByte() throws Exception {
    for (String fault : List.of("size", "links", "nullMap", "nullFilesystem", "filesystem")) {
      try (var f = new Fixture(temporary, true)) {
        var before = f.original();
        f.fault = fault;
        assertThrows(IOException.class, () -> f.subject(f).execute(CUTOFF));
        assertEquals(1, f.faultsInjected, "the intended fixture fault was reached");
        f.protectedWithoutMutation(before);
      }
    }
  }

  /** PT-OPS-TRANSFER-IO-003: both directory and file device mismatches are retained warnings. */
  @Test
  void transferIo003ChildAndFileDeviceMismatchNeverDelete() throws Exception {
    for (String role : List.of("child", "file")) {
      try (var f = new Fixture(temporary, true)) {
        var before = f.original();
        f.transform =
            (observed, values) -> {
              if (observed.equals(role)) values.put("dev", ((Long) values.get("dev")) + 1);
            };
        outcome(
            f.subject(f).execute(CUTOFF), 0, 0, 0, 1, 0, BatchStepResult.Reason.PROTECTED_RECORDS);
        assertEquals(1, f.observations.get(role), "the selected device input was inspected");
        f.protectedWithoutMutation(before);
      }
    }
  }

  /** PT-OPS-TRANSFER-IO-004: inode remains a separately necessary identity check. */
  @Test
  void transferIo004RootAndChildInodeChangesAbortWithoutDeletion() throws Exception {
    for (String role : List.of("root", "child")) {
      try (var f = new Fixture(temporary, true)) {
        var before = f.original();
        f.transform =
            (observed, values) -> {
              if (observed.equals(role) && f.observations.get(role) == 2)
                values.put("ino", ((Long) values.get("ino")) + 1);
            };
        assertThrows(IOException.class, () -> f.subject(f).execute(CUTOFF));
        assertEquals(2, f.observations.get(role));
        f.protectedWithoutMutation(before);
      }
    }
  }

  /** PT-OPS-TRANSFER-IO-005: removing redundant equality never removes fresh admission. */
  @Test
  void transferIo005EveryProtectedAttributeIsReadmittedBeforeMutation() throws Exception {
    for (String attribute : List.of("uid", "gid", "mode", "dev")) {
      try (var f = new Fixture(temporary, true)) {
        var before = f.original();
        f.transform =
            (role, values) -> {
              if (role.equals("root") && f.observations.get("root") == 2) {
                Object value = values.get(attribute);
                if (value instanceof Integer integer) values.put(attribute, integer + 1);
                else values.put(attribute, ((Long) value) + 1);
              }
            };
        assertThrows(IOException.class, () -> f.subject(f).execute(CUTOFF));
        assertEquals(2, f.observations.get("root"));
        f.protectedWithoutMutation(before);
      }
    }
  }

  /** PT-OPS-TRANSFER-IO-006: successful backend return does not prove actual absence. */
  @Test
  void transferIo006NonRemovingBackendCannotCountAFileAsDeleted() throws Exception {
    try (var f = new Fixture(temporary, true)) {
      var before = f.original();
      f.nonRemoving = true;
      outcome(f.subject(f).execute(CUTOFF), 1, 0, 1, 0, 0, BatchStepResult.Reason.IO_FAILURE);
      assertEquals(1, f.unlinks);
      assertEquals(0, f.removes);
      f.protectedBytes(before);
      f.borrowed();
    }
  }

  /** PT-OPS-TRANSFER-IO-007: invalid enumeration and IO fail closed with streams released. */
  @Test
  void transferIo007ReadFailuresAndInvalidElementsNeverBecomeEmptySuccess() throws Exception {
    for (String fault :
        List.of(
            "metadataIOException",
            "filesystemIOException",
            "openIOException",
            "iterator",
            "close",
            "nullStream",
            "nullEntry",
            "nullName")) {
      try (var f = new Fixture(temporary, true)) {
        var before = f.original();
        f.fault = fault;
        assertThrows(IOException.class, () -> f.subject(f).execute(CUTOFF));
        assertEquals(1, f.faultsInjected, "the intended fixture fault was reached");
        f.protectedWithoutMutation(before);
      }
    }
  }

  /** PT-OPS-TRANSFER-IO-008: factory invariant failure cannot consume the borrowed root. */
  @Test
  void transferIo008NullIoRefusesAndBorrowedRootRemainsOwned() throws Exception {
    try (var f = new Fixture(temporary, true)) {
      var before = f.original();
      assertThrows(NullPointerException.class, () -> f.subject(null));
      boolean heldDirectory = f.root.atDirectory(Files::isDirectory);
      assertTrue(heldDirectory);
      f.protectedWithoutMutation(before);
    }
  }

  private static void outcome(
      TransferCleanup.Outcome actual,
      long target,
      long success,
      long failure,
      long retained,
      long bytes,
      BatchStepResult.Reason reason) {
    assertEquals(target, actual.target());
    assertEquals(success, actual.success());
    assertEquals(failure, actual.failure());
    assertEquals(retained, actual.retained());
    assertEquals(bytes, actual.bytes());
    assertEquals(BatchStepResult.Status.WARNING, actual.result().status());
    assertEquals(reason, actual.result().reason());
  }

  private static Path directory(Path path) throws IOException {
    Files.createDirectory(path);
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-x---"));
    return path;
  }

  private static final class Fixture implements AutoCloseable, TransferCleanup.Io {
    final Path path;
    final Path date;
    final Path file;
    final OwnedTransferDirectory root;
    final TransferCleanup.NioIo nio = new TransferCleanup.NioIo();
    final Set<Integer> descriptors = new HashSet<>();
    final Map<String, Integer> observations = new HashMap<>();
    final long uid;
    final long gid;
    int openedStreams;
    int closedStreams;
    int unlinks;
    int removes;
    int guards;
    int faultsInjected;
    String fault = "";
    boolean nonRemoving;
    BiConsumer<String, Map<String, Object>> transform = (role, values) -> {};

    Fixture(Path temporary, boolean seed) throws Exception {
      path = directory(Files.createTempDirectory(temporary, "transfer-").resolve("root"));
      date = path.resolve("20260929");
      file = date.resolve(NAME);
      if (seed) {
        directory(date);
        Files.write(file, new byte[] {17, 23, 41});
        Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-r-----"));
        Files.setLastModifiedTime(file, FileTime.from(CUTOFF.minusSeconds(1)));
      }
      uid = Integer.toUnsignedLong((Integer) Files.getAttribute(path, "unix:uid"));
      gid = Integer.toUnsignedLong((Integer) Files.getAttribute(path, "unix:gid"));
      var nativeCalls = LinuxDirectoryCalls.create();
      DirectoryCalls calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    if (!Set.of(
                            "openRoot",
                            "openDirectory",
                            "openEntry",
                            "unlink",
                            "removeEmptyDirectory",
                            "sync",
                            "close")
                        .contains(name)) throw new AssertionError("cleanup cannot create/publish");
                    if (name.equals("unlink")) {
                      unlinks++;
                      if (nonRemoving) return null;
                    }
                    if (name.equals("removeEmptyDirectory")) removes++;
                    Object result;
                    try {
                      result = method.invoke(nativeCalls, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (name.equals("close"))
                      assertTrue(descriptors.remove((Integer) args[0]), "FD consumed once");
                    else if (name.startsWith("open"))
                      assertTrue(descriptors.add((Integer) result), "new owned FD");
                    return result;
                  });
      root = OwnedTransferDirectory.open(calls, path);
    }

    TransferCleanup subject(TransferCleanup.Io io) {
      return new TransferCleanup(root, LinuxInodeSecurity.create(), uid, gid, () -> guards++, io);
    }

    Map<String, Object> original() throws IOException {
      return Files.readAttributes(
          file, "unix:ino,ctime,size,lastModifiedTime", LinkOption.NOFOLLOW_LINKS);
    }

    void protectedBytes(Map<String, Object> before) throws IOException {
      assertArrayEquals(new byte[] {17, 23, 41}, Files.readAllBytes(file));
      assertEquals(before, original());
      assertTrue(Files.isDirectory(path));
      assertTrue(Files.isDirectory(date));
    }

    void protectedWithoutMutation(Map<String, Object> before) throws IOException {
      assertEquals(0, unlinks);
      assertEquals(0, removes);
      protectedBytes(before);
      borrowed();
    }

    void borrowed() {
      assertEquals(1, descriptors.size(), "only caller root remains");
      assertEquals(openedStreams, closedStreams, "all streams closed");
    }

    boolean injecting(String name) {
      if (!fault.equals(name)) return false;
      faultsInjected++;
      return true;
    }

    @Override
    public Map<String, Object> metadata(Path held) throws IOException {
      if (injecting("metadataIOException")) throw new IOException("synthetic metadata failure");
      if (injecting("nullMap")) return null;
      var values = new HashMap<>(nio.metadata(held));
      String role =
          Files.isSameFile(held, path) ? "root" : Files.isDirectory(held) ? "child" : "file";
      observations.merge(role, 1, Integer::sum);
      if (injecting("size")) values.put("size", -1L);
      if (injecting("links")) values.put("nlink", 1);
      transform.accept(role, values);
      return values;
    }

    @Override
    public String filesystem(Path held) throws IOException {
      if (injecting("filesystemIOException")) throw new IOException("synthetic filesystem failure");
      if (injecting("nullFilesystem")) return null;
      return injecting("filesystem") ? "unsupported-public-fixture" : nio.filesystem(held);
    }

    @Override
    public DirectoryStream<Path> openNames(Path held) throws IOException {
      if (injecting("openIOException")) throw new IOException("synthetic enumeration failure");
      if (injecting("nullStream")) return null;
      var delegate = nio.openNames(held);
      openedStreams++;
      return new DirectoryStream<>() {
        @Override
        public Iterator<Path> iterator() {
          if (injecting("iterator"))
            throw new DirectoryIteratorException(new IOException("synthetic iterator failure"));
          var iterator = delegate.iterator();
          return new Iterator<>() {
            @Override
            public boolean hasNext() {
              return iterator.hasNext();
            }

            @Override
            public Path next() {
              Path original = iterator.next();
              return injecting("nullEntry")
                  ? null
                  : injecting("nullName") ? Path.of("/") : original;
            }
          };
        }

        @Override
        public void close() throws IOException {
          delegate.close();
          closedStreams++;
          if (injecting("close")) throw new IOException("synthetic stream close failure");
        }
      };
    }

    @Override
    public void close() throws IOException {
      root.close();
      assertTrue(descriptors.isEmpty(), "all caller/child FDs closed");
      assertEquals(openedStreams, closedStreams);
    }
  }
}
