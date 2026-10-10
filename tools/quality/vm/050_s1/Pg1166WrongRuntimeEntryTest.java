package dev.codex.schubert.nk.batch.file;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
/** Independent public647 vector, real FD/all faults, synthetic Root; VM0/PTProduction0. */
public final class Pg1166WrongRuntimeEntryTest {
  static int checks;
  static void check(boolean v){checks++;if(!v)throw new AssertionError("wrong runtime independent oracle");}
  static final byte[] GOLD="x".repeat(647).getBytes(java.nio.charset.StandardCharsets.US_ASCII);
  static final class Fixture implements AutoCloseable,Pg1166WrongRuntimeEntry.Io {
    final BackupPublicationFixture f;boolean wrong;
    Fixture(Path temp)throws Exception {
      f=new BackupPublicationFixture(temp);Files.delete(f.child);Files.write(f.parent.resolve(Pg1166WrongRuntimeEntry.NAME),GOLD);
      Files.setAttribute(f.parent.resolve(Pg1166WrongRuntimeEntry.NAME),"unix:mode",0644);
      f.metadata=(role,m)->{m.put("uid",0);m.put("gid",0);};f.position=0;f.counts.clear();f.events.clear();
    }
    public Map<String,Object> metadata(Path p)throws IOException{
      var all=f.attributes(p);var m=new HashMap<String,Object>();
      for(String k:List.of("dev","ino","uid","gid","mode","nlink","size","lastModifiedTime","ctime"))m.put(k,all.get(k));
      if(wrong)m.put("mode",0100600);return m;
    }
    public byte[] read(Path p)throws IOException{f.point("readWrongRuntime");return Files.readAllBytes(p);}
    void retire()throws IOException{Pg1166WrongRuntimeEntry.retire(f.root,GOLD,()->f.point("verifyOwner"),this);}
    public void close()throws dev.codex.schubert.nk.storage.StorageIoException {f.close();}
  }
  public static void main(String[] ignored)throws Exception {
    Path temp=Files.createTempDirectory("pg1166-runtime-synthetic-");int positions;
    try(var f=new Fixture(temp)){f.retire();positions=f.f.position;check(!Files.exists(f.f.parent.resolve(Pg1166WrongRuntimeEntry.NAME)));check(f.f.events.contains("unlink") && f.f.events.contains("sync"));}
    for(int position=1;position<=positions;position++)try(var f=new Fixture(temp)){
      int fault=position;f.f.hook=(name,n)->{if(!name.equals("clock") && !name.equals("effectiveUid") && f.f.position+1==fault)f.f.faults.put(name+"#"+n,new dev.codex.schubert.nk.storage.StorageIoException(dev.codex.schubert.nk.storage.StorageIoException.Reason.UNAVAILABLE));};
      try{f.retire();throw new AssertionError("fault accepted");}catch(IOException expected){check(true);}
    }
    try(var f=new Fixture(temp)){f.wrong=true;try{f.retire();throw new AssertionError("wrong mode accepted");}catch(IOException expected){check(Files.exists(f.f.parent.resolve(Pg1166WrongRuntimeEntry.NAME)));}}
    try(var f=new Fixture(temp)){byte[] wrong=GOLD.clone();wrong[0]='y';try{Pg1166WrongRuntimeEntry.retire(f.f.root,wrong,()->{},f);throw new AssertionError("wrong byte accepted");}catch(IOException expected){check(Files.exists(f.f.parent.resolve(Pg1166WrongRuntimeEntry.NAME)));}}
    try(var f=new Fixture(temp)){try{Pg1166WrongRuntimeEntry.retire(f.f.root,null,()->{},f);throw new AssertionError("null accepted");}catch(IOException expected){check(Files.exists(f.f.parent.resolve(Pg1166WrongRuntimeEntry.NAME)));}}
    System.out.println("PG1166_TYPED_RUNTIME_ORACLE assertions="+checks+" faultPositions="+positions+" realFD=true syntheticRoot=true VM0=true productionPT0=true");
  }
}
