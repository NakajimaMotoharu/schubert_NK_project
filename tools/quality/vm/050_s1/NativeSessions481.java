import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** BREC198010-V06: nine fixed same-source/current-invocation native streams. */
public final class NativeSessions481 {
  public static void main(String[] args)throws Exception {
    if(args.length!=12)throw new IllegalArgumentException("nine fresh files and three time bounds required");
    long start=Long.parseLong(args[9]),parentEnd=Long.parseLong(args[10]),stopEnd=Long.parseLong(args[11]);
    if(start!=1791274945000L || parentEnd!=1791276746000L || stopEnd<parentEnd)throw new IllegalArgumentException("fixed run bounds required");
    String[] expected={null,null,null,null,"API-2aa0f2afd60b4041a9cc96bbdebf5e3c-root","WEB-aae7911f2fed454c8c95375bb784724a-root","API-2aa0f2afd60b4041a9cc96bbdebf5e3c-ordinary","WEB-aae7911f2fed454c8c95375bb784724a-ordinary","INSPECTOR-7a680e5bfa894529999fca22bc76390b-ordinary"};
    for(int i=0;i<9;i++){
      var loader=new ExecFileLoader();loader.load(new File(args[i]));var sessions=loader.getSessionInfoStore().getInfos();
      if(sessions.size()!=1)throw new IllegalStateException("fresh single session required");
      var session=sessions.getFirst();long upper=(i==6 || i==7)?stopEnd:parentEnd;
      if(session.getStartTimeStamp()<start || session.getStartTimeStamp()>parentEnd || session.getDumpTimeStamp()<session.getStartTimeStamp() || session.getDumpTimeStamp()>upper || session.getId()==null || session.getId().isEmpty() || expected[i]!=null && !expected[i].equals(session.getId()))throw new IllegalStateException("fixed current native session rejected");
      System.out.println("PG481_NATIVE_SESSION index="+i+" single=true start="+session.getStartTimeStamp()+" dump="+session.getDumpTimeStamp()+" roleIdMatched="+(expected[i]!=null));
    }
  }
}
