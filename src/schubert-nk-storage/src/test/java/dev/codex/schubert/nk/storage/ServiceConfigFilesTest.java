package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.FileTime;
import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.PosixFilePermissions;
import java.nio.file.attribute.UserPrincipal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-CFGFILE-001..007, SS343 fixed file names and held-inode byte contract. */
final class ServiceConfigFilesTest {
  private static final String API_POOL_FIXTURE_DOCUMENT = "nk.db.pool.api.max: '8'\n";
  private static final String FIXTURE_API_YML_77F26866 = "api.yml";
  private static final String FIXTURE_WRONG_D78ED9EF = "wrong";
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  @TempDir Path temporary;

  private Path root() throws Exception {
    Path root = Files.createDirectory(temporary.resolve("config"));
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwxr-x---"));
    write(root, "common.yml", "nk.protocol.version: '001'\n");
    write(root, FIXTURE_API_YML_77F26866, API_POOL_FIXTURE_DOCUMENT);
    write(root, "web.yml", "nk.web.http.port: '8080'\n");
    return root;
  }

  private static Path write(Path root, String name, String value) throws Exception {
    Path file = root.resolve(name);
    Files.writeString(file, value);
    Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-r-----"));
    return file;
  }

  private static StorageIdentity identity(Path path) throws Exception {
    Map<String, Object> attributes = Files.readAttributes(path, "unix:owner,group");
    return new StorageIdentity(
        ((UserPrincipal) attributes.get("owner")).getName(),
        ((GroupPrincipal) attributes.get("group")).getName());
  }

  private static ServiceConfigFiles.Contents read(Path root, ServiceConfigFiles.Service service)
      throws Exception {
    return ServiceConfigFiles.read(root, identity(root), LinuxDirectoryCalls.create(), service);
  }

  private static void unavailable(Throwing action) {
    var failure = assertThrows(StorageIoException.class, action::run);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals(0, failure.getSuppressed().length);
  }

  @FunctionalInterface
  interface Throwing {
    void run() throws Exception;
  }

  @Test
  void opsCfgfile001FixedNamesAndIndependentBytes() throws Exception {
    Path root = root();
    var api = read(root, ServiceConfigFiles.Service.API);
    var web = read(root, ServiceConfigFiles.Service.WEB);
    assertEquals("nk.protocol.version: '001'\n", api.commonYaml());
    assertEquals(API_POOL_FIXTURE_DOCUMENT, api.serviceYaml());
    assertEquals("nk.protocol.version: '001'\n", web.commonYaml());
    assertEquals("nk.web.http.port: '8080'\n", web.serviceYaml());
  }

  @Test
  void opsCfgfile002MissingSymlinkAndNonRegularAreRejected() throws Exception {
    Path root = root();
    Files.delete(root.resolve(FIXTURE_API_YML_77F26866));
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
    Files.createSymbolicLink(root.resolve(FIXTURE_API_YML_77F26866), root.resolve("web.yml"));
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
    Files.delete(root.resolve(FIXTURE_API_YML_77F26866));
    Files.createDirectory(root.resolve(FIXTURE_API_YML_77F26866));
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
  }

  @Test
  void opsCfgfile003LengthEncodingAndModeBoundaries() throws Exception {
    Path root = root();
    Path api = root.resolve(FIXTURE_API_YML_77F26866);
    Files.writeString(api, "");
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
    Files.writeString(api, "a".repeat(16_385));
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
    Files.write(api, new byte[] {(byte) 0xc3, (byte) 0x28});
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
    Files.writeString(api, "a".repeat(16_384));
    assertEquals("a".repeat(16_384), read(root, ServiceConfigFiles.Service.API).serviceYaml());
    Files.setPosixFilePermissions(api, PosixFilePermissions.fromString("rw-------"));
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
  }

  @Test
  void opsCfgfile004RootAndFileIdentityPolicy() throws Exception {
    Path root = root();
    Path api = root.resolve(FIXTURE_API_YML_77F26866);
    Files.createLink(root.resolve("alias.yml"), api);
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
    Files.delete(root.resolve("alias.yml"));
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwx------"));
    unavailable(() -> read(root, ServiceConfigFiles.Service.API));
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwxr-x---"));
    unavailable(
        () ->
            ServiceConfigFiles.read(
                root,
                new StorageIdentity(FIXTURE_WRONG_D78ED9EF, FIXTURE_WRONG_D78ED9EF),
                LinuxDirectoryCalls.create(),
                ServiceConfigFiles.Service.API));
    assertEquals(
        API_POOL_FIXTURE_DOCUMENT, read(root, ServiceConfigFiles.Service.API).serviceYaml());
  }

  @Test
  void opsCfgfile005IndependentAttributeMutationMatrix() throws Exception {
    Path root = root();
    Map<String, Object> genuine =
        Files.readAttributes(
            root.resolve(FIXTURE_API_YML_77F26866),
            "unix:owner,group,mode,nlink,dev,ino,size,ctime");
    StorageIdentity identity = identity(root);
    long device = (Long) genuine.get("dev");
    for (String key :
        List.of("owner", "group", "mode", "nlink", "dev", "ino", FIXTURE_SIZE_EB1E91E4, "ctime")) {
      var missing = new HashMap<>(genuine);
      missing.remove(key);
      unavailable(() -> ServiceConfigFiles.checked(missing, identity, false, device));
    }
    for (Map.Entry<String, Object> mutation :
        Map.<String, Object>of(
                "mode",
                0x8180 /* POSIX 0100600 */,
                "nlink",
                0,
                "dev",
                -1L,
                "ino",
                0L,
                FIXTURE_SIZE_EB1E91E4,
                -1L)
            .entrySet()) {
      var changed = new HashMap<>(genuine);
      changed.put(mutation.getKey(), mutation.getValue());
      unavailable(() -> ServiceConfigFiles.checked(changed, identity, false, device));
    }
    var extraLink = new HashMap<>(genuine);
    extraLink.put("nlink", 2);
    unavailable(() -> ServiceConfigFiles.checked(extraLink, identity, false, device));
    var zero = new HashMap<>(genuine);
    zero.put(FIXTURE_SIZE_EB1E91E4, 0L);
    unavailable(() -> ServiceConfigFiles.checked(zero, identity, false, device));
    var longFile = new HashMap<>(genuine);
    longFile.put(FIXTURE_SIZE_EB1E91E4, 16_385L);
    unavailable(() -> ServiceConfigFiles.checked(longFile, identity, false, device));
    unavailable(() -> ServiceConfigFiles.checked(genuine, identity, false, device + 1));
    unavailable(
        () ->
            ServiceConfigFiles.checked(
                genuine,
                new StorageIdentity(FIXTURE_WRONG_D78ED9EF, FIXTURE_WRONG_D78ED9EF),
                false,
                device));
    var wrongGroup = new HashMap<>(genuine);
    wrongGroup.put("group", (GroupPrincipal) () -> FIXTURE_WRONG_D78ED9EF);
    unavailable(() -> ServiceConfigFiles.checked(wrongGroup, identity, false, device));
    assertEquals(device, ServiceConfigFiles.checked(genuine, identity, false, device).device());
  }

  @Test
  void opsCfgfile006NullConcurrentAndOwnedCloseFailure() throws Exception {
    Path root = root();
    StorageIdentity identity = identity(root);
    assertThrows(
        NullPointerException.class,
        () ->
            ServiceConfigFiles.read(
                null, identity, LinuxDirectoryCalls.create(), ServiceConfigFiles.Service.API));
    assertThrows(
        NullPointerException.class,
        () ->
            ServiceConfigFiles.read(
                root, null, LinuxDirectoryCalls.create(), ServiceConfigFiles.Service.API));
    assertThrows(
        NullPointerException.class,
        () -> ServiceConfigFiles.read(root, identity, null, ServiceConfigFiles.Service.API));
    assertThrows(
        NullPointerException.class,
        () -> ServiceConfigFiles.read(root, identity, LinuxDirectoryCalls.create(), null));
    assertThrows(NullPointerException.class, () -> ServiceConfigFiles.production().read(null));
    assertThrows(NullPointerException.class, () -> new ServiceConfigFiles.Contents(null, "web"));
    assertThrows(NullPointerException.class, () -> new ServiceConfigFiles.Contents("common", null));
    assertThrows(
        NullPointerException.class,
        () ->
            ServiceConfigFiles.read(
                root,
                identity,
                LinuxDirectoryCalls.create(),
                null,
                ServiceConfigFiles.Service.API));
    try (var executor = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<java.util.concurrent.Future<ServiceConfigFiles.Contents>>();
      for (int i = 0; i < 32; i++)
        jobs.add(executor.submit(() -> read(root, ServiceConfigFiles.Service.WEB)));
      for (var job : jobs)
        assertEquals("nk.web.http.port: '8080'\n", job.get(10, TimeUnit.SECONDS).serviceYaml());
    }
    var calls = new CloseFaultCalls(LinuxDirectoryCalls.create(), root.getNameCount() + 3);
    unavailable(
        () -> ServiceConfigFiles.read(root, identity, calls, ServiceConfigFiles.Service.API));
    assertTrue(calls.closed >= root.getNameCount() + 3);
  }

  @Test
  void opsCfgfile007MidReadFaultsAndInodeDrift() throws Exception {
    Path root = root();
    StorageIdentity identity = identity(root);
    assertEquals(
        API_POOL_FIXTURE_DOCUMENT,
        ServiceConfigFiles.read(
                root,
                identity,
                LinuxDirectoryCalls.create(),
                new FaultIo(FaultKind.NONE),
                ServiceConfigFiles.Service.API)
            .serviceYaml());
    for (FaultKind kind : FaultKind.values()) {
      if (kind == FaultKind.NONE) continue;
      unavailable(
          () ->
              ServiceConfigFiles.read(
                  root,
                  identity,
                  LinuxDirectoryCalls.create(),
                  new FaultIo(kind),
                  ServiceConfigFiles.Service.API));
    }
  }

  private enum FaultKind {
    NONE,
    ROOT_DRIFT,
    FILE_DRIFT,
    FIRST_SIZE,
    FINAL_SIZE,
    ZERO_READ,
    SHORT_READ,
    OVERFLOW
  }

  private static final class FaultIo implements ServiceConfigFiles.Io {
    private final FaultKind kind;
    private int attributeCalls;
    private int channelCalls;

    FaultIo(FaultKind kind) {
      this.kind = kind;
    }

    @Override
    public Map<String, Object> attributes(Path path) throws IOException {
      Map<String, Object> real =
          Files.readAttributes(path, "unix:owner,group,mode,nlink,dev,ino,size,ctime");
      int call = attributeCalls + 1;
      attributeCalls = call;
      if ((kind == FaultKind.ROOT_DRIFT && call == 6)
          || (kind == FaultKind.FILE_DRIFT && call == 5)) {
        var changed = new HashMap<>(real);
        changed.put("ctime", FileTime.fromMillis(((FileTime) real.get("ctime")).toMillis() + 1000));
        return changed;
      }
      return real;
    }

    @Override
    public SeekableByteChannel openReadOnly(Path path) throws IOException {
      SeekableByteChannel real = Files.newByteChannel(path, Set.of(StandardOpenOption.READ));
      int call = channelCalls + 1;
      channelCalls = call;
      if (call != 2 || kind == FaultKind.ROOT_DRIFT || kind == FaultKind.FILE_DRIFT) return real;
      return new FaultChannel(real, kind);
    }
  }

  private static final class FaultChannel implements SeekableByteChannel {
    private final SeekableByteChannel real;
    private final FaultKind kind;
    private int sizeCalls;
    private int readCalls;

    FaultChannel(SeekableByteChannel real, FaultKind kind) {
      this.real = real;
      this.kind = kind;
    }

    @Override
    public int read(ByteBuffer destination) throws IOException {
      int call = readCalls + 1;
      readCalls = call;
      if (kind == FaultKind.ZERO_READ && call == 1) return 0;
      if (kind == FaultKind.SHORT_READ && call == 2) return -1;
      if (kind == FaultKind.SHORT_READ && call == 1) {
        int limit = destination.limit();
        destination.limit(destination.position() + 3);
        try {
          return real.read(destination);
        } finally {
          destination.limit(limit);
        }
      }
      if (kind == FaultKind.OVERFLOW && call == 1) {
        for (int i = 0; i < 16_385; i++) destination.put((byte) 'a');
        return 16_385;
      }
      return real.read(destination);
    }

    @Override
    public long size() throws IOException {
      int call = sizeCalls + 1;
      sizeCalls = call;
      if ((kind == FaultKind.FIRST_SIZE && call == 1)
          || (kind == FaultKind.FINAL_SIZE && call == 2)) return real.size() + 1;
      return real.size();
    }

    @Override
    public int write(ByteBuffer source) {
      throw new AssertionError();
    }

    @Override
    public long position() throws IOException {
      return real.position();
    }

    @Override
    public SeekableByteChannel position(long value) throws IOException {
      real.position(value);
      return this;
    }

    @Override
    public SeekableByteChannel truncate(long size) {
      throw new AssertionError();
    }

    @Override
    public boolean isOpen() {
      return real.isOpen();
    }

    @Override
    public void close() throws IOException {
      real.close();
    }
  }

  private static final class CloseFaultCalls implements DirectoryCalls {
    private final DirectoryCalls real;
    private final int failAt;
    int closed;

    CloseFaultCalls(DirectoryCalls real, int failAt) {
      this.real = real;
      this.failAt = failAt;
    }

    @Override
    public int openRoot() throws StorageIoException {
      return real.openRoot();
    }

    @Override
    public int openDirectory(int parent, String name) throws StorageIoException {
      return real.openDirectory(parent, name);
    }

    @Override
    public int openEntry(int parent, String name) throws StorageIoException {
      return real.openEntry(parent, name);
    }

    @Override
    public int createFile(int parent, String name) {
      throw new AssertionError();
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw new AssertionError();
    }

    @Override
    public void publish(int directory, String part, String ready) {
      throw new AssertionError();
    }

    @Override
    public void unlink(int directory, String name) {
      throw new AssertionError();
    }

    @Override
    public void sync(int directory) {
      throw new AssertionError();
    }

    @Override
    public void close(int directory) throws StorageIoException {
      real.close(directory);
      int call = closed + 1;
      closed = call;
      if (call == failAt) throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
