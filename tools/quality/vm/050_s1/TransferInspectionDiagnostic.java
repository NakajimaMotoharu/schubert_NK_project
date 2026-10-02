import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SecureDirectoryStream;

/** Read-only PG424 Transfer boundary observation; never grants readiness or changes storage. */
public final class TransferInspectionDiagnostic {
  private TransferInspectionDiagnostic() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 0) throw new IllegalArgumentException("no arguments accepted");
    try (var root = OwnedTransferDirectory.open(
        LinuxDirectoryCalls.create(), Path.of("/srv/schubert-nk/data/transfer"))) {
      System.out.println("heldRootOpened=true");
      root.atDirectory(handle -> {
        StorageAttributeGuard.directory(
            Files.readAttributes(handle, "unix:owner,group,mode,nlink"),
            new StorageIdentity("schubert-api", "schubert-web"));
        System.out.println("heldAttributesAccepted=true");
        var store = Files.getFileStore(handle);
        System.out.println("heldExt4=" + store.type().equals("ext4"));
        System.out.println("heldStoreReadOnly=" + store.isReadOnly());
        System.out.println("heldMountReadOnly="
            + LinuxInodeSecurity.create().readOnlyFilesystem(handle));
        System.out.println("heldWritable=" + Files.isWritable(handle));
        try (var entries = Files.newDirectoryStream(handle)) {
          System.out.println("heldSecureDirectoryStream="
              + (entries instanceof SecureDirectoryStream<?>));
        }
        return Boolean.TRUE;
      });
    }
  }
}
