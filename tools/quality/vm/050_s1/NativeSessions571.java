import java.io.File;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Objects;
import org.jacoco.core.tools.ExecFileLoader;

/** BUG861/YKT630: exactly one current Bootstrap session under its own PID1 time window. */
public final class NativeSessions571 {
  private NativeSessions571() {}
  public static void main(String[] args)throws Exception {
    if(args==null || args.length!=3 || Arrays.stream(args).anyMatch(Objects::isNull))
      throw new IllegalArgumentException("one stream and bounds required");
    long lower=Long.parseLong(args[0]),upper=Long.parseLong(args[1]);
    if(lower<=0 || upper<lower)throw new IllegalArgumentException("fixed cohort bounds required");
    var loader=new ExecFileLoader();loader.load(new File(args[2]));
    var sessions=loader.getSessionInfoStore().getInfos();
    if(sessions.size()!=1)throw new IllegalStateException("single current session required");
    var session=sessions.getFirst();
    if(session.getStartTimeStamp()<lower || session.getDumpTimeStamp()<session.getStartTimeStamp()
       || session.getDumpTimeStamp()>upper)throw new IllegalStateException("native outside current cohort");
    var hash=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(session.getId().getBytes(StandardCharsets.UTF_8)));
    System.out.println("{\"index\":0,\"sessions\":1,\"sessionIdSha256\":\""+hash+"\",\"startMs\":"+session.getStartTimeStamp()+",\"dumpMs\":"+session.getDumpTimeStamp()+"}");
  }
}
