package dev.codex.schubert.nk.batch.file;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.util.Optional;
/** SSC210/PT-OPS-PG515: data-only ISSUED binding. No expired parentsGuard or invented launch. */
public final class Pg515IssuedApiRecovery {
  private Pg515IssuedApiRecovery() {}
  static void require(boolean value)throws IOException { if(!value)throw new IOException("fixed issued API recovery unavailable"); }
  public static StartupPermitRecords.Permit issued(OwnedTransferDirectory root, StartupPermitRecords.Epoch epoch,
      MaintenanceActivation activation,String digest)throws IOException {
    return issued(root,epoch,activation,digest,LinuxInodeSecurity.create(),new StartupPermitFiles.NioIo());
  }
  static StartupPermitRecords.Permit issued(OwnedTransferDirectory root, StartupPermitRecords.Epoch epoch,
      MaintenanceActivation activation,String digest,InodeSecurityCalls security,StartupPermitFiles.Io io)throws IOException {
    require(root!=null && epoch!=null && activation!=null && digest!=null && security!=null && io!=null);
    require(epoch.state()==StartupPermitRecords.State.ISSUED && epoch.activation().equals(activation));
    var files=new StartupPermitFiles(root,security,io,java.util.UUID::randomUUID);
    require(epoch.equals(files.current()));var permit=files.readIssued();
    require(permit.releaseDigest().equals(digest) && permit.boot().equals(epoch.boot())
        && permit.epoch().equals(epoch.epoch()) && permit.activation().equals(activation));
    var owner=new StartupLaunchFiles(root,security,io,epoch).readOwner();
    require(owner.boot().equals(epoch.boot()) && owner.epoch().equals(epoch.epoch())
        && owner.run().equals(activation.run().id()) && owner.activation().equals(activation.id())
        && owner.cutoff().equals(activation.run().cutoff()) && owner.cleanup().isEmpty()
        && owner.morning().invocation().equals("bbb6dc1276a4459da65143db3e4ee3f0")
        && owner.morning().pid()==5872 && owner.morning().startTicks()==380665);
    require(epoch.equals(files.current()) && permit.equals(files.readIssued()));
    root.atDirectory(p->{
      var names=new java.util.HashSet<String>();
      try(var entries=java.nio.file.Files.newDirectoryStream(p)){for(var entry:entries)names.add(entry.getFileName().toString());}
      require(Pg513SingleApiIntent.namespace(names,epoch.epoch().toString(),true));return Boolean.TRUE;
    });
    new BackupStartIntentFiles(root,security,io,()->require(epoch.equals(files.current())),epoch.epoch()+".API.start.intent").observeQuarantine();
    return permit;
  }
  public static StartupPermitRecords.Epoch invalid(StartupPermitRecords.Epoch issued)throws IOException {
    require(issued!=null && issued.state()==StartupPermitRecords.State.ISSUED);
    return new StartupPermitRecords.Epoch(StartupPermitRecords.State.INVALID,issued.boot(),issued.epoch(),issued.activation(),Optional.empty());
  }
  /** Uncertainty before unlink preserves the existing marker, regardless of the completed revoke step. */
  public static void isolate(OwnedTransferDirectory root, StartupPermitRecords.Epoch original,
      MaintenanceActivation activation,String digest,Pg513SingleApiIntent.Gate currentMA)throws IOException {
    require(root!=null && original!=null && currentMA!=null);currentMA.verify();
    var current=new StartupPermitFiles(root,LinuxInodeSecurity.create()).current();
    if(current.equals(original)) {
      issued(root,original,activation,digest);
      root.atDirectory(p->{
        var names=new java.util.HashSet<String>();
        try(var list=java.nio.file.Files.newDirectoryStream(p)){for(var leaf:list)names.add(leaf.getFileName().toString());}
        require(Pg513SingleApiIntent.namespace(names,original.epoch().toString(),true));
        return Boolean.TRUE;
      });
      currentMA.verify();return;
    }
    require(current.equals(invalid(original)));
    Pg513SingleApiIntent.quarantine(root,current,activation,digest,currentMA);
  }
}
