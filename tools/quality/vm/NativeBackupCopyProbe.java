import dev.codex.schubert.nk.api.file.InspectorCredentialLoader;
import dev.codex.schubert.nk.batch.file.BackupDatabaseCopy;
import dev.codex.schubert.nk.batch.platform.BackupArchiveProcess;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;

/** PT-OPS-NATIVE-023: Production copy + actual dedicated dump/list, not full backup/root gate. */
public final class NativeBackupCopyProbe {
  public static void main(String[] args)throws Exception {
    var security=LinuxInodeSecurity.create();
    if(args.length!=0||security.effectiveUid()!=992||!System.getProperty("user.name").equals("schubert-backup")||
        !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new AssertionError("isolated dedicated worker required");
    var calls=LinuxDirectoryCalls.create();
    var process=new BackupArchiveProcess(security);
    Path output=Path.of("/srv/schubert-nk/backup/pgpt-db-308");
    Files.createDirectory(output,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    Files.createFile(output.resolve("schubert_nk.dump"),PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    var location=ServiceCredentialLocation.read(System.getenv());
    try(var credential=OwnedTransferDirectory.open(calls,location.directory());
        var runtime=OwnedTransferDirectory.open(calls,Path.of("/run/pgpt-backup-308"));
        var dumps=OwnedTransferDirectory.open(calls,output)) {
      byte[] raw=new InspectorCredentialLoader(credential,security).readBackupPgpass();
      new BackupDatabaseCopy(runtime,security,992,977).dump(raw,UUID.randomUUID(),p->
          dumps.atExistingEntryHandle("schubert_nk.dump",d->{process.dump(d,p,992);return true;}));
      for(byte value:raw)if(value!=0)throw new AssertionError("owned heap material not cleared");
    }
    if(Files.size(output.resolve("schubert_nk.dump"))<=0)throw new AssertionError("dump empty");
    try(var files=Files.list(Path.of("/run/pgpt-backup-308"))) {
      if(files.findAny().isPresent())throw new AssertionError("material not removed");
    }
    System.out.println("PT-OPS-NATIVE-023 PASS actualDedicatedUnit=true productionCopy=true actualDumpAndList=true copyRetired=true fullBackup=false fullGate=false");
  }
}
