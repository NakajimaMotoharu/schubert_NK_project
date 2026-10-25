import java.lang.classfile.ClassFile;
import java.lang.reflect.AccessFlag;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Set;
import java.util.stream.Collectors;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.ICoverageNode;
import org.jacoco.core.tools.ExecFileLoader;

/** All physical code plus structurally verified annotation/interface metadata, never exclusions. */
public final class BatchBoundaryCoverageMeasure {
  private BatchBoundaryCoverageMeasure() {}

  private static boolean packageMetadata(String name, int fields, int methods, int codeMethods) {
    return name.endsWith("/package-info") && fields == 0 && methods == 0 && codeMethods == 0;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException("exec, classes and full inventory required");
    if (!packageMetadata("fixture/package-info", 0, 0, 0)
        || packageMetadata("fixture/package-info", 1, 0, 0)
        || packageMetadata("fixture/package-info", 0, 1, 0)
        || packageMetadata("fixture/package-info", 0, 1, 1)
        || packageMetadata("fixture/package-info-near", 0, 0, 0)
        || packageMetadata("fixture/Ordinary", 0, 0, 0)) {
      throw new IllegalStateException("metadata positive and five negative vectors required");
    }
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    var sessions = exec.getSessionInfoStore().getInfos();
    if (sessions.size() != 1
        || !sessions.getFirst().getId().equals("PG9796-BATCH-BOUNDARY-VALUES")) {
      throw new IllegalStateException("one actual current storage session required");
    }
    var names = Files.readAllLines(Path.of(args[2]));
    Set<String> expected = new HashSet<>(names);
    if (names.size() != expected.size()
        || expected.size() != 12
        || expected.stream()
            .anyMatch(
                n ->
                    !n.matches(
                        "dev/codex/schubert/nk/batch/(?:[A-Za-z0-9_$]+/)*(?:[A-Za-z0-9_$]+|package-info)"))) {
      throw new IllegalStateException("entire physical storage inventory required");
    }
    var nonExecutable = new LinkedHashMap<String, String>();
    for (String name : names) {
      var model =
          ClassFile.of().parse(Files.readAllBytes(Path.of(args[1]).resolve(name + ".class")));
      if (!model.thisClass().asInternalName().equals(name))
        throw new IllegalStateException("physical identity mismatch");
      int code = (int) model.methods().stream().filter(m -> m.code().isPresent()).count();
      if (name.endsWith("/package-info")
          && !packageMetadata(name, model.fields().size(), model.methods().size(), code)) {
        throw new IllegalStateException(
            "package annotation with fields or methods cannot be metadata");
      }
      if (code == 0) {
        String kind;
        if (packageMetadata(name, model.fields().size(), model.methods().size(), code))
          kind = "PACKAGE_ANNOTATION";
        else if (model.flags().has(AccessFlag.INTERFACE)) kind = "NO_CODE_INTERFACE";
        else throw new IllegalStateException("unclassified no-code class is not exempt");
        nonExecutable.put(
            name, kind + "\t" + model.fields().size() + "\t" + model.methods().size());
      }
    }
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(Path.of(args[1]).toFile());
    var observed = builder.getClasses().stream().map(c -> c.getName()).collect(Collectors.toSet());
    var complete = new HashSet<>(observed);
    complete.addAll(nonExecutable.keySet());
    if (!expected.containsAll(observed)
        || !complete.equals(expected)
        || !builder.getNoMatchClasses().isEmpty()) {
      throw new IllegalStateException(
          "no missing executable class, extra class or mismatched execution CRC allowed");
    }
    var session = sessions.getFirst();
    System.out.println(
        "SESSION\t"
            + session.getId()
            + "\t"
            + session.getStartTimeStamp()
            + "\t"
            + session.getDumpTimeStamp());
    System.out.println("TOOL_SELFTEST\t6");
    for (var entry : nonExecutable.entrySet())
      System.out.println("NO_CODE\t" + entry.getKey() + "\t" + entry.getValue());
    for (var type :
        builder.getClasses().stream()
            .sorted(java.util.Comparator.comparing(c -> c.getName()))
            .toList()) {
      var actual = exec.getExecutionDataStore().get(type.getId());
      System.out.println(
          "CLASS\t"
              + type.getName()
              + "\t"
              + Long.toUnsignedString(type.getId(), 16)
              + "\t"
              + (actual != null));
      for (var kind :
          new ICoverageNode.CounterEntity[] {
            ICoverageNode.CounterEntity.LINE,
            ICoverageNode.CounterEntity.METHOD,
            ICoverageNode.CounterEntity.CLASS,
            ICoverageNode.CounterEntity.BRANCH
          }) {
        var counter = type.getCounter(kind);
        if (nonExecutable.containsKey(type.getName()) && counter.getTotalCount() != 0) {
          throw new IllegalStateException("structural no-code has executable counter");
        }
        System.out.println(
            "COUNTER\t"
                + type.getName()
                + "\t"
                + kind
                + "\t"
                + counter.getMissedCount()
                + "\t"
                + counter.getCoveredCount());
      }
      for (var method : type.getMethods()) {
        if (method.getLineCounter().getMissedCount() != 0
            || method.getBranchCounter().getMissedCount() != 0) {
          System.out.println(
              "MISS_METHOD\t"
                  + type.getName()
                  + "\t"
                  + method.getName()
                  + "\t"
                  + method.getDesc()
                  + "\t"
                  + method.getLineCounter().getMissedCount()
                  + "\t"
                  + method.getLineCounter().getCoveredCount()
                  + "\t"
                  + method.getBranchCounter().getMissedCount()
                  + "\t"
                  + method.getBranchCounter().getCoveredCount());
        }
      }
    }
  }
}
