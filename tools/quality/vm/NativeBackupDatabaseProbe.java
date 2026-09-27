import dev.codex.schubert.nk.api.file.InspectorCredentialLoader;
import dev.codex.schubert.nk.batch.platform.BackupArchiveProcess;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;

/** PT-OPS-NATIVE-022: actual dedicated Unit/systemd credential/libpq dump, not full backup. */
public final class NativeBackupDatabaseProbe {
  public static void main(String[] args)throws Exception {
    var security=LinuxInodeSecurity.create();
    if(args.length!=0||security.effectiveUid()!=992||!System.getProperty("user.name").equals("schubert-backup")||
        !Files.readString(Path.of("/var/lib/cloud/data/instance-id")).trim().equals("pgpt-r2-20260927-01"))throw new AssertionError("isolated dedicated worker required");
    var calls=LinuxDirectoryCalls.create();
    var process=new BackupArchiveProcess(security);
    Path output=Path.of("/srv/schubert-nk/backup/pgpt-db-305");
    Files.createDirectory(output,PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rwx------")));
    for(String name:List.of("negative.dump","schubert_nk.dump"))Files.createFile(output.resolve(name),PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    var location=ServiceCredentialLocation.read(System.getenv());
    try(var credential=OwnedTransferDirectory.open(calls,location.directory());
        var runtime=OwnedTransferDirectory.open(calls,Path.of("/run/pgpt-backup-305"));
        var dumps=OwnedTransferDirectory.open(calls,output)) {
      int sourceMode=credential.atExistingEntryHandle("backup-pgpass",p->(int)Files.getAttribute(p,"unix:mode"))&0777;
      if(sourceMode!=0440)throw new AssertionError("expected actual systemd ACL0440 fixture");
      boolean refused=false;
      try {credential.atExistingEntryHandle("backup-pgpass",p->dumps.atExistingEntryHandle("negative.dump",d->{process.dump(d,p,992);return true;}));}
      catch(IOException expected){refused=true;}
      if(!refused)throw new AssertionError("libpq must reject group-readable source");
      byte[] secret=new InspectorCredentialLoader(credential,security).readBackupPgpass();
      UUID material=UUID.randomUUID();
      try {
        runtime.createPrivatePart(material,p->{
          if(((int)Files.getAttribute(p,"unix:mode")&0777)!=0600||(int)Files.getAttribute(p,"unix:uid")!=992||security.accessAcl(p,44).length!=0||security.readOnlyFilesystem(p))throw new AssertionError("private copy admission failed");
          try(var channel=FileChannel.open(p,StandardOpenOption.WRITE)){ByteBuffer bytes=ByteBuffer.wrap(secret);while(bytes.hasRemaining())if(channel.write(bytes)<=0)throw new IOException("copy failed");channel.force(true);}
          Arrays.fill(secret,(byte)0);
          dumps.atExistingEntryHandle("schubert_nk.dump",d->{process.dump(d,p,992);return true;});
          // Only positive return guarantees all children/stdio have closed. Failure preserves copy.
          try(var channel=FileChannel.open(p,StandardOpenOption.WRITE)){ByteBuffer zero=ByteBuffer.allocate((int)channel.size());while(zero.hasRemaining())if(channel.write(zero)<=0)throw new IOException("erase failed");channel.force(true);}
          return true;
        });
        runtime.deletePart(material);
        runtime.atDirectory(p->{try(var directory=FileChannel.open(p,StandardOpenOption.READ)){directory.force(true);}return true;});
      } finally {Arrays.fill(secret,(byte)0);}
    }
    if(Files.size(output.resolve("schubert_nk.dump"))<=0)throw new AssertionError("dump empty");
    try(var files=Files.list(Path.of("/run/pgpt-backup-305"))) {
      if(files.findAny().isPresent())throw new AssertionError("private material not removed");
    }
    System.out.println("PT-OPS-NATIVE-022 PASS dedicatedUid=true dedicatedDatabaseRole=true actualSystemdCredential=true libpq0440Refused=true tmpfs0600=true actualDumpAndList=true secretCopyRemoved=true fullBackup=false fullGate=false");
  }
}
