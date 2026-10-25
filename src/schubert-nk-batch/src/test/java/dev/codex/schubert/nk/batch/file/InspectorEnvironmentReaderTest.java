package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.StringJoiner;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Real retained inodes/channels; only root/GID/FS admission is synthetic. EFILE001..008. */
final class InspectorEnvironmentReaderTest {
  @TempDir Path temporary;
  private static final String STATIC =
      "NK_INSPECTOR_DB_URL=jdbc:postgresql://127.0.0.1:5432/schubert_nk\n"
          + "NK_INSPECTOR_FINGERPRINT_VERSIONS=v1,v2\n";
  private static final String RUNTIME =
      "NK_INSPECTOR_RUN_ID=00000000-0000-0000-0000-000000000152\n"
          + "NK_INSPECTOR_CUTOFF=2026-09-12T00:00:00Z\n";
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("00000000-0000-0000-0000-000000000152"),
          Instant.parse("2026-09-12T00:00:00Z"));

  @Test
  void staticReadAndBoundaries() throws Exception {
    try (var f = fixture(false)) {
      byte[] first = f.reader().readStatic();
      assertArrayEquals(bytes(STATIC), first);
      first[0] = 0;
      assertArrayEquals(bytes(STATIC), f.reader().readStatic());
      assertEquals(STATIC, Files.readString(f.file));
      boolean rootAlive = f.root.atDirectory(Files::isDirectory);
      assertTrue(rootAlive);
      f.released();
    }
    try (var f = fixture(false)) {
      StringJoiner names = new StringJoiner(",");
      for (int i = 0; i < 4095; i++) names.add(String.format(Locale.ROOT, "v%014d", i));
      String all = names + "," + "Z".repeat(16);
      assertEquals(65536, all.length());
      String literal = STATIC.replace("v1,v2", all);
      Files.writeString(f.file, literal);
      assertArrayEquals(bytes(literal), f.reader().readStatic());
      f.released();
    }
  }

  @Test
  void runReadAndBinding() throws Exception {
    try (var f = fixture(true)) {
      assertArrayEquals(bytes(RUNTIME), f.reader().readRun(RUN));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              f.reader()
                  .readRun(
                      new BatchRun(
                          UUID.fromString("00000000-0000-0000-0000-000000000153"), RUN.cutoff())));
      for (long step : List.of(-1000L, 1000L))
        assertThrows(
            IllegalArgumentException.class,
            () -> f.reader().readRun(new BatchRun(RUN.id(), RUN.cutoff().plusNanos(step))));
      for (String stamp : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
        String literal = RUNTIME.replace("2026-09-12T00:00:00Z", stamp);
        Files.writeString(f.file, literal);
        assertArrayEquals(
            bytes(literal), f.reader().readRun(new BatchRun(RUN.id(), Instant.parse(stamp))));
      }
      Files.writeString(f.file, RUNTIME.replace("RUN_ID", "UNKNOWN"));
      assertThrows(IllegalArgumentException.class, () -> f.reader().readRun(RUN));
      f.released();
    }
    try (var f = fixture(false)) {
      Files.writeString(f.file, STATIC.replace("DB_URL", "RUN_ID"));
      var bad = assertThrows(IllegalArgumentException.class, () -> f.reader().readStatic());
      assertEquals("inspector static environment is invalid", bad.getMessage());
      f.released();
    }
  }

  @Test
  void permissionAndFilesystem() throws Exception {
    for (long uid : List.of(-1L, 1L, 4294967295L))
      try (var f = fixture(false)) {
        f.uid = uid;
        reject(f);
        assertEquals(0, f.count("attributes"));
      }
    for (boolean runtime : List.of(false, true))
      for (String role : List.of("dir", "file")) {
        for (String field : List.of("uid", "gid", "mode", "nlink", "size")) {
          List<Object> values =
              switch (field) {
                case "uid", "gid" -> List.of(7, -1);
                case "mode" -> List.of(0, 0120777, 0140600, 0100666, 040777);
                case "nlink" -> role.equals("dir") ? List.of(0, 1) : List.of(0, 2);
                case "size" ->
                    role.equals("dir") ? List.of(-1L) : List.of(-1L, 0L, runtime ? 111L : 65849L);
                default -> throw new AssertionError(field);
              };
          for (Object value : values)
            try (var f = fixture(runtime)) {
              f.change = change(role, field, value);
              reject(f);
              if (role.equals("dir")) assertEquals(0, f.count("openEntry"));
            }
        }
        for (String type : List.of("nfs", "cifs", "overlay", "", "unknown"))
          try (var f = fixture(runtime)) {
            f.badRole = role;
            f.filesystem = type;
            reject(f);
          }
        try (var f = fixture(runtime)) {
          f.badRole = role;
          f.acl = new byte[] {2, 0, 0, 0};
          reject(f);
        }
      }
    for (String type : List.of("ext2", "ext3", "ext4", "ext2/ext3/ext4", "xfs", "btrfs", "tmpfs")) {
      try (var f = fixture(false)) {
        f.filesystem = type;
        f.readonly = true;
        assertArrayEquals(bytes(STATIC), f.reader().readStatic());
      }
      if (!type.equals("tmpfs"))
        try (var f = fixture(true)) {
          f.filesystem = type;
          reject(f);
        }
    }
    try (var f = fixture(true)) {
      f.readonly = true;
      reject(f);
    }
    try (var f = fixture(false)) {
      f.change = change("file", "dev", Long.MAX_VALUE);
      reject(f);
    }
  }

  @Test
  void metadataAndNull() throws Exception {
    for (String role : List.of("dir", "file")) {
      for (String key :
          List.of(
              "mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime")) {
        for (Object wrong : Arrays.asList(null, "not-the-declared-type"))
          try (var f = fixture(false)) {
            f.change = change(role, key, wrong);
            reject(f);
          }
      }
      try (var f = fixture(false)) {
        f.badRole = role;
        f.nullAttributes = true;
        reject(f);
      }
      try (var f = fixture(false)) {
        f.badRole = role;
        f.filesystem = null;
        reject(f);
      }
      try (var f = fixture(false)) {
        f.badRole = role;
        f.acl = null;
        reject(f);
      }
    }
    try (var f = fixture(false)) {
      f.nullChannel = true;
      reject(f);
    }
    try (var f = fixture(false)) {
      for (long group : List.of(0L, -1L, 4294967296L))
        assertThrows(
            IllegalArgumentException.class,
            () -> new InspectorEnvironmentReader(f.root, f, group, f));
      for (long group : List.of(1L, 4294967295L)) {
        f.group = group;
        assertArrayEquals(bytes(STATIC), f.reader().readStatic());
      }
      assertThrows(NullPointerException.class, () -> new InspectorEnvironmentReader(null, f, 1, f));
      assertThrows(
          NullPointerException.class, () -> new InspectorEnvironmentReader(f.root, null, 1, f));
      assertThrows(
          NullPointerException.class, () -> new InspectorEnvironmentReader(f.root, f, 1, null));
      assertThrows(NullPointerException.class, () -> f.reader().readRun(null));
    }
  }

  @Test
  void boundedReadsAndMutation() throws Exception {
    for (String behavior : List.of("zero", "negative", "overflow", "position"))
      try (var f = fixture(false)) {
        f.readBehavior = behavior;
        reject(f);
      }
    for (int difference : List.of(-1, 1))
      try (var f = fixture(false)) {
        f.sizeDelta = difference;
        f.change =
            (role, values) -> {
              if (role.equals("file")) values.put("size", ((Long) values.get("size")) + difference);
            };
        reject(f);
      }
    try (var f = fixture(false)) {
      f.sizeDelta = 1;
      reject(f);
    }
    try (var f = fixture(false)) {
      f.endSizeDelta = 1;
      reject(f);
    }
    try (var f = fixture(false)) {
      byte[] over = new byte[65849];
      Files.write(f.file, over);
      f.sizeDelta = -1;
      f.change = change("file", "size", 65848L);
      reject(f);
      assertEquals(65849, f.maximumBuffer);
    }
    for (String field : List.of("ino", "dev", "ctime", "lastModifiedTime"))
      try (var f = fixture(false)) {
        f.afterRead =
            () ->
                f.change =
                    change(
                        "file",
                        field,
                        field.equals("ctime") || field.equals("lastModifiedTime")
                            ? FileTime.fromMillis(0)
                            : Long.MAX_VALUE);
        reject(f);
      }
    try (var f = fixture(false)) {
      f.readLimit = 7;
      assertArrayEquals(bytes(STATIC), f.reader().readStatic());
      f.released();
    }
  }

  @Test
  void inodeReplacementAndOwnership() throws Exception {
    try (var f = fixture(false)) {
      f.afterRead =
          () -> {
            Files.move(f.file, f.directory.resolve("original"));
            Files.writeString(f.file, STATIC);
          };
      reject(f);
      assertEquals(STATIC, Files.readString(f.directory.resolve("original")));
      assertEquals(STATIC, Files.readString(f.file));
      f.released();
    }
    try (var f = fixture(false)) {
      f.afterRead = () -> f.change = change("dir", "ino", Long.MAX_VALUE);
      reject(f);
    }
    for (String kind : List.of("missing", "symlink", "directory", "hardlink"))
      try (var f = fixture(false)) {
        Files.move(f.file, f.directory.resolve("original"));
        switch (kind) {
          case "symlink" -> Files.createSymbolicLink(f.file, Path.of("original"));
          case "directory" -> Files.createDirectory(f.file);
          case "hardlink" -> Files.createLink(f.file, f.directory.resolve("original"));
          case "missing" -> {}
          default -> throw new AssertionError(kind);
        }
        reject(f);
        assertEquals(0, f.count("openChannel"));
      }
  }

  @Test
  void ioFaultsAndRedaction() throws Exception {
    for (boolean runtime : List.of(false, true))
      for (boolean known : List.of(false, true))
        for (Throwable unknown :
            List.of(
                new IllegalStateException("public compound"),
                new NullPointerException("public compound"),
                new AssertionError("public compound")))
          try (var f = fixture(runtime)) {
            if (known) {
              f.fail = "read";
              f.failAt = 2;
            }
            f.compound =
                (name, count) -> {
                  if ((count == 1 && name.equals("channelClose"))
                      || (!known && count == 2 && name.equals("read"))) {
                    if (unknown instanceof RuntimeException failure) throw failure;
                    throw (Error) unknown;
                  }
                };
            assertSame(
                unknown,
                assertThrows(
                    unknown.getClass(),
                    () -> {
                      if (runtime) f.reader().readRun(RUN);
                      else f.reader().readStatic();
                    }));
            assertEquals(2, f.count("read"));
            assertEquals(1, f.count("channelClose"));
            assertEquals(known ? 0 : 1, unknown.getSuppressed().length);
            for (Throwable secondary : unknown.getSuppressed()) {
              var fixed = assertInstanceOf(StorageIoException.class, secondary);
              assertEquals(StorageIoException.Reason.UNAVAILABLE, fixed.reason());
              assertEquals("transfer storage operation failed", fixed.getMessage());
              assertNull(fixed.getCause());
              assertEquals(0, fixed.getSuppressed().length);
            }
            f.released();
            assertEquals(2, f.compoundBuffers.size());
            for (byte[] bytes : f.compoundBuffers) assertArrayEquals(new byte[bytes.length], bytes);
            assertEquals(runtime ? RUNTIME : STATIC, Files.readString(f.file));
          }
    // Independent read protocol counts; root is borrowed and already opened before counting.
    Map<String, Integer> inventory =
        Map.of(
            "attributes",
            5,
            "acl",
            5,
            "filesystem",
            5,
            "readonly",
            5,
            "openEntry",
            2,
            "entryClose",
            2,
            "openChannel",
            1,
            "size",
            2,
            "read",
            2,
            "channelClose",
            1);
    try (var f = fixture(false)) {
      assertArrayEquals(bytes(STATIC), f.reader().readStatic());
      for (var item : inventory.entrySet())
        assertEquals(item.getValue().intValue(), f.count(item.getKey()), item.getKey());
    }
    for (var item : inventory.entrySet())
      for (int at = 1; at <= item.getValue(); at++) {
        try (var f = fixture(false)) {
          f.fail = item.getKey();
          f.failAt = at;
          reject(f);
        }
      }
    try (var f = fixture(false)) {
      f.fail = "read";
      f.failAt = 1;
      f.failCloses = true;
      reject(f);
    }
    for (boolean primary : List.of(false, true))
      try (var f = fixture(false)) {
        f.rawClose = true;
        if (primary)
          f.afterRead =
              () -> {
                throw new IOException("synthetic-path/content must not escape");
              };
        reject(f);
      }
    try (var f = fixture(false)) {
      f.afterRead =
          () -> {
            throw new IllegalStateException("test unexpected runtime");
          };
      var fail = assertThrows(IllegalStateException.class, () -> f.reader().readStatic());
      assertEquals("test unexpected runtime", fail.getMessage());
      f.released();
    }
  }

  @Test
  void concurrentAndConstructor() throws Exception {
    try (var f = fixture(false)) {
      f.lateInterrupt = true;
      try {
        reject(f);
        assertEquals(5, f.count("readonly"));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
    try (var f = fixture(false);
        var pool = Executors.newFixedThreadPool(8)) {
      List<Callable<byte[]>> work = new ArrayList<>();
      for (int i = 0; i < 64; i++) work.add(() -> f.reader().readStatic());
      for (var done : pool.invokeAll(work))
        assertArrayEquals(bytes(STATIC), done.get(5, TimeUnit.SECONDS));
      f.released();
      Thread.currentThread().interrupt();
      try {
        reject(f);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
    try (var f = fixture(false)) {
      f.afterRead = () -> Thread.currentThread().interrupt();
      try {
        reject(f);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      // Public factory uses real non-root metadata; it must not borrow the fixture's fake owner.
      assertThrows(
          StorageIoException.class,
          () -> new InspectorEnvironmentReader(f.root, f, 2000).readStatic());
    }
    var f = fixture(false);
    try {
      f.root.close();
      assertThrows(StorageIoException.class, () -> f.reader().readStatic());
    } finally {
      f.close();
    }
  }

  private Fixture fixture(boolean runtime) throws Exception {
    return new Fixture(Files.createTempDirectory(temporary, "environment-"), runtime);
  }

  private static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static BiConsumer<String, Map<String, Object>> change(
      String role, String key, Object value) {
    return (observed, values) -> {
      if (role.equals(observed)) values.put(key, value);
    };
  }

  private static void reject(Fixture f) {
    var failure =
        assertThrows(
            StorageIoException.class,
            () -> {
              if (f.runtime) f.reader().readRun(RUN);
              else f.reader().readStatic();
            });
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    f.released();
  }

  @FunctionalInterface
  interface Action {
    void run() throws IOException;
  }

  private static final class Fixture
      implements AutoCloseable, InspectorEnvironmentReader.Io, InodeSecurityCalls {
    final Path directory;
    final Path file;
    final boolean runtime;
    final OwnedTransferDirectory root;
    final InspectorEnvironmentReader.NioIo real = new InspectorEnvironmentReader.NioIo();
    final Map<String, AtomicInteger> counts = new ConcurrentHashMap<>();
    final Set<Integer> entries = ConcurrentHashMap.newKeySet();
    final AtomicInteger channels = new AtomicInteger();
    long uid = 0;
    long group = 2000;
    String badRole = "*";
    String filesystem;
    byte[] acl = new byte[0];
    boolean readonly;
    boolean nullAttributes;
    boolean nullChannel;
    boolean failCloses;
    boolean lateInterrupt;
    boolean rawClose;
    String fail = "";
    String readBehavior = "normal";
    int failAt = 1;
    int sizeDelta;
    int endSizeDelta;
    int readLimit = Integer.MAX_VALUE;
    int maximumBuffer;
    BiConsumer<String, Map<String, Object>> change = (role, values) -> {};
    Action afterRead = () -> {};
    BiConsumer<String, Integer> compound = (name, count) -> {};
    final List<byte[]> compoundBuffers = new ArrayList<>();

    Fixture(Path directory, boolean runtime) throws Exception {
      this.directory = directory;
      this.runtime = runtime;
      this.filesystem = runtime ? "tmpfs" : "ext4";
      file = directory.resolve("inbox-inspector.env");
      Files.writeString(file, runtime ? RUNTIME : STATIC);
      DirectoryCalls delegate = LinuxDirectoryCalls.create();
      // Reflection only dispatches public SPI methods; no private production state is inspected.
      DirectoryCalls calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    if (name.equals("openEntry")) point("openEntry");
                    boolean ownedClose = name.equals("close") && entries.remove((Integer) args[0]);
                    Object result;
                    try {
                      result = method.invoke(delegate, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (name.equals("openEntry")) entries.add((Integer) result);
                    if (ownedClose) point("entryClose");
                    return result;
                  });
      root = OwnedTransferDirectory.open(calls, directory);
      counts.clear();
    }

    InspectorEnvironmentReader reader() {
      return new InspectorEnvironmentReader(root, this, group, this);
    }

    int count(String name) {
      return counts.getOrDefault(name, new AtomicInteger()).get();
    }

    void point(String name) throws StorageIoException {
      int n = counts.computeIfAbsent(name, key -> new AtomicInteger()).incrementAndGet();
      compound.accept(name, n);
      if (lateInterrupt && name.equals("readonly") && n == 5) Thread.currentThread().interrupt();
      if ((name.equals(fail) && n == failAt) || (failCloses && name.endsWith("Close")))
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }

    String role(Path held) throws IOException {
      return (((Integer) real.attributes(held).get("mode")) & 0170000) == 040000 ? "dir" : "file";
    }

    boolean selected(Path held) throws IOException {
      return badRole.equals("*") || badRole.equals(role(held));
    }

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      point("attributes");
      String role = role(held);
      if (nullAttributes && selected(held)) return null;
      Map<String, Object> values = new HashMap<>(real.attributes(held));
      int type = ((Integer) values.get("mode")) & 0170000;
      values.put(
          "mode", type | (role.equals("dir") ? (runtime ? 0700 : 0750) : (runtime ? 0600 : 0640)));
      values.put("uid", 0);
      values.put("gid", runtime ? 0 : (int) group);
      change.accept(role, values);
      return values;
    }

    @Override
    public String filesystem(Path held) throws IOException {
      point("filesystem");
      assertNotNull(real.filesystem(held));
      return selected(held) ? filesystem : (runtime ? "tmpfs" : "ext4");
    }

    @Override
    public byte[] accessAcl(Path held, int maximum) throws StorageIoException {
      point("acl");
      assertEquals(44, maximum);
      try {
        return selected(held) ? acl : new byte[0];
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public boolean readOnlyFilesystem(Path held) throws StorageIoException {
      point("readonly");
      try {
        return selected(held) && readonly;
      } catch (IOException failure) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public SeekableByteChannel open(Path held) throws IOException {
      point("openChannel");
      if (nullChannel) return null;
      SeekableByteChannel channel = real.open(held);
      channels.incrementAndGet();
      return new SeekableByteChannel() {
        int sizes;

        @Override
        public int read(ByteBuffer target) throws IOException {
          compoundBuffers.add(target.array());
          point("read");
          maximumBuffer = Math.max(maximumBuffer, target.capacity());
          int start = target.position();
          int remaining = target.remaining();
          switch (readBehavior) {
            case "zero":
              return 0;
            case "negative":
              return -2;
            case "overflow":
              return remaining + 1;
            default:
              break;
          }
          int oldLimit = target.limit();
          target.limit(start + Math.min(remaining, readLimit));
          int count = channel.read(target);
          target.limit(oldLimit);
          if (readBehavior.equals("position")) target.position(start);
          if (count == -1) afterRead.run();
          return count;
        }

        @Override
        public long size() throws IOException {
          point("size");
          return channel.size() + sizeDelta + (++sizes == 2 ? endSizeDelta : 0);
        }

        @Override
        public boolean isOpen() {
          return channel.isOpen();
        }

        @Override
        public void close() throws IOException {
          channel.close();
          channels.decrementAndGet();
          point("channelClose");
          if (rawClose) throw new IOException("synthetic-path/content from close must not escape");
        }

        @Override
        public int write(ByteBuffer input) {
          throw new AssertionError("read-only");
        }

        @Override
        public long position() {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel position(long position) {
          throw new AssertionError("no seek");
        }

        @Override
        public SeekableByteChannel truncate(long size) {
          throw new AssertionError("no write");
        }
      };
    }

    void released() {
      assertTrue(entries.isEmpty());
      assertEquals(0, channels.get());
    }

    @Override
    public void close() throws StorageIoException {
      root.close();
      released();
    }
  }
}
