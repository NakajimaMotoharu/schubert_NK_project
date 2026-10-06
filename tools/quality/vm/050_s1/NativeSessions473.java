import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Independent literal/time-bound exec metadata oracle; no agent or runtime attach. */
public final class NativeSessions473 {
  public static void main(String[] args)throws Exception{
    if(args.length!=10)throw new IllegalArgumentException("eight fresh files and capture bounds required");
    long start=Long.parseLong(args[8]);long end=Long.parseLong(args[9]);
    String[] expected={null,null,null,null,"API-e93ae37bc6b54a24abd2c62e0e8c431e-root","WEB-4504c595204d47f4a110059e71c13c63-root","API-e93ae37bc6b54a24abd2c62e0e8c431e-ordinary","WEB-4504c595204d47f4a110059e71c13c63-ordinary"};
    for(int i=0;i<8;i++){
      var loader=new ExecFileLoader();loader.load(new File(args[i]));var sessions=loader.getSessionInfoStore().getInfos();
      if(sessions.size()!=1)throw new IllegalStateException("fresh single session required");
      var s=sessions.getFirst();long upper=i<6?1791247797000L:end;
      if(s.getStartTimeStamp()<start || s.getStartTimeStamp()>1791247797000L
          || s.getDumpTimeStamp()<s.getStartTimeStamp() || s.getDumpTimeStamp()>upper
          || (expected[i]!=null && !expected[i].equals(s.getId())))throw new IllegalStateException("fixed current session rejected");
      System.out.println("PG473_NATIVE_SESSION index="+i+" single=true start="+s.getStartTimeStamp()+" dump="+s.getDumpTimeStamp()+" roleIdMatched="+(expected[i]!=null));
    }
  }
}
