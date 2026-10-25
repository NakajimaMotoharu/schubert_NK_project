package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * Independent literal release/ZIP/CRC fixture. Synthetic owner/RO policy is not native admission.
 */
final class ReleasePayloadVerificationTest {
  @Test
  void fullBom017InterruptDuringReadClosesAcquiredChannel() throws Exception {
    var f = new Fixture("interrupt-after-acquire");
    f.channelFault = "interrupt-after-position";
    try {
      refused(f);
    } finally {
      assertTrue(Thread.interrupted(), "cancellation is retained, then cleared by the test");
    }
    assertEquals(1, f.channelFaultReached);
    assertEquals(1, f.channelCloses);
    assertEquals(1, f.channelPositiveReads, "one completed read precedes cancellation");
  }

  @Test
  void fullBom018ManifestBoundsSameSizeTamperAndEnumerationLimitRefuse() throws Exception {
    for (int size : new int[] {0, 1_048_577}) {
      var f = new Fixture("manifest-size-" + size);
      Files.write(f.release.resolve("RELEASE-MANIFEST.json"), new byte[size]);
      refused(f);
    }
    var sameSize = new Fixture("same-size-tamper");
    Files.writeString(
        sameSize.release.resolve("VERSION"), "1.2.3-PG314\n", StandardCharsets.US_ASCII);
    refused(sameSize);
    var enumeration = new Fixture("enumeration-limit");
    enumeration.namesFault = "limit";
    refused(enumeration);
    assertEquals(1, enumeration.namesFaultReached);
    assertEquals(1, enumeration.namesCloses);
  }

  @Test
  void fullBom019RegisteredThirdPartyJarIsNotAnNkSharedDependency() throws Exception {
    var f = new Fixture("third-party-dependency");
    f.payload.put("api/lib/vendor.jar", jar(Map.of("org/example/Vendor.class", new byte[] {8})));
    f.literal.deps.put(
        "org.example:vendor:1.0",
        "{\"coordinate\":\"org.example:vendor:1.0\",\"paths\":[\"api/lib/vendor.jar\"]}");
    f.publish();
    var accepted = f.subject().verifyCandidate(f.approval);
    assertEquals(f.payload.size(), accepted.artifactHashes().size());
    assertEquals(
        hash(f.payload.get("api/lib/vendor.jar")),
        accepted.artifactHashes().get("api/lib/vendor.jar"));
    f.released();
  }

  @Test
  void fullBom014ArchiveMetadataAndStreamDisagreementRefuseAndClose() throws Exception {
    for (String fault :
        List.of(
            "duplicate",
            "negative-size",
            "oversized-entry",
            "short-stream",
            "long-stream",
            "too-many")) {
      var f = new Fixture("archive-contract-" + fault);
      f.archiveFault = fault;
      refused(f);
      assertEquals(1, f.archiveFaultReached, "the API archive contract was exercised");
      assertEquals(1, f.archiveCloses, "the acquired archive was closed exactly once");
      assertEquals(
          fault.endsWith("stream") ? 1 : 0,
          f.archiveStreamCloses,
          "entry stream ownership is not leaked on size disagreement");
    }
  }

  @Test
  void fullBom015MigrationEntriesBelongOnlyToApiAndHaveSqlSuffix() throws Exception {
    var wrongRole = new Fixture("migration-wrong-role");
    wrongRole.payload.put("web/web.jar", jar(Map.of(SQL_PATH, SQL)));
    wrongRole.publish();
    refused(wrongRole);
    var wrongSuffix = new Fixture("migration-wrong-suffix");
    wrongSuffix.payload.put(
        "api/api.jar", jar(Map.of(SQL_PATH, SQL, "db/migration/notes.txt", new byte[] {1})));
    wrongSuffix.publish();
    refused(wrongSuffix);
    var version = new Fixture("signed-wrong-version-bytes");
    version.payload.put("VERSION", "1.2.3-OTHER\n".getBytes(StandardCharsets.US_ASCII));
    version.publish();
    refused(version);
  }

  @Test
  void fullBom016ForeignDeviceAndOversizedMaterialRefuseBeforeRead() throws Exception {
    for (String fault : List.of("directory-device", "payload-device", "material-size")) {
      var f = new Fixture("metadata-" + fault);
      f.metadataFault = fault;
      refused(f);
      assertTrue(f.metadataFaultReached > 0, "the intended held inode metadata was observed");
      assertEquals(0, f.versionOpens, "invalid namespace/material is refused before VERSION read");
    }
  }

  @Test
  void fullBom011IndependentHostileZipAndManifestVectors() throws Exception {
    Map<String, byte[]> manifestVectors = new LinkedHashMap<>();
    for (String value :
        List.of("", " ", "lib/missing.jar", "../storage.jar", "/storage.jar", "lib\\storage.jar"))
      manifestVectors.put(
          "bad-" + manifestVectors.size(),
          ("Manifest-Version: 1.0\r\nClass-Path: " + value + "\r\n\r\n")
              .getBytes(StandardCharsets.US_ASCII));
    for (var item : manifestVectors.entrySet()) {
      var f = new Fixture("manifest-" + item.getKey());
      f.payload.put("web/web.jar", jar(Map.of("META-INF/MANIFEST.MF", item.getValue())));
      f.publish();
      refused(f);
    }
    for (String name :
        List.of(
            "/absolute.class",
            "x\\foreign.class",
            "../foreign.class",
            "x/../foreign.class",
            "nested.jar")) {
      var f = new Fixture("zip-name-" + Math.abs(name.hashCode()));
      f.payload.put("web/web.jar", jar(Map.of(name, new byte[] {1})));
      f.publish();
      refused(f);
    }
    var empty = new Fixture("empty-zip");
    empty.payload.put("web/web.jar", jar(Map.of()));
    empty.publish();
    refused(empty);
    var valid = new Fixture("manifest-without-classpath");
    valid.payload.put(
        "web/web.jar",
        jar(
            Map.of(
                "META-INF/MANIFEST.MF",
                "Manifest-Version: 1.0\r\n\r\n".getBytes(StandardCharsets.US_ASCII),
                "module-info.class",
                new byte[] {7},
                "META-INF/",
                new byte[0])));
    valid.publish();
    assertEquals(
        valid.payload.size(),
        valid.subject().verifyCandidate(valid.approval).artifactHashes().size());
    valid.released();
  }

  @Test
  void fullBom012PayloadChannelContractFailuresCloseEveryOwnedResource() throws Exception {
    for (String fault :
        List.of(
            "size",
            "initial-position",
            "zero",
            "invalid-eof",
            "count",
            "oversized",
            "position",
            "eof-buffer",
            "eof-position",
            "short",
            "final-size",
            "close",
            "open",
            "null")) {
      var f = new Fixture("channel-" + fault);
      f.channelFault = fault;
      if (fault.equals("null")) {
        assertThrows(NullPointerException.class, () -> f.subject().verifyCandidate(f.approval));
        f.released();
      } else refused(f);
      assertEquals(1, f.channelFaultReached, "intended VERSION channel was reached: " + fault);
      assertEquals(
          fault.equals("open") ? 0 : 1,
          f.channelCloses,
          "channel normal close attempted once: " + fault);
    }
  }

  @Test
  void fullBom013EnumerationNullForeignAndDuplicateAreNotSignedChildren() throws Exception {
    for (String fault : List.of("null", "foreign", "duplicate")) {
      var f = new Fixture("enumeration-" + fault);
      f.namesFault = fault;
      refused(f);
      assertEquals(1, f.namesFaultReached);
      assertEquals(1, f.namesCloses);
    }
  }

  @Test
  void fullBom010OnlyFixedSignedBootProvisioningFileIsPermittedAndTamperRefuses() throws Exception {
    var f = new Fixture("signed-fixed-tmpfiles");
    byte[] bytes =
        ("# PUBLIC FIXED BOOT PROVISIONING\n"
                + "d! /run/schubert-nk/expiry-request 0700 root root -\n"
                + "f! /run/schubert-nk/maintenance.lock 0600 root root -\n")
            .getBytes(StandardCharsets.US_ASCII);
    f.payload.put("config/tmpfiles/schubert-nk-maintenance.conf", bytes);
    f.publish();
    var observed = f.subject().verifyCandidate(f.approval);
    assertEquals(
        hash(bytes), observed.artifactHashes().get("config/tmpfiles/schubert-nk-maintenance.conf"));
    assertEquals(f.payload.size(), observed.artifactHashes().size());
    f.released();
    for (String forbidden :
        List.of(
            "config/tmpfiles/other.conf",
            "config/tmpfiles/schubert-nk-maintenance.conf.extra",
            "config/tmpfiles/private-key.pem",
            "config/tmpfiles/schubert-nk-maintenance.service")) {
      var negative = new Fixture("forbidden-tmpfiles-" + Math.abs(forbidden.hashCode()));
      negative.payload.put(forbidden, bytes);
      negative.publish();
      refused(negative);
    }
    Files.writeString(
        f.release.resolve("config/tmpfiles/schubert-nk-maintenance.conf"), "TAMPERED");
    refused(f);
  }

  @Test
  void fullBom009OnlyTwoApprovedPublicEffectiveInputsArePermitted() throws Exception {
    var f = new Fixture("signed-public-effective");
    byte[] profile = "PUBLIC CANONICAL PROFILE FIXTURE\n".getBytes(StandardCharsets.US_ASCII);
    byte[] recipient = "PUBLIC RECIPIENT FIXTURE\n".getBytes(StandardCharsets.US_ASCII);
    f.payload.put("config/effective/backup-profile.json", profile);
    f.payload.put("config/effective/backup-age-recipient", recipient);
    f.publish();
    var observed = f.subject().verifyCandidate(f.approval);
    assertEquals(
        hash(profile), observed.artifactHashes().get("config/effective/backup-profile.json"));
    assertEquals(
        hash(recipient), observed.artifactHashes().get("config/effective/backup-age-recipient"));
    assertEquals(f.payload.size(), observed.artifactHashes().size());
    f.released();
    for (String forbidden :
        List.of(
            "config/effective/private-key.pem",
            "config/effective/unapproved.json",
            "config/effective/backup-profile.json.extra")) {
      var negative = new Fixture("forbidden-effective-" + Math.abs(forbidden.hashCode()));
      negative.payload.put(forbidden, new byte[] {1});
      negative.publish();
      refused(negative);
    }
    Files.writeString(f.release.resolve("config/effective/backup-profile.json"), "TAMPERED");
    refused(f);
  }

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
    final Path opt;
    final Path release;
    final StartupReleaseManifestTest.Calls calls = new StartupReleaseManifestTest.Calls();
    final StartupReleaseManifest.NioIo nio = new StartupReleaseManifest.NioIo();
    final ReleaseInventoryTest.Fixture literal = new ReleaseInventoryTest.Fixture();
    final TreeMap<String, byte[]> payload = new TreeMap<>();
    ReleaseApproval approval;
    boolean readonly = true;
    boolean nullNames;
    boolean nullArchive;
    boolean failNames;
    boolean failArchive;
    String channelFault = "";
    String namesFault = "";
    String archiveFault = "";
    String metadataFault = "";
    int channelFaultReached;
    int channelCloses;
    int namesFaultReached;
    int namesCloses;
    int channelPositiveReads;
    int archiveFaultReached;
    int archiveCloses;
    int archiveStreamCloses;
    int metadataFaultReached;
    int versionOpens;

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
      if (metadataFault.equals("directory-device") && Files.isSameFile(held, release)) {
        value.put("dev", ((Number) value.get("dev")).longValue() + 1);
        metadataFaultReached++;
      } else if (!metadataFault.isEmpty() && Files.isSameFile(held, release.resolve("VERSION"))) {
        if (metadataFault.equals("payload-device"))
          value.put("dev", ((Number) value.get("dev")).longValue() + 1);
        else if (metadataFault.equals("material-size")) value.put("size", 67_108_865L);
        else throw new AssertionError("unregistered fixture");
        metadataFaultReached++;
      }
      return value;
    }

    public Path selector(Path parent) throws IOException {
      return nio.selector(parent);
    }

    public SeekableByteChannel open(Path held) throws IOException {
      if (Files.isSameFile(held, release.resolve("VERSION"))) versionOpens++;
      if (channelFault.isEmpty() || !Files.isSameFile(held, release.resolve("VERSION")))
        return nio.open(held);
      channelFaultReached++;
      if (channelFault.equals("open")) throw new IOException("synthetic provider unavailable");
      var channel = nio.open(held);
      if (channelFault.equals("null")) {
        channel.close();
        channelCloses++;
        return null;
      }
      return new SeekableByteChannel() {
        int reads;
        int sizes;

        public int read(ByteBuffer buffer) throws IOException {
          reads++;
          if (channelFault.equals("zero")) return 0;
          if (channelFault.equals("invalid-eof")) return -2;
          if (channelFault.equals("short")) return -1;
          int n = channel.read(buffer);
          if (n > 0) channelPositiveReads++;
          if (n >= 0 && channelFault.equals("count")) return n + 1;
          if (n >= 0 && channelFault.equals("oversized")) {
            buffer.put((byte) 7);
            return n + 1;
          }
          if (n < 0 && channelFault.equals("eof-buffer")) buffer.put((byte) 7);
          return n;
        }

        public long position() throws IOException {
          if (channelFault.equals("initial-position")
              || (reads > 0 && channelFault.equals("position"))
              || (reads > 1 && channelFault.equals("eof-position"))) return channel.position() + 1;
          long actual = channel.position();
          if (reads > 0 && channelFault.equals("interrupt-after-position"))
            Thread.currentThread().interrupt();
          return actual;
        }

        public long size() throws IOException {
          sizes++;
          return channel.size()
              + ((channelFault.equals("size") || (sizes > 1 && channelFault.equals("final-size")))
                  ? 1
                  : 0);
        }

        public void close() throws IOException {
          channel.close();
          channelCloses++;
          if (channelFault.equals("close")) throw new IOException("synthetic close unavailable");
        }

        public boolean isOpen() {
          return channel.isOpen();
        }

        public int write(ByteBuffer buffer) {
          throw new AssertionError("read-only verification");
        }

        public SeekableByteChannel position(long value) {
          throw new AssertionError("no seek authority");
        }

        public SeekableByteChannel truncate(long value) {
          throw new AssertionError("no mutation authority");
        }
      };
    }

    public DirectoryStream<Path> names(Path held) throws IOException {
      if (failNames) throw new IOException("PRIVATE");
      if (!namesFault.isEmpty() && Files.isSameFile(held, release)) {
        namesFaultReached++;
        var stream = StartupReleaseManifest.Io.super.names(held);
        var entries = new ArrayList<Path>();
        stream.forEach(entries::add);
        switch (namesFault) {
          case "null" -> entries.add(null);
          case "foreign" -> entries.add(temporary.resolve("foreign-child"));
          case "duplicate" -> entries.add(entries.getFirst());
          case "limit" -> {
            entries.clear();
            for (int index = 0; index <= 16384; index++)
              entries.add(held.resolve("unsigned-" + index));
          }
          default -> throw new AssertionError("unregistered fixture");
        }
        return new DirectoryStream<>() {
          public Iterator<Path> iterator() {
            return entries.iterator();
          }

          public void close() throws IOException {
            stream.close();
            namesCloses++;
          }
        };
      }
      return nullNames ? null : StartupReleaseManifest.Io.super.names(held);
    }

    public ZipFile archive(Path held) throws IOException {
      if (failArchive) throw new IOException("PRIVATE");
      if (!archiveFault.isEmpty() && Files.isSameFile(held, release.resolve("api/api.jar"))) {
        archiveFaultReached++;
        return new ZipFile(held.toFile()) {
          public int size() {
            return archiveFault.equals("too-many") ? 131073 : super.size();
          }

          public Enumeration<? extends ZipEntry> entries() {
            var entries = new ArrayList<ZipEntry>();
            super.entries().asIterator().forEachRemaining(entries::add);
            if (archiveFault.equals("duplicate")) entries.add(entries.getFirst());
            for (int index = 0; index < entries.size(); index++) {
              var entry = entries.get(index);
              if (entry.getName().equals(SQL_PATH)) {
                if (archiveFault.equals("negative-size"))
                  entries.set(
                      index,
                      new ZipEntry(entry) {
                        public long getSize() {
                          return -1;
                        }
                      });
                else if (archiveFault.equals("oversized-entry")) entry.setSize(67_108_865);
              }
            }
            return Collections.enumeration(entries);
          }

          public InputStream getInputStream(ZipEntry entry) throws IOException {
            if (!archiveFault.endsWith("stream") || !entry.getName().equals(SQL_PATH))
              return super.getInputStream(entry);
            byte[] bytes =
                Arrays.copyOf(SQL, SQL.length + (archiveFault.equals("short-stream") ? -1 : 1));
            return new ByteArrayInputStream(bytes) {
              public void close() throws IOException {
                super.close();
                archiveStreamCloses++;
              }
            };
          }

          public void close() throws IOException {
            super.close();
            archiveCloses++;
          }
        };
      }
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
    assertEquals("001", result.versions().get("schema"));
    assertEquals(
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(SQL)),
        result.artifactHashes().get(SQL_PATH));
    assertEquals(f.payload.size(), result.artifactHashes().size());
    assertThrows(UnsupportedOperationException.class, () -> result.versions().clear());
    assertThrows(UnsupportedOperationException.class, () -> result.artifactHashes().clear());
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
            "systemd/caddy.service.d/schubert-nk-startup-policy.conf",
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
    // SS343 section 6.8: fixed tools are executable payloads, not arbitrary bin entries.
    for (String tool : List.of("schubert-nkctl", "schubert-nk-inbox-inspector")) {
      var executable = new Fixture("approved-bin-" + tool);
      executable.payload.put(
          "operations/bin/" + tool, "#!/bin/sh\nexit 0\n".getBytes(StandardCharsets.US_ASCII));
      executable.publish();
      Files.setPosixFilePermissions(
          executable.release.resolve("operations/bin/" + tool),
          PosixFilePermissions.fromString("rwxr-x---"));
      assertEquals(VERSION, executable.subject().verify(executable.approval).version());
      executable.released();
      Files.setPosixFilePermissions(
          executable.release.resolve("operations/bin/" + tool),
          PosixFilePermissions.fromString("rw-r-----"));
      refused(executable);
    }
    var unknown = new Fixture("unknown-bin");
    unknown.payload.put("operations/bin/unapproved-tool", new byte[0]);
    unknown.publish();
    Files.setPosixFilePermissions(
        unknown.release.resolve("operations/bin/unapproved-tool"),
        PosixFilePermissions.fromString("rwxr-x---"));
    refused(unknown);
    for (String path :
        List.of(
            "systemd/caddy.service.d/arbitrary.conf",
            "systemd/other.service.d/schubert-nk-startup-policy.conf",
            "systemd/caddy.service.d/sub/schubert-nk-startup-policy.conf")) {
      var unapproved = new Fixture("unapproved-dropin-" + path.replace('/', '-'));
      unapproved.payload.put(path, new byte[0]);
      unapproved.publish();
      refused(unapproved);
    }
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
    var candidate = new Fixture("candidate-no-selector");
    Files.delete(candidate.opt.resolve("schubert-nk/current"));
    var candidateResult = candidate.subject().verifyCandidate(candidate.approval);
    assertEquals(VERSION, candidateResult.version());
    assertFalse(
        Files.exists(candidate.opt.resolve("schubert-nk/current"), LinkOption.NOFOLLOW_LINKS));
    candidate.released();
    int candidateOpens = candidate.calls.opened;
    int candidateCloses = candidate.calls.closed;
    assertThrows(IOException.class, () -> candidate.subject().verify(candidate.approval));
    candidate.released();
    assertThrows(NullPointerException.class, () -> candidate.subject().verifyCandidate(null));
    for (int i = 1; i <= candidateOpens; i++) {
      var fault = new Fixture("candidate-open-" + i);
      fault.calls.failOpenAt = i;
      assertThrows(Exception.class, () -> fault.subject().verifyCandidate(fault.approval));
      assertEquals(i, fault.calls.opened);
      fault.released();
    }
    for (int i = 1; i <= candidateCloses; i++) {
      var fault = new Fixture("candidate-close-" + i);
      fault.calls.failCloseAt = i;
      assertThrows(Exception.class, () -> fault.subject().verifyCandidate(fault.approval));
      assertTrue(fault.calls.closed >= i);
      fault.released();
    }
    var oldSelector = new Fixture("candidate-old-selector");
    Path selector = oldSelector.opt.resolve("schubert-nk/current");
    Files.delete(selector);
    Path oldTarget = oldSelector.opt.resolve("schubert-nk/releases/old-version");
    Files.createSymbolicLink(selector, oldTarget);
    assertEquals(VERSION, oldSelector.subject().verifyCandidate(oldSelector.approval).version());
    assertEquals(oldTarget, Files.readSymbolicLink(selector));
    oldSelector.released();
    assertThrows(
        IOException.class,
        () -> oldSelector.subject().verifyCandidate(new ReleaseApproval(VERSION, "a".repeat(64))));
    oldSelector.released();
    assertThrows(
        IOException.class,
        () ->
            oldSelector
                .subject()
                .verifyCandidate(
                    new ReleaseApproval("missing-version", oldSelector.approval.manifestSha256())));
    oldSelector.released();
    var normal = new Fixture("counts");
    normal.subject().verify(normal.approval);
    normal.released();
    int opened = normal.calls.opened;
    int closed = normal.calls.closed;
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
