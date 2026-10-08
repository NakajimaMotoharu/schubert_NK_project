import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.HexFormat;
import org.jacoco.core.data.SessionInfo;
import org.jacoco.core.tools.ExecFileLoader;

/** Independent JaCoCo vendor SessionInfo vectors, not Production-generated expectations. */
public final class NativeSessions571Test {
  public static void main(String[] args)throws Exception {
    for(String[] value:new String[][]{null,new String[]{},new String[]{"1","2"},new String[]{"1","2",null},new String[]{"1","2","x","extra"}}){
      try{NativeSessions571.main(value);throw new AssertionError("bad CLI admitted");}
      catch(IllegalArgumentException expected){/* fixed rejection, no NPE */}
    }
    var directory=Files.createTempDirectory("pg571-session-");var file=directory.resolve("literal.exec");
    try{
      for(long[] times:new long[][]{{6000,7000},{4999,7000},{6000,5999},{6000,9001}}){
        var loader=new ExecFileLoader();loader.getSessionInfoStore().visitSessionInfo(new SessionInfo("independent-literal",times[0],times[1]));loader.save(file.toFile(),false);
        if(times[0]==6000 && times[1]==7000){
          var old=System.out;var buffer=new ByteArrayOutputStream();
          try{System.setOut(new PrintStream(buffer,true,StandardCharsets.UTF_8));NativeSessions571.main(new String[]{"5000","9000",file.toString()});}finally{System.setOut(old);}
          var hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest("independent-literal".getBytes(StandardCharsets.UTF_8)));
          var expected="{\"index\":0,\"sessions\":1,\"sessionIdSha256\":\""+hash+"\",\"startMs\":6000,\"dumpMs\":7000}\n";
          if(!buffer.toString(StandardCharsets.UTF_8).equals(expected))throw new AssertionError("literal session mismatch");
        }else{
          try{NativeSessions571.main(new String[]{"5000","9000",file.toString()});throw new AssertionError("outside window admitted");}catch(IllegalStateException expected){/* reject */}
        }
      }
      for(int count:new int[]{0,2}){
        var loader=new ExecFileLoader();for(int n=0;n<count;n++)loader.getSessionInfoStore().visitSessionInfo(new SessionInfo("literal"+n,6000,7000));loader.save(file.toFile(),false);
        try{NativeSessions571.main(new String[]{"5000","9000",file.toString()});throw new AssertionError("multiple sessions admitted");}catch(IllegalStateException expected){/* reject */}
      }
      for(String[] bounds:new String[][]{{"0","9000"},{"9000","5000"},{"x","9000"}}){
        try{NativeSessions571.main(new String[]{bounds[0],bounds[1],file.toString()});throw new AssertionError("bad bounds admitted");}catch(IllegalArgumentException expected){/* reject */}
      }
    }finally{Files.deleteIfExists(file);Files.delete(directory);}
    System.out.println("PG571_SINGLE_SESSION_ORACLE literalBoundsArityNullNegative=true productionPT0=true");
  }
}
