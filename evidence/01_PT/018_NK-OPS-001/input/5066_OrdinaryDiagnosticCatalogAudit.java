import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.LiteralTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.ReturnTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** P018-10.03 source syntax audit. Product types are never compiled or loaded. */
final class OrdinaryDiagnosticCatalogAudit {
  public static void main(String[] args) throws Exception {
    if (args.length != 1)
      throw new IllegalArgumentException("provide one owned list of Java paths");
    List<Path> paths = Files.readAllLines(Path.of(args[0])).stream().map(Path::of).toList();
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
      var task =
          (JavacTask)
              compiler.getTask(
                  null,
                  files,
                  diagnostics,
                  List.of("-proc:none", "--release", "25"),
                  null,
                  files.getJavaFileObjectsFromPaths(paths));
      var position = Trees.instance(task).getSourcePositions();
      int units = 0;
      for (CompilationUnitTree unit : task.parse()) {
        units++;
        String file = Path.of(unit.getSourceFile().toUri()).getFileName().toString();
        if (!file.endsWith(".java")) throw new IllegalArgumentException("Java source required");
        String owner = file.substring(0, file.length() - ".java".length());
        ClassTree declaration =
            unit.getTypeDecls().stream()
                .filter(ClassTree.class::isInstance)
                .map(ClassTree.class::cast)
                .filter(t -> t.getSimpleName().contentEquals(owner))
                .findFirst()
                .orElseThrow();
        var methods =
            declaration.getMembers().stream()
                .filter(MethodTree.class::isInstance)
                .map(MethodTree.class::cast)
                .filter(m -> m.getName().contentEquals("toString") && m.getParameters().isEmpty())
                .toList();
        if (methods.isEmpty()) {
          System.out.printf("%s\t%s\t%s\t0%n", owner, declaration.getKind(), "NO_EXPLICIT_METHOD");
          continue;
        }
        if (methods.size() != 1)
          throw new IllegalStateException("duplicate diagnostic declaration");
        var method = methods.getFirst();
        var returns = new ArrayList<ReturnTree>();
        new TreePathScanner<Void, Void>() {
          @Override
          public Void visitReturn(ReturnTree statement, Void unused) {
            returns.add(statement);
            return super.visitReturn(statement, unused);
          }
        }.scan(Trees.instance(task).getPath(unit, method), null);
        String outcome = "EXPRESSION_OR_MULTIPLE_RETURNS";
        if (returns.size() == 1
            && returns.getFirst().getExpression() instanceof LiteralTree literal
            && literal.getValue() instanceof String fixed) {
          outcome =
              fixed.contains("<redacted>") || fixed.contains("REDACTED")
                  ? "FIXED_REDACTED_LITERAL"
                  : "FIXED_OTHER_LITERAL";
        }
        long line = unit.getLineMap().getLineNumber(position.getStartPosition(unit, method));
        System.out.printf("%s\t%s\t%s\t%d%n", owner, declaration.getKind(), outcome, line);
      }
      if (units != paths.size()
          || diagnostics.getDiagnostics().stream()
              .anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) {
        throw new IllegalStateException("parse inventory mismatch or errors");
      }
    }
  }
}
