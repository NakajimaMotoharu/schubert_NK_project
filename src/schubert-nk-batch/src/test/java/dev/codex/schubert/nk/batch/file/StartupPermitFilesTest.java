package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.file.StartupPermitRecords.*;
import dev.codex.schubert.nk.batch.repository.*;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.lang.reflect.*;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.*;
import java.security.*;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-PERMITFILE001..008; SS343 SSC089; real Linux FD IO, explicitly synthetic root/tmpfs. */
final class StartupPermitFilesTest {
  private static final UUID BOOT = UUID.fromString("11111111-1111-1111-1111-111111111111");
  private static final UUID EPOCH = UUID.fromString("33333333-3333-3333-3333-333333333333");
  private static final UUID RUN = UUID.fromString("44444444-4444-4444-4444-444444444444");
  private static final UUID ACT = UUID.fromString("55555555-5555-5555-5555-555555555555");
  private static final MaintenanceActivation ACTIVE =
      new MaintenanceActivation(new BatchRun(RUN, Instant.parse("2026-09-27T00:00:00Z")), ACT);
  private static final String BIND =
      "boot_id=11111111-1111-1111-1111-111111111111\n"
          + "epoch_id=33333333-3333-3333-3333-333333333333\n"
          + "run_id=44444444-4444-4444-4444-444444444444\n"
          + "cutoff_utc=2026-09-27T00:00:00.000000Z\n"
          + "activation_id=55555555-5555-5555-5555-555555555555\n";
  private static final String INVALID = "NKEPOCH1\nstate=INVALID\n" + BIND + "permit_sha256=-\n";
  private static final String GOLD =
      "NKPERMIT1\n"
          + BIND
          + "broker_invocation_id="
          + "2".repeat(32)
          + "\nrelease_sha256="
          + "b".repeat(64)
          + "\napi_config_sha256="
          + "c".repeat(64)
          + "\nweb_config_sha256="
          + "d".repeat(64)
          + "\nroots_sha256="
          + "e".repeat(64)
          + "\nprestart_steps_sha256="
          + "f".repeat(64)
          + "\n";

  private static Permit permit() {
    return new Permit(
        BOOT,
        EPOCH,
        ACTIVE,
        "2".repeat(32),
        "b".repeat(64),
        "c".repeat(64),
        "d".repeat(64),
        "e".repeat(64),
        "f".repeat(64));
  }

  private static Epoch invalid() {
    return new Epoch(State.INVALID, BOOT, EPOCH, ACTIVE, Optional.empty());
  }

  @TempDir Path temporary;

  private Fixture fixture() throws Exception {
    return new Fixture(Files.createTempDirectory(temporary, "permit-"));
  }

  private static void fail(Executable work) {
    var error = assertThrows(StorageIoException.class, work);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertEquals("transfer storage operation failed", error.getMessage());
  }

  @Test
  void originalsAndPublicationOrder() throws Exception {
    try (var f = fixture()) {
      Epoch current = f.store.invalidate(BOOT, EPOCH, ACTIVE);
      assertEquals(INVALID, Files.readString(f.current));
      assertEquals(invalid(), current);
      fail(f.store::readIssued);
      f.reset();
      Epoch issued = f.store.issue(current, permit());
      String digest =
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256")
                      .digest(GOLD.getBytes(java.nio.charset.StandardCharsets.US_ASCII)));
      assertEquals(
          "NKEPOCH1\nstate=ISSUED\n" + BIND + "permit_sha256=" + digest + "\n",
          Files.readString(f.current));
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(issued, f.store.current());
      assertEquals(permit(), f.store.readIssued());
      assertTrue(f.events.indexOf("force") < f.events.indexOf("publish"));
      assertTrue(f.events.indexOf("publish") < f.events.indexOf("replace"));
      assertEquals(0100600, Files.getAttribute(f.current, "unix:mode"));
      assertEquals(1, Files.getAttribute(f.permit, "unix:nlink"));
      f.released();
      f.store.invalidate(BOOT, ACT, ACTIVE);
      assertEquals(State.INVALID, f.store.current().state());
      assertEquals(GOLD, Files.readString(f.permit));
      fail(f.store::readIssued);
    }
  }

  @Test
  void missingCorruptAndWrongBindings() throws Exception {
    try (var f = fixture()) {
      fail(f.store::current);
      fail(f.store::readIssued);
      fail(() -> f.store.issue(invalid(), permit()));
    }
    for (String bad :
        List.of("corrupt", INVALID.replace("INVALID", "unknown"), "x".repeat(8193), ""))
      try (var f = fixture()) {
        f.seed(bad);
        fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
        assertEquals(bad, Files.readString(f.current));
      }
    for (Permit wrong :
        List.of(
            new Permit(
                ACT,
                EPOCH,
                ACTIVE,
                "2".repeat(32),
                "b".repeat(64),
                "c".repeat(64),
                "d".repeat(64),
                "e".repeat(64),
                "f".repeat(64)),
            new Permit(
                BOOT,
                ACT,
                ACTIVE,
                "2".repeat(32),
                "b".repeat(64),
                "c".repeat(64),
                "d".repeat(64),
                "e".repeat(64),
                "f".repeat(64)),
            new Permit(
                BOOT,
                EPOCH,
                new MaintenanceActivation(ACTIVE.run(), EPOCH),
                "2".repeat(32),
                "b".repeat(64),
                "c".repeat(64),
                "d".repeat(64),
                "e".repeat(64),
                "f".repeat(64))))
      try (var f = fixture()) {
        f.seed(INVALID);
        fail(() -> f.store.issue(invalid(), wrong));
        assertEquals(0, f.count("create"));
      }
    try (var f = fixture()) {
      f.seed(INVALID);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      fail(() -> f.store.issue(invalid().issued("a".repeat(64)), permit()));
      f.store.issue(invalid(), permit());
      fail(() -> f.store.issue(invalid(), permit()));
      Files.writeString(f.permit, GOLD.replace("2".repeat(32), "3".repeat(32)));
      fail(f.store::readIssued);
      Files.writeString(f.current, INVALID);
      fail(f.store::readIssued);
    }
    try (var f = fixture()) {
      f.seed(INVALID.replace(EPOCH.toString(), ACT.toString()));
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(0, f.count("create"));
    }
  }

  @Test
  void metadataAndSecurityMatrix() throws Exception {
    for (String role : List.of("dir", "file"))
      for (String key :
          List.of("mode", "uid", "gid", "nlink", "size", "dev", "ino", "lastModifiedTime", "ctime"))
        for (Object wrong : List.of("wrong type", -1))
          try (var f = fixture()) {
            f.seed(INVALID);
            f.mutate =
                (kind, values) -> {
                  if (kind.equals(role)) values.put(key, wrong);
                };
            fail(f.store::current);
          }
    for (String role : List.of("dir", "file"))
      for (String bad :
          List.of(
              "uid",
              "gid",
              "mode",
              "links",
              "size",
              "nullAttributes",
              "acl",
              "nullAcl",
              "filesystem",
              "nullFilesystem",
              "readonly"))
        try (var f = fixture()) {
          f.seed(INVALID);
          f.badRole = role;
          f.bad = bad;
          fail(f.store::current);
        }
    try (var f = fixture()) {
      f.uid = 1;
      fail(f.store::current);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      assertEquals(0, f.count("attributes"));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.mutate =
          (role, m) -> {
            if (role.equals("file")) m.put("dev", -17L);
          };
      fail(f.store::current);
    }
  }

  @Test
  void everyOwnedIoFaultAndUncertainPublication() throws Exception {
    try (var f = fixture()) {
      f.mutate =
          (role, m) -> {
            if (role.equals("file")) m.put("size", 1L);
          };
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      assertEquals(0, f.count("openWriter"));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.behavior = "fill";
      fail(f.store::current);
      f.released();
    }
    // Instrument each actual acquired owner/IO position; failures must never yield a result.
    for (String operation : List.of("new", "replace", "issue", "current", "read")) {
      Map<String, Integer> inventory;
      try (var f = fixture()) {
        f.setup(operation);
        f.run(operation);
        inventory = new HashMap<>(f.counts);
        f.released();
      }
      for (var event : inventory.entrySet())
        for (int i = 1; i <= event.getValue(); i++)
          try (var f = fixture()) {
            f.setup(operation);
            f.fail = event.getKey();
            f.failAt = i;
            fail(() -> f.run(operation));
            f.released();
          }
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.fail = "sync";
      f.failAt = 1;
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(INVALID, Files.readString(f.current));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.digestFailure = true;
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(INVALID, Files.readString(f.current));
    }
    for (String operation : List.of("new", "current"))
      for (String behavior : List.of("zero", "negative", "overflow", "position", "short"))
        try (var f = fixture()) {
          f.setup(operation);
          f.behavior = behavior;
          fail(() -> f.run(operation));
          f.released();
        }
    for (String operation : List.of("new", "current"))
      for (int at : List.of(1, 2, 3))
        try (var f = fixture()) {
          f.setup(operation);
          f.wrongSizeAt = at;
          if (operation.equals("current") && at == 3) continue;
          fail(() -> f.run(operation));
          f.released();
        }
    for (boolean writer : List.of(false, true))
      try (var f = fixture()) {
        if (!writer) f.seed(INVALID);
        f.nullWriter = writer;
        f.nullReader = !writer;
        if (writer) fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
        else fail(f.store::current);
      }
  }

  @Test
  void inodeChangesAndNoRepair() throws Exception {
    try (var f = fixture()) {
      Files.createSymbolicLink(f.current, Path.of("absent"));
      fail(f.store::current);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      assertTrue(Files.isSymbolicLink(f.current));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      Files.writeString(f.permit, GOLD);
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(INVALID, Files.readString(f.current));
      assertEquals(GOLD, Files.readString(f.permit));
    }
    for (String key : List.of("ino", "lastModifiedTime", "ctime"))
      try (var f = fixture()) {
        f.seed(INVALID);
        f.mutate =
            (role, m) -> {
              if (role.equals("file") && f.count("attributes") >= 3)
                m.put(
                    key, key.equals("ino") ? 888L : java.nio.file.attribute.FileTime.fromMillis(0));
            };
        fail(f.store::current);
      }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.mutate =
          (role, m) -> {
            if (role.equals("dir") && f.count("attributes") > 3) m.put("ino", 999L);
          };
      fail(f.store::current);
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.replaceFailure = true;
      fail(() -> f.store.invalidate(BOOT, ACT, ACTIVE));
      assertEquals(INVALID, Files.readString(f.current));
    }
  }

  @Test
  void interruptionNullAndUnknownIdentity() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(null, f));
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(f.root, null));
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(f.root, f, null, f));
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(f.root, f, f, null));
      assertThrows(NullPointerException.class, () -> f.store.issue(null, permit()));
      assertThrows(NullPointerException.class, () -> f.store.issue(invalid(), null));
      assertThrows(NullPointerException.class, () -> f.store.invalidate(null, EPOCH, ACTIVE));
      Thread.currentThread().interrupt();
      try {
        fail(f.store::current);
      } finally {
        Thread.interrupted();
      }
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      RuntimeException sentinel = new IllegalStateException("public sentinel");
      f.unknown = sentinel;
      f.fail = "read";
      assertSame(sentinel, assertThrows(IllegalStateException.class, f.store::current));
      f.released();
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.lateInterrupt = true;
      try {
        fail(f.store::current);
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
  }

  @Test
  void concurrentSinglePublication() throws Exception {
    try (var f = fixture();
        var workers = Executors.newFixedThreadPool(4)) {
      f.seed(INVALID);
      var pending = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 16; i++)
        pending.add(
            () -> {
              try {
                f.store.issue(invalid(), permit());
                return true;
              } catch (StorageIoException expected) {
                return false;
              }
            });
      int winners = 0;
      for (var result : workers.invokeAll(pending)) if (result.get()) winners++;
      assertEquals(1, winners);
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(permit(), f.store.readIssued());
      f.released();
    }
  }

  @Test
  void nativeIoAndBorrowedLifetime() throws Exception {
    try (var f = fixture()) {
      fail(
          () ->
              new StartupPermitFiles(f.root, LinuxInodeSecurity.create())
                  .invalidate(BOOT, EPOCH, ACTIVE));
      var nativeIo = new StartupPermitFiles.NioIo();
      f.seed(INVALID);
      assertNotNull(nativeIo.attributes(f.current));
      assertNotNull(nativeIo.filesystem(f.current));
      try (var channel = nativeIo.open(f.current)) {
        assertEquals(INVALID.length(), channel.size());
      }
      try (var writer = nativeIo.openWriter(f.current)) {
        assertEquals(INVALID.length(), writer.size());
        writer.force();
      }
      assertEquals("SHA-256", nativeIo.digest().getAlgorithm());
      Path part = f.directory.resolve("native.part");
      Files.writeString(part, "replacement");
      nativeIo.replace(f.directory, "native.part", "epoch.current");
      assertEquals("replacement", Files.readString(f.current));
      assertFalse(Files.exists(part));
      f.root.close();
      fail(f.store::current);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
    }
  }

  private static final class Fixture
      implements AutoCloseable,
          StartupPermitFiles.Io,
          StartupPermitFiles.Parts,
          InodeSecurityCalls {
    final Path directory, current, permit;
    final OwnedTransferDirectory root;
    final StartupPermitFiles store;
    final StartupPermitFiles.NioIo nativeIo = new StartupPermitFiles.NioIo();
    final Map<String, Integer> counts = new HashMap<>();
    final List<String> events = new ArrayList<>();
    final Set<Integer> entries = new HashSet<>();
    int readers, writers, failAt = 1, wrongSizeAt;
    long part, uid;
    String fail = "", bad = "", badRole = "", behavior = "";
    boolean nullReader, nullWriter, digestFailure, replaceFailure, lateInterrupt;
    RuntimeException unknown;
    BiConsumer<String, Map<String, Object>> mutate = (r, m) -> {};

    Fixture(Path dir) throws Exception {
      directory = dir;
      current = dir.resolve("epoch.current");
      permit = dir.resolve(EPOCH + ".permit");
      DirectoryCalls delegate = LinuxDirectoryCalls.create();
      DirectoryCalls port =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    String event =
                        switch (name) {
                          case "createPrivateFile" -> "create";
                          case "openEntry", "publish", "sync" -> name;
                          default -> "";
                        };
                    if (!event.isEmpty()) point(event);
                    boolean closed = name.equals("close") && entries.remove((Integer) args[0]);
                    Object result;
                    try {
                      result = method.invoke(delegate, args);
                    } catch (InvocationTargetException e) {
                      throw e.getCause();
                    }
                    if (name.equals("openEntry") || name.equals("createPrivateFile"))
                      entries.add((Integer) result);
                    if (closed) point("entryClose");
                    return result;
                  });
      root = OwnedTransferDirectory.open(port, dir);
      store = new StartupPermitFiles(root, this, this, this);
    }

    int count(String name) {
      return counts.getOrDefault(name, 0);
    }

    void reset() {
      counts.clear();
      events.clear();
      fail = "";
    }

    void seed(String content) throws IOException {
      Files.writeString(current, content);
      reset();
    }

    void setup(String operation) throws Exception {
      if (List.of("replace", "issue", "current", "read").contains(operation)) seed(INVALID);
      if (operation.equals("read")) store.issue(invalid(), StartupPermitFilesTest.permit());
      reset();
    }

    void run(String operation) throws Exception {
      switch (operation) {
        case "new" -> store.invalidate(BOOT, EPOCH, ACTIVE);
        case "replace" -> store.invalidate(BOOT, ACT, ACTIVE);
        case "issue" -> store.issue(invalid(), StartupPermitFilesTest.permit());
        case "current" -> store.current();
        case "read" -> store.readIssued();
        default -> throw new AssertionError();
      }
    }

    void point(String name) throws StorageIoException {
      events.add(name);
      int at = counts.merge(name, 1, Integer::sum);
      if (name.equals(fail) && at == failAt) {
        if (unknown != null) throw unknown;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public UUID next() {
      return new UUID(99, ++part);
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public Map<String, Object> attributes(Path p) throws IOException {
      point("attributes");
      Map<String, Object> m = new HashMap<>(nativeIo.attributes(p));
      int type = (Integer) m.get("mode") & 0170000;
      String role = type == 040000 ? "dir" : "file";
      m.put("uid", 0);
      m.put("gid", 0);
      m.put("mode", type | (role.equals("dir") ? 0700 : 0600));
      if (role.equals(badRole))
        switch (bad) {
          case "nullAttributes" -> {
            return null;
          }
          case "uid" -> m.put("uid", 1);
          case "gid" -> m.put("gid", 1);
          case "mode" -> m.put("mode", type | 0777);
          case "links" -> m.put("nlink", role.equals("dir") ? 1 : 2);
          case "size" -> m.put("size", role.equals("dir") ? -1L : 8193L);
          default -> {}
        }
      mutate.accept(role, m);
      return m;
    }

    private String role(Path p) throws IOException {
      return (((Integer) nativeIo.attributes(p).get("mode")) & 0170000) == 040000 ? "dir" : "file";
    }

    @Override
    public String filesystem(Path p) throws IOException {
      point("filesystem");
      if (role(p).equals(badRole)) {
        if (bad.equals("nullFilesystem")) return null;
        if (bad.equals("filesystem")) return "ext4";
      }
      return "tmpfs";
    }

    @Override
    public byte[] accessAcl(Path p, int maximum) throws StorageIoException {
      point("acl");
      assertEquals(44, maximum);
      try {
        if (role(p).equals(badRole)) {
          if (bad.equals("nullAcl")) return null;
          if (bad.equals("acl")) return new byte[] {1};
        }
      } catch (IOException e) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      return new byte[0];
    }

    @Override
    public boolean readOnlyFilesystem(Path p) throws StorageIoException {
      point("readonly");
      try {
        return role(p).equals(badRole) && bad.equals("readonly");
      } catch (IOException e) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public SeekableByteChannel open(Path p) throws IOException {
      point("openReader");
      if (nullReader) return null;
      SeekableByteChannel channel = nativeIo.open(p);
      readers++;
      return (SeekableByteChannel)
          Proxy.newProxyInstance(
              getClass().getClassLoader(),
              new Class<?>[] {SeekableByteChannel.class},
              (proxy, m, args) -> {
                String name = m.getName();
                if (name.equals("close")) {
                  channel.close();
                  readers--;
                  point("readClose");
                  if (lateInterrupt) Thread.currentThread().interrupt();
                  return null;
                }
                if (name.equals("read")) {
                  point("read");
                  ByteBuffer b = (ByteBuffer) args[0];
                  int start = b.position();
                  if (behavior.equals("zero")) return 0;
                  if (behavior.equals("negative")) return -2;
                  if (behavior.equals("short")) return -1;
                  if (behavior.equals("overflow")) return b.remaining() + 1;
                  if (behavior.equals("fill")) {
                    int count = b.remaining();
                    while (b.hasRemaining()) b.put((byte) 0);
                    return count;
                  }
                  int result = channel.read(b);
                  if (behavior.equals("position")) b.position(start);
                  return result;
                }
                if (name.equals("size")) {
                  point("readSize");
                  return channel.size() + (count("readSize") == wrongSizeAt ? 1 : 0);
                }
                try {
                  return m.invoke(channel, args);
                } catch (InvocationTargetException e) {
                  throw e.getCause();
                }
              });
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path p) throws IOException {
      point("openWriter");
      if (nullWriter) return null;
      var writer = nativeIo.openWriter(p);
      writers++;
      return new InspectorEnvironmentPublisher.Writer() {
        @Override
        public int write(ByteBuffer b) throws IOException {
          point("write");
          int position = b.position();
          if (behavior.equals("zero")) return 0;
          if (behavior.equals("negative")) return -1;
          if (behavior.equals("overflow")) return b.remaining() + 1;
          if (behavior.equals("short")) return 1;
          int result = writer.write(b);
          if (behavior.equals("position")) b.position(position);
          return result;
        }

        @Override
        public long size() throws IOException {
          point("writeSize");
          return writer.size() + (count("writeSize") == wrongSizeAt ? 1 : 0);
        }

        @Override
        public void force() throws IOException {
          point("force");
          writer.force();
        }

        @Override
        public void close() throws IOException {
          writer.close();
          writers--;
          point("writeClose");
        }
      };
    }

    @Override
    public void replace(Path p, String part, String current) throws IOException {
      point("replace");
      if (replaceFailure) throw new AtomicMoveNotSupportedException("public", "public", "public");
      nativeIo.replace(p, part, current);
    }

    @Override
    public MessageDigest digest() throws NoSuchAlgorithmException {
      if (digestFailure) throw new NoSuchAlgorithmException("public");
      return nativeIo.digest();
    }

    void released() {
      assertEquals(0, readers);
      assertEquals(0, writers);
      assertTrue(entries.isEmpty());
    }

    @Override
    public void close() throws IOException {
      root.close();
      released();
    }
  }
}
