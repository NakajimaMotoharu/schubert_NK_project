package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Base64;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-CREDSET-001..005; synthetic non-secret materials and held temp inode only. */
final class ServiceCredentialSetTest {
  @TempDir Path temporary;

  @Test
  void opsCredset001FiveFixedMaterialsPerServiceAreOwnedAndClosed() throws Exception {
    assertArrayEquals(
        new ServiceCredentialId.Kind[] {
          ServiceCredentialId.Kind.PASSWORD, ServiceCredentialId.Kind.KEY
        },
        ServiceCredentialId.Kind.values());
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      install(fixture, ServiceConfigFiles.Service.API);
      install(fixture, ServiceConfigFiles.Service.WEB);
      for (var service : ServiceConfigFiles.Service.values()) {
        var io = new InspectorCredentialLoaderTest.TestIo();
        var set = ServiceCredentialSet.load(reader(fixture, io, service), service);
        assertEquals("ServiceCredentialSet[REDACTED]", set.toString());
        for (var id : ServiceCredentialId.forService(service)) {
          if (id.kind() == ServiceCredentialId.Kind.PASSWORD) {
            char[] copy = set.copyPassword(id);
            try {
              assertArrayEquals(("pt-public-" + id.fileName()).toCharArray(), copy);
            } finally {
              Arrays.fill(copy, '\0');
            }
          } else {
            assertEquals("v", set.version(id));
            byte[] copy = set.copyKey(id);
            try {
              assertArrayEquals(new byte[32], copy);
            } finally {
              Arrays.fill(copy, (byte) 0);
            }
          }
        }
        assertEquals(5, io.opens);
        assertEquals(5, io.closes);
        assertCleared(io);
        set.close();
        set.close();
        assertThrows(
            IllegalStateException.class,
            () -> set.copyPassword(ServiceCredentialId.forService(service).getFirst()));
      }
    }
  }

  @Test
  void opsCredset002WrongIdNullAndClosedStateReject() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      install(fixture, ServiceConfigFiles.Service.API);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var reader = reader(fixture, io, ServiceConfigFiles.Service.API);
      assertThrows(
          NullPointerException.class,
          () -> ServiceCredentialSet.load(null, ServiceConfigFiles.Service.API));
      assertThrows(NullPointerException.class, () -> ServiceCredentialSet.load(reader, null));
      try (var set = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.API)) {
        assertThrows(NullPointerException.class, () -> set.copyPassword(null));
        assertThrows(NullPointerException.class, () -> set.copyKey(null));
        assertThrows(NullPointerException.class, () -> set.version(null));
        assertThrows(
            IllegalArgumentException.class, () -> set.copyPassword(ServiceCredentialId.DB_WEB));
        assertThrows(
            IllegalArgumentException.class,
            () -> set.copyPassword(ServiceCredentialId.API_CONTEXT_AES_CURRENT));
        assertThrows(IllegalArgumentException.class, () -> set.copyKey(ServiceCredentialId.DB_API));
        assertThrows(
            IllegalArgumentException.class,
            () -> set.copyKey(ServiceCredentialId.WEB_LOG_AES_CURRENT));
        assertThrows(IllegalArgumentException.class, () -> set.version(ServiceCredentialId.DB_API));
      }
      assertCleared(io);
    }
  }

  @Test
  void opsCredset003MissingMalformedAndUncheckedFailureClearPartial() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      install(fixture, ServiceConfigFiles.Service.API);
      Path last = fixture.root.resolve(ServiceCredentialId.OPERATION_HMAC_CURRENT.fileName());
      Files.delete(last);
      var missingIo = new InspectorCredentialLoaderTest.TestIo();
      assertThrows(
          ServiceCredentialException.class,
          () ->
              ServiceCredentialSet.load(
                  reader(fixture, missingIo, ServiceConfigFiles.Service.API),
                  ServiceConfigFiles.Service.API));
      assertCleared(missingIo);
      Files.write(last, new byte[54]);
      var malformedIo = new InspectorCredentialLoaderTest.TestIo();
      assertThrows(
          ServiceCredentialException.class,
          () ->
              ServiceCredentialSet.load(
                  reader(fixture, malformedIo, ServiceConfigFiles.Service.API),
                  ServiceConfigFiles.Service.API));
      assertCleared(malformedIo);
      Files.write(last, synthetic(ServiceCredentialId.OPERATION_HMAC_CURRENT));
      for (boolean fatal : new boolean[] {false, true}) {
        var io = new InspectorCredentialLoaderTest.TestIo();
        var count = new AtomicInteger();
        RuntimeException runtime = new IllegalStateException("test-only-private-marker");
        AssertionError error = new AssertionError("test-only-fatal-marker");
        io.fileChange =
            attributes -> {
              if (count.incrementAndGet() == 9) {
                if (fatal) throw error;
                throw runtime;
              }
            };
        if (fatal)
          assertSame(
              error,
              assertThrows(
                  AssertionError.class,
                  () ->
                      ServiceCredentialSet.load(
                          reader(fixture, io, ServiceConfigFiles.Service.API),
                          ServiceConfigFiles.Service.API)));
        else
          assertSame(
              runtime,
              assertThrows(
                  IllegalStateException.class,
                  () ->
                      ServiceCredentialSet.load(
                          reader(fixture, io, ServiceConfigFiles.Service.API),
                          ServiceConfigFiles.Service.API)));
        assertCleared(io);
      }
    }
  }

  @Test
  void opsCredset004ConcurrentIndependentLoads() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary);
        var pool = Executors.newFixedThreadPool(8)) {
      install(fixture, ServiceConfigFiles.Service.API);
      var tasks = new java.util.ArrayList<java.util.concurrent.Future<Boolean>>();
      for (int i = 0; i < 32; i++) {
        tasks.add(
            pool.submit(
                () -> {
                  var io = new InspectorCredentialLoaderTest.TestIo();
                  try (var set =
                      ServiceCredentialSet.load(
                          reader(fixture, io, ServiceConfigFiles.Service.API),
                          ServiceConfigFiles.Service.API)) {
                    byte[] copy = set.copyKey(ServiceCredentialId.OPERATION_HMAC_CURRENT);
                    try {
                      assertArrayEquals(new byte[32], copy);
                    } finally {
                      Arrays.fill(copy, (byte) 0);
                    }
                  }
                  assertCleared(io);
                  return true;
                }));
      }
      for (var task : tasks) assertTrue(task.get().booleanValue());
    }
  }

  @Test
  void opsCredset005CallerMonitorCannotDelaySecretCopyOrClose() throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary);
        var pool = Executors.newSingleThreadExecutor()) {
      install(fixture, ServiceConfigFiles.Service.API);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var set =
          ServiceCredentialSet.load(
              reader(fixture, io, ServiceConfigFiles.Service.API), ServiceConfigFiles.Service.API);
      synchronized (set) {
        var future =
            pool.submit(
                () -> {
                  char[] copy = set.copyPassword(ServiceCredentialId.DB_API);
                  try {
                    assertArrayEquals("pt-public-db-api".toCharArray(), copy);
                  } finally {
                    Arrays.fill(copy, '\0');
                  }
                  set.close();
                  return true;
                });
        assertTrue(future.get(5, TimeUnit.SECONDS).booleanValue());
      }
      assertThrows(IllegalStateException.class, () -> set.copyPassword(ServiceCredentialId.DB_API));
      assertCleared(io);
    }
  }

  private static ServiceCredentialReader reader(
      InspectorCredentialLoaderTest.Fixture fixture,
      InspectorCredentialLoaderTest.TestIo io,
      ServiceConfigFiles.Service service) {
    return new ServiceCredentialReader(
        fixture.held, new InspectorCredentialLoaderTest.TestSecurity(io), service, io);
  }

  private static void install(
      InspectorCredentialLoaderTest.Fixture fixture, ServiceConfigFiles.Service service)
      throws Exception {
    for (var id : ServiceCredentialId.forService(service))
      Files.write(fixture.root.resolve(id.fileName()), synthetic(id));
  }

  private static byte[] synthetic(ServiceCredentialId id) {
    if (id.kind() == ServiceCredentialId.Kind.PASSWORD)
      return ("pt-public-" + id.fileName() + "\n").getBytes(StandardCharsets.UTF_8);
    byte[] encoded = Base64.getEncoder().encode(new byte[32]);
    byte[] prefix = "NKKEY1\nv\n".getBytes(StandardCharsets.US_ASCII);
    byte[] result = Arrays.copyOf(prefix, prefix.length + encoded.length + 1);
    System.arraycopy(encoded, 0, result, prefix.length, encoded.length);
    result[result.length - 1] = '\n';
    Arrays.fill(encoded, (byte) 0);
    return result;
  }

  private static void assertCleared(InspectorCredentialLoaderTest.TestIo io) {
    for (byte[] buffer : io.buffers) {
      assertArrayEquals(new byte[buffer.length], buffer);
    }
    Arrays.fill(io.observedContent, (byte) 0);
  }
}
