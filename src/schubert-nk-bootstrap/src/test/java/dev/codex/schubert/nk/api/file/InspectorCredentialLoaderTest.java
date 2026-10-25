package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-DB-INBOX-129..140; real retained files/channels, explicitly synthetic privileged metadata. No
 * assertion of actual root-manager credential provisioning.
 */
final class InspectorCredentialLoaderTest {
  @TempDir Path temporary;
  private static final AesCredentialFile CURRENT = AesCredentialFile.CONTEXT_CURRENT;
  private static final AesCredentialFile PREVIOUS = AesCredentialFile.CONTEXT_PREVIOUS;
  private static final String SENTINEL = "UNTRUSTED_CREDENTIAL_IO_DETAIL";

  @Test
  void validAllIds() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (var id : AesCredentialFile.values()) {
        for (String version : List.of("v", "Abcdef0123456789")) {
          fixture.write(id, version);
          var io = new TestIo();
          var loader = fixture.loader(io);
          try (var material = loader.load(id).orElseThrow()) {
            assertEquals(version, material.version());
            byte[] actual = material.copyKey();
            try {
              assertArrayEquals(fixture.keys.get(id), actual);
            } finally {
              Arrays.fill(actual, (byte) 0);
            }
          }
          assertEquals(1, io.opens);
          assertEquals(1, io.closes);
          assertEquals(2, io.fileAttributes);
          assertEquals(2, io.rootAttributes);
          io.assertCleared();
        }
      }
    }
  }

  @Test
  void optionalMissingOnlyBeforeOpen() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (var id : AesCredentialFile.values()) {
        Files.delete(fixture.root.resolve(id.fileName()));
        var io = new TestIo();
        var loader = fixture.loader(io);
        if (id.optional()) assertTrue(loader.load(id).isEmpty());
        else failure(() -> loader.load(id));
        assertEquals(0, io.opens);
        fixture.write(id, "v");
      }
      for (String fault : List.of("file-missing", "file-missing-after", "close-missing")) {
        var io = new TestIo();
        io.fault = fault;
        failure(() -> fixture.loader(io).load(PREVIOUS));
        io.assertCleared();
      }
      fixture.calls.closeMissing = true;
      failure(() -> fixture.loader(new TestIo()).load(PREVIOUS));
      fixture.calls.closeMissing = false;
      fixture.calls.openFailure = true;
      failure(() -> fixture.loader(new TestIo()).load(PREVIOUS));
    }
  }

  @Test
  void rootAdmissionBeforeRead() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (var change :
          List.<Consumer<Map<String, Object>>>of(
              a -> a.put("uid", 12345), a -> a.put("mode", 040750),
              a -> a.put("mode", 0100440), a -> a.put("nlink", 0))) {
        var io = new TestIo();
        io.rootChange = change;
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(0, io.opens);
      }
      for (String fault : List.of("acl-root", "ro-root", "empty-acl-root")) {
        var io = new TestIo();
        io.securityFault = fault;
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(0, io.opens);
      }
      var actual = new InspectorCredentialLoader(fixture.held, LinuxInodeSecurity.create());
      failure(() -> actual.load(CURRENT)); // real owner on RW fixture is not admitted
      assertTrue(Files.isRegularFile(fixture.root.resolve(CURRENT.fileName())));
    }
  }

  @Test
  void inodeTypeBeforeNativeOrContent() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (int type : new int[] {0, 010000, 020000, 040000, 060000, 0120000, 0140000}) {
        var io = new TestIo();
        io.fileChange = a -> a.put("mode", type | 0440);
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(0, io.fileNative);
        assertEquals(0, io.opens);
      }
      Path file = fixture.root.resolve(CURRENT.fileName());
      Files.delete(file);
      Files.createSymbolicLink(file, fixture.root.resolve(PREVIOUS.fileName()));
      var io = new TestIo();
      failure(() -> fixture.loader(io).load(CURRENT));
      assertEquals(0, io.fileNative);
      assertEquals(0, io.opens);
    }
  }

  @Test
  void fileAttributesAndNulls() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (String key :
          List.of(
              "mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime")) {
        for (int variant = 0; variant < 3; variant++) {
          int mode = variant;
          var io = new TestIo();
          io.fileChange =
              map -> {
                if (mode == 0) map.remove(key);
                else map.put(key, mode == 1 ? null : "wrong-type");
              };
          failure(() -> fixture.loader(io).load(CURRENT));
          assertEquals(0, io.opens);
        }
      }
      var absent = new TestIo();
      absent.fault = "null-file-map";
      failure(() -> fixture.loader(absent).load(CURRENT));
      for (var change :
          List.<Consumer<Map<String, Object>>>of(
              a -> a.put("size", 53L),
              a -> a.put("size", 70L),
              a -> a.put("nlink", 2),
              a -> a.put("uid", -1),
              a -> a.put("mode", 0100640))) {
        var io = new TestIo();
        io.fileChange = change;
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(0, io.opens);
      }
    }
  }

  @Test
  void boundedReadsAndEof() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (int max : new int[] {1, 7, 54, 70}) {
        var io = new TestIo();
        io.maxRead = max;
        try (var material = fixture.loader(io).load(CURRENT).orElseThrow()) {
          assertEquals("v", material.version());
        }
        io.assertCleared();
      }
      for (String fault :
          List.of(
              "short",
              "long",
              "zero",
              "negative-read",
              "lying-read",
              "huge-read",
              "size-before",
              "size-after")) {
        var io = new TestIo();
        io.fault = fault;
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(1, io.closes);
        assertTrue(io.reads <= 3);
        io.assertCleared();
      }
    }
  }

  @Test
  void postReadChangesReject() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (String key :
          List.of(
              "uid", "gid", "nlink", "size", "dev", "ino", "mode", "lastModifiedTime", "ctime")) {
        var io = new TestIo();
        io.lateFileChange = map -> alter(map, key);
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(1, io.closes);
        io.assertCleared();
      }
      for (String key : List.of("gid", "size", "dev", "ino", "lastModifiedTime", "ctime")) {
        var io = new TestIo();
        io.lateRootChange = map -> alter(map, key);
        failure(() -> fixture.loader(io).load(CURRENT));
        io.assertCleared();
      }
      for (String fault :
          List.of(
              "ro-file-after", "ro-root-after", "empty-acl-file-after", "empty-acl-root-after")) {
        var io = new TestIo();
        io.securityFault = fault;
        failure(() -> fixture.loader(io).load(CURRENT));
        io.assertCleared();
      }
    }
  }

  @Test
  void ioAndCloseFailures() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (String fault :
          List.of(
              "attributes-root",
              "attributes-file",
              "root-final",
              "open",
              "read",
              "size-error-before",
              "size-error-after",
              "close",
              "unsupported")) {
        var io = new TestIo();
        io.fault = fault;
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(io.opens, io.closes);
        io.assertCleared();
      }
      for (String fault : List.of("acl-file", "ro-file", "empty-acl-file")) {
        var io = new TestIo();
        io.securityFault = fault;
        failure(() -> fixture.loader(io).load(CURRENT));
        assertEquals(0, io.opens);
      }
      fixture.calls.closeUnavailable = true;
      var io = new TestIo();
      failure(() -> fixture.loader(io).load(CURRENT));
      assertEquals(1, io.closes);
      io.assertCleared();
      fixture.calls.closeUnavailable = false;
      fixture.held.close();
      failure(() -> fixture.loader(new TestIo()).load(CURRENT));
    }
  }

  @Test
  void heldEntryAndRootReplacement() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      var io = new TestIo();
      Path file = fixture.root.resolve(CURRENT.fileName());
      byte[] expected = Files.readAllBytes(file);
      io.beforeRead =
          () -> {
            Files.move(file, fixture.root.resolve("retired"));
            Files.write(file, new byte[] {9});
          };
      failure(() -> fixture.loader(io).load(CURRENT));
      assertArrayEquals(expected, io.observedContent);
      assertArrayEquals(new byte[] {9}, Files.readAllBytes(file));
      io.assertCleared();
      Arrays.fill(expected, (byte) 0);
      Arrays.fill(io.observedContent, (byte) 0);
    }
    try (var fixture = new Fixture(temporary)) {
      var io = new TestIo();
      Path moved = fixture.root.resolveSibling(fixture.root.getFileName() + "-moved");
      io.beforeRead =
          () -> {
            Files.move(fixture.root, moved);
            Files.createDirectory(fixture.root);
          };
      try {
        failure(() -> fixture.loader(io).load(CURRENT));
        assertTrue(io.observedContent.length >= 54);
        io.assertCleared();
      } finally {
        Files.delete(fixture.root);
        Files.move(moved, fixture.root);
        Arrays.fill(io.observedContent, (byte) 0);
      }
    }
  }

  @Test
  void constructorAndEnumContracts() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      var io = new TestIo();
      var security = new TestSecurity(io);
      assertThrows(NullPointerException.class, () -> new InspectorCredentialLoader(null, security));
      assertThrows(
          NullPointerException.class, () -> new InspectorCredentialLoader(fixture.held, null));
      assertThrows(
          NullPointerException.class,
          () -> new InspectorCredentialLoader(fixture.held, security, null));
      assertThrows(NullPointerException.class, () -> fixture.loader(io).load(null));
      for (long uid : new long[] {-1, 0, 0xffff_ffffL}) {
        security.uid = uid;
        assertThrows(
            IllegalArgumentException.class,
            () -> new InspectorCredentialLoader(fixture.held, security, io));
      }
      assertEquals(
          List.of(
              "api-context-aes-current",
              "api-context-aes-previous",
              "api-inbox-response-aes-current",
              "api-inbox-response-aes-previous"),
          Arrays.stream(AesCredentialFile.values()).map(AesCredentialFile::fileName).toList());
      for (var id : AesCredentialFile.values())
        assertSame(id, AesCredentialFile.valueOf(id.name()));
      assertThrows(IllegalArgumentException.class, () -> AesCredentialFile.valueOf("../key"));
      boolean rootOpen = fixture.held.atDirectory(Files::isDirectory);
      assertTrue(rootOpen); // reader never closes borrowed root
    }
  }

  @Test
  void ownedBuffersAreCleared() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      var io = new TestIo();
      try (var material = fixture.loader(io).load(CURRENT).orElseThrow()) {
        io.assertCleared();
        byte[] key = material.copyKey();
        assertArrayEquals(fixture.keys.get(CURRENT), key);
        Arrays.fill(key, (byte) 0);
      }
      byte[] invalid = Files.readAllBytes(fixture.root.resolve(CURRENT.fileName()));
      invalid[0] = '?';
      Files.write(fixture.root.resolve(CURRENT.fileName()), invalid);
      Arrays.fill(invalid, (byte) 0);
      io = new TestIo();
      TestIo bad = io;
      failure(() -> fixture.loader(bad).load(CURRENT));
      assertEquals(1, io.closes);
      io.assertCleared();
    }
  }

  @Test
  void concurrentReadsAndRedaction() throws Exception {
    try (var fixture = new Fixture(temporary);
        var pool = Executors.newFixedThreadPool(12)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++) {
        var id = AesCredentialFile.values()[i % 4];
        tasks.add(
            () -> {
              var io = new TestIo();
              try (var material = fixture.loader(io).load(id).orElseThrow()) {
                byte[] actual = material.copyKey();
                try {
                  assertArrayEquals(fixture.keys.get(id), actual);
                } finally {
                  Arrays.fill(actual, (byte) 0);
                }
                io.assertCleared();
                assertFalse(material.toString().contains(SENTINEL));
              }
              return true;
            });
      }
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get(5, TimeUnit.SECONDS));
    }
  }

  private static void alter(Map<String, Object> map, String key) {
    Object value = map.get(key);
    if (value instanceof Integer number) map.put(key, number + 1);
    else if (value instanceof Long number) map.put(key, number + 1);
    else if (value instanceof FileTime time)
      map.put(key, FileTime.from(time.toInstant().plusNanos(1)));
    else fail("invalid test mutation");
  }

  private static void failure(Executable action) {
    var error = assertThrows(InspectorCredentialException.class, action);
    assertEquals("inspector credential cannot be loaded", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertFalse(error.toString().contains(SENTINEL));
  }

  static final class Fixture implements AutoCloseable {
    final Path root;
    final EntryCloseProbe calls = new EntryCloseProbe();
    final OwnedTransferDirectory held;
    final Map<AesCredentialFile, byte[]> keys = new EnumMap<>(AesCredentialFile.class);

    Fixture(Path parent) throws Exception {
      root = Files.createTempDirectory(parent, "credentials-");
      for (var id : AesCredentialFile.values()) {
        byte[] key = new byte[32];
        new SecureRandom().nextBytes(key);
        keys.put(id, key);
        write(id, "v");
      }
      held = OwnedTransferDirectory.open(calls, root);
    }

    void write(AesCredentialFile id, String version) throws IOException {
      byte[] prefix = ("NKKEY1\n" + version + "\n").getBytes(StandardCharsets.US_ASCII);
      byte[] encoded = Base64.getEncoder().encode(keys.get(id));
      byte[] value = Arrays.copyOf(prefix, prefix.length + encoded.length + 1);
      System.arraycopy(encoded, 0, value, prefix.length, encoded.length);
      value[value.length - 1] = '\n';
      try {
        Files.write(root.resolve(id.fileName()), value);
      } finally {
        Arrays.fill(encoded, (byte) 0);
        Arrays.fill(value, (byte) 0);
      }
    }

    InspectorCredentialLoader loader(TestIo io) {
      return new InspectorCredentialLoader(held, new TestSecurity(io), io);
    }

    @Override
    public void close() throws StorageIoException {
      try {
        held.close();
      } finally {
        keys.values().forEach(key -> Arrays.fill(key, (byte) 0));
      }
    }
  }

  @FunctionalInterface
  interface Hook {
    void run() throws IOException;
  }

  static final class TestIo implements InspectorCredentialLoader.Io {
    final InspectorCredentialLoader.NioIo actual = new InspectorCredentialLoader.NioIo();
    String fault = "";
    String securityFault = "";
    int rootAttributes;
    int fileAttributes;
    int opens;
    int reads;
    int closes;
    int fileNative;
    int rootRo;
    int fileRo;
    int maxRead = 70;
    Consumer<Map<String, Object>> rootChange = (a) -> {};
    Consumer<Map<String, Object>> fileChange = (a) -> {};
    Consumer<Map<String, Object>> lateRootChange = (a) -> {};
    Consumer<Map<String, Object>> lateFileChange = (a) -> {};
    Hook beforeRead = () -> {};
    final List<byte[]> buffers = new ArrayList<>();
    byte[] observedContent = new byte[0];

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      Map<String, Object> map = new HashMap<>(actual.attributes(held));
      boolean directory = ((Integer) map.get("mode") & 0170000) == 040000;
      if (directory) {
        rootAttributes++;
        if (fault.equals("attributes-root") || fault.equals("root-final") && rootAttributes > 1)
          throw new IOException(SENTINEL);
      } else {
        fileAttributes++;
        if (fault.equals("file-missing")
            || fault.equals("file-missing-after") && fileAttributes > 1)
          throw new NoSuchFileException(SENTINEL);
        if (fault.equals("attributes-file")) throw new IOException(SENTINEL);
        if (fault.equals("null-file-map")) return null; // deliberately broken boundary result
      }
      // Explicit OS metadata seam; never claims this nonprivileged fixture is root-owned.
      map.put("uid", 0);
      map.put("mode", ((Integer) map.get("mode") & 0170000) | (directory ? 0550 : 0440));
      (directory ? rootChange : fileChange).accept(map);
      if (directory && rootAttributes > 1) lateRootChange.accept(map);
      if (!directory && fileAttributes > 1) lateFileChange.accept(map);
      return map;
    }

    @Override
    public SeekableByteChannel openReadOnly(Path held) throws IOException {
      if (fault.equals("open")) throw new IOException(SENTINEL);
      if (fault.equals("unsupported")) throw new UnsupportedOperationException(SENTINEL);
      SeekableByteChannel delegate = actual.openReadOnly(held);
      opens++;
      return new SeekableByteChannel() {
        int sizes;

        @Override
        public int read(ByteBuffer buffer) throws IOException {
          buffers.add(buffer.array());
          if (reads++ == 0) beforeRead.run();
          switch (fault) {
            case "read":
              throw new IOException(SENTINEL);
            case "short":
              return -1;
            case "zero":
              return 0;
            case "negative-read":
              return -2;
            case "lying-read":
              return 1;
            case "huge-read":
              return Integer.MAX_VALUE;
            case "long":
              while (buffer.hasRemaining()) buffer.put((byte) 'X');
              return 70;
            default:
              break;
          }
          int originalLimit = buffer.limit();
          int start = buffer.position();
          buffer.limit(Math.min(originalLimit, start + maxRead));
          int count;
          try {
            count = delegate.read(buffer);
          } finally {
            buffer.limit(originalLimit);
          }
          if (count > 0 && start == 0) observedContent = Arrays.copyOf(buffer.array(), count);
          return count;
        }

        @Override
        public long size() throws IOException {
          sizes++;
          if (fault.equals(sizes == 1 ? "size-error-before" : "size-error-after"))
            throw new IOException(SENTINEL);
          long size = delegate.size();
          return fault.equals(sizes == 1 ? "size-before" : "size-after") ? size + 1 : size;
        }

        @Override
        public void close() throws IOException {
          delegate.close();
          closes++;
          if (fault.equals("close")) throw new IOException(SENTINEL);
          if (fault.equals("close-missing")) throw new NoSuchFileException(SENTINEL);
        }

        @Override
        public boolean isOpen() {
          return delegate.isOpen();
        }

        @Override
        public long position() throws IOException {
          return delegate.position();
        }

        @Override
        public SeekableByteChannel position(long position) {
          throw new AssertionError("no seek");
        }

        @Override
        public int write(ByteBuffer source) {
          throw new AssertionError("read only");
        }

        @Override
        public SeekableByteChannel truncate(long size) {
          throw new AssertionError("read only");
        }
      };
    }

    void assertCleared() {
      assertCleared(70);
    }

    void assertCleared(int expectedSize) {
      for (byte[] buffer : buffers) assertArrayEquals(new byte[expectedSize], buffer);
      Arrays.fill(observedContent, (byte) 0); // test-owned observation is cleared as well
    }
  }

  static final class TestSecurity implements InodeSecurityCalls {
    final TestIo io;
    long uid = 1000;

    TestSecurity(TestIo io) {
      this.io = io;
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public boolean readOnlyFilesystem(Path held) throws StorageIoException {
      boolean directory = Files.isDirectory(held);
      int count;
      if (directory) count = ++io.rootRo;
      else {
        count = ++io.fileRo;
        io.fileNative++;
      }
      String kind = directory ? "root" : "file";
      if (io.securityFault.equals("ro-" + kind))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      return io.securityFault.equals("ro-" + kind + "-after") && count > 1;
    }

    @Override
    public byte[] accessAcl(Path held, int maximumBytes) throws StorageIoException {
      assertEquals(44, maximumBytes);
      boolean directory = Files.isDirectory(held);
      String kind = directory ? "root" : "file";
      int count = directory ? io.rootRo : io.fileRo;
      if (io.securityFault.equals("acl-" + kind))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      if (io.securityFault.equals("empty-acl-" + kind)
          || io.securityFault.equals("empty-acl-" + kind + "-after") && count > 1)
        return new byte[0];
      byte[] acl =
          HexFormat.of()
              .parseHex(
                  "0200000001000400ffffffff02000400e803000004000000ffffffff10000400ffffffff20000000ffffffff");
      if (directory) for (int index : new int[] {6, 14, 30}) acl[index] = 5;
      return acl;
    }
  }

  static final class EntryCloseProbe implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Set<Integer> entries = new HashSet<>();
    boolean closeMissing;
    boolean closeUnavailable;
    boolean openFailure;

    @Override
    public int openRoot() throws StorageIoException {
      return delegate.openRoot();
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      return delegate.openDirectory(parent, name);
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      if (openFailure) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      int result = delegate.openEntry(parent, name);
      entries.add(result);
      return result;
    }

    @Override
    public void close(int descriptor) throws StorageIoException {
      boolean entry = entries.remove(descriptor);
      delegate.close(descriptor);
      if (entry && closeMissing) throw new StorageIoException(StorageIoException.Reason.MISSING);
      if (entry && closeUnavailable)
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }

    @Override
    public int createFile(int parent, String name) {
      throw new AssertionError("read only");
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw new AssertionError("read only");
    }

    @Override
    public void publish(int directory, String part, String ready) {
      throw new AssertionError("read only");
    }

    @Override
    public void unlink(int directory, String name) {
      throw new AssertionError("read only");
    }

    @Override
    public void sync(int directory) {
      throw new AssertionError("read only");
    }
  }
}
