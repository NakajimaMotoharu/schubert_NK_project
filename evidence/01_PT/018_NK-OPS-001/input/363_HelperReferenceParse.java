import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.TreeSet;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Source identifiers only. Never analyze/generate, load a Test, or evaluate an initializer. */
final class HelperReferenceParse {
  public static void main(String[] args) throws Exception {
    Path root = Path.of(args[0]).toRealPath();
    List<String> names = Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8);
    Set<String> helpers = new HashSet<>(Files.readAllLines(Path.of(args[2]), StandardCharsets.UTF_8));
    Set<String> held = Set.of("RootFailedStartRecoveryTest.java", "RootFailedStartPairRecoveryTest.java",
        "SnapshotKeyCloseWitness.java", "pg9892_snapshot_key_close_witness.py");
    var compiler = ToolProvider.getSystemJavaCompiler();
    if (compiler == null) throw new IllegalStateException("JDK compiler required");
    for (int offset = 0; offset < names.size(); offset += 100) {
      List<Path> paths = new ArrayList<>();
      for (String name : names.subList(offset, Math.min(offset + 100, names.size()))) {
        Path p = root.resolve(name).normalize();
        if (!name.startsWith("src/") || !name.contains("/src/test/java/") || !name.endsWith(".java")
            || held.contains(p.getFileName().toString()) || !p.startsWith(root)
            || Files.isSymbolicLink(p) || !p.toRealPath().startsWith(root))
          throw new IllegalArgumentException("unapproved source name");
        paths.add(p);
      }
      var diagnostics = new DiagnosticCollector<JavaFileObject>();
      try (var manager = compiler.getStandardFileManager(diagnostics, Locale.ROOT, StandardCharsets.UTF_8)) {
        JavacTask task = (JavacTask) compiler.getTask(null, manager, diagnostics,
            List.of("-proc:none", "--release", "25", "-encoding", "UTF-8", "-classpath", ""),
            null, manager.getJavaFileObjectsFromPaths(paths));
        for (CompilationUnitTree unit : task.parse()) {
          Set<String> found = new TreeSet<>();
          new TreeScanner<Void, Void>() {
            @Override public Void visitIdentifier(IdentifierTree tree, Void unused) {
              if (helpers.contains(tree.getName().toString())) found.add(tree.getName().toString());
              return super.visitIdentifier(tree, unused);
            }
            @Override public Void visitMemberSelect(MemberSelectTree tree, Void unused) {
              if (helpers.contains(tree.getIdentifier().toString())) found.add(tree.getIdentifier().toString());
              return super.visitMemberSelect(tree, unused);
            }
          }.scan(unit, null);
          if (!found.isEmpty()) {
            Path p = Path.of(unit.getSourceFile().toUri());
            System.out.println(root.relativize(p) + "\t" + String.join(",", found));
          }
        }
        if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR))
          throw new IllegalStateException("source parse failed; no analysis or generation performed");
      }
    }
  }
}
