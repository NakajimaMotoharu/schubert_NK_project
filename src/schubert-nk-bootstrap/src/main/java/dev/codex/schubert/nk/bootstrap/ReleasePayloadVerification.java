package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.StringReader;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.jar.Manifest;
import java.util.zip.CRC32;
import java.util.zip.ZipFile;
import org.jspecify.annotations.NullMarked;

/**
 * Actual immutable thin release under the outer selector/manifest/approval scope. No publisher,
 * authority token, repair or DB observation. NK-OPS-001/SYS002/004/OPS009/DAT009/UI212/251/253;
 * SS3439.1/11.1/SSC095096/PG-D314; PT-OPS-FULLBOM001..008/018156.
 */
@NullMarked
final class ReleasePayloadVerification {
  private static final java.lang.String LITERAL_RELEASE_MANIFEST_JSON = "RELEASE-MANIFEST.json";

  private static final java.lang.String LITERAL_DB_MIGRATION = "db/migration/";

  private static final int MAX_MATERIAL = 67_108_864;
  private final StartupReleaseManifest reader;
  private final long group;
  private final StartupReleaseManifest.Io io;
  private final InodeSecurityCalls security;
  private final Set<String> identities = new HashSet<>();
  private final Map<String, JarValue> jars = new HashMap<>();
  private final Map<String, Integer> checksums = new HashMap<>();

  private record FileValue(String hash, byte[] material) {}

  private record JarValue(Set<String> classes, Map<String, String> sql) {}

  ReleasePayloadVerification(
      StartupReleaseManifest reader,
      long group,
      StartupReleaseManifest.Io io,
      InodeSecurityCalls security) {
    this.reader = Objects.requireNonNull(reader);
    this.group = group;
    this.io = Objects.requireNonNull(io);
    this.security = Objects.requireNonNull(security);
  }

  StartupReleaseManifest.Contents verify(
      OwnedTransferDirectory release, String version, ReleaseApproval approval)
      throws StorageIoException {
    return release.atExistingEntryHandle(
        LITERAL_RELEASE_MANIFEST_JSON,
        held -> {
          require(version.equals(approval.version()));
          var original = checked(held, 0x81a0);
          require(original.size() > 0 && original.size() <= 1_048_576);
          own(original);
          FileValue value = read(held, original, true);
          require(value.hash().equals(approval.manifestSha256()));
          ReleaseInventory inventory = ReleaseInventory.parse(value.material());
          require(version.equals(inventory.release()));
          var expected = new TreeMap<String, ReleaseInventory.Artifact>();
          for (var artifact : inventory.artifacts()) {
            require(layout(artifact.path()));
            expected.put(artifact.path(), artifact);
          }
          var tree = new TreeMap<String, Set<String>>();
          for (String path : expected.keySet()) add(tree, path);
          add(tree, LITERAL_RELEASE_MANIFEST_JSON);
          add(tree, "SHA256SUMS");
          var sums = new TreeMap<String, String>();
          for (var a : expected.values()) sums.put(a.path(), a.sha256());
          sums.put(LITERAL_RELEASE_MANIFEST_JSON, value.hash());
          StringBuilder canonical = new StringBuilder();
          sums.forEach(
              (path, hash) -> canonical.append(hash).append("  ").append(path).append('\n'));
          byte[] sumBytes = canonical.toString().getBytes(StandardCharsets.US_ASCII);
          walk(release, "", tree, expected, original, sumBytes, inventory);
          require(original.equals(checked(held, 0x81a0)));
          agreement(inventory, expected);
          return new StartupReleaseManifest.Contents(
              version,
              value.hash(),
              inventory.migrations(),
              inventory.build(),
              inventory.platform(),
              inventory.versions(),
              inventory.artifacts().stream()
                  .collect(
                      java.util.stream.Collectors.toUnmodifiableMap(
                          ReleaseInventory.Artifact::path, ReleaseInventory.Artifact::sha256)));
        });
  }

  private static boolean layout(String path) {
    return path.equals("VERSION")
        || path.matches("(?:api/api|web/web|operations/batch)\\.jar")
        || path.matches("(?:api|web|operations)/lib/[^/]+\\.jar")
        || path.matches("db/migration/V[0-9]{3}__[a-z0-9_]+\\.sql")
        || path.matches("config/templates/[A-Za-z0-9._-]+\\.yml")
        || path.equals("config/effective/backup-profile.json")
        || path.equals("config/effective/backup-age-recipient")
        || path.equals("config/caddy/Caddyfile.template")
        || path.equals("config/artemis/broker.xml.template")
        || path.equals("config/tmpfiles/schubert-nk-maintenance.conf")
        || path.matches("systemd/[A-Za-z0-9._-]+\\.(?:service|target|timer)")
        || path.equals("systemd/caddy.service.d/schubert-nk-startup-policy.conf")
        || executable(path)
        || path.matches("operations/runbooks/[A-Za-z0-9._-]+");
  }

  private static boolean executable(String path) {
    return path.equals("operations/bin/schubert-nkctl")
        || path.equals("operations/bin/schubert-nk-inbox-inspector");
  }

  private static void add(Map<String, Set<String>> tree, String path) {
    var parent = new StringBuilder();
    for (String segment : path.split("/")) {
      tree.computeIfAbsent(parent.toString(), ignored -> new TreeSet<>()).add(segment);
      if (!parent.isEmpty()) parent.append('/');
      parent.append(segment);
    }
  }

  private void walk(
      OwnedTransferDirectory directory,
      String path,
      Map<String, Set<String>> tree,
      Map<String, ReleaseInventory.Artifact> expected,
      StartupReleaseManifest.Snapshot original,
      byte[] sumBytes,
      ReleaseInventory inventory)
      throws StorageIoException {
    var before = directory.atDirectory(p -> checked(p, 0x41e8));
    require(before.device() == original.device());
    own(before);
    Set<String> children = Objects.requireNonNull(tree.get(path), "declared directory children");
    names(directory, children);
    for (String name : children) {
      String child = path.isEmpty() ? name : path + "/" + name;
      if (tree.containsKey(child)) {
        ResourceScope.acquire(
            () -> directory.openExistingChild(name),
            OwnedTransferDirectory::close,
            nested -> {
              var first = nested.atDirectory(p -> checked(p, 0x41e8));
              walk(nested, child, tree, expected, original, sumBytes, inventory);
              ResourceScope.acquire(
                  () -> directory.openExistingChild(name),
                  OwnedTransferDirectory::close,
                  reopened -> {
                    require(first.equals(reopened.atDirectory(p -> checked(p, 0x41e8))));
                    return Boolean.TRUE;
                  });
              return Boolean.TRUE;
            });
      } else {
        directory.atExistingEntryHandle(
            name,
            held -> {
              int mode = executable(child) ? 0x81e8 : 0x81a0;
              var first = checked(held, mode);
              require(first.device() == original.device());
              if (child.equals(LITERAL_RELEASE_MANIFEST_JSON)) require(first.equals(original));
              else {
                own(first);
                boolean material =
                    child.equals("VERSION")
                        || child.equals("SHA256SUMS")
                        || child.startsWith(LITERAL_DB_MIGRATION);
                FileValue value = read(held, first, material);
                if (child.equals("SHA256SUMS")) require(Arrays.equals(sumBytes, value.material()));
                else {
                  var a = Objects.requireNonNull(expected.get(child), "declared payload");
                  require(first.size() == a.size() && value.hash().equals(a.sha256()));
                  if (child.equals("VERSION"))
                    require(
                        Arrays.equals(
                            (inventory.release() + "\n").getBytes(StandardCharsets.US_ASCII),
                            value.material()));
                  else if (child.startsWith(LITERAL_DB_MIGRATION))
                    checksums.put(child, sqlChecksum(value.material()));
                  else if (child.endsWith(".jar")) jars.put(child, archive(held, child, expected));
                }
              }
              require(first.equals(checked(held, mode)));
              directory.atExistingEntryHandle(
                  name,
                  reopened -> {
                    require(first.equals(checked(reopened, mode)));
                    return Boolean.TRUE;
                  });
              return Boolean.TRUE;
            });
      }
    }
    names(directory, children);
    require(before.equals(directory.atDirectory(p -> checked(p, 0x41e8))));
  }

  private StartupReleaseManifest.Snapshot checked(Path held, int mode) throws IOException {
    require(!Thread.currentThread().isInterrupted());
    var value = reader.checked(held, group, mode, mode == 0x41e8 ? 2 : 1, -1);
    require(security.readOnlyFilesystem(held));
    return value;
  }

  private void own(StartupReleaseManifest.Snapshot snapshot) throws StorageIoException {
    require(identities.add(snapshot.device() + ":" + snapshot.inode()));
  }

  private void names(OwnedTransferDirectory directory, Set<String> expected)
      throws StorageIoException {
    directory.atDirectory(
        held -> {
          return ResourceScope.acquire(
              () -> io.names(held),
              java.nio.file.DirectoryStream::close,
              names -> {
                var actual = new HashSet<String>();
                for (Path entry : names) {
                  require(entry != null && held.equals(entry.getParent()));
                  require(
                      actual.size() < 16384
                          && actual.add(
                              Objects.requireNonNull(entry.getFileName(), "directory child name")
                                  .toString()));
                }
                require(actual.equals(expected));
                return Boolean.TRUE;
              });
        });
  }

  private FileValue read(Path held, StartupReleaseManifest.Snapshot before, boolean material)
      throws IOException, NoSuchAlgorithmException {
    require(!material || before.size() <= MAX_MATERIAL);
    byte[] bytes = material ? new byte[(int) before.size()] : new byte[0];
    MessageDigest hash = MessageDigest.getInstance("SHA-256");
    return ResourceScope.acquire(
        () -> io.open(held),
        SeekableByteChannel::close,
        channel -> {
          require(channel.size() == before.size() && channel.position() == 0);
          ByteBuffer buffer = ByteBuffer.allocate(8192);
          long total = 0;
          while (true) {
            require(!Thread.currentThread().isInterrupted());
            int count = channel.read(buffer);
            if (count < 0) {
              require(count == -1 && buffer.position() == 0 && channel.position() == total);
              break;
            }
            require(count > 0 && count == buffer.position() && count <= before.size() - total);
            if (material) System.arraycopy(buffer.array(), 0, bytes, (int) total, count);
            total += count;
            require(channel.position() == total);
            buffer.flip();
            hash.update(buffer);
            buffer.clear();
          }
          require(total == before.size() && channel.size() == before.size());
          return new FileValue(HexFormat.of().formatHex(hash.digest()), bytes);
        });
  }

  private JarValue archive(Path held, String path, Map<String, ReleaseInventory.Artifact> expected)
      throws IOException, NoSuchAlgorithmException {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    return ResourceScope.acquire(
        () -> io.archive(held),
        ZipFile::close,
        zip -> {
          require(zip.size() > 0 && zip.size() <= 131072);
          Set<String> entries = new HashSet<>();
          Set<String> classes = new HashSet<>();
          Map<String, String> sql = new HashMap<>();
          var iterator = zip.entries();
          while (iterator.hasMoreElements()) {
            var entry = Objects.requireNonNull(iterator.nextElement(), "archive entry");
            String name = Objects.requireNonNull(entry.getName(), "archive entry name");
            require(
                entries.add(name)
                    && !name.startsWith("/")
                    && !name.contains("\\")
                    && !Arrays.asList(name.split("/", -1)).contains(".."));
            require(!name.endsWith(".jar"));
            if (name.endsWith(".class") && !name.endsWith("module-info.class")) classes.add(name);
            if (entry.isDirectory()) continue;
            if (name.startsWith(LITERAL_DB_MIGRATION) || name.equals("META-INF/MANIFEST.MF")) {
              require(entry.getSize() >= 0 && entry.getSize() <= MAX_MATERIAL);
              byte[] bytes =
                  ResourceScope.acquire(
                      () -> zip.getInputStream(entry),
                      java.io.InputStream::close,
                      stream -> stream.readNBytes((int) entry.getSize() + 1));
              require(bytes.length == entry.getSize());
              if (name.equals("META-INF/MANIFEST.MF")) {
                var manifest = new Manifest(new ByteArrayInputStream(bytes));
                String classpath = manifest.getMainAttributes().getValue("Class-Path");
                if (classpath != null) {
                  require(!classpath.isBlank());
                  for (String token : classpath.trim().split(" +")) {
                    require(token.matches("(?:lib/)?[A-Za-z0-9][A-Za-z0-9._-]*\\.jar"));
                    String target =
                        Objects.requireNonNull(Path.of(path).getParent()).resolve(token).toString();
                    require(expected.containsKey(target));
                  }
                }
              } else {
                require(path.equals("api/api.jar") && name.endsWith(".sql"));
                digest.reset();
                sql.put(name, HexFormat.of().formatHex(digest.digest(bytes)));
              }
            }
          }
          return new JarValue(Set.copyOf(classes), Map.copyOf(sql));
        });
  }

  private void agreement(
      ReleaseInventory inventory, Map<String, ReleaseInventory.Artifact> expected)
      throws StorageIoException {
    Set<String> sharedPaths = new HashSet<>();
    Set<String> sharedClasses = new HashSet<>();
    for (var dep : inventory.dependencies()) {
      if (dep.coordinate()
          .matches("dev\\.codex\\.schubert:schubert-nk-(?:protocol|storage|bootstrap):.+")) {
        sharedPaths.addAll(dep.paths());
        for (String path : dep.paths())
          sharedClasses.addAll(
              Objects.requireNonNull(jars.get(path), "declared shared archive").classes());
      }
    }
    for (var entry : jars.entrySet())
      if (!sharedPaths.contains(entry.getKey()))
        require(Collections.disjoint(sharedClasses, entry.getValue().classes()));
    var sql = Objects.requireNonNull(jars.get("api/api.jar"), "declared API archive").sql();
    require(sql.keySet().equals(checksums.keySet()));
    for (int i = 1; i < inventory.migrations().size(); i++) {
      var row = inventory.migrations().get(i);
      String path = LITERAL_DB_MIGRATION + row.script();
      require(
          Objects.requireNonNull(expected.get(path), "declared SQL artifact")
              .sha256()
              .equals(sql.get(path)));
      require(Objects.equals(row.checksum(), checksums.get(path)));
    }
  }

  /** Flyway13.4: UTF8, line endings ignored, first line BOM only; signed CRC32. */
  static int sqlChecksum(byte[] original) throws IOException {
    String text = StandardCharsets.UTF_8.newDecoder().decode(ByteBuffer.wrap(original)).toString();
    return ResourceScope.acquire(
        () -> new BufferedReader(new StringReader(text), 4096),
        BufferedReader::close,
        reader -> {
          var crc = new CRC32();
          boolean first = true;
          // PG-D804/2476: keep one read, then null termination, before the original body.
          while (true) {
            String line = reader.readLine();
            if (line == null) break;
            if (first && line.startsWith("\ufeff")) line = line.substring(1);
            crc.update(line.getBytes(StandardCharsets.UTF_8));
            first = false;
          }
          return (int) crc.getValue();
        });
  }

  private static void require(boolean valid) throws StorageIoException {
    if (!valid) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }
}
