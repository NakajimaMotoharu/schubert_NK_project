import dev.codex.schubert.nk.storage.*;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.util.*;

/** SSC174/BUG544: independent public nonempty fixture; operator tests, not Production PT count. */
public final class Pg444TransferPreservationTest {
  static int count;
  interface Work {void run() throws Exception;}
  static void reject(Work work) throws Exception {
    try {work.run();throw new AssertionError("unsafe observation accepted");}
    // Strict LocalDate rejects an invalid calendar date with DateTimeException, not IAE.
    // It remains a negative result; NPE/unknown runtime errors are deliberately not accepted.
    catch(IOException | IllegalStateException | IllegalArgumentException | java.time.DateTimeException expected){count++;}
  }
  static void mode(Path p,String mode) throws IOException {Files.setPosixFilePermissions(p,PosixFilePermissions.fromString(mode));}
  static final class Faults implements DirectoryCalls {
    final DirectoryCalls actual=LinuxDirectoryCalls.create();
    final Set<Integer> entries=new HashSet<>();final Path part;
    boolean mutate,failRead,failClose,primary,closeObserved;
    Faults(Path part){this.part=part;}
    public int openRoot()throws StorageIoException{return actual.openRoot();}
    public int openDirectory(int p,String n)throws StorageIoException{return actual.openDirectory(p,n);}
    public int openEntry(int p,String n)throws StorageIoException {
      if(failRead){primary=true;throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);}
      int fd=actual.openEntry(p,n);entries.add(fd);return fd;
    }
    public int createFile(int p,String n){throw new AssertionError("write during observation");}
    public void createDirectory(int p,String n){throw new AssertionError("mkdir during observation");}
    public void publish(int p,String a,String b){throw new AssertionError("publish during observation");}
    public void unlink(int p,String n){throw new AssertionError("unlink during observation");}
    public void sync(int p){throw new AssertionError("fsync during read-only observation");}
    public void close(int fd)throws StorageIoException {
      boolean entry=entries.remove(fd);actual.close(fd);closeObserved=true;
      if(entry && mutate) {
        mutate=false;try {Files.write(part,new byte[]{7},StandardOpenOption.APPEND);}
        catch(IOException failure){throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);}
      }
      if(failClose && (entry || primary))throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
  public static void main(String[] args)throws Exception {
    Path root=Files.createTempDirectory("pg444-transfer-");mode(root,"rwxr-x---");
    try {
      var attrs=Files.readAttributes(root,"posix:owner,group");
      var identity=new StorageIdentity(((java.nio.file.attribute.UserPrincipal)attrs.get("owner")).getName(),
          ((java.nio.file.attribute.GroupPrincipal)attrs.get("group")).getName());
      var empty=Pg428ColdBootPreparation.transferSnapshot(root,identity);
      if(!empty.keySet().equals(Set.of("")))throw new AssertionError("empty root inventory");count++;
      Path day=Files.createDirectory(root.resolve("20261003"));mode(day,"rwxr-x---");
      String id="00000000-0000-4000-8000-000000000001";
      Path part=Files.write(day.resolve(id+".part"),new byte[0]);mode(part,"rw-r-----");
      byte[] literal=new byte[4800];Arrays.fill(literal,(byte)' ');
      Path ready=Files.write(day.resolve(id+".ready"),literal);mode(ready,"rw-r-----");
      String independentHash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(literal));
      var valid=Pg428ColdBootPreparation.transferSnapshot(root,identity);
      if(!valid.keySet().equals(Set.of("","20261003","20261003/"+id+".part","20261003/"+id+".ready"))
          || !valid.get("20261003/"+id+".ready").endsWith("/"+independentHash)
          || !valid.get("20261003/"+id+".part").endsWith("/e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"))throw new AssertionError("nonempty independent hash/inventory");count++;
      mode(ready,"rw-------");reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity));mode(ready,"rw-r-----");
      Files.write(ready,new byte[]{1});reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity));Files.write(ready,literal);
      mode(day,"rwx------");reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity));mode(day,"rwxr-x---");
      reject(()->Pg428ColdBootPreparation.transferSnapshot(root,new StorageIdentity("nobody","nogroup")));
      Path foreign=Files.write(day.resolve("foreign"),new byte[0]);reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity));Files.delete(foreign);
      Path link=day.resolve("00000000-0000-4000-8000-000000000002.part");
      Files.createSymbolicLink(link,part);reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity));Files.delete(link);
      Files.createLink(link,part);reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity));Files.delete(link);
      var mutation=new Faults(part);mutation.mutate=true;reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity,mutation));
      Files.write(part,new byte[0]);
      var readFailure=new Faults(part);readFailure.failRead=true;reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity,readFailure));
      if(!readFailure.primary || !readFailure.closeObserved)throw new AssertionError("read failure/close observation");count++;
      var closeFailure=new Faults(part);closeFailure.failClose=true;reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity,closeFailure));
      if(!closeFailure.closeObserved)throw new AssertionError("owned close failure observation");count++;
      var both=new Faults(part);both.failRead=both.failClose=true;reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity,both));
      if(!both.primary || !both.closeObserved)throw new AssertionError("primary and close failure distinct");count++;
      reject(()->Pg428ColdBootPreparation.transferSnapshot(null,identity));
      reject(()->Pg428ColdBootPreparation.transferSnapshot(root,null));
      reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity,null));
      Path invalid=Files.createDirectory(root.resolve("20260230"));mode(invalid,"rwxr-x---");
      reject(()->Pg428ColdBootPreparation.transferSnapshot(root,identity));Files.delete(invalid);
      if(!Pg428ColdBootPreparation.transferSnapshot(root,identity).keySet().equals(valid.keySet()))throw new AssertionError("fixtures preserved");count++;
      System.out.println("PG444_TRANSFER_PRESERVATION success=true independentAssertions="+count+" productionTestCount=0");
    }finally {
      // Only this newly created public temporary fixture; do not follow links.
      try(var paths=Files.walk(root)){for(var p:paths.sorted(Comparator.reverseOrder()).toList())Files.delete(p);}
    }
  }
}
