import java.io.File;
import java.io.FileOutputStream;
import org.jacoco.core.analysis.*;
import org.jacoco.core.tools.ExecFileLoader;
import org.jacoco.report.MultiSourceFileLocator;
import org.jacoco.report.xml.XMLFormatter;

/** Diagnostic same-byte XML for gap selection; never a formal pass or waiver. */
public final class NativeCoverageXml471 {
  public static void main(String[] args)throws Exception{
    if(args.length<3)throw new IllegalArgumentException("jar, new XML, real exec required");
    var output=new File(args[1]);if(!output.createNewFile())throw new IllegalStateException("new-only XML required");
    var loader=new ExecFileLoader();for(int i=2;i<args.length;i++)loader.load(new File(args[i]));
    var builder=new CoverageBuilder();new Analyzer(loader.getExecutionDataStore(),builder).analyzeAll(new File(args[0]));
    for(var c:builder.getClasses())if(c.isNoMatch())throw new IllegalStateException("same source class mismatch");
    try(var stream=new FileOutputStream(output)){
      var visitor=new XMLFormatter().createVisitor(stream);
      visitor.visitInfo(loader.getSessionInfoStore().getInfos(),loader.getExecutionDataStore().getContents());
      visitor.visitBundle(builder.getBundle("same-frozen-eight-native-gap"),new MultiSourceFileLocator(4));visitor.visitEnd();
    }
    System.out.println("PG471_GAP_XML sameBytes=true classMismatch0=true formal=false");
  }
}
