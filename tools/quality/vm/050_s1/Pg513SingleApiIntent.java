package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

/** SSC209/PT-OPS-PG513: fixed pre-Java API marker, operator only. No child proof or selector. */
public final class Pg513SingleApiIntent {
  private Pg513SingleApiIntent() {}
  @FunctionalInterface public interface Gate { void verify() throws IOException; }
  private static void require(boolean value) throws IOException {
    if (!value) throw new IOException("fixed single API recovery unavailable");
  }
  public static boolean namespace(Set<String> actual, String epoch, boolean present) {
    if (actual == null || epoch == null || !epoch.matches("(?!00000000-0000-0000-0000-000000000000)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")) return false;
    var expected = new HashSet<>(Set.of("epoch.current", epoch+".permit", epoch+".owner"));
    if (present) expected.add(epoch+".API.start.intent");
    return actual.equals(expected);
  }
  private static Set<String> names(OwnedTransferDirectory root) throws IOException {
    return root.atDirectory(held -> {
      var result = new HashSet<String>();
      try (var entries = java.nio.file.Files.newDirectoryStream(held)) {
        for (var entry : entries) {
          var leaf = entry.getFileName(); require(leaf != null);
          require(result.add(Objects.requireNonNull(leaf).toString()));
        }
      }
      return Set.copyOf(result);
    });
  }
  public static MaintenanceOwnerFrame correlate(OwnedTransferDirectory root,
      StartupPermitRecords.Epoch expected, MaintenanceActivation activation,
      String digest) throws IOException {
    return correlate(root, expected, activation, digest, LinuxInodeSecurity.create(), new StartupPermitFiles.NioIo());
  }
  static MaintenanceOwnerFrame correlate(OwnedTransferDirectory root,
      StartupPermitRecords.Epoch expected, MaintenanceActivation activation,
      String digest, InodeSecurityCalls security, StartupPermitFiles.Io io) throws IOException {
    require(root != null && expected != null && activation != null && digest != null && security != null && io != null);
    require(expected.state() == StartupPermitRecords.State.INVALID && expected.activation().equals(activation));
    var permits = new StartupPermitFiles(root, security, io, java.util.UUID::randomUUID);
    require(expected.equals(permits.current()));
    var revoked = permits.readRevoked(expected);
    require(revoked.permit().releaseDigest().equals(digest));
    var owner = new StartupLaunchFiles(root, security, io, revoked.formerIssued()).readOwner();
    require(owner.boot().equals(expected.boot()) && owner.epoch().equals(expected.epoch())
        && owner.run().equals(activation.run().id()) && owner.activation().equals(activation.id())
        && owner.cutoff().equals(activation.run().cutoff()) && owner.cleanup().isEmpty()
        && owner.morning().invocation().equals("bbb6dc1276a4459da65143db3e4ee3f0")
        && owner.morning().pid() == 5872 && owner.morning().startTicks() == 380665);
    require(expected.equals(permits.current()));
    return owner; // Data correlation only. NEVER call the expired original parentsGuard.
  }
  public static void retire(OwnedTransferDirectory root, StartupPermitRecords.Epoch expected,
      MaintenanceActivation activation, String digest,
      Gate completeProof, Gate confirmedOwnership) throws IOException {
    retire(root, expected, activation, digest, completeProof, confirmedOwnership,
        LinuxInodeSecurity.create(), new StartupPermitFiles.NioIo());
  }
  static void retire(OwnedTransferDirectory root, StartupPermitRecords.Epoch expected,
      MaintenanceActivation activation, String digest, Gate completeProof, Gate confirmedOwnership,
      InodeSecurityCalls security, StartupPermitFiles.Io io) throws IOException {
    require(completeProof != null && confirmedOwnership != null);
    var owner = correlate(root, expected, activation, digest, security, io);
    String epoch = expected.epoch().toString();
    Gate correlation = () -> {
      confirmedOwnership.verify();
      require(owner.equals(correlate(root, expected, activation, digest, security, io)));
      var actual = names(root);
      require(namespace(actual, epoch, true) || namespace(actual, epoch, false));
    };
    correlation.verify(); require(namespace(names(root), epoch, true)); completeProof.verify();
    BackupStartIntentFiles.Gate success = () -> { correlation.verify(); completeProof.verify(); };
    var marker = new BackupStartIntentFiles(root, security, io, success, epoch+".API.start.intent");
    var captured = marker.observeQuarantine();
    try {
      marker.retire(captured); root.sync(); correlation.verify(); completeProof.verify();
      require(namespace(names(root), epoch, false));
    } catch (IOException | RuntimeException | Error primary) {
      try {
        var quarantine = new BackupStartIntentFiles(root, security, io, correlation::verify, epoch+".API.start.intent");
        quarantine.quarantineService(expected, ServiceConfigFiles.Service.API); root.sync();
      } catch (IOException | RuntimeException | Error secondary) { primary.addSuppressed(secondary); }
      throw primary;
    }
  }
  /** Fail-closed only. Caller proves CURRENT M/A and usable root, never consumed DB/Ref grants. */
  public static void quarantine(OwnedTransferDirectory root, StartupPermitRecords.Epoch expected,
      MaintenanceActivation activation, String digest, Gate currentMA) throws IOException {
    require(currentMA != null);
    currentMA.verify();var owner=correlate(root,expected,activation,digest);
    BackupStartIntentFiles.Gate correlation=()->{
      currentMA.verify();require(owner.equals(correlate(root,expected,activation,digest)));
      var actual=names(root);require(namespace(actual,expected.epoch().toString(),true)
          || namespace(actual,expected.epoch().toString(),false));
    };
    var marker=new BackupStartIntentFiles(root,LinuxInodeSecurity.create(),new StartupPermitFiles.NioIo(),correlation,
        expected.epoch()+".API.start.intent");
    marker.quarantineService(expected,ServiceConfigFiles.Service.API);root.sync();correlation.verify();
    require(namespace(names(root),expected.epoch().toString(),true));
  }
}
