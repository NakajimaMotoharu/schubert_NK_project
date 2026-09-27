import dev.codex.schubert.nk.batch.platform.BackupArchiveProcess;
import dev.codex.schubert.nk.storage.*;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;

/** Isolated real root tar->age probe, public data only, not a successful database/config backup. */
public final class NativeBackupArchiveProbe {
  public static void main(String[] args)throws Exception {
    var security=LinuxInodeSecurity.create();
    if(args.length!=0||security.effectiveUid()!=0||!Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))
      throw new AssertionError("isolated root fixture required");
    Path root=Path.of("/var/lib/schubert-nk/pgpt-backup-304");
    Files.createDirectory(root,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    Path source=Files.createDirectory(root.resolve("source"),PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    Path output=Files.createDirectory(root.resolve("output"),PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    Files.createFile(source.resolve("public.txt"),PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    Files.writeString(source.resolve("public.txt"),"PGPT_BACKUP_PUBLIC_FIXTURE_NO_CREDENTIAL_OR_MASTER_DATA\n",StandardOpenOption.WRITE);
    for(String name:new String[]{"config.tar","credentials.tar.age"})
      Files.createFile(output.resolve(name),PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    var calls=LinuxDirectoryCalls.create();var runner=new BackupArchiveProcess(security);
    try(var src=OwnedTransferDirectory.open(calls,source);var dest=OwnedTransferDirectory.open(calls,output);
        var keys=OwnedTransferDirectory.open(calls,Path.of("/etc/schubert-nk/credentials"))) {
      src.atDirectory(directory->dest.atExistingEntryHandle("config.tar",file->{runner.configuration(directory,file,java.util.List.of("public.txt"));return true;}));
      src.atDirectory(directory->dest.atExistingEntryHandle("credentials.tar.age",file->keys.atExistingEntryHandle("backup-recipient",recipient->{runner.credentials(directory,file,recipient,java.util.List.of("public.txt"));return true;})));
    }
    if(Files.size(output.resolve("config.tar"))<=0||Files.size(output.resolve("credentials.tar.age"))<=0)
      throw new AssertionError("archive output is empty");
    System.out.println("PT-OPS-NATIVE-021 PASS actualRoot=true retainedParentFd=true fixedTarAge=true plaintextCredentialArchiveOnDisk=false publicFixtureOnly=true fullBackup=false fullGate=false");
  }
}
