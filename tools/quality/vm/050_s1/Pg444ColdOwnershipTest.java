import dev.codex.schubert.nk.batch.file.*;
import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.*;

/** SSC174: independent inode/exception/all-backup fixtures; no runtime authorization. */
public final class Pg444ColdOwnershipTest {
  static int count;
  interface Work {void run() throws Exception;}
  static void reject(Work work) throws Exception {
    try {work.run();throw new AssertionError("invalid ownership accepted");}
    catch(IOException | IllegalArgumentException | IllegalStateException expected){count++;}
  }
  public static void main(String[] args)throws Exception {
    Path root=Files.createTempDirectory("pg444-ownership-");
    try {
      var lock=Files.write(root.resolve("test.lock"),new byte[0]);
      Files.setPosixFilePermissions(lock,PosixFilePermissions.fromString("rw-------"));
      try(var owner=OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),root)) {
        owner.atExistingEntryHandle("test.lock",held->{
          int fd=Integer.parseInt(held.getFileName().toString());
          var identity=Files.readAttributes(held,"unix:uid,gid,mode,nlink,dev,ino,ctime,lastModifiedTime,size");
          var admission=new StartupAdmissionFile.Admission(fd,(Long)identity.get("dev"),(Long)identity.get("ino"));
          try {
            Pg428ColdBootPreparation.admissionIdentity(admission,identity);count++;
            for(String key:identity.keySet()) {
              var changed=new HashMap<>(identity);changed.put(key,null);
              reject(()->Pg428ColdBootPreparation.admissionIdentity(admission,changed));
            }
            reject(()->Pg428ColdBootPreparation.admissionIdentity(null,identity));
            reject(()->Pg428ColdBootPreparation.admissionIdentity(admission,null));
            reject(()->Pg428ColdBootPreparation.admissionIdentity(new StartupAdmissionFile.Admission(-1,admission.device(),admission.inode()),identity));
            reject(()->Pg428ColdBootPreparation.admissionIdentity(new StartupAdmissionFile.Admission(fd,admission.device(),admission.inode()+1),identity));
            // Named replacement while old held inode remains open is a distinct identity.
            Files.move(lock,root.resolve("retained.lock"));Files.write(lock,new byte[0]);
            var replaced=Files.readAttributes(lock,"unix:uid,gid,mode,nlink,dev,ino,ctime,lastModifiedTime,size");
            reject(()->Pg428ColdBootPreparation.admissionIdentity(admission,replaced));
          }catch(IOException failure){throw failure;}
          catch(Exception failure){throw new IOException("public fixture failed",failure);}
          return Boolean.TRUE;
        });
      }
      var checked=new Exception("DO_NOT_LOG_PRIVATE_MESSAGE");
      try {Pg428ColdBootPreparation.checked(()->{throw checked;});throw new AssertionError("checked failure erased");}
      catch(IOException wrapped){if(wrapped.getCause()!=checked)throw new AssertionError("primary cause lost");count++;}
      var io=new IOException("DO_NOT_LOG_PRIVATE_IO");
      try {Pg428ColdBootPreparation.checked(()->{throw io;});throw new AssertionError("IO accepted");}
      catch(IOException actual){if(actual!=io)throw new AssertionError("IO identity lost");count++;}
      var unknown=new IllegalArgumentException("DO_NOT_LOG_UNKNOWN");
      try {Pg428ColdBootPreparation.checked(()->{throw unknown;});throw new AssertionError("unknown accepted");}
      catch(IllegalArgumentException actual){if(actual!=unknown)throw new AssertionError("unknown identity lost");count++;}
      try {Pg428ColdBootPreparation.checked(()->{throw new InterruptedException();});throw new AssertionError("interrupt accepted");}
      catch(IOException actual){if(!(actual.getCause() instanceof InterruptedException) || !Thread.interrupted())throw new AssertionError("interrupt lost");count++;}
      if(Pg428ColdBootPreparation.checked(()->Boolean.TRUE)!=Boolean.TRUE)throw new AssertionError("positive callback");count++;
      Path backup=Files.createDirectory(root.resolve("backup"));
      Files.write(backup.resolve("noncanonical.public.fixture"),new byte[]{'a','b','c'});
      var inventory=Pg428ColdBootPreparation.backupPass(backup);
      if(!inventory.keySet().equals(Set.of("","noncanonical.public.fixture"))
          || !inventory.get("noncanonical.public.fixture").endsWith("/ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"))throw new AssertionError("all-backup independent SHA");count++;
      Path child=Files.createDirectory(backup.resolve("retained"));Files.write(child.resolve("extra.fixture"),new byte[0]);
      if(!Pg428ColdBootPreparation.backupPass(backup).keySet().equals(Set.of("","noncanonical.public.fixture","retained","retained/extra.fixture")))throw new AssertionError("nested backup coverage");count++;
      Path link=backup.resolve("foreign.link");Files.createSymbolicLink(link,root);reject(()->Pg428ColdBootPreparation.backupPass(backup));Files.delete(link);
      Files.createLink(link,backup.resolve("noncanonical.public.fixture"));reject(()->Pg428ColdBootPreparation.backupPass(backup));Files.delete(link);
      reject(()->Pg428ColdBootPreparation.emptyRoot(backup));
      System.out.println("PG444_COLD_OWNERSHIP success=true independentAssertions="+count+" productionTestCount=0");
    }finally {
      // Only this new synthetic temporary directory, without following links.
      try(var paths=Files.walk(root)){for(var p:paths.sorted(Comparator.reverseOrder()).toList())Files.delete(p);}
    }
  }
}
