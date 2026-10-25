package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.BiConsumer;

/** Writer-only fixture; real FD/IO, public bytes, synthetic UID. BAT242..257/SS341 6.8. */
final class BackupPublicationFixture
    implements AutoCloseable,
        InspectorEnvironmentPublisher.Io,
        BackupBundlePublisher.Io,
        InodeSecurityCalls {
  static final UUID PART = UUID.fromString("11111111-2222-4333-8444-555555555555");
  static final long UID = 2000;
  static final long GID = 2001;
  final Path parent;
  final Path child;
  final OwnedTransferDirectory root;
  final DirectoryCalls calls;
  final InspectorEnvironmentPublisher.NioIo nativeIo = new InspectorEnvironmentPublisher.NioIo();
  final Set<Integer> descriptors = ConcurrentHashMap.newKeySet();
  final Set<byte[]> buffers = ConcurrentHashMap.newKeySet();
  final Map<String, Integer> counts = new ConcurrentHashMap<>();
  final Map<String, Throwable> faults = new HashMap<>();
  final List<String> events = Collections.synchronizedList(new ArrayList<>());
  final int rootFd;
  int channels;
  int streams;
  int faultAt;
  int position;
  boolean bundle;
  long effective = 0;
  long time = 100;
  int chunk = Integer.MAX_VALUE;
  volatile boolean track = true;
  boolean nullMap;
  boolean nullWriter;
  boolean nullReader;
  boolean readonly;
  byte[] acl = new byte[0];
  String writeMode = "";
  String readMode = "";
  String copyFilesystem = "tmpfs";
  String changedSize = "";
  BiConsumer<String, Integer> hook = (name, n) -> {};
  BiConsumer<String, Map<String, Object>> metadata = (role, values) -> {};

  BackupPublicationFixture(Path temporary) throws Exception {
    parent = Files.createTempDirectory(temporary, "publication-");
    child = Files.createDirectory(parent.resolve(BackupArtifactFixture.DIR + ".part"));
    Files.setPosixFilePermissions(parent, PosixFilePermissions.fromString("rwx------"));
    Files.setPosixFilePermissions(child, PosixFilePermissions.fromString("rwx------"));
    DirectoryCalls nativeCalls = LinuxDirectoryCalls.create();
    calls =
        (DirectoryCalls)
            Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {DirectoryCalls.class},
                (proxy, method, args) -> {
                  String name = method.getName();
                  if (!Set.of(
                          "openRoot",
                          "openDirectory",
                          "openEntry",
                          "createPrivateFile",
                          "unlink",
                          "publish",
                          "sync",
                          "close")
                      .contains(name)) throw new AssertionError("unapproved mutation " + name);
                  if (!name.equals("close")) point(name);
                  Object result;
                  try {
                    result = method.invoke(nativeCalls, args);
                  } catch (InvocationTargetException failure) {
                    throw failure.getCause();
                  }
                  if (name.equals("close")) {
                    descriptors.remove((Integer) args[0]);
                    point("close");
                  } else if (Set.of("openRoot", "openDirectory", "openEntry", "createPrivateFile")
                      .contains(name)) descriptors.add((Integer) result);
                  return result;
                });
    track = false;
    root = OwnedTransferDirectory.open(calls, parent);
    rootFd = descriptors.iterator().next();
    track = true;
  }

  BackupManifestPublisher publisher() {
    return new BackupManifestPublisher(root, this, UID, GID, this, this::clock);
  }

  void create() throws StorageIoException {
    publisher().create(BackupArtifactFixture.expected(), PART);
  }

  BackupBundlePublisher bundlePublisher() {
    return new BackupBundlePublisher(root, this, UID, GID, this, this::clock);
  }

  void seedBundle() throws IOException {
    bundle = true;
    Files.write(child.resolve("MANIFEST.json"), BackupArtifactFixture.golden());
    Files.writeString(child.resolve("schubert_nk.dump"), "PG166 public dump fixture\n");
    Files.writeString(child.resolve("config.tar"), "PG166 public configuration fixture\n");
    Files.writeString(child.resolve("credentials.tar.age"), "PG166 public ciphertext fixture\n");
    for (String name : BackupArtifactFixture.NAMES)
      Files.setPosixFilePermissions(
          child.resolve(name), PosixFilePermissions.fromString("rw-------"));
  }

  long clock() {
    try {
      point("clock");
    } catch (IOException failure) {
      throw new AssertionError("clock IO not supported", failure);
    }
    return time;
  }

  void point(String name) throws StorageIoException {
    if (!track) return;
    int n = counts.merge(name, 1, Integer::sum);
    hook.accept(name, n);
    int observedPosition;
    if (!name.equals("clock") && !name.equals("effectiveUid")) {
      synchronized (this) {
        observedPosition = ++position;
        events.add(name);
      }
    } else {
      observedPosition = position;
    }
    Throwable failure = faults.get(name + "#" + n);
    if (failure instanceof RuntimeException value) throw value;
    if (failure instanceof Error value) throw value;
    if (failure != null || (faultAt > 0 && faultAt == observedPosition))
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
  }

  @Override
  public Map<String, Object> attributes(Path held) throws IOException {
    point("attributes");
    if (nullMap) return null;
    var values = new HashMap<>(nativeIo.attributes(held));
    boolean directory = ((Integer) values.get("mode") & 0170000) == 040000;
    boolean dump =
        bundle && Files.readSymbolicLink(held).getFileName().toString().equals("schubert_nk.dump");
    values.put("uid", directory || dump ? (int) UID : 0);
    values.put("gid", directory || dump ? (int) GID : 0);
    String role = Files.isSameFile(held, parent) ? "parent" : directory ? "child" : "file";
    metadata.accept(role, values);
    return values;
  }

  @Override
  public String filesystem(Path held) {
    return copyFilesystem; // DBCP public fixture only; other publishers do not infer admission.
  }

  @Override
  public byte[] accessAcl(Path held, int maximum) throws StorageIoException {
    point("acl");
    assertEquals(44, maximum);
    return acl;
  }

  @Override
  public boolean readOnlyFilesystem(Path held) throws StorageIoException {
    point("readonly");
    return readonly;
  }

  @Override
  public long effectiveUid() {
    try {
      point("effectiveUid");
    } catch (IOException failure) {
      throw new AssertionError("UID IO not supported", failure);
    }
    return effective;
  }

  @Override
  public InspectorEnvironmentPublisher.Writer openWriter(Path held) throws IOException {
    point("openWriter");
    if (nullWriter) return null;
    var delegate = nativeIo.openWriter(held);
    synchronized (this) {
      channels++;
    }
    return new InspectorEnvironmentPublisher.Writer() {
      @Override
      public int write(ByteBuffer buffer) throws IOException {
        if (bundle) throw new AssertionError("bundle force must not write content");
        point("write");
        buffers.add(buffer.array());
        if (writeMode.equals("zero")) return 0;
        if (writeMode.equals("negative")) return -1;
        if (writeMode.equals("large")) return buffer.remaining() + 1;
        if (writeMode.equals("position")) return 1;
        int limit = buffer.limit();
        buffer.limit(buffer.position() + Math.min(buffer.remaining(), chunk));
        int n = delegate.write(buffer);
        buffer.limit(limit);
        return n;
      }

      @Override
      public long size() throws IOException {
        point("writerSize");
        long actual = delegate.size();
        return changedSize.equals("writerSize#" + counts.get("writerSize")) ? actual + 1 : actual;
      }

      @Override
      public void force() throws IOException {
        point("force");
        delegate.force();
      }

      @Override
      public void close() throws IOException {
        try {
          delegate.close();
        } finally {
          synchronized (BackupPublicationFixture.this) {
            channels--;
          }
        }
        point("closeWriter");
      }
    };
  }

  @Override
  public SeekableByteChannel open(Path held) throws IOException {
    point("openReader");
    if (nullReader) return null;
    var delegate = nativeIo.open(held);
    synchronized (this) {
      channels++;
    }
    return (SeekableByteChannel)
        Proxy.newProxyInstance(
            getClass().getClassLoader(),
            new Class<?>[] {SeekableByteChannel.class},
            (proxy, method, args) -> {
              String name = method.getName();
              if (!Set.of("read", "size", "close").contains(name))
                throw new AssertionError("unexpected channel operation");
              if (name.equals("close")) {
                try {
                  delegate.close();
                } finally {
                  synchronized (BackupPublicationFixture.this) {
                    channels--;
                  }
                }
                point("closeReader");
                return null;
              }
              point(name);
              if (name.equals("size")) {
                long actual = delegate.size();
                return changedSize.equals("size#" + counts.get("size")) ? actual + 1 : actual;
              }
              ByteBuffer buffer = (ByteBuffer) args[0];
              buffers.add(buffer.array());
              if (readMode.equals("zero")) return 0;
              if (readMode.equals("short")) return -1;
              if (readMode.equals("large")) return buffer.remaining() + 1;
              if (readMode.equals("position")) return 1;
              if (buffer.remaining() == 1 && readMode.equals("extra")) {
                buffer.put((byte) 1);
                return 1;
              }
              if (buffer.remaining() == 1 && readMode.equals("eof-position")) {
                buffer.put((byte) 1);
                return -1;
              }
              int limit = buffer.limit();
              buffer.limit(buffer.position() + Math.min(buffer.remaining(), chunk));
              int n = delegate.read(buffer);
              buffer.limit(limit);
              if (n == -1 && readMode.equals("extra-any")) {
                point("extraInjected");
                buffer.put((byte) 1);
                return 1;
              }
              if (n == -1 && readMode.equals("eof-position-any")) {
                point("eofPositionInjected");
                buffer.put((byte) 1);
              }
              if (readMode.equals("content") && n > 0) buffer.put(0, (byte) 0);
              if (readMode.equals("nonzero") && n > 0) buffer.put(0, (byte) 1);
              return n;
            });
  }

  void released() {
    assertEquals(Set.of(rootFd), descriptors);
    assertEquals(0, channels);
    assertEquals(0, streams);
    for (byte[] buffer : buffers) for (byte value : buffer) assertEquals(0, value);
  }

  @Override
  public void close() throws StorageIoException {
    track = false;
    root.close();
    assertTrue(descriptors.isEmpty());
    assertEquals(0, channels);
    assertEquals(0, streams);
  }

  @Override
  public DirectoryStream<Path> openNames(Path held) throws IOException {
    point("openNames");
    var delegate = Files.newDirectoryStream(held);
    synchronized (this) {
      streams++;
    }
    return new DirectoryStream<>() {
      @Override
      public Iterator<Path> iterator() {
        iteratePoint("iterator");
        var iterator = delegate.iterator();
        return new Iterator<>() {
          @Override
          public boolean hasNext() {
            iteratePoint("hasNext");
            return iterator.hasNext();
          }

          @Override
          public Path next() {
            iteratePoint("next");
            return iterator.next();
          }
        };
      }

      @Override
      public void close() throws IOException {
        try {
          delegate.close();
        } finally {
          synchronized (BackupPublicationFixture.this) {
            streams--;
          }
        }
        point("closeNames");
      }
    };
  }

  private void iteratePoint(String name) {
    try {
      point(name);
    } catch (IOException failure) {
      throw new DirectoryIteratorException(failure);
    }
  }
}
