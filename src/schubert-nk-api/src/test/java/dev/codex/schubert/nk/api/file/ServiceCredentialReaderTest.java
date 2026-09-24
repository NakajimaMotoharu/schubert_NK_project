package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-OPS-CREDREAD-001..012; real held files/channels with explicit synthetic privileged metadata.
 * Never claims that systemd distributed these temporary files.
 */
final class ServiceCredentialReaderTest {
  @TempDir Path temporary;
  private static final ServiceCredentialId KEY = ServiceCredentialId.API_CONTEXT_AES_CURRENT;
  private static final ServiceCredentialId PASSWORD = ServiceCredentialId.DB_API;

  @Test
  void opsCredread001AllFixedIdsReturnOwnedExactBytes() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      for (var id : ServiceCredentialId.values()) {
        byte[] expected = synthetic(id);
        Files.write(fixture.root.resolve(id.fileName()), expected);
        var io = new InspectorCredentialLoaderTest.TestIo();
        byte[] actual = reader(fixture, io, id.service()).read(id);
        try {
          assertArrayEquals(expected, actual);
          assertEquals(1, io.opens);
          assertEquals(1, io.closes);
          assertEquals(2, io.rootAttributes);
          assertEquals(2, io.fileAttributes);
        } finally {
          Arrays.fill(actual, (byte) 0);
          Arrays.fill(expected, (byte) 0);
          io.assertCleared(id.kind() == ServiceCredentialId.Kind.KEY ? 70 : 65537);
        }
      }
    }
  }

  @Test
  void opsCredread002RejectsCrossServiceAndNullBeforeIo() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      var io = new InspectorCredentialLoaderTest.TestIo();
      var api = reader(fixture, io, ServiceConfigFiles.Service.API);
      failure(() -> api.read(ServiceCredentialId.DB_WEB));
      assertEquals(0, io.opens);
      assertThrows(NullPointerException.class, () -> api.read(null));
      assertThrows(
          NullPointerException.class,
          () ->
              new ServiceCredentialReader(
                  fixture.held, new InspectorCredentialLoaderTest.TestSecurity(io), null, io));
      assertThrows(
          NullPointerException.class,
          () ->
              new ServiceCredentialReader(
                  null,
                  new InspectorCredentialLoaderTest.TestSecurity(io),
                  ServiceConfigFiles.Service.API,
                  io));
      assertThrows(
          NullPointerException.class,
          () ->
              new ServiceCredentialReader(fixture.held, null, ServiceConfigFiles.Service.API, io));
      assertThrows(
          NullPointerException.class,
          () ->
              new ServiceCredentialReader(
                  fixture.held,
                  new InspectorCredentialLoaderTest.TestSecurity(io),
                  ServiceConfigFiles.Service.API,
                  null));
    }
  }

  @Test
  void opsCredread003MissingSymlinkAndNonregularFailClosed() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      var io = new InspectorCredentialLoaderTest.TestIo();
      failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(PASSWORD));
      Path path = fixture.root.resolve(PASSWORD.fileName());
      Files.createSymbolicLink(path, fixture.root.resolve(KEY.fileName()));
      failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(PASSWORD));
      Files.delete(path);
      Files.createDirectory(path);
      failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(PASSWORD));
      assertEquals(0, io.opens);
    }
  }

  @Test
  void opsCredread004RootAndAclAdmissionBeforeContent() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      Files.write(fixture.root.resolve(KEY.fileName()), synthetic(KEY));
      for (String fault :
          List.of(
              "acl-root", "ro-root", "empty-acl-root", "acl-file", "ro-file", "empty-acl-file")) {
        var io = new InspectorCredentialLoaderTest.TestIo();
        io.securityFault = fault;
        failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(KEY));
        assertEquals(0, io.opens);
      }
      var actual =
          new ServiceCredentialReader(
              fixture.held, LinuxInodeSecurity.create(), ServiceConfigFiles.Service.API);
      failure(() -> actual.read(KEY));
    }
  }

  @Test
  void opsCredread005KeyPasswordSizeMetadataAndDeviceBoundaries() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      Path key = fixture.root.resolve(KEY.fileName());
      Path password = fixture.root.resolve(PASSWORD.fileName());
      for (int length : new int[] {0, 53, 70}) {
        Files.write(key, new byte[length]);
        var io = new InspectorCredentialLoaderTest.TestIo();
        failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(KEY));
        assertEquals(0, io.opens);
      }
      Files.write(key, synthetic(KEY));
      for (int length : new int[] {0, 65537}) {
        Files.write(password, new byte[length]);
        var io = new InspectorCredentialLoaderTest.TestIo();
        failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(PASSWORD));
        assertEquals(0, io.opens);
      }
      Files.write(password, new byte[] {'x'});
      var changed = new InspectorCredentialLoaderTest.TestIo();
      changed.fileChange = a -> a.put("dev", ((Long) a.get("dev")) + 1);
      failure(() -> reader(fixture, changed, ServiceConfigFiles.Service.API).read(KEY));
      assertEquals(0, changed.opens);
      var late = new InspectorCredentialLoaderTest.TestIo();
      late.lateFileChange = a -> a.put("ino", ((Long) a.get("ino")) + 1);
      failure(() -> reader(fixture, late, ServiceConfigFiles.Service.API).read(KEY));
      assertEquals(1, late.closes);
      late.assertCleared();
    }
  }

  @Test
  void opsCredread006ReadSizeCloseAndRootDriftFailuresEraseBuffer() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      Files.write(fixture.root.resolve(KEY.fileName()), synthetic(KEY));
      for (String fault :
          List.of(
              "open",
              "read",
              "short",
              "zero",
              "size-before",
              "size-after",
              "close",
              "root-final")) {
        var io = new InspectorCredentialLoaderTest.TestIo();
        io.fault = fault;
        failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(KEY));
        io.assertCleared();
      }
    }
  }

  @Test
  void opsCredread007EntryCloseAndBorrowedRootLifetime() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      Files.write(fixture.root.resolve(KEY.fileName()), synthetic(KEY));
      fixture.calls.closeUnavailable = true;
      var io = new InspectorCredentialLoaderTest.TestIo();
      failure(() -> reader(fixture, io, ServiceConfigFiles.Service.API).read(KEY));
      io.assertCleared();
      fixture.calls.closeUnavailable = false;
      boolean stillOpen = fixture.held.atDirectory(Files::isDirectory);
      assertTrue(stillOpen);
    }
  }

  @Test
  void opsCredread008ConcurrentIndependentOwnedReads() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary);
        var pool = Executors.newFixedThreadPool(8)) {
      byte[] expected = synthetic(KEY);
      Files.write(fixture.root.resolve(KEY.fileName()), expected);
      var tasks = new ArrayList<java.util.concurrent.Future<Boolean>>();
      for (int i = 0; i < 32; i++) {
        tasks.add(
            pool.submit(
                () -> {
                  var io = new InspectorCredentialLoaderTest.TestIo();
                  byte[] actual = reader(fixture, io, ServiceConfigFiles.Service.API).read(KEY);
                  try {
                    assertArrayEquals(expected, actual);
                    io.assertCleared();
                    return true;
                  } finally {
                    Arrays.fill(actual, (byte) 0);
                  }
                }));
      }
      for (var task : tasks) assertTrue(task.get().booleanValue());
      Arrays.fill(expected, (byte) 0);
    }
  }

  @Test
  void opsCredread009DbAndMqPasswordDecodeWithOwnedCopies() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      for (var id : List.of(ServiceCredentialId.DB_API, ServiceCredentialId.MQ_API)) {
        Files.write(fixture.root.resolve(id.fileName()), synthetic(id));
        var io = new InspectorCredentialLoaderTest.TestIo();
        try (var material = reader(fixture, io, id.service()).readPassword(id)) {
          char[] copy = material.copyPassword();
          try {
            assertArrayEquals(("public-pt-only-" + id.fileName()).toCharArray(), copy);
            assertFalse(material.toString().contains("public-pt-only"));
          } finally {
            Arrays.fill(copy, '\0');
          }
        }
        var closedMaterial =
            reader(fixture, new InspectorCredentialLoaderTest.TestIo(), id.service())
                .readPassword(id);
        closedMaterial.close();
        assertThrows(IllegalStateException.class, closedMaterial::copyPassword);
        io.assertCleared(65537);
      }
    }
    byte[] owned = "literal-test-only\n".getBytes(StandardCharsets.UTF_8);
    try (var decoded = ServiceCredentialReader.consumePassword(owned)) {
      assertArrayEquals("literal-test-only".toCharArray(), decoded.copyPassword());
    }
    assertArrayEquals(new byte[owned.length], owned);
  }

  @Test
  void opsCredread010SixKeysDecodeCanonicalCurrentMaterial() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      for (var id : ServiceCredentialId.values()) {
        if (id.kind() != ServiceCredentialId.Kind.KEY) continue;
        Files.write(fixture.root.resolve(id.fileName()), synthetic(id));
        var io = new InspectorCredentialLoaderTest.TestIo();
        try (var material = reader(fixture, io, id.service()).readKey(id)) {
          assertEquals("v", material.version());
          byte[] copy = material.copyKey();
          try {
            assertArrayEquals(new byte[32], copy);
          } finally {
            Arrays.fill(copy, (byte) 0);
          }
          assertFalse(material.toString().contains("NKKEY1"));
        }
        io.assertCleared(70);
      }
    }
    byte[] owned = synthetic(KEY);
    try (var decoded = ServiceCredentialReader.consumeKey(owned)) {
      assertEquals("v", decoded.version());
    }
    assertArrayEquals(new byte[owned.length], owned);
  }

  @Test
  void opsCredread011KindServiceAndNullRejectBeforeIo() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      var io = new InspectorCredentialLoaderTest.TestIo();
      var api = reader(fixture, io, ServiceConfigFiles.Service.API);
      failure(() -> api.readPassword(KEY));
      failure(() -> api.readKey(PASSWORD));
      failure(() -> api.readPassword(ServiceCredentialId.DB_WEB));
      failure(() -> api.readKey(ServiceCredentialId.WEB_LOG_AES_CURRENT));
      assertThrows(NullPointerException.class, () -> api.readPassword(null));
      assertThrows(NullPointerException.class, () -> api.readKey(null));
      assertThrows(NullPointerException.class, () -> ServiceCredentialReader.consumePassword(null));
      assertThrows(NullPointerException.class, () -> ServiceCredentialReader.consumeKey(null));
      assertEquals(0, io.opens);
    }
  }

  @Test
  void opsCredread012MalformedContentErasesOwnedBytesAndRedacts() throws Exception {
    byte[] password = new byte[] {'x', 0, 'y'};
    failure(() -> ServiceCredentialReader.consumePassword(password));
    assertArrayEquals(new byte[password.length], password);
    byte[] key = synthetic(KEY);
    key[key.length - 1] = '\r';
    failure(() -> ServiceCredentialReader.consumeKey(key));
    assertArrayEquals(new byte[key.length], key);
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      Files.write(fixture.root.resolve(PASSWORD.fileName()), new byte[] {'x', 0});
      Files.write(fixture.root.resolve(KEY.fileName()), new byte[54]);
      var passwordIo = new InspectorCredentialLoaderTest.TestIo();
      failure(
          () -> reader(fixture, passwordIo, ServiceConfigFiles.Service.API).readPassword(PASSWORD));
      passwordIo.assertCleared(65537);
      var keyIo = new InspectorCredentialLoaderTest.TestIo();
      failure(() -> reader(fixture, keyIo, ServiceConfigFiles.Service.API).readKey(KEY));
      keyIo.assertCleared(70);
    }
  }

  private static ServiceCredentialReader reader(
      InspectorCredentialLoaderTest.Fixture fixture,
      InspectorCredentialLoaderTest.TestIo io,
      ServiceConfigFiles.Service service) {
    return new ServiceCredentialReader(
        fixture.held, new InspectorCredentialLoaderTest.TestSecurity(io), service, io);
  }

  private static byte[] synthetic(ServiceCredentialId id) {
    if (id.kind() == ServiceCredentialId.Kind.PASSWORD)
      return ("public-pt-only-" + id.fileName() + "\n").getBytes(StandardCharsets.UTF_8);
    byte[] key = new byte[32];
    byte[] encoded = Base64.getEncoder().encode(key);
    byte[] prefix = "NKKEY1\nv\n".getBytes(StandardCharsets.US_ASCII);
    byte[] result = Arrays.copyOf(prefix, prefix.length + encoded.length + 1);
    System.arraycopy(encoded, 0, result, prefix.length, encoded.length);
    result[result.length - 1] = '\n';
    Arrays.fill(key, (byte) 0);
    Arrays.fill(encoded, (byte) 0);
    return result;
  }

  private static void failure(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(ServiceCredentialException.class, action);
    assertEquals("service credential cannot be loaded", error.getMessage());
    assertEquals(0, error.getSuppressed().length);
    assertFalse(error.toString().contains("/run/credentials"));
  }
}
