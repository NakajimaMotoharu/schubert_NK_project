package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.HashSet;
import java.util.Set;

/** Synthetic abc assets only. Counts actual native FD ownership and prohibits mutation calls. */
public final class MediaAssetFixture implements AutoCloseable {
  final Path root;
  final Path manifest;
  public final StorageIdentity identity;
  final Calls calls = new Calls();
  public final OwnedTransferDirectory held;

  public MediaAssetFixture(Path path) throws IOException {
    root = Files.createDirectory(path);
    mode(root, "rwxr-x---");
    var attrs = Files.readAttributes(root, PosixFileAttributes.class);
    identity = new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
    Path manifests = Files.createDirectory(root.resolve("manifests"));
    mode(manifests, "rwxr-x---");
    manifest = manifests.resolve("master.sha256");
    StringBuilder lines = new StringBuilder();
    for (String[] format : AssetChecksumManifestTest.FORMATS) {
      Path file = root.resolve(format[1]);
      Files.createDirectories(file.getParent());
      mode(file.getParent(), "rwxr-x---");
      Files.writeString(file, "abc");
      mode(file, "rw-r-----");
      lines.append(AssetChecksumManifestTest.line(format[1]));
    }
    Files.writeString(manifest, lines.toString());
    mode(manifest, "rw-r-----");
    held = OwnedTransferDirectory.open(calls, root);
    assertEquals(1, calls.live.size());
  }

  static void mode(Path path, String permissions) throws IOException {
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString(permissions));
  }

  void assertRootOwned() throws IOException {
    assertEquals(Boolean.TRUE, held.atDirectory(Files::isDirectory));
    assertEquals(1, calls.live.size());
  }

  @Override
  public void close() throws IOException {
    held.close();
    assertTrue(calls.live.isEmpty());
    assertEquals(calls.opens, calls.closes);
  }

  static final class Calls implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Set<Integer> live = new HashSet<>();
    int opens;
    int closes;
    int failCloseAfter = Integer.MAX_VALUE;
    int directoryOpens;
    int entryOpens;

    private synchronized int own(int fd) {
      assertTrue(live.add(fd), "live FD must not be reused");
      opens++;
      return fd;
    }

    @Override
    public int openRoot() throws StorageIoException {
      return own(delegate.openRoot());
    }

    @Override
    public synchronized int openDirectory(int parent, String name) throws StorageIoException {
      directoryOpens++;
      return own(delegate.openDirectory(parent, name));
    }

    @Override
    public synchronized int openEntry(int parent, String name) throws StorageIoException {
      entryOpens++;
      return own(delegate.openEntry(parent, name));
    }

    @Override
    public synchronized void close(int fd) throws StorageIoException {
      assertTrue(live.remove(fd), "close exactly once");
      delegate.close(fd);
      closes++;
      if (--failCloseAfter == 0)
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }

    @Override
    public int createFile(int parent, String name) {
      return fail("read-only file creation");
    }

    @Override
    public void createDirectory(int parent, String name) {
      fail("read-only mkdir");
    }

    @Override
    public void publish(int parent, String part, String ready) {
      fail("read-only publish");
    }

    @Override
    public void unlink(int parent, String name) {
      fail("read-only unlink");
    }

    @Override
    public void sync(int parent) {
      fail("read-only sync");
    }
  }
}
