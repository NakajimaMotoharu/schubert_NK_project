package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupManifestFixture;
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
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.function.BiConsumer;
import java.util.function.Function;

/**
 * Public synthetic content, real Linux FD/IO, synthetic root/dedicated UID policy.
 * PG166/BAT194..209.
 */
final class BackupArtifactFixture
    implements AutoCloseable,
        BackupArtifactVerifier.Io,
        BackupManifestReader.Io,
        InodeSecurityCalls {
  static final String DIR = "20260913-000002-12345678-9abc-def0-8123-456789abcdef";
  static final long UID = 2000;
  static final long GID = 2001;
  static final String DUMP_HASH =
      "9ae12cbba1c4e9e71419a38fde527ad49dac8ecd22d408173df80165d27d0aa9";
  static final String CONFIG_HASH =
      "0793bedfb1288edbbf286aeda46ff08601492dc311bcc9ef352d5b76b4a0eb9a";
  static final String CREDS_HASH =
      "de5619301aab91cfd8872a1bd80b7f9c793bf01ca40fa38bfe2ac15ff93debb2";
  static final String MANIFEST_HASH =
      "bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370";
  static final List<String> NAMES =
      List.of("MANIFEST.json", "schubert_nk.dump", "config.tar", "credentials.tar.age");
  static final Map<String, Integer> COUNTS =
      Map.ofEntries(
          Map.entry("attributes", 17),
          Map.entry("acl", 17),
          Map.entry("readonly", 17),
          Map.entry("openNames", 2),
          Map.entry("iterator", 2),
          Map.entry("hasNext", 10),
          Map.entry("next", 8),
          Map.entry("closeNames", 2),
          Map.entry("digest", 4),
          Map.entry("openChannel", 4),
          Map.entry("size", 8),
          Map.entry("read", 8),
          Map.entry("closeChannel", 4),
          Map.entry("openDirectory", 2),
          Map.entry("closeDirectory", 2),
          Map.entry("openEntry", 8),
          Map.entry("closeEntry", 8),
          Map.entry("effectiveUid", 2),
          Map.entry("clock", 207));

  final Path parent;
  final Path child;
  final OwnedTransferDirectory root;
  final BackupArtifactVerifier.NioIo real = new BackupArtifactVerifier.NioIo();
  final Map<String, Integer> counts = new LinkedHashMap<>();
  final List<String> events = new ArrayList<>();
  final Set<Integer> directories = new HashSet<>();
  final Set<Integer> entries = new HashSet<>();
  final Set<byte[]> buffers = Collections.newSetFromMap(new IdentityHashMap<>());
  final Map<String, byte[]> initial;
  final int rootDescriptor;
  int channelCount;
  int streamCount;
  int faultAt;
  int position;
  int smallRead = Integer.MAX_VALUE;
  long effective = 0;
  long clockValue = 100;
  boolean tracking;
  boolean readonly;
  boolean nullAttributes;
  boolean nullChannel;
  boolean nullNames;
  boolean nullDigest;
  byte[] acl = new byte[0];
  String selectedRole = "*";
  String readMode = "";
  String sizeMode = "";
  Throwable primary;
  final Set<String> extraFaults = new HashSet<>();
  final Map<String, Throwable> faultTypes = new HashMap<>();
  Function<Path, List<Path>> listing;
  BiConsumer<String, Integer> hook = (name, n) -> {};
  BiConsumer<String, Map<String, Object>> metadata = (role, values) -> {};
  BackupManifest expected = expected();

  BackupArtifactFixture(Path temporary) throws Exception {
    parent =
        Files.createDirectory(Files.createTempDirectory(temporary, "artifact-").resolve("backup"));
    child = Files.createDirectory(parent.resolve(DIR));
    Files.write(child.resolve("MANIFEST.json"), golden());
    Files.writeString(
        child.resolve("schubert_nk.dump"),
        "PG166 public dump fixture\n",
        StandardCharsets.US_ASCII);
    Files.writeString(
        child.resolve("config.tar"),
        "PG166 public configuration fixture\n",
        StandardCharsets.US_ASCII);
    Files.writeString(
        child.resolve("credentials.tar.age"),
        "PG166 public ciphertext fixture\n",
        StandardCharsets.US_ASCII);
    Files.setPosixFilePermissions(
        parent, java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
    Files.setPosixFilePermissions(
        child, java.nio.file.attribute.PosixFilePermissions.fromString("rwx------"));
    for (String name : NAMES)
      Files.setPosixFilePermissions(
          child.resolve(name),
          java.nio.file.attribute.PosixFilePermissions.fromString("rw-------"));
    initial = disk();
    DirectoryCalls nativeCalls = LinuxDirectoryCalls.create();
    DirectoryCalls calls =
        (DirectoryCalls)
            Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {DirectoryCalls.class},
                (proxy, method, args) -> {
                  String name = method.getName();
                  if (!Set.of("openRoot", "openDirectory", "openEntry", "close").contains(name))
                    throw new AssertionError("verifier attempted a mutation");
                  boolean close = name.equals("close");
                  String event =
                      close
                          ? (entries.contains((Integer) args[0]) ? "closeEntry" : "closeDirectory")
                          : name;
                  if (!close) nativePoint(event);
                  Object result;
                  try {
                    result = method.invoke(nativeCalls, args);
                  } catch (InvocationTargetException failure) {
                    throw failure.getCause();
                  }
                  if (close) {
                    entries.remove((Integer) args[0]);
                    directories.remove((Integer) args[0]);
                    nativePoint(event);
                  } else if (name.equals("openEntry")) entries.add((Integer) result);
                  else directories.add((Integer) result);
                  return result;
                });
    root = OwnedTransferDirectory.open(calls, parent);
    assertEquals(1, directories.size());
    rootDescriptor = directories.iterator().next();
    tracking = true;
  }

  static BackupManifest expected() {
    return BackupManifestFixture.manifest(
        6, new BackupFileDigest(26, DUMP_HASH),
        7, new BackupFileDigest(35, CONFIG_HASH),
        8, new BackupFileDigest(32, CREDS_HASH));
  }

  static byte[] golden() throws IOException {
    try (var in =
        Objects.requireNonNull(
            BackupArtifactFixture.class.getResourceAsStream("/backup/artifact-manifest.json"))) {
      return in.readAllBytes();
    }
  }

  BackupArtifactVerifier verifier() {
    return new BackupArtifactVerifier(root, this, UID, GID, this, this::digest, this::clock);
  }

  MessageDigest digest() throws NoSuchAlgorithmException {
    try {
      point("digest");
    } catch (IOException failure) {
      throw new NoSuchAlgorithmException("public synthetic provider fault");
    }
    return nullDigest ? null : MessageDigest.getInstance("SHA-256");
  }

  long clock() {
    uncheckedPoint("clock");
    return clockValue;
  }

  void point(String name) throws IOException {
    if (!tracking) return;
    int n = counts.merge(name, 1, Integer::sum);
    hook.accept(name, n);
    if (!name.equals("clock") && !name.equals("effectiveUid")) {
      position++;
      events.add(name);
      if (faultAt == position || extraFaults.contains(name + "#" + n)) {
        Throwable selected = faultTypes.getOrDefault(name + "#" + n, primary);
        if (selected instanceof RuntimeException value) throw value;
        if (selected instanceof Error value) throw value;
        throw new IOException("public synthetic raw IO detail");
      }
    }
  }

  void nativePoint(String name) throws StorageIoException {
    try {
      point(name);
    } catch (IOException failure) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  void uncheckedPoint(String name) {
    try {
      point(name);
    } catch (IOException failure) {
      throw new DirectoryIteratorException(failure);
    }
  }

  String role(Path held) throws IOException {
    String name = Files.readSymbolicLink(held).getFileName().toString();
    if (name.endsWith(" (deleted)")) name = name.substring(0, name.length() - 10);
    if (name.equals("backup")) return "parent";
    if (name.equals(DIR)) return "child";
    return name;
  }

  boolean selected(String role) {
    return selectedRole.equals("*") || selectedRole.equals(role);
  }

  @Override
  public Map<String, Object> attributes(Path held) throws IOException {
    point("attributes");
    if (nullAttributes) return null;
    var values = new HashMap<>(real.attributes(held));
    String role = role(held);
    int type = ((Integer) values.get("mode")) & 0170000;
    boolean directory = type == 040000;
    values.put("uid", directory || role.equals("schubert_nk.dump") ? (int) UID : 0);
    values.put("gid", directory || role.equals("schubert_nk.dump") ? (int) GID : 0);
    if (selected(role)) metadata.accept(role, values);
    return values;
  }

  @Override
  public byte[] accessAcl(Path held, int maximum) throws StorageIoException {
    nativePoint("acl");
    assertEquals(44, maximum);
    try {
      return selected(role(held)) ? acl : new byte[0];
    } catch (IOException failure) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  @Override
  public boolean readOnlyFilesystem(Path held) throws StorageIoException {
    nativePoint("readonly");
    try {
      return selected(role(held)) && readonly;
    } catch (IOException failure) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }

  @Override
  public long effectiveUid() {
    uncheckedPoint("effectiveUid");
    return effective;
  }

  @Override
  public DirectoryStream<Path> openNames(Path held) throws IOException {
    point("openNames");
    if (nullNames) return null;
    DirectoryStream<Path> delegate = real.openNames(held);
    List<Path> listed = listing == null ? null : listing.apply(held);
    streamCount++;
    return new DirectoryStream<>() {
      @Override
      public Iterator<Path> iterator() {
        uncheckedPoint("iterator");
        Iterator<Path> iterator = listed == null ? delegate.iterator() : listed.iterator();
        return new Iterator<>() {
          @Override
          public boolean hasNext() {
            uncheckedPoint("hasNext");
            return iterator.hasNext();
          }

          @Override
          public Path next() {
            uncheckedPoint("next");
            return iterator.next();
          }
        };
      }

      @Override
      public void close() throws IOException {
        try {
          delegate.close();
        } finally {
          streamCount--;
        }
        point("closeNames");
      }
    };
  }

  @Override
  public SeekableByteChannel open(Path held) throws IOException {
    point("openChannel");
    if (nullChannel) return null;
    SeekableByteChannel delegate = real.open(held);
    String role = role(held);
    channelCount++;
    return new SeekableByteChannel() {
      int reads;
      int sizes;

      @Override
      public int read(ByteBuffer buffer) throws IOException {
        point("read");
        reads++;
        buffers.add(buffer.array());
        if (selected(role)) {
          if (readMode.equals("zero")) return 0;
          if (readMode.equals("short")) return -1;
          if (readMode.equals("count")) return buffer.limit() + 1;
          if (readMode.equals("position")) return 1;
          if (reads == 2 && readMode.equals("extra")) {
            buffer.put((byte) 1);
            return 1;
          }
          if (reads == 2 && readMode.equals("eof-position")) {
            buffer.put((byte) 1);
            return -1;
          }
        }
        int limit = buffer.limit();
        // PG169: accumulated manifest reads and reset-per-chunk artifact reads share this port.
        buffer.limit(buffer.position() + Math.min(buffer.remaining(), smallRead));
        int actual = delegate.read(buffer);
        buffer.limit(limit);
        if (selected(role) && readMode.equals("content") && actual > 0)
          buffer.put(0, (byte) (buffer.get(0) ^ 1));
        return actual;
      }

      @Override
      public long size() throws IOException {
        point("size");
        sizes++;
        long value = delegate.size();
        if (selected(role)
            && (sizeMode.equals("first") && sizes == 1 || sizeMode.equals("last") && sizes == 2))
          return value + 1;
        return value;
      }

      @Override
      public long position() {
        throw new AssertionError("unexpected position access");
      }

      @Override
      public SeekableByteChannel position(long p) {
        throw new AssertionError("position mutation");
      }

      @Override
      public SeekableByteChannel truncate(long s) {
        throw new AssertionError("truncate mutation");
      }

      @Override
      public int write(ByteBuffer b) {
        throw new AssertionError("write mutation");
      }

      @Override
      public boolean isOpen() {
        return delegate.isOpen();
      }

      @Override
      public void close() throws IOException {
        try {
          delegate.close();
        } finally {
          channelCount--;
        }
        point("closeChannel");
      }
    };
  }

  Map<String, byte[]> disk() throws IOException {
    var result = new TreeMap<String, byte[]>();
    try (var paths = Files.list(child)) {
      for (Path path : paths.toList())
        if (Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS))
          result.put(path.getFileName().toString(), Files.readAllBytes(path));
    }
    return result;
  }

  void unchanged() throws IOException {
    var actual = disk();
    assertEquals(initial.keySet(), actual.keySet());
    for (String name : initial.keySet()) assertArrayEquals(initial.get(name), actual.get(name));
  }

  void released() {
    assertEquals(Set.of(rootDescriptor), directories);
    assertEquals(Set.of(), entries);
    assertEquals(0, channelCount);
    assertEquals(0, streamCount);
    for (byte[] buffer : buffers) for (byte value : buffer) assertEquals(0, value);
  }

  @Override
  public void close() throws StorageIoException {
    tracking = false;
    root.close();
    assertTrue(directories.isEmpty());
    assertTrue(entries.isEmpty());
    assertEquals(0, channelCount);
    assertEquals(0, streamCount);
  }
}
