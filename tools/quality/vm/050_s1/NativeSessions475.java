import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Independent literal/time-bound exec metadata oracle; no agent or runtime attach. */
public final class NativeSessions475 {
  public static void main(String[] args)throws Exception{
    if(args.length!=10)throw new IllegalArgumentException("eight fresh files and capture bounds required");
    long start=Long.parseLong(args[8]);long end=Long.parseLong(args[9]);
    String[] expected={null,null,null,null,"API-b6276c2ccb3d4c0ba2bd7fdd4f24e302-root","WEB-1ad09e1a4edf422f9abc9a89109fe535-root","API-b6276c2ccb3d4c0ba2bd7fdd4f24e302-ordinary","WEB-1ad09e1a4edf422f9abc9a89109fe535-ordinary"};
    for(int i=0;i<8;i++){
      var loader=new ExecFileLoader();loader.load(new File(args[i]));var sessions=loader.getSessionInfoStore().getInfos();
      if(sessions.size()!=1)throw new IllegalStateException("fresh single session required");
      var s=sessions.getFirst();long upper=i<6?1791258970000L:end;
      if(s.getStartTimeStamp()<start || s.getStartTimeStamp()>1791258970000L
          || s.getDumpTimeStamp()<s.getStartTimeStamp() || s.getDumpTimeStamp()>upper
          || (expected[i]!=null && !expected[i].equals(s.getId())))throw new IllegalStateException("fixed current session rejected");
      System.out.println("PG475_NATIVE_SESSION index="+i+" single=true start="+s.getStartTimeStamp()+" dump="+s.getDumpTimeStamp()+" roleIdMatched="+(expected[i]!=null));
    }
  }
}
