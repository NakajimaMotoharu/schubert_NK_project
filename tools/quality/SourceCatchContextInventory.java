import com.sun.source.tree.AssignmentTree;
import com.sun.source.tree.CatchTree;
import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.ContinueTree;
import com.sun.source.tree.BreakTree;
import com.sun.source.tree.LambdaExpressionTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.ReturnTree;
import com.sun.source.tree.ThrowTree;
import com.sun.source.tree.UnionTypeTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import javax.lang.model.element.Element;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Resolved catch facts only; a direct rethrow is NOT an applicability disposition. */
final class SourceCatchContextInventory {
  private static Element symbol(Trees trees, CompilationUnitTree unit, com.sun.source.tree.Tree tree) {
    TreePath path = TreePath.getPath(unit, tree);
    return path == null ? null : trees.getElement(path);
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25) {
      throw new IllegalArgumentException("JDK25 source root and qualified classpath required");
    }
    Path root = Path.of(args[0]).toRealPath();
    List<Path> files;
    try (var paths = Files.walk(root)) {
      files = paths.filter(p -> p.toString().endsWith(".java")).sorted().toList();
    }
    if (files.isEmpty()) throw new IllegalArgumentException("nonempty source required");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var compiler = ToolProvider.getSystemJavaCompiler();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics,
          List.of("--release", "25", "-proc:none", "-implicit:none", "-classpath", args[1]),
          null, manager.getJavaFileObjectsFromPaths(files));
      var units = new ArrayList<CompilationUnitTree>();
      task.parse().forEach(units::add);
      task.analyze();
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) {
        throw new IllegalArgumentException("actual catch symbols must resolve without errors");
      }
      Trees trees = Trees.instance(task);
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri()).toRealPath();
        if (!source.startsWith(root)) throw new IllegalArgumentException("source outside fixed root");
        String relative = root.relativize(source).toString();
        new TreePathScanner<Void, Void>() {
          @Override
          public Void visitCatch(CatchTree node, Void unused) {
            Element parameter = symbol(trees, unit, node.getParameter());
            long start = trees.getSourcePositions().getStartPosition(unit, node.getParameter());
            long end = trees.getSourcePositions().getEndPosition(unit, node.getParameter());
            if (parameter == null || start < 0 || end <= start) {
              throw new IllegalArgumentException("resolved bounded catch parameter required");
            }
            String method = "<initializer>";
            for (TreePath path = getCurrentPath(); path != null; path = path.getParentPath()) {
              if (path.getLeaf() instanceof MethodTree enclosing) {
                Element owner = trees.getElement(path);
                method = owner == null ? enclosing.getName().toString() : owner.getEnclosingElement() + "#" + owner;
                break;
              }
            }
            int[] counts = new int[6]; // same throw, other throw, return, assignment, break, continue
            new TreePathScanner<Void, Void>() {
              @Override public Void visitClass(ClassTree tree, Void u) { return null; }
              @Override public Void visitLambdaExpression(LambdaExpressionTree tree, Void u) { return null; }
              @Override public Void visitThrow(ThrowTree tree, Void u) {
                counts[parameter.equals(symbol(trees, unit, tree.getExpression())) ? 0 : 1]++;
                return super.visitThrow(tree, u);
              }
              @Override public Void visitReturn(ReturnTree tree, Void u) { counts[2]++; return super.visitReturn(tree, u); }
              @Override public Void visitAssignment(AssignmentTree tree, Void u) {
                if (parameter.equals(symbol(trees, unit, tree.getVariable()))) counts[3]++;
                return super.visitAssignment(tree, u);
              }
              @Override public Void visitBreak(BreakTree tree, Void u) { counts[4]++; return super.visitBreak(tree, u); }
              @Override public Void visitContinue(ContinueTree tree, Void u) { counts[5]++; return super.visitContinue(tree, u); }
            }.scan(new TreePath(getCurrentPath(), node.getBlock()), null);
            var statements = node.getBlock().getStatements();
            boolean finalDirect = !statements.isEmpty()
                && statements.getLast() instanceof ThrowTree last
                && parameter.equals(symbol(trees, unit, last.getExpression()));
            String caught = parameter.asType().toString();
            if (node.getParameter().getType() instanceof UnionTypeTree union) {
              var alternatives = new ArrayList<String>();
              for (var alternative : union.getTypeAlternatives()) {
                var mirror = trees.getTypeMirror(TreePath.getPath(unit, alternative));
                if (mirror == null) throw new IllegalArgumentException("resolved union alternatives required");
                alternatives.add(mirror.toString());
              }
              caught = String.join("|", alternatives);
            }
            List<String> fields = List.of("CATCH", relative, method, caught,
                Long.toString(unit.getLineMap().getLineNumber(start)),
                Long.toString(unit.getLineMap().getLineNumber(end - 1)),
                Long.toString(start), Long.toString(end), Boolean.toString(finalDirect),
                Integer.toString(counts[0]), Integer.toString(counts[1]), Integer.toString(counts[2]),
                Integer.toString(counts[3]), Integer.toString(counts[4]), Integer.toString(counts[5]));
            if (fields.stream().anyMatch(s -> s.indexOf('\t') >= 0 || s.indexOf('\n') >= 0 || s.indexOf('\r') >= 0)) {
              throw new IllegalArgumentException("bounded scalar catch metadata required");
            }
            System.out.println(String.join("\t", fields));
            return super.visitCatch(node, unused);
          }
        }.scan(unit, null);
      }
    }
  }
}
