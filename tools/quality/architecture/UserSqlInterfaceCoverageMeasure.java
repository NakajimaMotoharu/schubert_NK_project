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
public final class UserSqlInterfaceCoverageMeasure {
  private UserSqlInterfaceCoverageMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("exec and exact normal class directory");
    var expected =
        Map.of(
            "dev/codex/schubert/nk/api/application/admin/UserQueryRequest", "UserQueryRequest.java",
            "dev/codex/schubert/nk/api/application/persistence/UserQueryRepository",
                "UserQueryRepository.java");
    var root = Path.of(args[1]);
    Set<String> names;
    try (var paths = Files.walk(root)) {
      var files = paths.filter(p -> p.toString().endsWith(".class")).toList();
      if (files.size() != 2) throw new IllegalStateException("two complete source units");
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
    if (sessions.size() != 1 || !sessions.getFirst().getId().equals("PG10044-USER-SQL-INTERFACE"))
      throw new IllegalStateException("one current session only");
    int forbidden = 0;
    for (var value : exec.getExecutionDataStore().getContents()) {
      if (java.util.Set.of(
              "dev/codex/schubert/nk/api/error/TemporaryInfrastructureException",
              "dev/codex/schubert/nk/web/bootstrap/WebStartupException",
              "dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing",
              "dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec")
          .contains(value.getName())) {
        for (boolean probe : value.getProbes()) if (probe) forbidden++;
      }
    }
    if (forbidden != 0) throw new IllegalStateException("held product path unexpectedly executed");
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(root.toFile());
    if (builder.getClasses().size() != 2 || !builder.getNoMatchClasses().isEmpty())
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
          || exec.getExecutionDataStore().get(type.getId()) == null)
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
  }
}
