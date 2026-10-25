package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SSC118/TRANSFER001..003: real Linux retained FDs, independent fixed files/counts. */
final class TransferCleanupTest {
  @TempDir Path fixture;
  private static final Instant CUTOFF = Instant.parse("2026-09-30T00:00:00Z");
  private static final String A = "11111111-2222-4333-8444-555555555555.part";
  private static final String B = "21111111-2222-4333-8444-555555555555.ready";

  @Test
  void transfer001DeletesOldRegularFilesAndOnlyEmptyCanonicalDatesKeepsRoot() throws Exception {
    Path root = directory(fixture.resolve("transfer"));
    Path date = directory(root.resolve("20260929"));
    file(date.resolve(A), new byte[] {1, 2, 3}, CUTOFF.minusSeconds(1));
    file(date.resolve(B), new byte[] {4, 5}, CUTOFF.minusSeconds(2));
    directory(root.resolve("20260928"));
    var guard = new AtomicInteger();
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var outcome = service(held, root, guard::incrementAndGet).execute(CUTOFF);
      assertEquals(new TransferCleanup.Outcome(2, 2, 0, 0, 5), outcome);
      assertEquals(BatchStepResult.Status.SUCCESS, outcome.result().status());
      assertEquals(BatchStepResult.Reason.NONE, outcome.result().reason());
      assertEquals("TransferCleanupOutcome[counts=<redacted>]", outcome.toString());
      assertTrue(guard.get() > 10);
    }
    assertTrue(Files.isDirectory(root));
    try (var stream = Files.list(root)) {
      assertEquals(0, stream.count());
    }
  }

  @Test
  void transfer002KeepsBoundaryFutureUnknownSymlinkHardlinkBadModeAndDepthThree() throws Exception {
    Path root = directory(fixture.resolve("transfer"));
    Path date = directory(root.resolve("20260929"));
    file(date.resolve(A), new byte[] {1, 2, 3}, CUTOFF.minusSeconds(1));
    file(date.resolve(B), new byte[] {4, 5}, CUTOFF);
    file(
        date.resolve("31111111-2222-4333-8444-555555555555.part"),
        new byte[] {6},
        CUTOFF.plusSeconds(1));
    file(date.resolve("unknown.part"), new byte[] {7}, CUTOFF.minusSeconds(1));
    Path outside = file(fixture.resolve("outside"), new byte[] {8, 9}, CUTOFF.minusSeconds(1));
    Files.createSymbolicLink(date.resolve("41111111-2222-4333-8444-555555555555.ready"), outside);
    Files.createLink(date.resolve("51111111-2222-4333-8444-555555555555.part"), outside);
    Path wrong =
        file(
            date.resolve("61111111-2222-4333-8444-555555555555.part"),
            new byte[] {10},
            CUTOFF.minusSeconds(1));
    Files.setPosixFilePermissions(wrong, PosixFilePermissions.fromString("rw-------"));
    Path nested = directory(date.resolve("20260928"));
    file(nested.resolve(A), new byte[] {11}, CUTOFF.minusSeconds(1));
    file(
        date.resolve("AAAAAAAA-2222-4333-8444-555555555555.part"),
        new byte[] {12},
        CUTOFF.minusSeconds(1));
    directory(root.resolve("20260230"));
    file(root.resolve("note"), new byte[] {13}, CUTOFF.minusSeconds(1));
    Files.createSymbolicLink(root.resolve("20260928"), fixture);
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var result = service(held, root, () -> {}).execute(CUTOFF);
      assertEquals(new TransferCleanup.Outcome(1, 1, 0, 11, 3), result);
      assertEquals(BatchStepResult.Status.WARNING, result.result().status());
      assertEquals(BatchStepResult.Reason.PROTECTED_RECORDS, result.result().reason());
    }
    assertFalse(Files.exists(date.resolve(A)));
    assertTrue(Files.exists(date.resolve(B)));
    assertArrayEquals(new byte[] {8, 9}, Files.readAllBytes(outside));
    assertArrayEquals(new byte[] {11}, Files.readAllBytes(nested.resolve(A)));
    assertTrue(Files.isSymbolicLink(root.resolve("20260928")));
  }

  @Test
  void transfer003RetainedRootIsNotRedirectedAndFailedGuardDoesNotDelete() throws Exception {
    Path root = directory(fixture.resolve("transfer"));
    Path date = directory(root.resolve("20260929"));
    file(date.resolve(A), new byte[] {1, 2, 3}, CUTOFF.minusSeconds(1));
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      Path old = fixture.resolve("held-old");
      Files.move(root, old);
      directory(root);
      Path newDate = directory(root.resolve("20260929"));
      file(newDate.resolve(A), new byte[] {7, 8}, CUTOFF.minusSeconds(1));
      var failed = new AtomicInteger();
      assertThrows(
          IOException.class,
          () ->
              service(
                      held,
                      old,
                      () -> {
                        if (failed.incrementAndGet() == 2)
                          throw new IOException("synthetic guard unavailable");
                      })
                  .execute(CUTOFF));
      assertArrayEquals(
          new byte[] {1, 2, 3}, Files.readAllBytes(old.resolve("20260929").resolve(A)));
      assertEquals(
          new TransferCleanup.Outcome(1, 1, 0, 0, 3), service(held, old, () -> {}).execute(CUTOFF));
      assertArrayEquals(new byte[] {7, 8}, Files.readAllBytes(newDate.resolve(A)));
      assertTrue(Files.isDirectory(old));
    }
  }

  @Test
  void nullInvalidIdentityAndRootModeRefuseWithoutMutation() throws Exception {
    Path root = directory(fixture.resolve("transfer"));
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var security = LinuxInodeSecurity.create();
      assertThrows(
          NullPointerException.class, () -> new TransferCleanup(null, security, 1, 1, () -> {}));
      assertThrows(
          NullPointerException.class, () -> new TransferCleanup(held, null, 1, 1, () -> {}));
      assertThrows(
          NullPointerException.class, () -> new TransferCleanup(held, security, 1, 1, null));
      for (long value : new long[] {-1, 0, 4294967295L}) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new TransferCleanup(held, security, value, 1, () -> {}));
        assertThrows(
            IllegalArgumentException.class,
            () -> new TransferCleanup(held, security, 1, value, () -> {}));
      }
      assertThrows(NullPointerException.class, () -> service(held, root, () -> {}).execute(null));
      Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwx------"));
      assertThrows(IOException.class, () -> service(held, root, () -> {}).execute(CUTOFF));
    }
    for (long[] bad :
        new long[][] {
          // PT-OPS-TRANSFER3046-001: each signed counter must independently reject negatives.
          {-1, 0, 0, 0, 0},
          {1, -1, 2, 0, 0},
          {1, 1, -1, 0, 0},
          {1, 2, 0, 0, 0},
          {1, 0, 0, 0, 0},
          {1, 0, 1, -1, 0},
          {1, 0, 1, 0, -1}
        })
      assertThrows(
          IllegalArgumentException.class,
          () -> new TransferCleanup.Outcome(bad[0], bad[1], bad[2], bad[3], bad[4]));
    var failed = new TransferCleanup.Outcome(1, 0, 1, 0, 0).result();
    assertEquals(BatchStepResult.Status.WARNING, failed.status());
    assertEquals(BatchStepResult.Reason.IO_FAILURE, failed.reason());
  }

  /** PT-OPS-TRANSFER3048-001: untrusted ownership/ACL/filesystem cannot begin deletion. */
  @Test
  void transfer3048001RootIdentityAclAndReadOnlyRefuseBeforeDeletingAnyByte() throws Exception {
    for (String fault : new String[] {"uid", "gid", "nullAcl", "acl", "readonly"}) {
      Path root = directory(fixture.resolve("transfer-" + fault));
      Path date = directory(root.resolve("20260929"));
      Path original = file(date.resolve(A), new byte[] {17, 23, 41}, CUTOFF.minusSeconds(1));
      long uid = Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid"));
      long gid = Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:gid"));
      InodeSecurityCalls security =
          new InodeSecurityCalls() {
            @Override
            public byte[] accessAcl(Path held, int maximumBytes) {
              assertEquals(44, maximumBytes);
              return fault.equals("nullAcl")
                  ? null
                  : fault.equals("acl") ? new byte[] {1} : new byte[0];
            }

            @Override
            public boolean readOnlyFilesystem(Path held) {
              return fault.equals("readonly");
            }

            @Override
            public long effectiveUid() {
              throw new AssertionError("not an ownership substitute");
            }
          };
      try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
        var subject =
            new TransferCleanup(
                held,
                security,
                fault.equals("uid") ? uid + 1 : uid,
                fault.equals("gid") ? gid + 1 : gid,
                () -> {});
        assertThrows(IOException.class, () -> subject.execute(CUTOFF), fault);
      }
      assertArrayEquals(new byte[] {17, 23, 41}, Files.readAllBytes(original), fault);
      assertTrue(Files.isDirectory(date), fault);
      assertTrue(Files.isDirectory(root), fault);
    }
  }

  /** PT-OPS-TRANSFER3048-002: eight-digit grammar does not make year zero a valid date. */
  @Test
  void transfer3048002CalendarLowerUpperBoundaryAndYearZeroAreIndependent() throws Exception {
    Path root = directory(fixture.resolve("calendar"));
    Path zero = directory(root.resolve("00000101"));
    Path lower = directory(root.resolve("00010101"));
    Path upper = directory(root.resolve("99991231"));
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var actual = service(held, root, () -> {}).execute(CUTOFF);
      assertEquals(new TransferCleanup.Outcome(0, 0, 0, 1, 0), actual);
      assertEquals(BatchStepResult.Status.WARNING, actual.result().status());
      assertEquals(BatchStepResult.Reason.PROTECTED_RECORDS, actual.result().reason());
    }
    assertTrue(Files.isDirectory(root));
    assertTrue(Files.isDirectory(zero));
    assertFalse(Files.exists(lower));
    assertFalse(Files.exists(upper));
  }

  private TransferCleanup service(
      OwnedTransferDirectory held, Path root, TransferCleanup.Guard guard) throws IOException {
    return new TransferCleanup(
        held,
        LinuxInodeSecurity.create(),
        Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid")),
        Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:gid")),
        guard);
  }

  private static Path directory(Path path) throws IOException {
    Files.createDirectory(path);
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-x---"));
    return path;
  }

  private static Path file(Path path, byte[] bytes, Instant modified) throws IOException {
    Files.write(path, bytes);
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rw-r-----"));
    Files.setLastModifiedTime(path, FileTime.from(modified));
    return path;
  }
}
