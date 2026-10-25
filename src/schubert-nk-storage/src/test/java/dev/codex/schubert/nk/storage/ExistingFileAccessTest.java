package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent inode, Unix attributes, byte and fault oracles. NK-MED-001; PT-MED-021..025. */
class ExistingFileAccessTest {
  @TempDir Path root;
  private StorageIdentity identity;

  @BeforeEach
  void prepare() throws Exception {
    directory(root);
    var attrs = Files.readAttributes(root, java.nio.file.attribute.PosixFileAttributes.class);
    identity = new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
  }

  @Test
  void med021NestedAndLargeAssetsReadExactBytesAndCloseChannels() throws Exception {
    Path nested = Files.createDirectories(root.resolve("music/日本語 folder"));
    directory(root.resolve("music"));
    directory(nested);
    file(nested.resolve("音源.ogg"));
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var access = new ExistingFileAccess(held, identity);
      AtomicReference<SeekableByteChannel> owned = new AtomicReference<>();
      assertArrayEquals(
          new byte[] {1, 2, 3},
          access.read(
              List.of("music", "日本語 folder", "音源.ogg"),
              3,
              channel -> {
                owned.set(channel);
                assertTrue(channel.isOpen());
                return bytes(channel);
              }));
      assertFalse(owned.get().isOpen());
      assertEquals(Boolean.TRUE, held.atDirectory(p -> Files.isDirectory(p)));
      Path large = root.resolve("large.flac");
      file(large);
      try (var writer = FileChannel.open(large, StandardOpenOption.WRITE)) {
        writer.position(48_000_001L);
        assertEquals(3, writer.write(ByteBuffer.wrap(new byte[] {11, 12, 13})));
      }
      assertArrayEquals(
          new byte[] {11, 12, 13},
          access.read(
              List.of("large.flac"),
              48_000_004L,
              channel -> {
                assertEquals(48_000_004L, channel.size());
                channel.position(48_000_001L);
                return bytes(channel);
              }));
      assertEquals(48_000_004L, Files.size(large));
    }
  }

  @Test
  void med022NullSizeAndSegmentContractsFailBeforeContentRead() throws Exception {
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      assertThrows(NullPointerException.class, () -> new ExistingFileAccess(null, identity));
      assertThrows(NullPointerException.class, () -> new ExistingFileAccess(held, null));
      assertThrows(NullPointerException.class, () -> new ExistingFileAccess(held, identity, null));
      var access = new ExistingFileAccess(held, identity);
      ExistingFileAccess.ReadOperation<Boolean> never = channel -> fail("invalid request read");
      assertThrows(NullPointerException.class, () -> access.read(null, 3, never));
      assertThrows(NullPointerException.class, () -> access.read(List.of("x"), 3, null));
      assertThrows(
          NullPointerException.class, () -> access.read(Arrays.asList("x", null), 3, never));
      assertThrows(IllegalArgumentException.class, () -> access.read(List.of(), 3, never));
      assertThrows(
          IllegalArgumentException.class,
          () -> access.read(java.util.Collections.nCopies(257, "a"), 3, never));
      for (long size : new long[] {0, -1, Long.MIN_VALUE}) {
        assertThrows(IllegalArgumentException.class, () -> access.read(List.of("x"), size, never));
      }
      for (String name : new String[] {"", ".", "..", "a/b", "a\0b"}) {
        assertThrows(IllegalArgumentException.class, () -> access.read(List.of(name), 3, never));
        assertThrows(
            IllegalArgumentException.class, () -> access.read(List.of(name, "x"), 3, never));
      }
      List<String> names = new ArrayList<>();
      Path current = root;
      for (int i = 0; i < 255; i++) {
        names.add("a");
        current = Files.createDirectory(current.resolve("a"));
        directory(current);
      }
      file(current.resolve("x"));
      names.add("x");
      assertArrayEquals(new byte[] {1, 2, 3}, access.read(names, 3, ExistingFileAccessTest::bytes));
    }
  }

  @Test
  void med023LinksMissingAndWrongUnixAttributesNeverExposeContent() throws Exception {
    Path nested = Files.createDirectory(root.resolve("nested"));
    directory(nested);
    Path target = nested.resolve("x");
    file(target);
    var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
    var access = new ExistingFileAccess(held, identity);
    ExistingFileAccess.ReadOperation<Boolean> never = c -> fail("invalid inode content read");
    try (held) {
      reject(() -> access.read(List.of("missing"), 3, never));
      reject(() -> access.read(List.of("missing", "x"), 3, never));
      reject(() -> access.read(List.of("nested", "x", "x"), 3, never));
      Files.createSymbolicLink(root.resolve("link"), nested);
      reject(() -> access.read(List.of("link", "x"), 3, never));
      reject(() -> access.read(List.of("link"), 3, never));
      Files.createSymbolicLink(nested.resolve("symlink"), target);
      reject(() -> access.read(List.of("nested", "symlink"), 3, never));
      Files.createLink(nested.resolve("hard"), target);
      reject(() -> access.read(List.of("nested", "x"), 3, never));
      Files.delete(nested.resolve("hard"));
      reject(() -> access.read(List.of("nested", "x"), 4, never));
      for (Path changed : List.of(root, nested, target)) {
        var before = Files.getPosixFilePermissions(changed);
        Files.setPosixFilePermissions(changed, PosixFilePermissions.fromString("rwx------"));
        reject(() -> access.read(List.of("nested", "x"), 3, never));
        assertEquals(
            PosixFilePermissions.fromString("rwx------"), Files.getPosixFilePermissions(changed));
        Files.setPosixFilePermissions(changed, before);
      }
      reject(
          () ->
              new ExistingFileAccess(held, new StorageIdentity("different", identity.group()))
                  .read(List.of("nested", "x"), 3, never));
      reject(
          () ->
              new ExistingFileAccess(held, new StorageIdentity(identity.owner(), "different"))
                  .read(List.of("nested", "x"), 3, never));
      assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(target));
      assertTrue(Files.isSymbolicLink(nested.resolve("symlink")));
      assertFalse(Files.exists(root.resolve("missing")));
    }
    reject(() -> access.read(List.of("nested", "x"), 3, never));
  }

  @Test
  void med024OpenReadAttributeAndCloseFailuresAreRedactedAndOwned() throws Exception {
    compoundOwnership();
    Path nested = Files.createDirectory(root.resolve("nested"));
    directory(nested);
    file(nested.resolve("x"));
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      for (String fault :
          List.of(
              "attrs1",
              "attrs2",
              "attrs3",
              "attrs4",
              "unsupported",
              "open",
              "size1",
              "size2",
              "wrong-size1",
              "wrong-size2",
              "close",
              "read",
              "callback-close",
              "bad-post")) {
        FaultIo io = new FaultIo(fault);
        var access = new ExistingFileAccess(held, identity, io);
        reject(
            () ->
                access.read(
                    List.of("nested", "x"),
                    3,
                    channel -> {
                      if (fault.equals("callback-close"))
                        throw new IOException("SYNTHETIC_PRIVATE_PATH");
                      return bytes(channel);
                    }));
        assertEquals(io.opens, io.closes);
        assertEquals(io.opens, io.channels.size());
        assertTrue(io.channels.stream().noneMatch(SeekableByteChannel::isOpen));
        assertEquals(Boolean.TRUE, held.atDirectory(Files::isDirectory));
        if (List.of("attrs1", "attrs2", "attrs3", "unsupported", "open").contains(fault)) {
          assertEquals(0, io.opens);
        }
      }
    }
    assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(nested.resolve("x")));
  }

  @Test
  void med025ConcurrentAndReplacedNamesRetainIndependentInodes() throws Exception {
    Path nested = Files.createDirectory(root.resolve("nested"));
    directory(nested);
    file(nested.resolve("x"));
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var access = new ExistingFileAccess(held, identity);
      synchronized (held) {
        var tasks = new ArrayList<java.util.concurrent.Future<byte[]>>();
        for (int i = 0; i < 100; i++) {
          tasks.add(
              executor.submit(
                  () -> {
                    FaultIo io = new FaultIo("none");
                    byte[] result =
                        new ExistingFileAccess(held, identity, io)
                            .read(
                                List.of("nested", "x"),
                                3,
                                channel -> {
                                  assertEquals(0, channel.position());
                                  return bytes(channel);
                                });
                    assertEquals(1, io.opens);
                    assertEquals(1, io.closes);
                    assertFalse(io.channels.getFirst().isOpen());
                    return result;
                  }));
        }
        for (var task : tasks)
          assertArrayEquals(new byte[] {1, 2, 3}, task.get(10, TimeUnit.SECONDS));
      }
      Path outside = Files.createDirectory(root.resolve("outside"));
      Files.write(outside.resolve("x"), new byte[] {9, 9, 9});
      assertArrayEquals(
          new byte[] {1, 2, 3},
          access.read(
              List.of("nested", "x"),
              3,
              channel -> {
                Files.move(nested.resolve("x"), nested.resolve("saved"));
                Files.createSymbolicLink(nested.resolve("x"), outside.resolve("x"));
                Files.move(nested, root.resolve("retained"));
                Files.createSymbolicLink(nested, outside);
                return bytes(channel);
              }));
      assertArrayEquals(new byte[] {9, 9, 9}, Files.readAllBytes(outside.resolve("x")));
      assertArrayEquals(
          new byte[] {1, 2, 3},
          access.read(List.of("retained", "saved"), 3, ExistingFileAccessTest::bytes));
      // Replace the configured root after admission. Held root must still select its old inode.
      Path old = root.resolveSibling(root.getFileName() + "-retained");
      Files.move(root, old);
      try {
        Files.createDirectory(root);
        assertArrayEquals(
            new byte[] {1, 2, 3},
            access.read(List.of("retained", "saved"), 3, ExistingFileAccessTest::bytes));
      } finally {
        Files.delete(root);
        Files.move(old, root);
      }
    }
  }

  private static void directory(Path path) throws IOException {
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-x---"));
  }

  private static void file(Path path) throws IOException {
    Files.write(path, new byte[] {1, 2, 3});
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rw-r-----"));
  }

  private static byte[] bytes(SeekableByteChannel channel) throws IOException {
    ByteBuffer bytes = ByteBuffer.allocate(3);
    while (bytes.hasRemaining()) assertTrue(channel.read(bytes) > 0);
    return bytes.array();
  }

  private static void reject(org.junit.jupiter.api.function.Executable action) {
    StorageIoException failure = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private void compoundOwnership() throws Exception {
    Path nested = Files.createDirectory(root.resolve("compound"));
    directory(nested);
    file(nested.resolve("x"));
    for (boolean childClose : List.of(false, true))
      for (boolean known : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("public compound"),
                new NullPointerException("public compound"),
                new AssertionError("public compound"))) {
          var childDescriptors = new HashSet<Integer>();
          var childCloses = new AtomicInteger();
          DirectoryCalls nativeCalls = LinuxDirectoryCalls.create();
          DirectoryCalls calls =
              (DirectoryCalls)
                  Proxy.newProxyInstance(
                      getClass().getClassLoader(),
                      new Class<?>[] {DirectoryCalls.class},
                      (proxy, method, arguments) -> {
                        boolean released =
                            method.getName().equals("close")
                                && childDescriptors.remove((Integer) arguments[0]);
                        Object result;
                        try {
                          result = method.invoke(nativeCalls, arguments);
                        } catch (InvocationTargetException failure) {
                          throw failure.getCause();
                        }
                        if (method.getName().equals("openDirectory")
                            && arguments[1].equals("compound"))
                          assertTrue(childDescriptors.add((Integer) result));
                        if (released) {
                          childCloses.incrementAndGet();
                          if (childClose) raiseUnknown(unknown);
                        }
                        return result;
                      });
          try (var held = OwnedTransferDirectory.open(calls, root)) {
            var io = new FaultIo("none");
            if (!childClose) io.closeFailure = unknown;
            var access = new ExistingFileAccess(held, identity, io);
            assertSame(
                unknown,
                assertThrows(
                    unknown.getClass(),
                    () ->
                        access.read(
                            List.of("compound", "x"),
                            3,
                            channel -> {
                              assertArrayEquals(new byte[] {1, 2, 3}, bytes(channel));
                              if (known) throw new IOException("public I/O");
                              raiseUnknown(unknown);
                              return true;
                            })));
            assertEquals(1, io.opens);
            assertEquals(1, io.closes);
            assertTrue(io.channels.stream().noneMatch(SeekableByteChannel::isOpen));
            assertEquals(1, childCloses.get());
            assertTrue(childDescriptors.isEmpty());
            assertEquals(Boolean.TRUE, held.atDirectory(Files::isDirectory));
            assertEquals(known ? 0 : 1, unknown.getSuppressed().length);
            for (Throwable secondary : unknown.getSuppressed())
              reject(
                  () -> {
                    throw secondary;
                  });
          }
          assertArrayEquals(new byte[] {1, 2, 3}, Files.readAllBytes(nested.resolve("x")));
        }
  }

  private static void raiseUnknown(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static final class FaultIo implements ExistingFileAccess.Io {
    final String fault;
    final List<SeekableByteChannel> channels = new ArrayList<>();
    int attributes;
    int opens;
    int closes;
    Throwable closeFailure;

    FaultIo(String fault) {
      this.fault = fault;
    }

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      attributes++;
      if (fault.equals("attrs" + attributes)) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      if (fault.equals("unsupported"))
        throw new UnsupportedOperationException("SYNTHETIC_PRIVATE_PATH");
      Map<String, Object> result =
          new HashMap<>(Files.readAttributes(held, "unix:owner,group,mode,nlink,size"));
      if (fault.equals("bad-post") && attributes == 4) result.put("nlink", 2);
      return result;
    }

    @Override
    public SeekableByteChannel openReadOnly(Path path) throws IOException {
      if (fault.equals("open")) throw new IOException("SYNTHETIC_PRIVATE_PATH");
      SeekableByteChannel delegate = FileChannel.open(path, StandardOpenOption.READ);
      channels.add(delegate);
      opens++;
      return new SeekableByteChannel() {
        int sizes;

        @Override
        public int read(ByteBuffer bytes) throws IOException {
          if (fault.equals("read")) throw new IOException("SYNTHETIC_PRIVATE_PATH");
          return delegate.read(bytes);
        }

        @Override
        public int write(ByteBuffer bytes) {
          return fail("read-only capability write");
        }

        @Override
        public long position() throws IOException {
          return delegate.position();
        }

        @Override
        public SeekableByteChannel position(long value) throws IOException {
          delegate.position(value);
          return this;
        }

        @Override
        public long size() throws IOException {
          sizes++;
          if (fault.equals("size" + sizes)) throw new IOException("SYNTHETIC_PRIVATE_PATH");
          if (fault.equals("wrong-size" + sizes)) return 99;
          return delegate.size();
        }

        @Override
        public SeekableByteChannel truncate(long value) {
          return fail("read-only capability truncate");
        }

        @Override
        public boolean isOpen() {
          return delegate.isOpen();
        }

        @Override
        public void close() throws IOException {
          closes++;
          delegate.close();
          if (closeFailure != null) raiseUnknown(closeFailure);
          if (fault.equals("close") || fault.equals("callback-close"))
            throw new IOException("SYNTHETIC_PRIVATE_PATH");
        }
      };
    }
  }
}
