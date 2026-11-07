package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

/** PT-DIRFACT-001..003 / SS333 SSC308: real host root O_PATH, no VM/role/start authority. */
final class OwnedDirectoryFactoryTest {
  @Test
  void dirfactory001RootWrapperIsSameKernelInodeAndClosesOnce() throws Exception {
    var calls = new Calls();
    var root = OwnedTransferDirectory.openRoot(calls);
    try {
      assertEquals(1, calls.opens);
      assertEquals(0, calls.closes);
      boolean sameInode = root.atDirectory(held -> Files.isSameFile(held, Path.of("/")));
      assertTrue(sameInode);
      root.close();
      assertEquals(1, calls.closes);
      root.close();
      assertEquals(1, calls.closes);
      var failure =
          assertThrows(StorageIoException.class, () -> root.atDirectory(held -> Boolean.TRUE));
      assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    } finally {
      root.close();
    }
    assertEquals(1, calls.closes);
  }

  @Test
  void dirfactory002NullAndFailedOpenHaveNoOwnedDescriptorToRelease() {
    assertThrows(NullPointerException.class, () -> OwnedTransferDirectory.openRoot(null));
    for (var reason : StorageIoException.Reason.values()) {
      var calls = new Calls();
      var failure = new StorageIoException(reason);
      calls.openFailure = failure;
      assertSame(
          failure,
          assertThrows(StorageIoException.class, () -> OwnedTransferDirectory.openRoot(calls)));
      assertEquals(1, calls.opens);
      assertEquals(0, calls.closes);
    }
  }

  @Test
  void dirfactory003CloseFailureConsumesDescriptorAndConfiguredRootStillRefusesSlash()
      throws Exception {
    var calls = new Calls();
    var root = OwnedTransferDirectory.openRoot(calls);
    var failure = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    calls.closeFailure = failure;
    assertSame(failure, assertThrows(StorageIoException.class, root::close));
    assertEquals(1, calls.closes);
    root.close();
    assertEquals(1, calls.closes);
    var unopened = new Calls();
    assertThrows(
        IllegalArgumentException.class, () -> OwnedTransferDirectory.open(unopened, Path.of("/")));
    assertEquals(0, unopened.opens);
    assertEquals(0, unopened.closes);
  }

  private static final class Calls implements DirectoryCalls {
    private final DirectoryCalls actual = LinuxDirectoryCalls.create();
    private int opens;
    private int closes;
    private @org.jspecify.annotations.Nullable StorageIoException openFailure;
    private @org.jspecify.annotations.Nullable StorageIoException closeFailure;

    @Override
    public int openRoot() throws StorageIoException {
      opens++;
      if (openFailure != null) throw openFailure;
      return actual.openRoot();
    }

    @Override
    public void close(int descriptor) throws StorageIoException {
      closes++;
      actual.close(descriptor);
      if (closeFailure != null) throw closeFailure;
    }

    @Override
    public int openDirectory(int parent, String name) {
      throw new AssertionError("unexpected traversal");
    }

    @Override
    public int openEntry(int parent, String name) {
      throw new AssertionError("unexpected entry");
    }

    @Override
    public int createFile(int parent, String name) {
      throw new AssertionError("unexpected create");
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw new AssertionError("unexpected create");
    }

    @Override
    public void publish(int parent, String part, String ready) {
      throw new AssertionError("unexpected publish");
    }

    @Override
    public void unlink(int parent, String name) {
      throw new AssertionError("unexpected unlink");
    }

    @Override
    public void sync(int parent) {
      throw new AssertionError("unexpected sync");
    }
  }
}
