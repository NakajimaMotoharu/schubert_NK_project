package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.util.Objects;

/**
 * SSC198 / BUG771 / PT-OPS-BREC198001..008. Isolated Root operator tool only: not
 * packaged into Production or a runtime admission fallback. Caller continuously owns
 * authenticated M/A/DB/advisory/10Refs, signed pending original and exact old state.
 * Borrows the fixed request root; NEVER closes it, starts a unit or edits DB/request.
 */
public final class BackupInterruptedStartRecovery {
  public enum Phase { OBSERVING, BEFORE_RETIRE, RETIRING, RETIRED, REISOLATING, QUARANTINED }
  @FunctionalInterface
  public interface Proof { void verify(Phase phase) throws IOException; }

  private BackupInterruptedStartRecovery() {}

  public static void retire(OwnedTransferDirectory root, InodeSecurityCalls security,
      Proof proof) throws IOException {
    Objects.requireNonNull(root, "borrowed fixed Backup root");
    Objects.requireNonNull(security, "native inode security");
    Objects.requireNonNull(proof, "continuous privileged operator proof");
    retire(root, security, new InspectorEnvironmentPublisher.NioIo(), proof);
  }

  static void retire(OwnedTransferDirectory root, InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io source, Proof proof) throws IOException {
    Objects.requireNonNull(root, "borrowed fixed Backup root");
    Objects.requireNonNull(security, "native inode security");
    Objects.requireNonNull(source, "strict metadata source");
    Objects.requireNonNull(proof, "continuous privileged operator proof");
    Phase[] phase={Phase.OBSERVING};
    var files=new BackupStartIntentFiles(root,security,source,()->proof.verify(phase[0]));
    boolean mightRetire=false;
    try {
      proof.verify(Phase.OBSERVING);
      var intent=files.observeQuarantine();
      files.requirePresent(intent);
      phase[0]=Phase.BEFORE_RETIRE;
      proof.verify(phase[0]);
      phase[0]=Phase.RETIRING;
      mightRetire=true;
      files.retire(intent);
      root.sync();
      phase[0]=Phase.RETIRED;
      files.requireClear();
      proof.verify(phase[0]);
    } catch(IOException|RuntimeException|Error failure) {
      if(mightRetire) {
        try { quarantine(root,security,source,proof); }
        catch(IOException|RuntimeException|Error secondary) {
          if(secondary!=failure) failure.addSuppressed(secondary);
        }
      }
      throw failure;
    }
  }

  /** Caller may use after a later readback/DB/ref close failure, while M/A still hold. */
  public static void quarantine(OwnedTransferDirectory root, InodeSecurityCalls security,
      Proof proof) throws IOException {
    quarantine(root,security,new InspectorEnvironmentPublisher.NioIo(),proof);
  }

  static void quarantine(OwnedTransferDirectory root, InodeSecurityCalls security,
      InspectorEnvironmentPublisher.Io source, Proof proof) throws IOException {
    Objects.requireNonNull(root, "borrowed fixed Backup root");
    Objects.requireNonNull(security, "native inode security");
    Objects.requireNonNull(source, "strict metadata source");
    Objects.requireNonNull(proof, "continuous privileged operator proof");
    var files=new BackupStartIntentFiles(root,security,source,()->proof.verify(Phase.REISOLATING));
    proof.verify(Phase.REISOLATING);
    BackupStartIntentFiles.Intent intent;
    try { intent=files.observeQuarantine(); }
    catch(StorageIoException missing) {
      if(missing.reason()!=StorageIoException.Reason.MISSING) throw missing;
      intent=files.begin();
    }
    root.sync();
    files.requirePresent(intent);
    proof.verify(Phase.QUARANTINED);
  }
}
