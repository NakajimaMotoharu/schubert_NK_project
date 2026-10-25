package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.ScenarioFileInspector;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS333 §7.4 probe-before-scan actual ext4 boundary, PT-SCN-008-P04/P05. */
final class TransferStoragePreparationTest {
  private static final Instant NOW = Instant.parse("2026-09-07T15:00:00Z");

  @TempDir(factory = TransferRootInspectionTest.Ext4Fixture.class)
  Path fixture;

  @Test
  void p04ProbePrecedesCompleteScanAndPublisherUsesScannedQuota() throws Exception {
    Path path = root("normal");
    var identity = identity(path);
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), path)) {
      var prepared = TransferStoragePreparation.prepare(held, identity, NOW);
      assertEquals(0, prepared.usage().bytes());
      assertEquals(0, prepared.usage().files());
      assertEquals(TransferCapacity.Level.NORMAL, prepared.usage().level());
      Path date = path.resolve("20260908");
      assertTrue(Files.isDirectory(date));
      try (var entries = Files.list(date)) {
        assertEquals(0, entries.count());
      }
      var record =
          new ScenarioEntryRecord(
              new EntryId(71),
              1,
              42,
              EntryType.NARRATION,
              Optional.empty(),
              "本文 0",
              0,
              Optional.empty(),
              Optional.empty());
      var descriptor = prepared.publisher().publish(List.of(record), NOW);
      assertEquals(4800, descriptor.byteLength());
      assertEquals(1, descriptor.recordCount());
      assertEquals(
          ScenarioFileInspector.Availability.PRESENT, prepared.inspector().inspect(descriptor));
      assertEquals(4800, prepared.usage().bytes());
      assertEquals(1, prepared.usage().files());
    }
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), path)) {
      var resumed = TransferStoragePreparation.prepare(held, identity, NOW);
      assertEquals(4800, resumed.usage().bytes());
      assertEquals(1, resumed.usage().files());
      try (var entries = Files.list(path.resolve("20260908"))) {
        assertEquals(1, entries.count());
      }
    }
  }

  @Test
  void p05InvalidRootAndIncompleteScanNeverYieldPreparedCapabilities() throws Exception {
    Path path = root("invalid");
    var identity = identity(path);
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), path)) {
      assertThrows(
          NullPointerException.class,
          () -> TransferStoragePreparation.prepare(null, identity, NOW));
      assertThrows(
          NullPointerException.class, () -> TransferStoragePreparation.prepare(held, null, NOW));
      assertThrows(
          NullPointerException.class,
          () -> TransferStoragePreparation.prepare(held, identity, null));
      assertThrows(
          StorageIoException.class,
          () ->
              TransferStoragePreparation.prepare(
                  held, new StorageIdentity(identity.owner(), "wrong"), NOW));
      assertFalse(Files.exists(path.resolve("20260908")));
      Files.writeString(path.resolve("unapproved-entry"), "synthetic");
      assertThrows(
          StorageIoException.class, () -> TransferStoragePreparation.prepare(held, identity, NOW));
      assertTrue(Files.exists(path.resolve("unapproved-entry")));
      assertThrows(
          NullPointerException.class,
          () ->
              new TransferStoragePreparation.Prepared(
                  null,
                  descriptor -> ScenarioFileInspector.Availability.MISSING,
                  new TransferCapacity(0, 0)));
      assertThrows(
          NullPointerException.class,
          () ->
              new TransferStoragePreparation.Prepared(
                  (records, at) -> null, null, new TransferCapacity(0, 0)));
      ScenarioFilePublisher publisher = (records, at) -> null;
      ScenarioFileInspector inspector = descriptor -> ScenarioFileInspector.Availability.MISSING;
      assertThrows(
          NullPointerException.class,
          () -> new TransferStoragePreparation.Prepared(publisher, inspector, null));
    }
  }

  private Path root(String name) throws Exception {
    Path path = Files.createDirectory(fixture.resolve(name));
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-x---"));
    Files.setAttribute(
        path,
        "posix:group",
        path.getFileSystem().getUserPrincipalLookupService().lookupPrincipalByGroupName("users"));
    return path;
  }

  private static StorageIdentity identity(Path path) throws Exception {
    var attributes = Files.readAttributes(path, PosixFileAttributes.class);
    return new StorageIdentity(attributes.owner().getName(), attributes.group().getName());
  }
}
