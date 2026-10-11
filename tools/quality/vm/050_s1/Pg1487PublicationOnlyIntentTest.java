package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Public handwritten bytes + real FD/synthetic UID/tmpfs, no expired owner/Pair/worker. */
public final class Pg1487PublicationOnlyIntentTest {
  static int checks;
  static void check(boolean value){checks++;if(!value)throw new AssertionError("publication-only independent oracle");}
  static final String E="31100027-4444-4333-8444-555555555555";
  static final String B="boot_id=31100027-3333-4333-8444-555555555555\nepoch_id="+E+"\nrun_id=31100027-2222-4333-8444-555555555555\ncutoff_utc=2026-09-27T15:00:00.000000Z\nactivation_id=31100027-6666-4777-8888-999999999999\n";
  static final String CURRENT="NKEPOCH1\nstate=INVALID\n"+B+"permit_sha256=-\n";
  static final String PERMIT="NKPERMIT1\n"+B+"broker_invocation_id="+"2".repeat(32)+"\nrelease_sha256="+"b".repeat(64)+"\napi_config_sha256="+"c".repeat(64)+"\nweb_config_sha256="+"d".repeat(64)+"\nroots_sha256="+"e".repeat(64)+"\nprestart_steps_sha256="+"f".repeat(64)+"\n";
  static final class Fixture implements AutoCloseable,StartupPermitFiles.Io {
    final BackupPublicationFixture f;
    final StartupPermitRecords.Epoch epoch;
    Fixture(Path temporary)throws Exception {
      f=new BackupPublicationFixture(temporary);Files.delete(f.child);
      f.metadata=(role,v)->{v.put("uid",0);v.put("gid",0);};
      put("epoch.current",CURRENT);put(E+".permit",PERMIT);put("permit-start.intent","");
      epoch=StartupPermitRecords.readEpoch(CURRENT.getBytes(java.nio.charset.StandardCharsets.US_ASCII));
      f.events.clear();f.counts.clear();f.position=0;
    }
    void put(String name,String bytes)throws IOException{Files.writeString(f.parent.resolve(name),bytes);Files.setAttribute(f.parent.resolve(name),"unix:mode",0600);}
    void immutable()throws IOException {
      check(Files.readString(f.parent.resolve("epoch.current")).equals(CURRENT));
      check(Files.readString(f.parent.resolve(E+".permit")).equals(PERMIT));
      for(String name:List.of(E+".owner",E+".API.launch",E+".WEB.launch",E+".API.start.intent",E+".WEB.start.intent"))check(!Files.exists(f.parent.resolve(name)));
    }
    void retire(Pg1487PublicationOnlyIntent.Gate full,Pg1487PublicationOnlyIntent.Gate ma)throws Exception {
      Pg1487PublicationOnlyIntent.retire(f.root,epoch,epoch.activation(),"b".repeat(64),"2".repeat(32),full,ma,f,this);
    }
    public Map<String,Object> attributes(Path p)throws IOException{return f.attributes(p);}
    public String filesystem(Path p){return f.filesystem(p);}
    public SeekableByteChannel open(Path p)throws IOException{return f.open(p);}
    public InspectorEnvironmentPublisher.Writer openWriter(Path p)throws IOException{return f.openWriter(p);}
    public void replace(Path directory,String part,String current){throw new AssertionError("epoch rewrite forbidden");}
    public MessageDigest digest()throws NoSuchAlgorithmException{return MessageDigest.getInstance("SHA-256");}
    public void close()throws StorageIoException{f.track=false;f.close();}
  }
  public static void main(String[] ignored)throws Exception {
    var two=Set.of("epoch.current",E+".permit");var three=new HashSet<>(two);three.add("permit-start.intent");
    check(Pg1487PublicationOnlyIntent.namespace(two,E,false));check(Pg1487PublicationOnlyIntent.namespace(three,E,true));
    check(!Pg1487PublicationOnlyIntent.namespace(two,E,true));check(!Pg1487PublicationOnlyIntent.namespace(three,E,false));
    check(!Pg1487PublicationOnlyIntent.namespace(null,E,true));check(!Pg1487PublicationOnlyIntent.namespace(three,null,true));
    for(String bad:List.of("","foreign","00000000-0000-0000-0000-000000000000",E.replace("31100027","3110002a").toUpperCase(java.util.Locale.ROOT)))check(!Pg1487PublicationOnlyIntent.namespace(three,bad,true));
    Path temporary=Files.createTempDirectory(Path.of("/dev/shm"),"pg1487-synthetic-");
    int positions;
    try(var v=new Fixture(temporary)) {
      v.retire(v::immutable,()->{});v.immutable();check(!Files.exists(v.f.parent.resolve("permit-start.intent")));
      check(v.f.events.contains("unlink")&&v.f.events.contains("sync"));positions=v.f.position;
    }
    for(int fault=1;fault<=positions;fault++)try(var v=new Fixture(temporary)) {
      int point=fault;
      v.f.hook=(name,n)->{if(!name.equals("clock")&&!name.equals("effectiveUid")&&v.f.position+1==point)v.f.faults.put(name+"#"+n,new StorageIoException(StorageIoException.Reason.UNAVAILABLE));};
      try{v.retire(v::immutable,()->{});throw new AssertionError("fault accepted");}catch(IOException expected){check(true);}
      v.f.faultAt=0;v.immutable();
      if(v.f.events.contains("unlink"))check(Files.exists(v.f.parent.resolve("permit-start.intent")));
    }
    for(String name:List.of("foreign",E+".owner",E+".API.launch",E+".WEB.start.intent"))try(var v=new Fixture(temporary)) {
      v.put(name,"");try{v.retire(()->{},()->{});throw new AssertionError("foreign namespace accepted");}catch(IOException expected){check(true);}
      check(!v.f.events.contains("unlink"));check(Files.exists(v.f.parent.resolve("permit-start.intent")));
      check(Files.readString(v.f.parent.resolve("epoch.current")).equals(CURRENT));check(Files.readString(v.f.parent.resolve(E+".permit")).equals(PERMIT));
    }
    try(var v=new Fixture(temporary)) {
      v.put("permit-start.intent","nonempty");try{v.retire(v::immutable,()->{});throw new AssertionError("nonempty accepted");}catch(IOException expected){check(true);}
      check(Files.readString(v.f.parent.resolve("permit-start.intent")).equals("nonempty"));v.immutable();
    }
    for(boolean ma:new boolean[]{false,true})try(var v=new Fixture(temporary)) {
      Pg1487PublicationOnlyIntent.Gate fail=()->{throw new IOException("independent missing owner/whole-stop proof");};
      try{v.retire(ma?()->{}:fail,ma?fail:()->{});throw new AssertionError("missing proof accepted");}catch(IOException expected){check(true);}
      check(!v.f.events.contains("unlink"));v.immutable();
    }
    try(var v=new Fixture(temporary)) {
      final boolean[] failed={false};
      try {
        v.retire(()->{v.immutable();if(!Files.exists(v.f.parent.resolve("permit-start.intent"))&&!failed[0]){failed[0]=true;throw new IOException("independent post-unlink uncertainty");}},()->{});
        throw new AssertionError("post uncertainty accepted");
      } catch(IOException expected){check(true);}
      check(failed[0]);check(Files.exists(v.f.parent.resolve("permit-start.intent")));v.immutable();
    }
    System.out.println("PG1487_PUBLICATION_ONLY independentAssertions="+checks+" faultPositions="+positions+" realFD=true syntheticRootTmpfs=true businessMutations0=true");
  }
}
