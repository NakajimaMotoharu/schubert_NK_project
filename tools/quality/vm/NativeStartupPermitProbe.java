import dev.codex.schubert.nk.batch.file.StartupPermitFiles;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.time.Instant;
import java.util.UUID;

/** VM-only genuine root/tmpfs IO, public fixture, never the production permit namespace/issuer. */
public final class NativeStartupPermitProbe {
  public static void main(String[] arguments) throws Exception {
    var security = LinuxInodeSecurity.create();
    if (arguments.length != 0 || security.effectiveUid() != 0
        || !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim()
            .equals("pgpt-r2-20260927-01"))
      throw new AssertionError("isolated root fixture required");
    Path directory = Path.of("/run/schubert-nk/startup-pgpt-303");
    // Fresh test-only namespace; never repair/overwrite an old run, never the fixed original.
    Files.createDirectory(directory,
        PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    if (!Files.getFileStore(directory).type().equals("tmpfs"))
      throw new AssertionError("actual volatile filesystem required");
    UUID boot = UUID.fromString(Files.readString(Path.of("/proc/sys/kernel/random/boot_id")).trim());
    UUID epoch = UUID.fromString("33333333-3333-3333-3333-333333333333");
    var activation = new MaintenanceActivation(
        new BatchRun(UUID.fromString("44444444-4444-4444-4444-444444444444"),
            Instant.parse("2026-09-27T00:00:00.000000Z")),
        UUID.fromString("55555555-5555-5555-5555-555555555555"));
    try (var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), directory)) {
      var records = new StartupPermitFiles(root, security);
      var invalid = records.invalidate(boot, epoch, activation);
      var fixture = new StartupPermitRecords.Permit(boot, epoch, activation, "2".repeat(32),
          "b".repeat(64), "c".repeat(64), "d".repeat(64), "e".repeat(64), "f".repeat(64));
      var issued = records.issue(invalid, fixture);
      if (!issued.equals(records.current()) || !fixture.equals(records.readIssued()))
        throw new AssertionError("original readback mismatch");
      if (!Files.getAttribute(directory.resolve("epoch.current"),"unix:mode").equals(0100600)
          || !Files.getAttribute(directory.resolve(epoch+".permit"),"unix:nlink").equals(1))
        throw new AssertionError("native mode/link mismatch");
      records.invalidate(boot, UUID.fromString("66666666-6666-6666-6666-666666666666"), activation);
      try { records.readIssued(); throw new AssertionError("old permit accepted"); }
      catch (StorageIoException expected) {
        if (expected.reason() != StorageIoException.Reason.UNAVAILABLE)
          throw new AssertionError("unexpected refusal");
      }
    }
    System.out.println("PT-OPS-NATIVE-020 PASS actualRoot=true actualTmpfs=true privateMode=true "
        + "canonicalOriginalReadback=true atomicCurrent=true oldPermitRefused=true "
        + "testNamespaceOnly=true fullGate=false businessProcess=false");
  }
}
