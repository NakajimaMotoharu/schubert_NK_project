package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** LAUNCHFILE001..006: actual FD fixture, synthetic root/tmpfs explicitly not native authority. */
final class StartupLaunchFilesTest {
  @TempDir Path temporary;
  static final String OWNER =
      """
      NKMAINTOWNER1
      boot=31100027-3333-4333-8444-555555555555
      run=31100027-2222-4333-8444-555555555555
      activation=31100027-6666-4777-8888-999999999999
      cutoff=2026-09-27T15:00:00Z
      epoch=31100027-4444-4333-8444-555555555555
      morning_invocation=11111111111111111111111111111111
      morning_pid=200
      morning_start_ticks=100
      cleanup_invocation=-
      cleanup_pid=-
      cleanup_start_ticks=-
      deadline_nanos=1800000000001
      """;
  static final String BIND =
      """
      boot_id=31100027-3333-4333-8444-555555555555
      epoch_id=31100027-4444-4333-8444-555555555555
      run_id=31100027-2222-4333-8444-555555555555
      cutoff_utc=2026-09-27T15:00:00.000000Z
      activation_id=31100027-6666-4777-8888-999999999999
      """;
  static final String EPOCH = "31100027-4444-4333-8444-555555555555";

  static StartupPermitRecords.Epoch epoch() throws Exception {
    return StartupPermitRecords.readEpoch(
        StartupLaunchRecordTest.bytes(
            "NKEPOCH1\nstate=ISSUED\n" + BIND + "permit_sha256=" + "a".repeat(64) + "\n"));
  }

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    Files.delete(f.child); // Own empty synthetic fixture only.
    f.metadata =
        (role, metadata) -> {
          metadata.put("uid", 0);
          metadata.put("gid", 0);
        };
    Files.writeString(f.parent.resolve("epoch.current"), "PUBLIC_CURRENT_FIXTURE");
    Files.writeString(f.parent.resolve(EPOCH + ".permit"), "PUBLIC_PERMIT_FIXTURE");
    return f;
  }

  private static String launch(ServiceConfigFiles.Service service) throws Exception {
    String ownerHash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(OWNER.getBytes(StandardCharsets.US_ASCII)));
    return StartupLaunchRecordTest.GOLD
        .replace("service=API", "service=" + service.name())
        .replace("b".repeat(64), ownerHash);
  }

  @Test
  void sameEpochOwnerBothServiceLaunchWholeBytesAndOldArtifactPreservation() throws Exception {
    try (var f = fixture()) {
      var files = new StartupLaunchFiles(f.root, f, f, epoch());
      assertNotNull(new StartupLaunchFiles(f.root, f, epoch()));
      var owner = MaintenanceOwnerFrame.consume(StartupLaunchRecordTest.bytes(OWNER));
      files.prepareOwner(owner, UUID.randomUUID());
      assertEquals(OWNER, Files.readString(f.parent.resolve(EPOCH + ".owner")));
      assertEquals(owner, files.readOwner());
      String old = "41100027-4444-4333-8444-555555555555.owner";
      Files.writeString(f.parent.resolve(old), "PUBLIC_OLD_ARTIFACT");
      for (var service : ServiceConfigFiles.Service.values()) {
        String literal = launch(service);
        var record = StartupLaunchRecord.consume(StartupLaunchRecordTest.bytes(literal));
        files.prepareLaunch(record, UUID.randomUUID());
        assertEquals(
            literal, Files.readString(f.parent.resolve(EPOCH + "." + service.name() + ".launch")));
        assertEquals(record, files.readLaunch(service));
      }
      assertEquals("PUBLIC_OLD_ARTIFACT", Files.readString(f.parent.resolve(old)));
      f.released();
    }
  }

  @Test
  void fixedCurrentIntentIsRequiredAndAnyOldIntentQuarantinesNextMorning() throws Exception {
    try (var f = fixture()) {
      var files = new StartupLaunchFiles(f.root, f, f, epoch());
      for (var service : ServiceConfigFiles.Service.values()) {
        assertThrows(IOException.class, () -> files.requireStartIntent(service));
        Path intent = f.parent.resolve(EPOCH + "." + service.name() + ".start.intent");
        Files.createFile(intent);
        Files.setAttribute(intent, "unix:mode", 0600);
        files.requireStartIntent(service);
        assertThrows(
            IOException.class, () -> StartupLaunchFiles.requireNoServiceResidue(f.root, f, f));
        Files.writeString(intent, "PUBLIC_NONEMPTY");
        assertThrows(IOException.class, () -> files.requireStartIntent(service));
        Files.delete(intent); // Own public TempDir only; never a native recovery.
      }
      StartupLaunchFiles.requireNoServiceResidue(f.root, f, f);
      for (String bad :
          java.util.List.of(
              "41100027-4444-4333-8444-555555555555.API.start.intent",
              "unknown",
              "current",
              "permit-start.intent",
              "stray.part")) {
        Path entry = f.parent.resolve(bad);
        Files.createFile(entry);
        assertThrows(IOException.class, files::requireNamespace);
        assertThrows(
            IOException.class, () -> StartupLaunchFiles.requireNoServiceResidue(f.root, f, f));
        Files.delete(entry);
      }
      assertThrows(NullPointerException.class, () -> files.requireStartIntent(null));
      f.released();
    }
  }

  @Test
  void namespaceResidueAndEveryBindingMismatchRefuseWithoutRepair() throws Exception {
    for (String residue :
        new String[] {
          "permit-start.intent",
          "broker-start.intent",
          UUID.randomUUID() + ".part",
          "unknown",
          "00000000-0000-0000-0000-000000000000.owner"
        }) {
      try (var f = fixture()) {
        var files = new StartupLaunchFiles(f.root, f, f, epoch());
        Files.writeString(f.parent.resolve(residue), "PUBLIC_RESIDUE");
        assertThrows(IOException.class, files::requireNamespace);
        assertEquals("PUBLIC_RESIDUE", Files.readString(f.parent.resolve(residue)));
      }
    }
    for (String[] difference :
        new String[][] {
          {"31100027-3333", "41100027-3333"},
          {"31100027-4444", "41100027-4444"},
          {"31100027-2222", "41100027-2222"},
          {"31100027-6666", "41100027-6666"},
          {"T15:00:00Z", "T15:00:01Z"},
          {
            "cleanup_invocation=-\ncleanup_pid=-\ncleanup_start_ticks=-",
            "cleanup_invocation=33333333333333333333333333333333\ncleanup_pid=400\ncleanup_start_ticks=300"
          }
        }) {
      try (var f = fixture()) {
        var files = new StartupLaunchFiles(f.root, f, f, epoch());
        var owner =
            MaintenanceOwnerFrame.consume(
                StartupLaunchRecordTest.bytes(OWNER.replace(difference[0], difference[1])));
        assertThrows(IOException.class, () -> files.prepareOwner(owner, UUID.randomUUID()));
        assertFalse(Files.exists(f.parent.resolve(EPOCH + ".owner")));
      }
    }
    for (String[] difference :
        new String[][] {
          {"31100027-3333", "41100027-3333"},
          {"31100027-4444", "41100027-4444"},
          {"a".repeat(64), "c".repeat(64)},
          {"2".repeat(32), "1".repeat(32)},
          {"pid=300", "pid=200"}
        }) {
      try (var f = fixture()) {
        var files = new StartupLaunchFiles(f.root, f, f, epoch());
        files.prepareOwner(
            MaintenanceOwnerFrame.consume(StartupLaunchRecordTest.bytes(OWNER)), UUID.randomUUID());
        var record =
            StartupLaunchRecord.consume(
                StartupLaunchRecordTest.bytes(
                    launch(ServiceConfigFiles.Service.API).replace(difference[0], difference[1])));
        assertThrows(IOException.class, () -> files.prepareLaunch(record, UUID.randomUUID()));
        assertFalse(Files.exists(f.parent.resolve(EPOCH + ".API.launch")));
      }
    }
  }

  @Test
  void duplicatesMissingAndProfileCannotInvokeCleanupApi() throws Exception {
    try (var f = fixture()) {
      var expected = epoch();
      var files = new StartupLaunchFiles(f.root, f, f, expected);
      assertThrows(IOException.class, files::readOwner);
      var owner = MaintenanceOwnerFrame.consume(StartupLaunchRecordTest.bytes(OWNER));
      files.prepareOwner(owner, UUID.randomUUID());
      assertThrows(IOException.class, () -> files.prepareOwner(owner, UUID.randomUUID()));
      assertEquals(OWNER, Files.readString(f.parent.resolve(EPOCH + ".owner")));
      var primitive =
          CleanupWorkerRequestFiles.forStartup(
              f.root, f, f, expected, CleanupWorkerRequestFiles.StartupSource.API);
      assertThrows(IOException.class, primitive::read);
      assertThrows(IOException.class, primitive::readExpiry);
      assertThrows(IOException.class, primitive::readOwner);
      assertThrows(IOException.class, primitive::requireOwnedCycle);
      assertThrows(
          IOException.class, () -> primitive.prepareStartup(new byte[0], UUID.randomUUID()));
      assertThrows(
          IOException.class, () -> primitive.prepareStartup(new byte[1025], UUID.randomUUID()));
      f.released();
    }
  }
}
