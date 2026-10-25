package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-RELEASE-001..008; literal SHA256 abc vector, real retained FD and independent faults. */
final class StartupReleaseManifestTest {
  @TempDir Path temporary;

  @Test
  void release010HostFactoryDoesNotGrantUnprivilegedRootInspection() throws Exception {
    assertNotEquals(0, LinuxInodeSecurity.create().effectiveUid(), "host PT runs unprivileged");
    var host = StartupReleaseManifest.createHost(986);
    IOException failure = assertThrows(IOException.class, host::sha256);
    assertEquals("release manifest unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    for (long invalid : new long[] {-1, 0, 4294967295L})
      assertThrows(
          IllegalArgumentException.class, () -> StartupReleaseManifest.createHost(invalid));
  }

  @Test
  void release011CompatibilityContentsCopiesMetadataAndHasNoImplicitAuthority() {
    var build = new HashMap<String, String>();
    build.put("jdkVersion", "25.0.4");
    var platform = new HashMap<String, String>();
    platform.put("osId", "linux");
    var value =
        new StartupReleaseManifest.Contents(
            "literal-release", "a".repeat(64), List.of(), build, platform);
    build.put("jdkVersion", "changed-after-construction");
    platform.clear();
    assertEquals("literal-release", value.version());
    assertEquals("a".repeat(64), value.sha256());
    assertEquals(List.of(), value.migrations());
    assertEquals(Map.of("jdkVersion", "25.0.4"), value.build());
    assertEquals(Map.of("osId", "linux"), value.platform());
    assertEquals(Map.of(), value.versions());
    assertEquals(Map.of(), value.artifactHashes());
    assertThrows(UnsupportedOperationException.class, () -> value.build().put("x", "y"));
    assertThrows(UnsupportedOperationException.class, () -> value.platform().put("x", "y"));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupReleaseManifest.Contents(null, "a".repeat(64), List.of(), build, platform));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents("v", null, List.of(), build, platform));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents("v", "a".repeat(64), null, build, platform));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents("v", "a".repeat(64), List.of(), null, platform));
    assertThrows(
        NullPointerException.class,
        () -> new StartupReleaseManifest.Contents("v", "a".repeat(64), List.of(), build, null));
  }

  @Test
  void release009PublicInfoOnlyFromSameHeldAdmittedBytes() throws Exception {
    var f = new Fixture("public-info");
    String json = new ReleaseInventoryTest.Fixture().text().replace("1.2.3-PG313", "v1");
    Files.writeString(f.manifest, json);
    String expectedDigest =
        HexFormat.of()
            .formatHex(
                java.security.MessageDigest.getInstance("SHA-256")
                    .digest(json.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
    var expected =
        Map.of(
            "commit",
            "a".repeat(40),
            "app",
            "0.1.0",
            "config",
            "1",
            "schema",
            "001",
            "protocol",
            "0.1.0");
    var actual = f.subject().publicInformation(expectedDigest);
    assertEquals(expected, actual);
    assertThrows(UnsupportedOperationException.class, () -> actual.put("secret", "PRIVATE"));
    assertTrue(f.calls.owned.isEmpty());
    assertEquals(f.calls.opened, f.calls.closed);
    assertThrows(IOException.class, () -> f.subject().publicInformation("0".repeat(64)));
    assertThrows(NullPointerException.class, () -> f.subject().publicInformation(null));
    Files.writeString(f.manifest, json.replace("\"release\":\"v1\"", "\"release\":\"v2\""));
    String changed = f.subject().sha256();
    assertThrows(IOException.class, () -> f.subject().publicInformation(changed));
    Files.writeString(f.manifest, "abc");
    assertThrows(
        IOException.class,
        () ->
            f.subject()
                .publicInformation(
                    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"));
    assertTrue(f.calls.owned.isEmpty());
  }

  static class Calls implements DirectoryCalls {
    final DirectoryCalls delegate = LinuxDirectoryCalls.create();
    final Set<Integer> owned = new HashSet<>();
    int opened;
    int closed;
    int failOpenAt;
    int failCloseAt;
    RuntimeException unknown;

    int add(int fd) throws StorageIoException {
      owned.add(fd);
      if (++opened == failOpenAt) {
        delegate.close(fd);
        owned.remove(fd);
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      return fd;
    }

    public int openRoot() throws StorageIoException {
      return add(delegate.openRoot());
    }

    public int openDirectory(int p, String n) throws StorageIoException {
      return add(delegate.openDirectory(p, n));
    }

    public int openEntry(int p, String n) throws StorageIoException {
      return add(delegate.openEntry(p, n));
    }

    public void close(int fd) throws StorageIoException {
      assertTrue(owned.remove(fd), "one close per owner");
      delegate.close(fd);
      if (++closed == failCloseAt) {
        if (unknown != null) throw unknown;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    public int createFile(int p, String n) {
      throw new AssertionError("reader must not create");
    }

    public void createDirectory(int p, String n) {
      throw new AssertionError("reader must not create");
    }

    public void publish(int p, String a, String b) {
      throw new AssertionError("reader must not publish");
    }

    public void unlink(int p, String n) {
      throw new AssertionError("reader must not unlink");
    }

    public void sync(int p) {
      throw new AssertionError("reader must not sync");
    }
  }

  final class Fixture implements StartupReleaseManifest.Io, InodeSecurityCalls {
    final Path opt;
    final Path app;
    final Path releases;
    final Path release;
    final Path manifest;
    final Calls calls = new Calls();
    final StartupReleaseManifest.NioIo nio = new StartupReleaseManifest.NioIo();
    Consumer<Map<String, Object>> mutation = a -> {};
    int observations;
    int changeAt;
    int selectors;
    int selectorChangeAt;
    int channelsClosed;
    String changedKey = "ino";
    byte[] acl = {};
    boolean zeroRead;
    boolean shortRead;
    boolean oversizedRead;
    boolean alteredSize;
    boolean channelCloseFailure;
    boolean failAttributes;
    boolean failSelector;
    boolean failRead;
    boolean failOpen;
    RuntimeException unknown;

    Fixture(String name) throws Exception {
      opt = Files.createDirectories(temporary.resolve(name).resolve("opt"));
      Files.setPosixFilePermissions(opt, PosixFilePermissions.fromString("rwxr-xr-x"));
      app = Files.createDirectory(opt.resolve("schubert-nk"));
      releases = Files.createDirectory(app.resolve("releases"));
      release = Files.createDirectory(releases.resolve("v1"));
      for (Path p : List.of(app, releases, release))
        Files.setPosixFilePermissions(p, PosixFilePermissions.fromString("rwxr-x---"));
      manifest = release.resolve("RELEASE-MANIFEST.json");
      Files.writeString(manifest, "abc");
      Files.setPosixFilePermissions(manifest, PosixFilePermissions.fromString("rw-r-----"));
      Files.createSymbolicLink(app.resolve("current"), release);
    }

    StartupReleaseManifest subject() {
      return new StartupReleaseManifest(opt, 986, calls, this, this);
    }

    public Map<String, Object> attributes(Path held) throws IOException {
      if (unknown != null) throw unknown;
      if (failAttributes) throw new IOException("PRIVATE");
      Map<String, Object> a = new HashMap<>(nio.attributes(held));
      a.put("uid", 0);
      int mode = (Integer) a.get("mode");
      a.put("gid", mode == 040755 || mode == 0120777 ? 0 : 986);
      mutation.accept(a);
      if (++observations == changeAt) {
        if (changedKey.equals("ino")) a.put("ino", (Long) a.get("ino") + 1);
        else a.put(changedKey, FileTime.fromMillis(1));
      }
      return a;
    }

    public Path selector(Path held) throws IOException {
      if (failSelector) throw new IOException("PRIVATE");
      return ++selectors == selectorChangeAt ? releases.resolve("v2") : nio.selector(held);
    }

    public SeekableByteChannel open(Path held) throws IOException {
      if (failOpen) throw new IOException("PRIVATE");
      SeekableByteChannel source = nio.open(held);
      return new SeekableByteChannel() {
        int sizes;
        int reads;

        public int read(ByteBuffer b) throws IOException {
          if (failRead) throw new IOException("PRIVATE");
          if (zeroRead) return 0;
          if (shortRead) return -1;
          if (oversizedRead) {
            b.put(new byte[b.remaining()]);
            return b.position();
          }
          reads++;
          return source.read(b);
        }

        public long size() throws IOException {
          return alteredSize && ++sizes == 2 ? 4 : source.size();
        }

        public void close() throws IOException {
          source.close();
          channelsClosed++;
          if (channelCloseFailure) throw new IOException("PRIVATE");
        }

        public boolean isOpen() {
          return source.isOpen();
        }

        public long position() throws IOException {
          return source.position();
        }

        public SeekableByteChannel position(long p) throws IOException {
          source.position(p);
          return this;
        }

        public int write(ByteBuffer b) {
          throw new AssertionError("read only");
        }

        public SeekableByteChannel truncate(long n) {
          throw new AssertionError("read only");
        }
      };
    }

    public byte[] accessAcl(Path held, int limit) {
      assertEquals(44, limit);
      return acl;
    }

    public boolean readOnlyFilesystem(Path held) {
      throw new AssertionError("private read does not assert host RW");
    }

    public long effectiveUid() {
      throw new AssertionError("reader does not assert caller root");
    }
  }

  static void denied(Fixture f) {
    IOException e = assertThrows(IOException.class, () -> f.subject().sha256());
    assertEquals("release manifest unavailable", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
    assertEquals(Set.of(), f.calls.owned);
  }

  @Test
  void release001ActualBytesFixedGoldenAndNoExportedOwner() throws Exception {
    var f = new Fixture("golden");
    assertEquals(
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", f.subject().sha256());
    assertEquals(Set.of(), f.calls.owned);
    assertEquals(f.calls.opened, f.calls.closed);
    assertEquals(1, f.channelsClosed);
    assertEquals("abc", Files.readString(f.manifest));
    assertEquals(f.release, Files.readSymbolicLink(f.app.resolve("current")));
  }

  @Test
  void release002SelectorCanonicalBoundariesAndNonfollowTargets() throws Exception {
    Path opt = Path.of("/opt");
    for (String v : List.of("a", "v1.2_-", "a".repeat(64)))
      assertEquals(
          v, StartupReleaseManifest.version(Path.of("/opt/schubert-nk/releases").resolve(v), opt));
    for (String bad :
        List.of(
            "v1",
            "/",
            "/tmp/v1",
            "/opt/schubert-nk/releases/..",
            "/opt/schubert-nk/releases/v1/x",
            "/opt/schubert-nk/releases/.hidden",
            "/opt/schubert-nk/releases/-v1",
            "/opt/schubert-nk/releases/vä",
            "/opt/schubert-nk/releases/" + "a".repeat(65)))
      assertThrows(IOException.class, () -> StartupReleaseManifest.version(Path.of(bad), opt));
    var f = new Fixture("selector");
    Files.delete(f.app.resolve("current"));
    Files.writeString(f.app.resolve("current"), "abc");
    denied(f);
    Files.delete(f.app.resolve("current"));
    Files.createSymbolicLink(f.app.resolve("current"), Path.of("releases/v1"));
    denied(f);
    Files.delete(f.app.resolve("current"));
    Files.createSymbolicLink(f.app.resolve("current"), f.release);
    Files.move(f.release, f.releases.resolve("other"));
    Files.createSymbolicLink(f.release, f.releases.resolve("other"));
    denied(f);
    Files.delete(f.release);
    Files.move(f.releases.resolve("other"), f.release);
    Files.delete(f.manifest);
    Files.createSymbolicLink(f.manifest, f.app.resolve("current"));
    denied(f);
  }

  @Test
  void release003EveryTypedAttributeOwnerModeLinkAndAclRejection() throws Exception {
    var f = new Fixture("metadata");
    for (String key :
        List.of("uid", "gid", "mode", "nlink", "dev", "ino", "size", "lastModifiedTime", "ctime")) {
      f.mutation = a -> a.remove(key);
      denied(f);
      f.mutation = a -> a.put(key, "wrong");
      denied(f);
    }
    for (var bad :
        Map.<String, Object>of(
                "uid", 1, "gid", 1, "mode", 040777, "nlink", 0, "dev", 0L, "ino", 0L, "size", -1L)
            .entrySet()) {
      f.mutation = a -> a.put(bad.getKey(), bad.getValue());
      denied(f);
    }
    f.mutation =
        a -> {
          if ((Integer) a.get("mode") == 0120777) a.put("nlink", 2);
        };
    denied(f);
    f.mutation =
        a -> {
          if ((Integer) a.get("mode") == 0100640) a.put("size", 0L);
        };
    denied(f);
    f.mutation =
        a -> {
          if ((Integer) a.get("mode") == 0100640) a.put("size", 1_048_577L);
        };
    denied(f);
    f.mutation = a -> {};
    f.acl = new byte[] {1};
    denied(f);
    f.acl = new byte[0];
    assertEquals(64, f.subject().sha256().length());
  }

  @Test
  void release004NamespaceAndMetadataChangesAtEveryRecheck() throws Exception {
    var baseline = new Fixture("count");
    baseline.subject().sha256();
    // Every held/namespace recheck is an independently mutated observation, not a digest oracle.
    for (int n = 1; n <= baseline.observations; n++) {
      var f = new Fixture("mutation" + n);
      f.changeAt = n;
      denied(f);
    }
    for (String time : List.of("lastModifiedTime", "ctime")) {
      var f = new Fixture(time);
      f.changeAt = 7;
      f.changedKey = time;
      denied(f);
    }
    var f = new Fixture("changedselector");
    f.selectorChangeAt = 2;
    denied(f);
  }

  @Test
  void release005ReadLengthEofBoundaryAndIoFailures() throws Exception {
    for (String fault :
        List.of("zero", "short", "over", "size", "attr", "selector", "read", "open", "close")) {
      var f = new Fixture(fault);
      switch (fault) {
        case "zero" -> f.zeroRead = true;
        case "short" -> f.shortRead = true;
        case "over" -> f.oversizedRead = true;
        case "size" -> f.alteredSize = true;
        case "attr" -> f.failAttributes = true;
        case "selector" -> f.failSelector = true;
        case "read" -> f.failRead = true;
        case "open" -> f.failOpen = true;
        case "close" -> f.channelCloseFailure = true;
        default -> throw new AssertionError();
      }
      denied(f);
    }
    var mismatched = new Fixture("sizeinitial");
    mismatched.mutation =
        a -> {
          if ((Integer) a.get("mode") == 0100640) a.put("size", 4L);
        };
    denied(mismatched);
    var bound = new Fixture("bound");
    Files.write(bound.manifest, new byte[1_048_576]);
    assertEquals(
        "30e14955ebf1352266dc2ff8067e68104607e750abb9d3b36582b8af909fcb58",
        bound.subject().sha256());
    assertEquals(Set.of(), bound.calls.owned);
  }

  @Test
  void release006EveryAcquisitionCloseFailureAndUnknownPriority() throws Exception {
    var base = new Fixture("ownership");
    base.subject().sha256();
    for (int n = 1; n <= base.calls.opened; n++) {
      var f = new Fixture("open" + n);
      f.calls.failOpenAt = n;
      denied(f);
    }
    for (int n = 1; n <= base.calls.closed; n++) {
      var f = new Fixture("close" + n);
      f.calls.failCloseAt = n;
      denied(f);
    }
    var f = new Fixture("unknown");
    var unknown = new IllegalStateException("UNKNOWN");
    f.unknown = unknown;
    assertSame(unknown, assertThrows(IllegalStateException.class, () -> f.subject().sha256()));
    assertEquals(Set.of(), f.calls.owned);
    var close = new Fixture("unknownclose");
    close.calls.failCloseAt = 1;
    close.calls.unknown = unknown;
    assertSame(unknown, assertThrows(IllegalStateException.class, () -> close.subject().sha256()));
    assertEquals(Set.of(), close.calls.owned);
  }

  @Test
  void release007NullInvariantUnsignedMetadataAndConcurrency() throws Exception {
    var f = new Fixture("invariant");
    assertThrows(
        NullPointerException.class, () -> new StartupReleaseManifest(null, 986, f.calls, f, f));
    assertThrows(
        NullPointerException.class, () -> new StartupReleaseManifest(f.opt, 986, null, f, f));
    assertThrows(
        NullPointerException.class, () -> new StartupReleaseManifest(f.opt, 986, f.calls, null, f));
    assertThrows(
        NullPointerException.class, () -> new StartupReleaseManifest(f.opt, 986, f.calls, f, null));
    for (Path bad : List.of(Path.of("relative"), Path.of("/"), Path.of("/opt/../etc")))
      assertThrows(
          IllegalArgumentException.class,
          () -> new StartupReleaseManifest(bad, 986, f.calls, f, f));
    for (long group : List.of(0L, -1L, 4294967295L))
      assertThrows(
          IllegalArgumentException.class,
          () -> new StartupReleaseManifest(f.opt, group, f.calls, f, f));
    assertThrows(NullPointerException.class, () -> StartupReleaseManifest.version(null, f.opt));
    f.mutation =
        a -> {
          a.put("dev", -1L);
          a.put("ino", -1L);
        };
    assertEquals(64, f.subject().sha256().length());
    var maxGroup =
        new StartupReleaseManifest(
            f.opt,
            4294967294L,
            f.calls,
            f,
            new StartupReleaseManifest.Io() {
              public Map<String, Object> attributes(Path p) throws IOException {
                var a = f.attributes(p);
                if ((Integer) a.get("gid") == 986) a.put("gid", -2);
                return a;
              }

              public Path selector(Path p) throws IOException {
                return f.selector(p);
              }

              public SeekableByteChannel open(Path p) throws IOException {
                return f.open(p);
              }
            });
    assertEquals(64, maxGroup.sha256().length());
    var subjects = new ArrayList<Fixture>();
    for (int n = 0; n < 16; n++) subjects.add(new Fixture("parallel" + n));
    try (var executor = Executors.newFixedThreadPool(4)) {
      var futures = new ArrayList<Future<String>>();
      for (var subject : subjects) futures.add(executor.submit(() -> subject.subject().sha256()));
      for (var future : futures)
        assertEquals(
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", future.get());
    }
    subjects.forEach(subject -> assertEquals(Set.of(), subject.calls.owned));
  }

  @Test
  void release008NativeReaderDoesNotBypassOwnershipGate() throws Exception {
    StartupReleaseManifest production = StartupReleaseManifest.create(986);
    assertNotNull(production);
    assertThrows(IOException.class, production::sha256);
    var f = new Fixture("nativeio");
    var io = new StartupReleaseManifest.NioIo();
    assertEquals(f.release, io.selector(f.app));
    assertEquals(0100640, io.attributes(f.manifest).get("mode"));
    try (var channel = io.open(f.manifest)) {
      var bytes = ByteBuffer.allocate(3);
      assertEquals(3, channel.read(bytes));
      assertArrayEquals(new byte[] {97, 98, 99}, bytes.array());
    }
  }
}
