package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.nio.file.Files;
import java.util.HashSet;
import java.util.Set;

/** SSC266/PT-OPS-PUB1487001: INVALID data correlation, not historical ISSUED authority. */
public final class Pg1487PublicationOnlyIntent {
  private Pg1487PublicationOnlyIntent() {}
  @FunctionalInterface public interface Gate { void verify() throws IOException; }
  private static void require(boolean value)throws IOException {
    if(!value)throw new IOException("fixed publication-only recovery refused");
  }
  public static boolean namespace(Set<String> actual,String epoch,boolean marker) {
    if(actual==null||epoch==null||!epoch.matches("(?!00000000-0000-0000-0000-000000000000)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}"))return false;
    var expected=new HashSet<>(Set.of("epoch.current",epoch+".permit"));
    if(marker)expected.add("permit-start.intent");
    return actual.equals(expected);
  }
  private static Set<String> names(OwnedTransferDirectory root)throws IOException {
    return root.atDirectory(p->{
      var result=new HashSet<String>();
      try(var entries=Files.newDirectoryStream(p)) {
        for(var entry:entries){var name=entry.getFileName();require(name!=null&&result.add(name.toString()));}
      }
      return Set.copyOf(result);
    });
  }
  private static void correlate(OwnedTransferDirectory root,StartupPermitRecords.Epoch expected,
      MaintenanceActivation activation,String release,String broker,
      InodeSecurityCalls security,StartupPermitFiles.Io io)throws IOException {
    require(root!=null&&expected!=null&&activation!=null&&release!=null&&broker!=null&&security!=null&&io!=null);
    require(expected.state()==StartupPermitRecords.State.INVALID&&expected.activation().equals(activation));
    var permits=new StartupPermitFiles(root,security,io,java.util.UUID::randomUUID);
    require(expected.equals(permits.current()));
    var permit=permits.readRevoked(expected).permit(); // Never use formerIssued or forge owner/Pair.
    require(permit.boot().equals(expected.boot())&&permit.epoch().equals(expected.epoch())
        &&permit.activation().equals(activation)&&permit.releaseDigest().equals(release)
        &&permit.brokerInvocation().equals(broker));
    require(expected.equals(permits.current()));
    var actual=names(root);require(namespace(actual,expected.epoch().toString(),true)||namespace(actual,expected.epoch().toString(),false));
  }
  public static void retire(OwnedTransferDirectory root,StartupPermitRecords.Epoch expected,
      MaintenanceActivation activation,String release,String broker,Gate fullStoppedProof,Gate freshMA)throws IOException {
    retire(root,expected,activation,release,broker,fullStoppedProof,freshMA,LinuxInodeSecurity.create(),new StartupPermitFiles.NioIo());
  }
  static void retire(OwnedTransferDirectory root,StartupPermitRecords.Epoch expected,
      MaintenanceActivation activation,String release,String broker,Gate fullStoppedProof,Gate freshMA,
      InodeSecurityCalls security,StartupPermitFiles.Io io)throws IOException {
    require(fullStoppedProof!=null&&freshMA!=null);
    Gate data=()->{freshMA.verify();correlate(root,expected,activation,release,broker,security,io);};
    data.verify();require(namespace(names(root),expected.epoch().toString(),true));
    fullStoppedProof.verify();
    BackupStartIntentFiles.Gate gate=()->{data.verify();fullStoppedProof.verify();};
    var marker=new BackupStartIntentFiles(root,security,io,gate,"permit-start.intent");
    var captured=marker.observeQuarantine();
    try {
      marker.retire(captured);root.sync();gate.verify();
      require(namespace(names(root),expected.epoch().toString(),false));
    } catch(IOException|RuntimeException|Error primary) {
      try {
        // Unknown outcome: only still-proven M/A/data may preserve fixed quarantine.
        data.verify();
        var quarantine=new BackupStartIntentFiles(root,security,io,data::verify,"permit-start.intent");
        quarantine.quarantinePublication();root.sync();data.verify();
        require(namespace(names(root),expected.epoch().toString(),true));
      } catch(IOException|RuntimeException|Error secondary){primary.addSuppressed(secondary);}
      throw primary;
    }
  }
}
