import java.io.File;
import java.time.Instant;
import java.util.*;
import org.jacoco.core.analysis.*;
import org.jacoco.core.data.ExecutionDataStore;
import org.jacoco.core.tools.ExecFileLoader;

/** Individual stream provenance before union. Never reports a formal pass or a raw session id. */
public final class NativeStreamInspect538 {
  static final long BOOT_START=1791416025194L;
  static final long BOOT_END=1791416026860L;
  static boolean current(String role,String id,long start,long dump){
    if("ordinary-bootstrap196".equals(role)){
      String expected="BOOTSTRAP-"+"08face250787426aab68796452a0289f"+"-ordinary";
      return expected.equals(id) && start>=BOOT_START && start<=BOOT_END && dump>=start && dump<=BOOT_END;
    }
    return NativeStreamInspect531.current(role,id,start,dump);
  }
  public static void main(String[] args)throws Exception {
    if(args==null || args.length!=8)throw new IllegalArgumentException("role, real exec, frozen six jars required");
    var expected=new HashMap<String,Long>();
    for(int i=2;i<8;i++){
      var classes=new CoverageBuilder();new Analyzer(new ExecutionDataStore(),classes).analyzeAll(new File(args[i]));
      for(var c:classes.getClasses()){
        Long prior=expected.putIfAbsent(c.getName(),c.getId());
        if(prior!=null && prior.longValue()!=c.getId())throw new IllegalStateException("frozen class map conflict");
      }
    }
    var loader=new ExecFileLoader();loader.load(new File(args[1]));var sessions=loader.getSessionInfoStore().getInfos();
    boolean one=sessions.size()==1;long start=one?sessions.getFirst().getStartTimeStamp():-1,dump=one?sessions.getFirst().getDumpTimeStamp():-1;
    boolean window=one && current(args[0],sessions.getFirst().getId(),start,dump);
    int mismatch=0,missing=0,production=0;
    for(var d:loader.getExecutionDataStore().getContents())if(d.getName().startsWith("dev/codex/schubert/nk/")){
      production++;Long id=expected.get(d.getName());
      if(id==null)missing++;else if(id.longValue()!=d.getId())mismatch++;
    }
    System.out.println("{\"role\":\""+args[0]+"\",\"singleSession\":"+one+",\"currentWindowAndRole\":"+window+",\"startMillis\":"+start+",\"dumpMillis\":"+dump+",\"productionExecutionClasses\":"+production+",\"classByteMismatch\":"+mismatch+",\"unknownProductionClasses\":"+missing+",\"formal\":false}");
  }
}

