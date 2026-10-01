package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.*;

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
          "ULKREQ01");

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
  void prep001RealProbeFullScanAndExisting24GraphAreBorrowedNotReady() throws Exception {
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
          processors -> {
            assertEquals(EXPECTED, processors.keySet());
            assertEquals(24, processors.size());
            assertThrows(UnsupportedOperationException.class, () -> processors.clear());
            assertThrows(IOException.class, () -> new ApiSyncRequestDispatcher(processors));
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
                    ignored -> calls.incrementAndGet()));
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
                  ignored -> calls.incrementAndGet()));
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
                  ignored -> calls.incrementAndGet()));
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
                        ignored -> {
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
  void prep004PublicNullAndPartialMissingRootsNeverCallOperation() throws Exception {
    var database = unusedDatabase();
    var operation =
        (ApiApplicationPreparation.Operation)
            ignored -> {
              throw new AssertionError("must not expose");
            };
    Path transfer = transfer();
    try (var credential = new PublicApiCredentialFixture(directory)) {
      var credentials = credential.credentials();
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  null, credentials, transfer, directory, 7, CLOCK, operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database, null, transfer, directory, 7, CLOCK, operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database, credentials, null, directory, 7, CLOCK, operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database, credentials, transfer, null, 7, CLOCK, operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database, credentials, transfer, directory, 7, null, operation));
      assertThrows(
          NullPointerException.class,
          () ->
              ApiApplicationPreparation.execute(
                  database, credentials, transfer, directory, 7, CLOCK, null));
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
