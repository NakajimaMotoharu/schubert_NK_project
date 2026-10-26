import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.Map;
import java.util.Set;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** Exact two complete normal source units; one exec, no target class initialization. */
public final class UidOracleCoverageMeasureV2 {
  private UidOracleCoverageMeasureV2() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException(
          "exec, exact normal Main directory, normal selected Test class");
    var expected =
        Map.of(
            "dev/codex/schubert/nk/storage/LinuxInodeSecurity", "LinuxInodeSecurity.java",
            "dev/codex/schubert/nk/storage/LinuxInodeSecurity$GetXattrCall",
                "LinuxInodeSecurity.java",
            "dev/codex/schubert/nk/storage/LinuxInodeSecurity$StatvfsCall",
                "LinuxInodeSecurity.java",
            "dev/codex/schubert/nk/storage/LinuxInodeSecurity$UidCall", "LinuxInodeSecurity.java");
    var root = Path.of(args[1]);
    Set<String> names;
    try (var paths = Files.walk(root)) {
      var files = paths.filter(p -> p.toString().endsWith(".class")).toList();
      if (files.size() != 4)
        throw new IllegalStateException("four physical classes of one complete source unit");
      for (var file : files) {
        var model = ClassFile.of().parse(Files.readAllBytes(file));
        String name = model.thisClass().asInternalName();
        if (!expected.containsKey(name)
            || !file.equals(root.resolve(name + ".class"))
            || !model
                .findAttribute(Attributes.sourceFile())
                .orElseThrow()
                .sourceFile()
                .stringValue()
                .equals(expected.get(name)))
          throw new IllegalStateException("literal source and physical identity required");
        if (!name.equals("dev/codex/schubert/nk/storage/LinuxInodeSecurity")
            && (!model.flags().has(java.lang.reflect.AccessFlag.INTERFACE)
                || model.methods().stream().anyMatch(method -> method.code().isPresent())))
          throw new IllegalStateException("declared no-Code interface only");
      }
      names =
          files.stream()
              .map(p -> root.relativize(p).toString().replace(".class", ""))
              .collect(java.util.stream.Collectors.toSet());
    }
    if (!names.equals(expected.keySet())) throw new IllegalStateException("missing or extra unit");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG10132-UID-ORACLE"))
      throw new IllegalStateException("one current session only");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents()) {
      if (java.util.Set.of("api", "web", "batch", "bootstrap").stream()
          .anyMatch(
              module -> value.getName().startsWith("dev/codex/schubert/nk/" + module + "/"))) {
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
      }
    }
    if (forbidden != 0) throw new IllegalStateException("held product path unexpectedly executed");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    if (builder.getClasses().size() != 4 || !builder.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("complete two units / matching CRC only");
    var session = sessions.getFirst();
    System.out.println(
        "SESSION\t"
            + session.getId()
            + "\t"
            + session.getStartTimeStamp()
            + "\t"
            + session.getDumpTimeStamp());
    System.out.println("FORBIDDEN_PROBE_HITS\t" + forbidden);
    for (var type :
        builder.getClasses().stream().sorted(Comparator.comparing(t -> t.getName())).toList()) {
      if (!expected.containsKey(type.getName())
          || (type.getName().equals("dev/codex/schubert/nk/storage/LinuxInodeSecurity")
              && exec.getExecutionDataStore().get(type.getId()) == null))
        throw new IllegalStateException("actual class execution required");
      System.out.println(
          "CLASS\t" + type.getName() + "\t" + Long.toUnsignedString(type.getId(), 16));
      for (var kind :
          new ICoverageNode.CounterEntity[] {
            ICoverageNode.CounterEntity.LINE, ICoverageNode.CounterEntity.METHOD,
            ICoverageNode.CounterEntity.CLASS, ICoverageNode.CounterEntity.BRANCH
          }) {
        var counter = type.getCounter(kind);
        System.out.println(
            "COUNTER\t"
                + kind.name()
                + "\t"
                + counter.getMissedCount()
                + "\t"
                + counter.getCoveredCount());
      }
    }
    var forbiddenMethods =
        Set.of(
            "accessAcl",
            "readAcl",
            "requireNoFileCapabilities",
            "readOnlyFilesystem",
            "capability",
            "failure");
    int checked = 0;
    for (var type : builder.getClasses()) {
      if (!type.getName().equals("dev/codex/schubert/nk/storage/LinuxInodeSecurity")) continue;
      for (var method : type.getMethods()) {
        if (!forbiddenMethods.contains(method.getName())) continue;
        if (method.getMethodCounter().getCoveredCount() != 0
            || method.getInstructionCounter().getCoveredCount() != 0)
          throw new IllegalStateException("unselected native product method unexpectedly executed");
        checked++;
        System.out.println("UNRUN_METHOD\t" + method.getName() + "\t0\t0");
      }
    }
    if (checked != 6) throw new IllegalStateException("complete forbidden native method inventory");
    byte[] testBytes = Files.readAllBytes(Path.of(args[2]));
    var testModel = ClassFile.of().parse(testBytes);
    if (!testModel
            .thisClass()
            .asInternalName()
            .equals("dev/codex/schubert/nk/storage/LinuxInodeSecurityTest")
        || !testModel
            .findAttribute(Attributes.sourceFile())
            .orElseThrow()
            .sourceFile()
            .stringValue()
            .equals("LinuxInodeSecurityTest.java"))
      throw new IllegalStateException("exact selected Test physical identity");
    var tests = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), tests).analyzeClass(testBytes, "selected-test");
    if (tests.getClasses().size() != 1 || !tests.getNoMatchClasses().isEmpty())
      throw new IllegalStateException("one Test matching current CRC");
    var testNames =
        Set.of(
            "actualAclAndUid",
            "filesystemFlagsAndFailures",
            "heldElfCapabilityAbsenceRequiresExactEnodataAndNativeHeldFile",
            "aclReturnAndErrnoBoundaries",
            "canonicalCapabilityAndBounds",
            "platformAndSymbolAdmission",
            "heldInodeSurvivesReplacement",
            "concurrentReadsStayIndependent",
            "interfacesAndRedaction");
    int seen = 0;
    for (var type : tests.getClasses())
      for (var method : type.getMethods()) {
        if (Set.of("setAcl", "golden", "noAcl", "failure").contains(method.getName())
            && method.getInstructionCounter().getCoveredCount() != 0)
          throw new IllegalStateException("unselected Test process/ACL helper executed");
        if (!testNames.contains(method.getName())) continue;
        int hit = method.getMethodCounter().getCoveredCount();
        int instructions = method.getInstructionCounter().getCoveredCount();
        boolean selected = method.getName().equals("platformAndSymbolAdmission");
        if ((selected && (hit != 1 || instructions == 0))
            || (!selected && (hit != 0 || instructions != 0)))
          throw new IllegalStateException("only closed selected Test method may run");
        System.out.println("TEST_METHOD\t" + method.getName() + "\t" + hit + "\t" + instructions);
        seen++;
      }
    if (seen != 9) throw new IllegalStateException("complete nine Test method inventory");
  }
}
