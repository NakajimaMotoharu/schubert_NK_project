import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Reads only saved measurement/class bytes; never initializes a product class. */
public final class CredlocOracleCoverageMeasure {
  private CredlocOracleCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("exec and exact class bytes");
    String expected = "dev/codex/schubert/nk/storage/ServiceCredentialLocation";
    byte[] bytes = Files.readAllBytes(Path.of(args[1]));
    var model = ClassFile.of().parse(bytes);
    if (!model.thisClass().asInternalName().equals(expected)
        || !model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile().stringValue()
            .equals("ServiceCredentialLocation.java"))
      throw new IllegalStateException("complete fixed source class required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG10158-CREDLOC-ORACLE"))
      throw new IllegalStateException("one actual current session required");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents()) {
      if (value.getName().startsWith("dev/codex/schubert/")
          && !value.getName().equals(expected) && !value.getName().equals(expected + "Test"))
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
    }
    if (forbidden != 0) throw new IllegalStateException("unexpected product execution");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeClass(bytes, "selected-main");
    if (builder.getClasses().size() != 1 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("complete matching source unit required");
    var type = builder.getClasses().iterator().next();
    if (exec.getExecutionDataStore().get(type.getId()) == null)
      throw new IllegalStateException("actual class execution required");
    var session = sessions.getFirst();
    System.out.println("SESSION\t" + session.getId() + "\t" + session.getStartTimeStamp()
        + "\t" + session.getDumpTimeStamp());
    System.out.println("FORBIDDEN_PROBE_HITS\t" + forbidden);
    System.out.println("CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
    for (var kind : new ICoverageNode.CounterEntity[] {
        ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
        ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH}) {
      var counter = type.getCounter(kind);
      System.out.println("COUNTER\t" + kind.name() + "\t" + counter.getMissedCount()
          + "\t" + counter.getCoveredCount());
    }
  }
}
