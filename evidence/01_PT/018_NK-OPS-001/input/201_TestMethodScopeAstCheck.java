import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Explicit Test source parse-only scope witness; no attribution to runtime thread ownership. */
public final class TestMethodScopeAstCheck {
  private TestMethodScopeAstCheck() {}

  public static void main(String[] args) throws Exception {
    Path root = Path.of(args[0]).toAbsolutePath();
    List<String> names = new ArrayList<>();
    for (int i = 1; i < args.length; i++) {
      String name = args[i];
      if (!name.startsWith("src/") || !name.contains("/src/test/java/")
          || name.contains("RootFailedStart") || name.contains("SnapshotKeyCloseWitness")) {
        throw new IllegalArgumentException("not explicit Test input");
      }
      names.add(root.resolve(name).toString());
    }
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
      var task = (JavacTask) compiler.getTask(null, files, diagnostics,
          List.of("-proc:none", "--release", "25"), null,
          files.getJavaFileObjectsFromStrings(names));
      var units = task.parse();
      var trees = Trees.instance(task);
      for (CompilationUnitTree unit : units) {
        String path = root.relativize(Path.of(unit.getSourceFile().toUri())).toString();
        new TreePathScanner<Void, Void>() {
          @Override public Void visitMethod(MethodTree method, Void unused) {
            List<String> owners = new ArrayList<>();
            for (TreePath p = getCurrentPath(); p != null; p = p.getParentPath()) {
              if (p.getLeaf() instanceof ClassTree cl && !cl.getSimpleName().isEmpty()) {
                owners.add(cl.getSimpleName().toString());
              }
            }
            Collections.reverse(owners);
            long begin = trees.getSourcePositions().getStartPosition(unit, method);
            long end = trees.getSourcePositions().getEndPosition(unit, method);
            if (begin >= 0 && end > begin) {
              System.out.println(path + "\t" + String.join(".", owners) + "\t"
                  + method.getName() + "\t" + unit.getLineMap().getLineNumber(begin)
                  + "\t" + unit.getLineMap().getLineNumber(end - 1));
            }
            return super.visitMethod(method, unused);
          }
        }.scan(unit, null);
      }
      if (diagnostics.getDiagnostics().stream().anyMatch(d ->
          d.getKind() == Diagnostic.Kind.ERROR)) throw new IllegalStateException("parse errors");
    }
  }
}
