import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Independent literal/time-bound exec metadata oracle; no agent or runtime attach. */
public final class NativeSessions474 {
  public static void main(String[] args)throws Exception{
    if(args.length!=10)throw new IllegalArgumentException("eight fresh files and capture bounds required");
    long start=Long.parseLong(args[8]);long end=Long.parseLong(args[9]);
    String[] expected={null,null,null,null,"API-354cbffa0db149ae88dd59c02a98f157-root","WEB-9cfb59cef62d4a0498a3702172803ca2-root","API-354cbffa0db149ae88dd59c02a98f157-ordinary","WEB-9cfb59cef62d4a0498a3702172803ca2-ordinary"};
    for(int i=0;i<8;i++){
      var loader=new ExecFileLoader();loader.load(new File(args[i]));var sessions=loader.getSessionInfoStore().getInfos();
      if(sessions.size()!=1)throw new IllegalStateException("fresh single session required");
      var s=sessions.getFirst();long upper=i<6?1791254571000L:end;
      if(s.getStartTimeStamp()<start || s.getStartTimeStamp()>1791254571000L
          || s.getDumpTimeStamp()<s.getStartTimeStamp() || s.getDumpTimeStamp()>upper
          || (expected[i]!=null && !expected[i].equals(s.getId())))throw new IllegalStateException("fixed current session rejected");
      System.out.println("PG474_NATIVE_SESSION index="+i+" single=true start="+s.getStartTimeStamp()+" dump="+s.getDumpTimeStamp()+" roleIdMatched="+(expected[i]!=null));
    }
  }
}
