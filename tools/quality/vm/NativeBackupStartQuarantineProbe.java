import dev.codex.schubert.nk.batch.platform.BackupArchiveProcess;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.List;

/** PT-OPS-NATIVE-024: masked fixed age binary forces unconfirmed native pipeline start. */
public final class NativeBackupStartQuarantineProbe {
  public static void main(String[] args)throws Exception {
    var security=LinuxInodeSecurity.create();
    if(args.length!=0||security.effectiveUid()!=0||!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new AssertionError("isolated root probe required");
    Path fixture=Path.of("/var/lib/schubert-nk/pgpt-backup-307");
    Files.createDirectory(fixture,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    Files.writeString(fixture.resolve("public.txt"),"PUBLIC_QUARANTINE_FIXTURE\n",StandardOpenOption.CREATE_NEW);
    Files.createFile(fixture.resolve("credentials.tar.age"),PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    var calls=LinuxDirectoryCalls.create();
    try(var source=OwnedTransferDirectory.open(calls,fixture);
        var credential=OwnedTransferDirectory.open(calls,Path.of("/etc/schubert-nk/credentials"))) {
      System.out.println("PT-OPS-NATIVE-024 ENTER publicFixture=true expectedUnitTimeout=true fullGate=false");
      source.atDirectory(dir->source.atExistingEntryHandle("credentials.tar.age",out->credential.atExistingEntryHandle("backup-recipient",recipient->{
        new BackupArchiveProcess(security).credentials(dir,out,recipient,List.of("public.txt"));
        Files.writeString(fixture.resolve("unexpected-return"),"NON_SUCCESS_BOUNDARY_BROKEN\n",StandardOpenOption.CREATE_NEW);
        return true;
      })));
    }
    throw new AssertionError("unconfirmed start must not return");
  }
}
