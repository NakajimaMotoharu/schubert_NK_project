import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Full PayloadCodec source-unit metadata; saved exec only, no product initialization. */
public final class CancelWireCoverageMeasure {
  private CancelWireCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3) throw new IllegalArgumentException("exec, exact Main directory, Test bytes");
    String subject = "dev/codex/schubert/nk/protocol/codec/PayloadCodec";
    var expected = Set.of(subject, subject + "$1");
    var root = Path.of(args[1]);
    try (var walk = Files.walk(root)) {
      var paths = walk.filter(p -> p.toString().endsWith(".class")).toList();
      if (paths.size() != 2) throw new IllegalStateException("two physical Main classes");
      for (var p : paths) {
        var model = ClassFile.of().parse(Files.readAllBytes(p));
        String name = model.thisClass().asInternalName();
        if (!expected.contains(name) || !p.equals(root.resolve(name + ".class"))
            || !model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile().stringValue()
                .equals("PayloadCodec.java"))
          throw new IllegalStateException("complete fixed source identity required");
      }
    }
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG10172-CANCEL-WIRE"))
      throw new IllegalStateException("one current session only");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents())
      if (value.getName().startsWith("dev/codex/schubert/")
          && !value.getName().startsWith("dev/codex/schubert/nk/protocol/"))
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
    if (forbidden != 0) throw new IllegalStateException("unexpected other product module execution");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    if (builder.getClasses().size() != 2 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("complete current matching Main classes required");
    var session = sessions.getFirst();
    System.out.println("SESSION\t" + session.getId() + "\t" + session.getStartTimeStamp()
        + "\t" + session.getDumpTimeStamp());
    System.out.println("FORBIDDEN_PROBE_HITS\t" + forbidden);
    for (var type : builder.getClasses().stream().sorted(Comparator.comparing(t -> t.getName())).toList()) {
      if (!expected.contains(type.getName())
          || (type.getName().equals(subject) && exec.getExecutionDataStore().get(type.getId()) == null))
        throw new IllegalStateException("actual matching Main required");
      System.out.println("CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
      for (var kind : new ICoverageNode.CounterEntity[] {ICoverageNode.CounterEntity.LINE,
          ICoverageNode.CounterEntity.METHOD, ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH}) {
        var counter = type.getCounter(kind);
        System.out.println("COUNTER\t" + kind.name() + "\t" + counter.getMissedCount() + "\t" + counter.getCoveredCount());
      }
    }
    byte[] testBytes = Files.readAllBytes(Path.of(args[2]));
    var model = ClassFile.of().parse(testBytes);
    if (!model.thisClass().asInternalName().equals(subject + "Test")
        || !model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile().stringValue().equals("PayloadCodecTest.java"))
      throw new IllegalStateException("fixed selected Test identity required");
    var tests = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), tests).analyzeClass(testBytes, "selected-test");
    if (tests.getClasses().size() != 1 || !tests.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("current Test CRC required");
    var names = Set.of("allSixtyFourLayoutsRoundTripMinimumSuccessValues",
        "everyResponseLayoutUsesExactErrorFillersAndNoRecords",
        "resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState",
        "fixedAndIndependentGoldenFieldsEncodeAtExactOffsets",
        "encodeRejectsUnknownMissingWrongTypeAndRecordViolations",
        "decodeRejectsLengthsNullsFixedValuesAndBadErrorFillers",
        "valuesAreImmutableNullSafeAndRedacted", "numericDigitLimitIsCheckedWithoutOverflow");
    int seen = 0;
    for (var type : tests.getClasses())
      for (var method : type.getMethods()) {
        if (!names.contains(method.getName())) continue;
        int hit = method.getMethodCounter().getCoveredCount();
        int instructions = method.getInstructionCounter().getCoveredCount();
        boolean selected = method.getName().equals("resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState");
        if ((selected && (hit != 1 || instructions == 0)) || (!selected && (hit != 0 || instructions != 0)))
          throw new IllegalStateException("only selected Test method may execute");
        System.out.println("TEST_METHOD\t" + method.getName() + "\t" + hit + "\t" + instructions);
        seen++;
      }
    if (seen != 8) throw new IllegalStateException("full eight Test inventory required");
  }
}
