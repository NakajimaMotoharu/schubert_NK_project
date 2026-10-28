package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.bootstrap.ApiNativeCodecs;
import dev.codex.schubert.nk.api.dispatch.ApiSyncRequestDispatcher;
import dev.codex.schubert.nk.api.file.MediaAssetFixture;
import dev.codex.schubert.nk.api.file.MediaIntegrityException;
import dev.codex.schubert.nk.api.file.PublicApiCredentialFixture;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-OPS-API-PREP-001..004: real retained FD/probe/usage, synthetic credential metadata. Component
 * evidence only; native Root/ordinary full registration/ready remains separate.
 */
final class ApiApplicationPreparationTest {
  private static final String FIXTURE_DISPATCH_BEFORE_EXPOSURE_28246F61 =
      "dispatch before exposure";
  private static final String FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470 = "no JMS during assembly";

  @TempDir(factory = TransferRootInspectionTest.Ext4Fixture.class)
  Path directory;

  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-07T15:00:00Z"), ZoneOffset.UTC);
  private static final Set<String> EXPECTED =
      Set.of(
          "LGNREQ01",
          "LOGREQ01",
          "GAMREQ01",
          "SPKREQ01",
          "SRCREQ01",
          "RTEREQ01",
          "SCFREQ01",
          "SCNREQ01",
          "LGSREQ01",
          "AUDREQ01",
          "ANMREQ01",
          "ANLREQ01",
          "VIDREQ01",
          "MCTREQ01",
          "MCSREQ01",
          "MTRREQ01",
          "MEDREQ01",
          "USRREQ01",
          "UDTREQ01",
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "QSSREQ01",
          "QSDREQ01",
          "NTSREQ01",
          "NTDREQ01",
          "NTCREQ01",
          "QDLREQ01");

  private DataSource unusedDatabase() {
    return (DataSource)
        java.lang.reflect.Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (proxy, method, arguments) -> {
              throw new AssertionError("assembly may not use database before requests");
            });
  }

  @Test
  void prep001RealProbeFullScanAndAll31GraphAreBorrowedNotProcessReady() throws Exception {
    Path transfer = transfer();
    var identity = identity(transfer);
    var observed = new java.util.concurrent.atomic.AtomicReference<Set<String>>();
    try (var credential = new PublicApiCredentialFixture(directory);
        var codecs = ApiNativeCodecs.create(credential.credentials());
        var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), transfer);
        var assets = new MediaAssetFixture(directory.resolve("assets"))) {
      ApiApplicationPreparation.executeBorrowed(
          unusedDatabase(),
          codecs,
          root,
          identity,
          assets.held,
          assets.identity,
          7,
          CLOCK,
          () -> {
            throw new AssertionError("no dispatch before request");
          },
          (processors, outbox) -> {
            assertEquals(EXPECTED, processors.keySet());
            assertEquals(31, processors.size());
            assertThrows(UnsupportedOperationException.class, () -> processors.clear());
            assertNotNull(new ApiSyncRequestDispatcher(processors));
            assertInstanceOf(
                dev.codex.schubert.nk.api.application.question.QuestionSubmissionService.class,
                processors.get("QSBREQ01"));
            assertInstanceOf(
                dev.codex.schubert.nk.api.application.question.QuestionQueryApplicationService
                    .class,
                processors.get("QSSREQ01"));
            assertSame(processors.get("QSSREQ01"), processors.get("NTDREQ01"));
            assertInstanceOf(
                dev.codex.schubert.nk.api.application.question.QuestionMutationApplicationService
                    .class,
                processors.get("QDLREQ01"));
            assertSame(processors.get("QDLREQ01"), processors.get("NTCREQ01"));
            assertTrue(Files.isDirectory(transfer.resolve("20260908")));
            try (var names = Files.list(transfer.resolve("20260908"))) {
              assertEquals(0, names.count());
            }
            observed.set(Set.copyOf(processors.keySet()));
          });
      assertEquals(Boolean.TRUE, root.atDirectory(Files::isDirectory));
      assertEquals(Boolean.TRUE, assets.held.atDirectory(Files::isDirectory));
      assertEquals(
          "fp1",
          credential
              .credentials()
              .version(dev.codex.schubert.nk.storage.ServiceCredentialId.OPERATION_HMAC_CURRENT));
    }
    assertEquals(EXPECTED, observed.get());
  }

  @Test
  void prep002ManifestAndRootFailuresNeverExposeProcessors() throws Exception {
    Path transfer = transfer();
    var calls = new AtomicInteger();
    try (var credential = new PublicApiCredentialFixture(directory);
        var codecs = ApiNativeCodecs.create(credential.credentials());
        var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), transfer);
        var assets = new MediaAssetFixture(directory.resolve("assets"))) {
      for (int count : new int[] {1, 6, 8})
        assertThrows(
            MediaIntegrityException.class,
            () ->
                ApiApplicationPreparation.executeBorrowed(
                    unusedDatabase(),
                    codecs,
                    root,
                    identity(transfer),
                    assets.held,
                    assets.identity,
                    count,
                    CLOCK,
                    () -> {
                      throw new AssertionError(FIXTURE_DISPATCH_BEFORE_EXPOSURE_28246F61);
                    },
                    (ignored, outbox) -> calls.incrementAndGet()));
      assertThrows(
          MediaIntegrityException.class,
          () ->
              ApiApplicationPreparation.executeBorrowed(
                  unusedDatabase(),
                  codecs,
                  root,
                  identity(transfer),
                  assets.held,
                  new StorageIdentity("unknown", assets.identity.group()),
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_DISPATCH_BEFORE_EXPOSURE_28246F61);
                  },
                  (ignored, outbox) -> calls.incrementAndGet()));
      Files.setPosixFilePermissions(transfer, PosixFilePermissions.fromString("rwx------"));
      assertThrows(
          IOException.class,
          () ->
              ApiApplicationPreparation.executeBorrowed(
                  unusedDatabase(),
                  codecs,
                  root,
                  identity(transfer),
                  assets.held,
                  assets.identity,
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_DISPATCH_BEFORE_EXPOSURE_28246F61);
                  },
                  (ignored, outbox) -> calls.incrementAndGet()));
      assertEquals(0, calls.get());
    }
  }

  @Test
  void prep003PrimaryIoRuntimeAndFatalIdentityDoNotCloseBorrowedOwners() throws Exception {
    Path transfer = transfer();
    try (var credential = new PublicApiCredentialFixture(directory);
        var codecs = ApiNativeCodecs.create(credential.credentials());
        var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), transfer);
        var assets = new MediaAssetFixture(directory.resolve("assets"))) {
      for (Throwable failure :
          java.util.List.of(
              new IOException("public IO"),
              new IllegalStateException("public runtime"),
              new AssertionError("public fatal"))) {
        var actual =
            assertThrows(
                failure.getClass(),
                () ->
                    ApiApplicationPreparation.executeBorrowed(
                        unusedDatabase(),
                        codecs,
                        root,
                        identity(transfer),
                        assets.held,
                        assets.identity,
                        7,
                        CLOCK,
                        () -> {
                          throw new AssertionError(FIXTURE_DISPATCH_BEFORE_EXPOSURE_28246F61);
                        },
                        (ignored, outbox) -> {
                          if (failure instanceof IOException io) throw io;
                          if (failure instanceof RuntimeException runtime) throw runtime;
                          throw (Error) failure;
                        }));
        assertSame(failure, actual);
        assertEquals(Boolean.TRUE, root.atDirectory(Files::isDirectory));
        assertEquals(Boolean.TRUE, assets.held.atDirectory(Files::isDirectory));
      }
    }
  }

  @Test
  @org.junit.jupiter.api.parallel.ResourceLock("JCA_PROVIDERS")
  void own003MissingCryptographyHasFixedDiagnosticAndKeepsBorrowedRoots() throws Exception {
    Path transfer = transfer();
    var transferIdentity = identity(transfer);
    var original = java.security.Security.getProviders();
    AtomicInteger probeDate = new AtomicInteger(-1);
    AtomicInteger transitions = new AtomicInteger();
    AtomicInteger operations = new AtomicInteger();
    var nativeCalls = LinuxDirectoryCalls.create();
    var calls =
        (dev.codex.schubert.nk.storage.DirectoryCalls)
            java.lang.reflect.Proxy.newProxyInstance(
                nativeCalls.getClass().getClassLoader(),
                new Class<?>[] {dev.codex.schubert.nk.storage.DirectoryCalls.class},
                (proxy, method, arguments) -> {
                  Object returned;
                  try {
                    returned = method.invoke(nativeCalls, arguments);
                  } catch (java.lang.reflect.InvocationTargetException failure) {
                    throw failure.getCause();
                  }
                  if (method.getName().equals("openDirectory")
                      && arguments != null
                      && arguments[1].equals("20260908")
                      && probeDate.get() == -1) probeDate.set((Integer) returned);
                  if (method.getName().equals("close")
                      && arguments != null
                      && arguments[0].equals(probeDate.get())
                      && transitions.get() == 0) {
                    transitions.incrementAndGet();
                    for (var provider : java.security.Security.getProviders())
                      if (provider.getService("MessageDigest", "SHA-256") != null)
                        java.security.Security.removeProvider(provider.getName());
                    assertThrows(
                        java.security.NoSuchAlgorithmException.class,
                        () -> java.security.MessageDigest.getInstance("SHA-256"));
                  }
                  return returned;
                });
    try (var credential = new PublicApiCredentialFixture(directory);
        var codecs = ApiNativeCodecs.create(credential.credentials());
        var root = OwnedTransferDirectory.open(calls, transfer);
        var assets = new MediaAssetFixture(directory.resolve("own003-assets"))) {
      try {
        var failure =
            assertThrows(
                IOException.class,
                () ->
                    ApiApplicationPreparation.executeBorrowed(
                        unusedDatabase(),
                        codecs,
                        root,
                        transferIdentity,
                        assets.held,
                        assets.identity,
                        7,
                        CLOCK,
                        () -> {
                          throw new AssertionError(FIXTURE_DISPATCH_BEFORE_EXPOSURE_28246F61);
                        },
                        (processors, outbox) -> operations.incrementAndGet()));
        assertEquals("API cryptography unavailable", failure.getMessage());
        assertNull(failure.getCause(), "private provider details must not escape");
        assertEquals(1, transitions.get());
        assertEquals(0, operations.get());
        assertEquals(Boolean.TRUE, root.atDirectory(Files::isDirectory));
        assertEquals(Boolean.TRUE, assets.held.atDirectory(Files::isDirectory));
      } finally {
        for (int i = 0; i < original.length; i++)
          if (java.security.Security.getProvider(original[i].getName()) == null)
            java.security.Security.insertProviderAt(original[i], i + 1);
      }
      var restored = java.security.Security.getProviders();
      assertEquals(original.length, restored.length);
      for (int i = 0; i < original.length; i++) assertSame(original[i], restored[i]);
      assertEquals(
          32, java.security.MessageDigest.getInstance("SHA-256").digest(new byte[0]).length);
    }
  }

  @Test
  void prep004PublicNullAndPartialMissingRootsNeverCallOperation() throws Exception {
    var database = unusedDatabase();
    var operation =
        (ApiApplicationPreparation.Operation)
            (ignored, outbox) -> {
              throw new AssertionError("must not expose");
            };
    Path transfer = transfer();
    try (var credential = new PublicApiCredentialFixture(directory)) {
      var credentials = credential.credentials();
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  null,
                  credentials,
                  transfer,
                  directory,
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470);
                  },
                  operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database,
                  null,
                  transfer,
                  directory,
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470);
                  },
                  operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database,
                  credentials,
                  null,
                  directory,
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470);
                  },
                  operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database,
                  credentials,
                  transfer,
                  null,
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470);
                  },
                  operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database,
                  credentials,
                  transfer,
                  directory,
                  7,
                  null,
                  () -> {
                    throw new AssertionError(FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470);
                  },
                  operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database,
                  credentials,
                  transfer,
                  directory,
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470);
                  },
                  null));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database, credentials, transfer, directory, 7, CLOCK, null, operation));
      assertThrows(
          IOException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database,
                  credentials,
                  transfer,
                  directory.resolve("missing"),
                  7,
                  CLOCK,
                  () -> {
                    throw new AssertionError(FIXTURE_NO_JMS_DURING_ASSEMBLY_F0C35470);
                  },
                  operation));
      assertEquals(
          "fp1",
          credentials.version(
              dev.codex.schubert.nk.storage.ServiceCredentialId.OPERATION_HMAC_CURRENT));
    }
  }

  private Path transfer() throws IOException {
    Path path = Files.createDirectory(directory.resolve("transfer"));
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-x---"));
    return path;
  }

  private static StorageIdentity identity(Path path) throws IOException {
    var attrs = Files.readAttributes(path, PosixFileAttributes.class);
    return new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
  }
}
