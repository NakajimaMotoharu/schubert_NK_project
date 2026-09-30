import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;
import org.jacoco.core.analysis.*;
/** Same-class-byte union diagnostic; not a formal collector or coverage waiver. */
public final class NativeCoverage {
  public static void main(String[] args) throws Exception {
    if(args.length<2)throw new IllegalArgumentException("class artifact and real exec files required");
    var data=new ExecFileLoader();
    for(int i=1;i<args.length;i++)data.load(new File(args[i]));
    var builder=new CoverageBuilder();
    new Analyzer(data.getExecutionDataStore(),builder).analyzeAll(new File(args[0]));
    for(var c:builder.getClasses())if(c.isNoMatch())throw new IllegalStateException("actual class byte mismatch");
    var result=builder.getBundle("actual same-byte union");
    System.out.println("{\"formal\":false,\"classByteMismatch\":0,\"LINE\":"+value(result.getLineCounter())+",\"METHOD\":"+value(result.getMethodCounter())+",\"CLASS\":"+value(result.getClassCounter())+",\"BRANCH\":"+value(result.getBranchCounter())+"}");
  }
  static String value(ICounter c){return "{\"missed\":"+c.getMissedCount()+",\"covered\":"+c.getCoveredCount()+"}";}
}
