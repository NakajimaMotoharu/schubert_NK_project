import java.io.File;
import org.jacoco.core.tools.ExecFileLoader;

/** Merge same-class-byte host unit and isolated native PT execution data; never a gate waiver. */
public final class MergeNativeCoverage {
  public static void main(String[] args)throws Exception {
    if(args.length<3||args.length>4)throw new IllegalArgumentException("two or three inputs and a new report output required");
    File output=new File(args[args.length-1]);
    if(output.exists())throw new IllegalArgumentException("preserve existing report");
    var loader=new ExecFileLoader();
    for(int i=0;i<args.length-1;i++)loader.load(new File(args[i]));
    loader.save(output,false);
    System.out.println("same-source PT execution data streams merged; formal acceptance is separate");
  }
}
