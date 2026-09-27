package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.*;
import java.io.*;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;
import java.util.zip.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * Independent literal release/ZIP/CRC fixture. Synthetic owner/RO policy is not native admission.
 */
final class ReleasePayloadVerificationTest {
  @TempDir Path temporary;
  private static final String VERSION = "1.2.3-PG313";
  private static final String SQL_PATH = "db/migration/V001__first.sql";
  private static final byte[] SQL = "select 1;\n".getBytes(StandardCharsets.UTF_8);

  private static String hash(byte[] bytes) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }

  private static byte[] jar(Map<String, byte[]> entries) throws IOException {
    var output = new ByteArrayOutputStream();
    try (var zip = new ZipOutputStream(output)) {
      for (var item : new TreeMap<>(entries).entrySet()) {
        var entry = new ZipEntry(item.getKey());
        entry.setTime(0);
        zip.putNextEntry(entry);
        zip.write(item.getValue());
        zip.closeEntry();
      }
    }
    return output.toByteArray();
  }

  final class Fixture implements StartupReleaseManifest.Io, InodeSecurityCalls {
    final Path opt, release;
    final StartupReleaseManifestTest.Calls calls = new StartupReleaseManifestTest.Calls();
    final StartupReleaseManifest.NioIo nio = new StartupReleaseManifest.NioIo();
    final ReleaseInventoryTest.Fixture literal = new ReleaseInventoryTest.Fixture();
    final TreeMap<String, byte[]> payload = new TreeMap<>();
    ReleaseApproval approval;
    boolean readonly = true, nullNames, nullArchive, failNames, failArchive;

    Fixture(String name) throws Exception {
      opt = Files.createDirectories(temporary.resolve(name).resolve("opt"));
      release = Files.createDirectories(opt.resolve("schubert-nk/releases/" + VERSION));
      Files.createSymbolicLink(opt.resolve("schubert-nk/current"), release);
      payload.put("VERSION", (VERSION + "\n").getBytes(StandardCharsets.US_ASCII));
      payload.put(SQL_PATH, SQL.clone());
      payload.put(
          "api/api.jar",
          jar(Map.of("dev/codex/schubert/nk/api/Main.class", new byte[] {1}, SQL_PATH, SQL)));
      payload.put(
          "web/web.jar", jar(Map.of("dev/codex/schubert/nk/web/Main.class", new byte[] {2})));
      payload.put(
          "operations/batch.jar",
          jar(Map.of("dev/codex/schubert/nk/batch/Main.class", new byte[] {3})));
      for (String namePart : List.of("bootstrap", "storage", "protocol")) {
        byte[] value =
            jar(Map.of("dev/codex/schubert/nk/" + namePart + "/Shared.class", new byte[] {4}));
        for (String role :
            namePart.equals("protocol")
                ? List.of("api", "web")
                : List.of("api", "web", "operations"))
          payload.put(role + "/lib/" + namePart + ".jar", value);
      }
      literal.migrations.set(
          1, literal.migrations.get(1).replace("\"checksum\":0", "\"checksum\":-690524359"));
      publish();
    }

    void publish() throws Exception {
      literal.files.clear();
      var hashes = new TreeMap<String, String>();
      for (var entry : payload.entrySet()) {
        String sha = hash(entry.getValue());
        literal.files.put(
            entry.getKey(),
            "{\"path\":\""
                + entry.getKey()
                + "\",\"size\":"
                + entry.getValue().length
                + ",\"sha256\":\""
                + sha
                + "\"}");
        hashes.put(entry.getKey(), sha);
        write(entry.getKey(), entry.getValue());
      }
      byte[] manifest = literal.text().getBytes(StandardCharsets.UTF_8);
      write("RELEASE-MANIFEST.json", manifest);
      hashes.put("RELEASE-MANIFEST.json", hash(manifest));
      var sums = new StringBuilder();
      hashes.forEach((path, sha) -> sums.append(sha).append("  ").append(path).append('\n'));
      write("SHA256SUMS", sums.toString().getBytes(StandardCharsets.US_ASCII));
      approval = new ReleaseApproval(VERSION, hash(manifest));
      try (var paths = Files.walk(opt)) {
        for (Path p : paths.filter(Files::isDirectory).toList())
          Files.setPosixFilePermissions(
              p, PosixFilePermissions.fromString(p.equals(opt) ? "rwxr-xr-x" : "rwxr-x---"));
      }
    }

    void write(String path, byte[] bytes) throws IOException {
      Path file = release.resolve(path);
      Files.createDirectories(file.getParent());
      Files.write(file, bytes);
      Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-r-----"));
    }

    StartupReleaseManifest subject() {
      return new StartupReleaseManifest(opt, 986, calls, this, this);
    }

    public Map<String, Object> attributes(Path held) throws IOException {
      var value = new HashMap<>(nio.attributes(held));
      value.put("uid", 0);
      int mode = (Integer) value.get("mode");
      value.put("gid", mode == 040755 || mode == 0120777 ? 0 : 986);
      return value;
    }

    public Path selector(Path parent) throws IOException {
      return nio.selector(parent);
    }

    public SeekableByteChannel open(Path held) throws IOException {
      return nio.open(held);
    }

    public DirectoryStream<Path> names(Path held) throws IOException {
      if (failNames) throw new IOException("PRIVATE");
      return nullNames ? null : StartupReleaseManifest.Io.super.names(held);
    }

    public ZipFile archive(Path held) throws IOException {
      if (failArchive) throw new IOException("PRIVATE");
      return nullArchive ? null : StartupReleaseManifest.Io.super.archive(held);
    }

    public byte[] accessAcl(Path held, int limit) {
      return new byte[0];
    }

    public boolean readOnlyFilesystem(Path held) {
      return readonly;
    }

    public long effectiveUid() {
      throw new AssertionError("not actual root proof");
    }

    void released() {
      assertEquals(Set.of(), calls.owned);
      // Calls.add closes the failing attempt before transferring ownership to the caller.
      if (calls.failOpenAt > 0) {
        assertEquals(calls.failOpenAt, calls.opened, "the intended open fault was reached");
        assertEquals(calls.opened, calls.closed + 1, "one self-close before failed transfer");
      } else assertEquals(calls.opened, calls.closed);
      if (calls.failCloseAt > 0)
        assertTrue(calls.closed >= calls.failCloseAt, "the intended close fault was reached");
    }
  }

  private void refused(Fixture f) {
    IOException failure = assertThrows(IOException.class, () -> f.subject().verify(f.approval));
    assertEquals("release manifest unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    f.released();
  }

  @Test
  void fullBom001IndependentLiteralAndAllOwners() throws Exception {
    var f = new Fixture("normal");
    var result = f.subject().verify(f.approval);
    assertEquals(VERSION, result.version());
    assertEquals(f.approval.manifestSha256(), result.sha256());
    assertEquals(2, result.migrations().size());
    assertEquals("25.0.4", result.build().get("jdkVersion"));
    assertEquals("PUBLIC VENDOR", result.build().get("jdkVendor"));
    assertEquals("ubuntu", result.platform().get("osId"));
    assertEquals("26.04", result.platform().get("osVersion"));
    assertThrows(UnsupportedOperationException.class, () -> result.build().clear());
    assertThrows(UnsupportedOperationException.class, () -> result.platform().clear());
    assertEquals(-690524359, result.migrations().get(1).checksum());
    assertThrows(UnsupportedOperationException.class, () -> result.migrations().clear());
    f.released();
  }

  @Test
  void fullBom002ByteInventoryAndNullContracts() throws Exception {
    for (String path : List.of("VERSION", "SHA256SUMS", "api/api.jar", SQL_PATH)) {
      var f = new Fixture("alter-" + path.replace('/', '-'));
      Files.writeString(f.release.resolve(path), "wrong");
      refused(f);
    }
    var f = new Fixture("extra");
    f.write("unknown", new byte[0]);
    refused(f);
    f = new Fixture("missing");
    Files.delete(f.release.resolve("web/web.jar"));
    refused(f);
    var valid = new Fixture("null");
    assertThrows(NullPointerException.class, () -> valid.subject().verify(null));
    valid.released();
  }

  @Test
  void fullBom003ReadonlyAndNamespace() throws Exception {
    var f = new Fixture("rw");
    f.readonly = false;
    refused(f);
    f = new Fixture("hardlink");
    Files.createLink(f.release.resolve("other"), f.release.resolve("VERSION"));
    refused(f);
    f = new Fixture("directory");
    Files.createDirectory(f.release.resolve("empty"));
    refused(f);
    f = new Fixture("symlink");
    Files.delete(f.release.resolve("VERSION"));
    Files.createSymbolicLink(f.release.resolve("VERSION"), Path.of("SHA256SUMS"));
    refused(f);
  }

  @Test
  void fullBom004AcquisitionNullAndIo() throws Exception {
    var f = new Fixture("names");
    f.failNames = true;
    refused(f);
    f = new Fixture("archive");
    f.failArchive = true;
    refused(f);
    var n = new Fixture("nullnames");
    n.nullNames = true;
    assertThrows(NullPointerException.class, () -> n.subject().verify(n.approval));
    n.released();
    var a = new Fixture("nullarchive");
    a.nullArchive = true;
    assertThrows(NullPointerException.class, () -> a.subject().verify(a.approval));
    a.released();
  }

  @Test
  void fullBom005IndependentSqlVectorsAndEmbeddedAgreement() throws Exception {
    for (String text : List.of("select 1;", "select 1;\n", "select 1;\r\n", "\ufeffselect 1;\n"))
      assertEquals(
          -690524359,
          ReleasePayloadVerification.sqlChecksum(text.getBytes(StandardCharsets.UTF_8)));
    assertEquals(0, ReleasePayloadVerification.sqlChecksum(new byte[0]));
    assertEquals(
        -593479011,
        ReleasePayloadVerification.sqlChecksum(
            "select 1;\nselect 2;\n".getBytes(StandardCharsets.UTF_8)));
    assertEquals(
        -921921223,
        ReleasePayloadVerification.sqlChecksum(
            "select 1;\n\ufeffselect 2;\n".getBytes(StandardCharsets.UTF_8)));
    assertEquals(
        1060918784,
        ReleasePayloadVerification.sqlChecksum("select 'é';".getBytes(StandardCharsets.UTF_8)));
    assertThrows(
        IOException.class, () -> ReleasePayloadVerification.sqlChecksum(new byte[] {(byte) 0xff}));
    var f = new Fixture("sql-missing");
    f.payload.put("api/api.jar", jar(Map.of("own.class", new byte[] {1})));
    f.publish();
    refused(f);
    f = new Fixture("sql-wrong");
    f.payload.put("api/api.jar", jar(Map.of(SQL_PATH, new byte[] {1})));
    f.publish();
    refused(f);
  }

  @Test
  void fullBom006ThinLayoutAndSharedShadow() throws Exception {
    var accepted = new Fixture("allowed-layout");
    for (String path :
        List.of(
            "config/templates/common.yml",
            "config/caddy/Caddyfile.template",
            "config/artemis/broker.xml.template",
            "systemd/test.service",
            "systemd/test.target",
            "systemd/test.timer",
            "operations/runbooks/readme.md")) accepted.payload.put(path, new byte[0]);
    accepted.payload.put(
        "web/web.jar",
        jar(
            Map.of(
                "META-INF/",
                new byte[0],
                "META-INF/MANIFEST.MF",
                "Manifest-Version: 1.0\r\nClass-Path: lib/bootstrap.jar lib/storage.jar\r\n\r\n"
                    .getBytes(StandardCharsets.US_ASCII))));
    accepted.publish();
    assertEquals(VERSION, accepted.subject().verify(accepted.approval).version());
    accepted.released();
    var f = new Fixture("nested");
    f.payload.put("api/lib/sub/x.jar", new byte[] {1});
    f.publish();
    refused(f);
    f = new Fixture("shaded");
    f.payload.put(
        "web/web.jar", jar(Map.of("dev/codex/schubert/nk/storage/Shared.class", new byte[] {4})));
    f.publish();
    refused(f);
    f = new Fixture("nestedzip");
    f.payload.put("web/web.jar", jar(Map.of("inner.jar", new byte[] {4})));
    f.publish();
    refused(f);
    f = new Fixture("classpath");
    f.payload.put(
        "web/web.jar",
        jar(
            Map.of(
                "META-INF/MANIFEST.MF",
                "Manifest-Version: 1.0\r\nClass-Path: https://wrong/x.jar\r\n\r\n"
                    .getBytes(StandardCharsets.US_ASCII))));
    f.publish();
    refused(f);
  }

  @Test
  void fullBom007IndependentConcurrentScopes() throws Exception {
    var fixtures = new ArrayList<Fixture>();
    for (int i = 0; i < 4; i++) fixtures.add(new Fixture("parallel-" + i));
    var barrier = new CyclicBarrier(4);
    try (var pool = Executors.newFixedThreadPool(4)) {
      var tasks = new ArrayList<Future<String>>();
      for (var f : fixtures)
        tasks.add(
            pool.submit(
                () -> {
                  barrier.await();
                  return f.subject().verify(f.approval).version();
                }));
      for (var result : tasks) assertEquals(VERSION, result.get(20, TimeUnit.SECONDS));
    }
    fixtures.forEach(Fixture::released);
    var f = new Fixture("interrupt");
    Thread.currentThread().interrupt();
    try {
      refused(f);
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void fullBom008EveryRetainedOwnerAndUntrustedDigest() throws Exception {
    var normal = new Fixture("counts");
    normal.subject().verify(normal.approval);
    normal.released();
    int opened = normal.calls.opened, closed = normal.calls.closed;
    for (int i = 1; i <= opened; i++) {
      var f = new Fixture("open-" + i);
      f.calls.failOpenAt = i;
      refused(f);
    }
    for (int i = 1; i <= closed; i++) {
      var f = new Fixture("close-" + i);
      f.calls.failCloseAt = i;
      refused(f);
    }
    var f = new Fixture("digest");
    f.approval = new ReleaseApproval(VERSION, "a".repeat(64));
    refused(f);
    f = new Fixture("version");
    f.approval = new ReleaseApproval("other", f.approval.manifestSha256());
    refused(f);
  }
}
