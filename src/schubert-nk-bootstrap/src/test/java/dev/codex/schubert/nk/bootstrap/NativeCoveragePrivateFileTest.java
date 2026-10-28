package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Actual host held inode byte/owner oracle; not the native outer fixed-path/process admission. */
final class NativeCoveragePrivateFileTest {
  private static final String FIXTURE_REPLACE_197D1A17 = "replace";
  private static final String FIXTURE_NLINK_3DDD828B = "nlink";
  private static final byte[] GOLDEN = {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1};
  private static final String NAME = "1234567890abcdef1234567890abcdef.terminal.exec";
  @TempDir Path root;

  private static final String PUBLIC_CGROUP = "0::/system.slice/schubert-nk-api.service\n";

  private static ChildStartupContext.Observed observed(int difference) {
    return new ChildStartupContext.Observed(
        difference == 1 ? "PUBLIC_BOOT_B" : "PUBLIC_BOOT_A",
        difference == 2 ? 43 : 42,
        difference == 3 ? 101 : 100,
        difference == 4 ? 201 : 200,
        difference == 5 ? 202 : 201,
        difference == 6 ? List.of(201L, 203L) : List.of(201L, 202L),
        difference == 7 ? "0::/PUBLIC_OTHER\n" : PUBLIC_CGROUP,
        difference != 8,
        difference != 9);
  }

  private static void processRefused(org.junit.jupiter.api.function.Executable operation) {
    var error = assertThrows(IOException.class, operation);
    assertEquals("fixed PT native capture unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  @Test
  void nexport598001OrdinaryObservedDataRequiresEveryRoleAndPrivilegeField() throws Exception {
    var fixed = new FixedServiceIdentity.Value(200, 201, List.of(201L, 202L));
    NativeCoveragePrivateFile.verifyOrdinaryProcess(fixed, observed(0), PUBLIC_CGROUP);
    for (int difference = 4; difference <= 9; difference++) {
      int field = difference;
      processRefused(
          () ->
              NativeCoveragePrivateFile.verifyOrdinaryProcess(
                  fixed, observed(field), PUBLIC_CGROUP));
    }
    processRefused(
        () -> NativeCoveragePrivateFile.verifyOrdinaryProcess(null, observed(0), PUBLIC_CGROUP));
    processRefused(
        () -> NativeCoveragePrivateFile.verifyOrdinaryProcess(fixed, null, PUBLIC_CGROUP));
    processRefused(() -> NativeCoveragePrivateFile.verifyOrdinaryProcess(fixed, observed(0), null));
    // Literal data validation is not a real UID/cgroup/native process or startup proof.
  }

  @Test
  void nexport598002EveryChangedFullObservedFieldAndMissingSnapshotRefusesAcceptance()
      throws Exception {
    var before = observed(0);
    NativeCoveragePrivateFile.verifySameOrdinaryProcess(before, observed(0));
    for (int difference = 1; difference <= 9; difference++) {
      int field = difference;
      processRefused(
          () -> NativeCoveragePrivateFile.verifySameOrdinaryProcess(before, observed(field)));
    }
    processRefused(() -> NativeCoveragePrivateFile.verifySameOrdinaryProcess(null, before));
    processRefused(() -> NativeCoveragePrivateFile.verifySameOrdinaryProcess(before, null));
  }

  private long uid() throws IOException {
    return Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:uid"));
  }

  private long gid() throws IOException {
    return Integer.toUnsignedLong((Integer) Files.getAttribute(root, "unix:gid"));
  }

  private OwnedTransferDirectory open(DirectoryCalls calls) throws Exception {
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwx------"));
    return OwnedTransferDirectory.open(calls, root);
  }

  @Test
  void nexport193001NewHeldBytesAreForcedClosedAndVerifiedWithoutMutation() throws Exception {
    var calls = new Calls();
    try (var directory = open(calls)) {
      NativeCoveragePrivateFile.write(
          directory, LinuxInodeSecurity.create(), uid(), gid(), NAME, GOLDEN);
      assertArrayEquals(GOLDEN, Files.readAllBytes(root.resolve(NAME)));
      assertEquals(0100600, Files.getAttribute(root.resolve(NAME), "unix:mode"));
      assertEquals(1, Files.getAttribute(root.resolve(NAME), "unix:nlink"));
      assertEquals(
          uid(),
          Integer.toUnsignedLong((Integer) Files.getAttribute(root.resolve(NAME), "unix:uid")));
      assertEquals(
          gid(),
          Integer.toUnsignedLong((Integer) Files.getAttribute(root.resolve(NAME), "unix:gid")));
      assertEquals(1, calls.syncs);
      assertEquals(1, calls.live.size());
      assertArrayEquals(new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1}, GOLDEN);
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void nexport193002ExistingRegularSymlinkAndPartialAreNeverOpenedForWrite() throws Exception {
    try (var directory = open(LinuxDirectoryCalls.create())) {
      Files.write(root.resolve(NAME), new byte[] {9});
      assertThrows(
          IOException.class,
          () ->
              NativeCoveragePrivateFile.write(
                  directory, LinuxInodeSecurity.create(), uid(), gid(), NAME, GOLDEN));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(root.resolve(NAME)));
      Files.createSymbolicLink(root.resolve("link.exec"), root.resolve(NAME));
      assertThrows(
          IOException.class,
          () ->
              NativeCoveragePrivateFile.write(
                  directory, LinuxInodeSecurity.create(), uid(), gid(), "link.exec", GOLDEN));
      assertTrue(Files.isSymbolicLink(root.resolve("link.exec")));
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(root.resolve(NAME)));
    }
  }

  @Test
  void nexport193003NullSizeAndDirectoryOwnerPermissionRejectBeforeCreate() throws Exception {
    var calls = new Calls();
    try (var directory = open(calls)) {
      var security = LinuxInodeSecurity.create();
      assertThrows(
          IllegalArgumentException.class,
          () -> NativeCoveragePrivateFile.write(null, security, uid(), gid(), NAME, GOLDEN));
      assertThrows(
          IllegalArgumentException.class,
          () -> NativeCoveragePrivateFile.write(directory, null, uid(), gid(), NAME, GOLDEN));
      assertThrows(
          IllegalArgumentException.class,
          () -> NativeCoveragePrivateFile.write(directory, security, uid(), gid(), null, GOLDEN));
      assertThrows(
          IllegalArgumentException.class,
          () -> NativeCoveragePrivateFile.write(directory, security, uid(), gid(), NAME, null));
      for (int size : new int[] {0, 4, 16 * 1024 * 1024 + 1})
        assertThrows(
            IOException.class,
            () ->
                NativeCoveragePrivateFile.write(
                    directory, security, uid(), gid(), NAME, new byte[size]));
      assertThrows(
          IOException.class,
          () ->
              NativeCoveragePrivateFile.write(directory, security, uid() + 1, gid(), NAME, GOLDEN));
      assertThrows(
          IOException.class,
          () ->
              NativeCoveragePrivateFile.write(directory, security, uid(), gid() + 1, NAME, GOLDEN));
      Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwxr-x---"));
      assertThrows(
          IOException.class,
          () -> NativeCoveragePrivateFile.write(directory, security, uid(), gid(), NAME, GOLDEN));
      assertEquals(0, calls.creates);
      assertEquals(1, calls.live.size());
    }
    assertTrue(calls.live.isEmpty());
  }

  @Test
  void nexport193004CloseSyncAndNamespaceReplacementAreNonSuccessAndPreserveBytes()
      throws Exception {
    for (String fault : List.of("close", "sync", FIXTURE_REPLACE_197D1A17)) {
      var calls = new Calls();
      calls.fault = fault;
      String name = fault + ".exec";
      calls.output = root.resolve(name);
      try (var directory = open(calls)) {
        assertThrows(
            IOException.class,
            () ->
                NativeCoveragePrivateFile.write(
                    directory, LinuxInodeSecurity.create(), uid(), gid(), name, GOLDEN));
        assertArrayEquals(
            GOLDEN,
            Files.readAllBytes(
                fault.equals(FIXTURE_REPLACE_197D1A17)
                    ? root.resolve(name + ".saved")
                    : root.resolve(name)));
        if (fault.equals(FIXTURE_REPLACE_197D1A17))
          assertArrayEquals(new byte[] {9}, Files.readAllBytes(root.resolve(name)));
        assertEquals(1, calls.live.size());
        calls.fault = "";
        assertThrows(
            IOException.class,
            () ->
                NativeCoveragePrivateFile.write(
                    directory, LinuxInodeSecurity.create(), uid(), gid(), name, GOLDEN));
        assertEquals(1, calls.live.size());
      }
      assertTrue(calls.live.isEmpty());
    }
  }

  @Test
  void nexport193005MetadataMissingNullUnknownAclLinksAndIdentityRejectIndependently()
      throws Exception {
    var golden =
        Map.<String, Object>of(
            "uid",
            999,
            "gid",
            981,
            "mode",
            0100600,
            FIXTURE_NLINK_3DDD828B,
            1,
            "dev",
            17L,
            "ino",
            23L);
    assertEquals(
        new NativeCoveragePrivateFile.Identity(999, 981, 0100600, 1, 17, 23),
        NativeCoveragePrivateFile.checked(golden, new byte[0], 999, 981, 0100600));
    assertThrows(
        IOException.class,
        () -> NativeCoveragePrivateFile.checked(null, new byte[0], 999, 981, 0100600));
    assertThrows(
        IOException.class,
        () -> NativeCoveragePrivateFile.checked(golden, null, 999, 981, 0100600));
    assertThrows(
        IOException.class,
        () -> NativeCoveragePrivateFile.checked(golden, new byte[] {1}, 999, 981, 0100600));
    for (String field : golden.keySet())
      for (Object value : Arrays.asList(null, "unknown")) {
        var bad = new HashMap<>(golden);
        bad.put(field, value);
        assertThrows(
            IOException.class,
            () -> NativeCoveragePrivateFile.checked(bad, new byte[0], 999, 981, 0100600),
            field);
        bad.remove(field);
        assertThrows(
            IOException.class,
            () -> NativeCoveragePrivateFile.checked(bad, new byte[0], 999, 981, 0100600),
            field);
      }
    for (String field : golden.keySet()) {
      var bad = new HashMap<>(golden);
      switch (field) {
        case "uid", "gid", "mode", FIXTURE_NLINK_3DDD828B -> bad.put(field, 0);
        case "dev", "ino" -> bad.put(field, 0L);
        default -> fail("unregistered fixture field");
      }
      assertThrows(
          IOException.class,
          () -> NativeCoveragePrivateFile.checked(bad, new byte[0], 999, 981, 0100600),
          field);
    }
    var linked = new HashMap<>(golden);
    linked.put(FIXTURE_NLINK_3DDD828B, 2);
    assertThrows(
        IOException.class,
        () -> NativeCoveragePrivateFile.checked(linked, new byte[0], 999, 981, 0100600));
    var directory = new HashMap<>(linked);
    directory.put("mode", 040700);
    assertEquals(
        new NativeCoveragePrivateFile.Identity(999, 981, 040700, 2, 17, 23),
        NativeCoveragePrivateFile.checked(directory, new byte[0], 999, 981, 040700));
    directory.put(FIXTURE_NLINK_3DDD828B, 1);
    assertThrows(
        IOException.class,
        () -> NativeCoveragePrivateFile.checked(directory, new byte[0], 999, 981, 040700));
  }

  private static final class Calls implements DirectoryCalls {
    final DirectoryCalls actual = LinuxDirectoryCalls.create();
    final Set<Integer> live = new HashSet<>();
    String fault = "";
    Path output;
    int createdFd = -1;
    int creates;
    int syncs;

    private int own(int fd) {
      assertTrue(live.add(fd));
      return fd;
    }

    @Override
    public int openRoot() throws StorageIoException {
      return own(actual.openRoot());
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      return own(actual.openDirectory(parent, name));
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      return own(actual.openEntry(parent, name));
    }

    @Override
    public int createFile(int parent, String name) throws StorageIoException {
      return own(actual.createFile(parent, name));
    }

    @Override
    public int createPrivateFile(int parent, String name) throws StorageIoException {
      creates++;
      createdFd = own(actual.createPrivateFile(parent, name));
      return createdFd;
    }

    @Override
    public void createDirectory(int parent, String name) throws StorageIoException {
      actual.createDirectory(parent, name);
    }

    @Override
    public void publish(int parent, String from, String to) throws StorageIoException {
      actual.publish(parent, from, to);
    }

    @Override
    public void unlink(int parent, String name) throws StorageIoException {
      actual.unlink(parent, name);
    }

    @Override
    public void sync(int fd) throws StorageIoException {
      syncs++;
      actual.sync(fd);
      if (fault.equals("sync")) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }

    @Override
    public void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd));
      actual.close(fd);
      if (fd == createdFd) {
        createdFd = -1; // The consumed descriptor number may immediately be reused for readback.
        if (fault.equals("close"))
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        if (fault.equals(FIXTURE_REPLACE_197D1A17)) {
          try {
            Files.move(output, output.resolveSibling(output.getFileName() + ".saved"));
            Files.write(output, new byte[] {9});
          } catch (IOException failure) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }
      }
    }
  }
}
