import java.io.File;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import org.jacoco.core.tools.ExecFileLoader;

/** Current ordinary cohort diagnostic. Session identity is hashed, not exported raw. */
public final class NativeSessions561 {
  private NativeSessions561() {}
  public static void main(String[] args)throws Exception {
    if(args==null || args.length!=11)throw new IllegalArgumentException("nine streams and bounds required");
    long lower=Long.parseLong(args[0]),upper=Long.parseLong(args[1]);
    if(lower<=0 || upper<lower)throw new IllegalArgumentException("fixed cohort bounds required");
    for(int i=2;i<args.length;i++){
      var loader=new ExecFileLoader();loader.load(new File(args[i]));
      var sessions=loader.getSessionInfoStore().getInfos();
      if(sessions.size()!=1)throw new IllegalStateException("single current session required");
      var s=sessions.getFirst();
      if(s.getStartTimeStamp()<lower || s.getDumpTimeStamp()<s.getStartTimeStamp() || s.getDumpTimeStamp()>upper)
        throw new IllegalStateException("native outside current cohort");
      var hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getId().getBytes(StandardCharsets.UTF_8)));
      System.out.println("{\"index\":"+(i-2)+",\"sessions\":1,\"sessionIdSha256\":\""+hash+"\",\"startMs\":"+s.getStartTimeStamp()+",\"dumpMs\":"+s.getDumpTimeStamp()+"}");
    }
  }
}
