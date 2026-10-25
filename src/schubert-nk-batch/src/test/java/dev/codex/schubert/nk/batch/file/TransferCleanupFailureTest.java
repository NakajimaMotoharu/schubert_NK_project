package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.HashSet;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS341/343/SSC118: real retained FDs, one failed unlink does not erase or count a success. */
final class TransferCleanupFailureTest {
  @TempDir Path temporary;

  @Test
  void transferFailure001OneUnlinkFailureRetainsBytesCountsWarningAndContinuesOtherFile()
      throws Exception {
    Path root = Files.createDirectory(temporary.resolve("transfer"));
    Path date = Files.createDirectory(root.resolve("20260929"));
    for (Path p : new Path[] {root, date})
      Files.setPosixFilePermissions(p, PosixFilePermissions.fromString("rwxr-x---"));
    String failed = "11111111-2222-4333-8444-555555555555.part";
    String succeeds = "21111111-2222-4333-8444-555555555555.ready";
    Instant cutoff = Instant.parse("2026-09-30T00:00:00Z");
    Files.write(date.resolve(failed), new byte[] {1, 2, 3});
    Files.write(date.resolve(succeeds), new byte[] {4, 5});
    for (String name : new String[] {failed, succeeds}) {
      Files.setPosixFilePermissions(
          date.resolve(name), PosixFilePermissions.fromString("rw-r-----"));
      Files.setLastModifiedTime(date.resolve(name), FileTime.from(cutoff.minusSeconds(1)));
    }
    var nativeCalls = LinuxDirectoryCalls.create();
    Set<Integer> owned = new HashSet<>();
    var calls =
        new DirectoryCalls() {
          private int retain(int fd) {
            assertTrue(owned.add(fd));
            return fd;
          }

          public int openRoot() throws StorageIoException {
            return retain(nativeCalls.openRoot());
          }

          public int openDirectory(int parent, String name) throws StorageIoException {
            return retain(nativeCalls.openDirectory(parent, name));
          }

          public int openEntry(int parent, String name) throws StorageIoException {
            return retain(nativeCalls.openEntry(parent, name));
          }

          public int createFile(int parent, String name) {
            throw new AssertionError("cleanup must not create files");
          }

          public void createDirectory(int parent, String name) {
            throw new AssertionError("cleanup must not create directories");
          }

          public void publish(int parent, String part, String ready) {
            throw new AssertionError("cleanup must not publish");
          }

          public void unlink(int parent, String name) throws StorageIoException {
            if (name.equals(failed))
              throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
            nativeCalls.unlink(parent, name);
          }

          public void removeEmptyDirectory(int parent, String name) throws StorageIoException {
            nativeCalls.removeEmptyDirectory(parent, name);
          }

          public void sync(int parent) throws StorageIoException {
            nativeCalls.sync(parent);
          }

          public void close(int fd) throws StorageIoException {
            assertTrue(owned.remove(fd), "each FD is consumed exactly once");
            nativeCalls.close(fd);
          }
        };
    long uid = Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid"));
    long gid = Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:gid"));
    try (var held = OwnedTransferDirectory.open(calls, root)) {
      var result =
          new TransferCleanup(held, LinuxInodeSecurity.create(), uid, gid, () -> {})
              .execute(cutoff);
      assertEquals(new TransferCleanup.Outcome(2, 1, 1, 0, 2), result);
      assertEquals(BatchStepResult.Status.WARNING, result.result().status());
      assertEquals(BatchStepResult.Reason.IO_FAILURE, result.result().reason());
      assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(date.resolve(failed)));
      assertFalse(Files.exists(date.resolve(succeeds)));
      assertTrue(Files.isDirectory(date), "nonempty date/root must be retained");
    }
    assertTrue(owned.isEmpty(), "all actual Linux FDs closed after recoverable file failure");
    assertTrue(Files.isDirectory(root));
  }
}
