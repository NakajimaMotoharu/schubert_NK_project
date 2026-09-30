import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;
import org.jacoco.core.analysis.*;
/** Non-secret native same-byte reachability diagnostic, not acceptance/coverage waiver. */
public final class NativeReached {
  public static void main(String[] args) throws Exception {
    var data=new ExecFileLoader();data.load(new File(args[0]));
    var builder=new CoverageBuilder();
    new Analyzer(data.getExecutionDataStore(),builder).analyzeAll(new File(args[1]));
    for(var c:builder.getClasses()) {
      if(c.isNoMatch())throw new IllegalStateException("class byte mismatch");
      if(!c.getName().contains(args[2]) || c.getInstructionCounter().getCoveredCount()==0) continue;
      System.out.println(c.getName()+" classId="+Long.toUnsignedString(c.getId(),16));
      for(var m:c.getMethods())if(m.getInstructionCounter().getCoveredCount()>0)
        System.out.println("  "+m.getName()+m.getDesc()+" L="+m.getLineCounter().getCoveredCount()+"/"+m.getLineCounter().getTotalCount()+" B="+m.getBranchCounter().getCoveredCount()+"/"+m.getBranchCounter().getTotalCount());
      System.out.print("  coveredLines=");
      for(int line=c.getFirstLine();line<=c.getLastLine();line++)if(c.getLine(line).getInstructionCounter().getCoveredCount()>0)System.out.print(line+",");
      System.out.println();
    }
  }
}
