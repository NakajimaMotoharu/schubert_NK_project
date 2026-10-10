import java.io.File;
import java.io.FileOutputStream;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.tools.ExecFileLoader;
import org.jacoco.report.DirectorySourceFileLocator;
import org.jacoco.report.xml.XMLFormatter;

/** Reports only explicit target class files; does not assert any module-wide gate. */
public final class ScopedCoverageReport {
  private ScopedCoverageReport() {}

  public static void main(String[] args) throws Exception {
    if (args.length < 4) throw new IllegalArgumentException("exec xml source target-classes required");
    var loader = new ExecFileLoader();
    loader.load(new File(args[0]));
    var builder = new CoverageBuilder();
    var analyzer = new Analyzer(loader.getExecutionDataStore(), builder);
    for (int i = 3; i < args.length; i++) analyzer.analyzeAll(new File(args[i]));
    if (builder.getClasses().isEmpty()) throw new IllegalStateException("no target classes");
    try (var out = new FileOutputStream(args[1])) {
      var visitor = new XMLFormatter().createVisitor(out);
      visitor.visitInfo(loader.getSessionInfoStore().getInfos(),
          loader.getExecutionDataStore().getContents());
      visitor.visitBundle(builder.getBundle("explicit-deputy-targets"),
          new DirectorySourceFileLocator(new File(args[2]), "UTF-8", 4));
      visitor.visitEnd();
    }
  }
}
