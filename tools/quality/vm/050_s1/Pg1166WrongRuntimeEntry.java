package dev.codex.schubert.nk.batch.file;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
/** SSC260/PT-DEP-1166002: single typed held-entry retirement, never directory repair. */
public final class Pg1166WrongRuntimeEntry {
  private Pg1166WrongRuntimeEntry() {}
  static final String NAME="pg1160-once-resume.conf";
  @FunctionalInterface public interface Verify {void run()throws IOException;}
  interface Io {Map<String,Object> metadata(Path p)throws IOException;byte[] read(Path p)throws IOException;}
  static void require(boolean v)throws IOException{if(!v)throw new IOException("fixed wrong runtime entry refused");}
  public static void retire(OwnedTransferDirectory root,byte[] expected,Verify verify)throws IOException {
    retire(root,expected,verify,new Io(){
      public Map<String,Object> metadata(Path p)throws IOException{return Map.copyOf(Files.readAttributes(p,"unix:dev,ino,uid,gid,mode,nlink,size,lastModifiedTime,ctime"));}
      public byte[] read(Path p)throws IOException{return Files.readAllBytes(p);}
    });
  }
  static void retire(OwnedTransferDirectory root,byte[] expected,Verify verify,Io io)throws IOException {
    require(root!=null && expected!=null && expected.length==647 && verify!=null && io!=null);
    byte[] frozen=expected.clone();
    root.atExistingEntryHandle(NAME,held->{
      var before=io.metadata(held);
      require(before!=null && before.keySet().equals(java.util.Set.of("dev","ino","uid","gid","mode","nlink","size","lastModifiedTime","ctime"))
        && Integer.valueOf(0).equals(before.get("uid")) && Integer.valueOf(0).equals(before.get("gid"))
        && Integer.valueOf(0100644).equals(before.get("mode")) && Integer.valueOf(1).equals(before.get("nlink")) && Long.valueOf(647).equals(before.get("size")));
      require(Arrays.equals(frozen,io.read(held)) && before.equals(io.metadata(held)));
      verify.run();require(before.equals(io.metadata(held)) && Arrays.equals(frozen,io.read(held)));
      root.unlinkEntry(NAME);root.sync();return Boolean.TRUE;
    });
  }
}
