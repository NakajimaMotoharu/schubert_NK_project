import java.io.File;
import java.time.Instant;
import java.util.*;
import org.jacoco.core.analysis.*;
import org.jacoco.core.data.ExecutionDataStore;
import org.jacoco.core.tools.ExecFileLoader;

/** Individual stream provenance before union. Never reports a formal pass or a raw session id. */
public final class NativeStreamInspect531 {
  static final long START=Instant.parse("2026-10-07T19:46:29.837227Z").toEpochMilli();
  static final long PARENT_END=Instant.parse("2026-10-07T20:08:51.344734Z").toEpochMilli();
  static final Map<String,String> IDS=Map.of(
      "root-api193","API-844d2217a6494e4f9f852fc4f488a0fa-root",
      "root-web193","WEB-7127bb06489a4218acd2b72570ce1ec5-root",
      "ordinary-api193","API-844d2217a6494e4f9f852fc4f488a0fa-ordinary",
      "ordinary-web193","WEB-7127bb06489a4218acd2b72570ce1ec5-ordinary");
  static boolean current(String role,String id,long start,long dump){
    if(role==null || id==null || id.isEmpty() || !Set.of("parent","backup","cleanup","expiry","root-api193","root-web193","ordinary-api193","ordinary-web193").contains(role))return false;
    long end=role.equals("ordinary-api193")?1791407716520L:role.equals("ordinary-web193")?1791407714709L:PARENT_END;
    return start>=START && start<=PARENT_END && dump>=start && dump<=end && (!IDS.containsKey(role) || IDS.get(role).equals(id));
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
