package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.file.ScenarioFileInspector.Availability;
import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-SCN-009-V01..V03. Physical-only verification; synthetic bytes are not a record codec oracle.
 */
final class ScenarioReadyFileInspectorTest {
  private static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000123");

  @TempDir(factory = TransferRootInspectionTest.Ext4Fixture.class)
  Path fixture;

  @Test
  void realReadyFilesMissingNamesAndConcurrentReadsStayReadOnly() throws Exception {
    for (int count : List.of(1, 10_000)) {
      Path root = root();
      var identity = identity(root);
      var calls = new Calls();
      try (var held = OwnedTransferDirectory.open(calls.port(), root)) {
        var inspector = new ScenarioReadyFileInspector(held, identity);
        var absent =
            new LargeResultDescriptor(
                ID, "20260908/" + ID + ".ready", 4800L * count, "a".repeat(64), count);
        assertEquals(Availability.MISSING, inspector.inspect(absent));
        try (var entries = Files.list(root)) {
          assertEquals(0, entries.count());
        }
        Path date = Files.createDirectory(root.resolve("20260908"));
        mode(date, "rwxr-x---");
        assertEquals(Availability.MISSING, inspector.inspect(absent));
        try (var entries = Files.list(date)) {
          assertEquals(0, entries.count());
        }
        var expected = create(root, count);
        Path ready = root.resolve(expected.relativePath());
        var before =
            Files.readAttributes(ready, "unix:owner,group,mode,nlink,size,lastModifiedTime");
        assertEquals(Availability.PRESENT, inspector.inspect(expected));
        if (count == 1) {
          try (var workers = Executors.newFixedThreadPool(16)) {
            List<Future<Availability>> results = new ArrayList<>();
            for (int i = 0; i < 100; i++)
              results.add(workers.submit(() -> inspector.inspect(expected)));
            for (var result : results)
              assertEquals(Availability.PRESENT, result.get(20, TimeUnit.SECONDS));
          }
        }
        assertEquals(
            before,
            Files.readAttributes(ready, "unix:owner,group,mode,nlink,size,lastModifiedTime"));
        assertEquals(expected.sha256(), digestFile(ready));
        try (var entries = Files.list(date)) {
          assertEquals(1, entries.count());
        }
      }
      assertTrue(calls.live.isEmpty());
    }
  }

  @Test
  void presentButInvalidFilesAreNeverDeclaredMissing() throws Exception {
    for (String fault :
        List.of(
            "rootMode", "dayMode", "fileMode", "size", "hash", "symlink", "hardlink", "identity")) {
      Path root = root();
      var expected = create(root, 1);
      Path file = root.resolve(expected.relativePath());
      var identity = identity(root);
      switch (fault) {
        case "rootMode" -> mode(root, "rwx------");
        case "dayMode" -> mode(file.getParent(), "rwx------");
        case "fileMode" -> mode(file, "rw-------");
        case "size" -> Files.write(file, new byte[] {1}, StandardOpenOption.APPEND);
        case "hash" -> Files.write(file, new byte[4800], StandardOpenOption.TRUNCATE_EXISTING);
        case "symlink" -> {
          Path other = fixture.resolve(UUID.randomUUID().toString());
          Files.move(file, other);
          Files.createSymbolicLink(file, other);
        }
        case "hardlink" -> Files.createLink(fixture.resolve(UUID.randomUUID().toString()), file);
        case "identity" -> identity = new StorageIdentity("not-the-owner", identity.group());
        default -> throw new AssertionError(fault);
      }
      var calls = new Calls();
      try (var held = OwnedTransferDirectory.open(calls.port(), root)) {
        var inspector = new ScenarioReadyFileInspector(held, identity);
        reject(() -> inspector.inspect(expected));
        assertTrue(Files.exists(file, LinkOption.NOFOLLOW_LINKS));
      }
      assertTrue(calls.live.isEmpty());
    }
  }

  @Test
  void nullNativeCallbackAndCloseFailuresNeverBecomeAbsence() throws Exception {
    Path root = root();
    var descriptor = create(root, 1);
    var identity = identity(root);
    var calls = new Calls();
    try (var held = OwnedTransferDirectory.open(calls.port(), root)) {
      TransferFileIo real = new HeldTransferFileIo(identity);
      assertThrows(
          NullPointerException.class, () -> new ScenarioReadyFileInspector(null, identity));
      assertThrows(NullPointerException.class, () -> new ScenarioReadyFileInspector(held, null));
      assertThrows(
          NullPointerException.class, () -> new ScenarioReadyFileInspector(null, identity, real));
      assertThrows(
          NullPointerException.class, () -> new ScenarioReadyFileInspector(held, null, real));
      assertThrows(
          NullPointerException.class, () -> new ScenarioReadyFileInspector(held, identity, null));
      assertThrows(
          NullPointerException.class,
          () -> new ScenarioReadyFileInspector(held, identity).inspect(null));
      for (String fault : List.of("openDay", "openEntry", "entryClose", "dayClose")) {
        calls.fault = fault;
        reject(() -> new ScenarioReadyFileInspector(held, identity).inspect(descriptor));
        calls.fault = "";
        assertEquals(1, calls.live.size(), "only caller's root FD remains");
      }
      var missing =
          new LargeResultDescriptor(
              new UUID(0, 99),
              "20260908/" + new UUID(0, 99) + ".ready",
              4800,
              descriptor.sha256(),
              1);
      calls.fault = "dayClose";
      reject(() -> new ScenarioReadyFileInspector(held, identity).inspect(missing));
      calls.fault = "";
      for (String fault : List.of("missing", "io", "crypto", "runtime", "postAttributes")) {
        TransferFileIo failed =
            new TransferFileIo() {
              @Override
              public void initializeDirectory(Path handle) {
                fail("read-only inspection initialized directory");
              }

              @Override
              public LargeResultContent writePart(Path handle, ScenarioRecordStream records) {
                return fail("read-only inspection wrote file");
              }

              @Override
              public void verify(Path handle, LargeResultContent expected)
                  throws IOException, NoSuchAlgorithmException {
                switch (fault) {
                  case "missing" ->
                      throw new NoSuchFileException("synthetic confidential capability");
                  case "io" -> throw new IOException("synthetic confidential I/O");
                  case "crypto" ->
                      throw new NoSuchAlgorithmException("synthetic confidential crypto");
                  case "runtime" ->
                      throw new IllegalStateException("synthetic confidential runtime");
                  case "postAttributes" -> mode(handle, "rw-------");
                  default -> throw new AssertionError(fault);
                }
              }
            };
        reject(() -> new ScenarioReadyFileInspector(held, identity, failed).inspect(descriptor));
        assertEquals(1, calls.live.size());
      }
    }
    assertTrue(calls.live.isEmpty());
    var closed = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
    var inspector = new ScenarioReadyFileInspector(closed, identity);
    closed.close();
    reject(() -> inspector.inspect(descriptor));
  }

  private Path root() throws IOException {
    Path root = Files.createTempDirectory(fixture, "ready-");
    mode(root, "rwxr-x---");
    return root;
  }

  private static void mode(Path path, String value) throws IOException {
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString(value));
  }

  private static StorageIdentity identity(Path root) throws IOException {
    var attributes = Files.readAttributes(root, PosixFileAttributes.class);
    return new StorageIdentity(attributes.owner().getName(), attributes.group().getName());
  }

  private static LargeResultDescriptor create(Path root, int count) throws Exception {
    Path date = root.resolve("20260908");
    if (!Files.exists(date)) {
      Files.createDirectory(date);
      mode(date, "rwxr-x---");
    }
    Path ready = date.resolve(ID + ".ready");
    byte[] record = new byte[4800];
    Arrays.fill(record, (byte) 0x53);
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var output = Files.newOutputStream(ready, StandardOpenOption.CREATE_NEW)) {
      for (int i = 0; i < count; i++) {
        output.write(record);
        digest.update(record);
      }
    }
    mode(ready, "rw-r-----");
    return new LargeResultDescriptor(
        ID,
        "20260908/" + ID + ".ready",
        4800L * count,
        HexFormat.of().formatHex(digest.digest()),
        count);
  }

  private static String digestFile(Path file) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var input = Files.newInputStream(file)) {
      byte[] buffer = new byte[8192];
      for (int read; (read = input.read(buffer)) != -1; ) digest.update(buffer, 0, read);
    }
    return HexFormat.of().formatHex(digest.digest());
  }

  private static void reject(Executable action) {
    var failure = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Calls {
    private final DirectoryCalls real = LinuxDirectoryCalls.create();
    private final Set<Integer> live = ConcurrentHashMap.newKeySet();
    private String fault = "";
    private int date = -1;
    private int entry = -1;

    DirectoryCalls port() {
      return (DirectoryCalls)
          Proxy.newProxyInstance(
              DirectoryCalls.class.getClassLoader(),
              new Class<?>[] {DirectoryCalls.class},
              (proxy, method, args) -> {
                String name = method.getName();
                boolean dayOpen = name.equals("openDirectory") && args[1].equals("20260908");
                if (fault.equals("openDay") && dayOpen
                    || fault.equals("openEntry") && name.equals("openEntry"))
                  throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                // Remove before kernel close makes the number reusable by another opening thread.
                // DirectoryCalls consumes ownership even on close failure; do not erase a reused
                // FD.
                if (name.equals("close")) assertTrue(live.remove((int) args[0]));
                Object result;
                try {
                  result = method.invoke(real, args);
                } catch (InvocationTargetException failure) {
                  throw failure.getCause();
                }
                if (name.startsWith("open")) {
                  int descriptor = (int) result;
                  live.add(descriptor);
                  if (dayOpen) date = descriptor;
                  if (name.equals("openEntry")) entry = descriptor;
                }
                if (name.equals("close")) {
                  int descriptor = (int) args[0];
                  if (fault.equals("entryClose") && descriptor == entry
                      || fault.equals("dayClose") && descriptor == date)
                    throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
                }
                if (List.of("createFile", "createDirectory", "publish", "unlink", "sync")
                    .contains(name)) fail("inspector wrote to storage");
                return result;
              });
    }
  }
}
