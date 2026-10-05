import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Independent literal/time-bound exec metadata oracle; no agent or runtime attach. */
public final class NativeSessions471 {
  public static void main(String[] args)throws Exception{
    if(args.length!=10)throw new IllegalArgumentException("eight fresh files and capture bounds required");
    long start=Long.parseLong(args[8]);long end=Long.parseLong(args[9]);
    String[] expected={null,null,null,null,"API-8d6e47b48a58468aaac34643bbeddb16-root","WEB-a0e695e907204a7eaf84ae16013493ad-root","API-8d6e47b48a58468aaac34643bbeddb16-ordinary","WEB-a0e695e907204a7eaf84ae16013493ad-ordinary"};
    for(int i=0;i<8;i++){
      var loader=new ExecFileLoader();loader.load(new File(args[i]));var sessions=loader.getSessionInfoStore().getInfos();
      if(sessions.size()!=1)throw new IllegalStateException("fresh single session required");
      var s=sessions.getFirst();long upper=i<6?1791233674000L:end;
      if(s.getStartTimeStamp()<start || s.getStartTimeStamp()>1791233674000L
          || s.getDumpTimeStamp()<s.getStartTimeStamp() || s.getDumpTimeStamp()>upper
          || (expected[i]!=null && !expected[i].equals(s.getId())))throw new IllegalStateException("fixed current session rejected");
      System.out.println("PG471_NATIVE_SESSION index="+i+" single=true start="+s.getStartTimeStamp()+" dump="+s.getDumpTimeStamp()+" roleIdMatched="+(expected[i]!=null));
    }
  }
}
