import com.sun.source.tree.BinaryTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import javax.lang.model.element.ElementKind;
import javax.lang.model.type.TypeKind;
import javax.lang.model.type.TypeMirror;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Exact reference comparison facts. No opinion about whether identity is appropriate. */
final class SourceReferenceIdentityInventory {
  private static boolean reference(TypeMirror type) {
    return type != null && (type.getKind() == TypeKind.DECLARED
        || type.getKind() == TypeKind.ARRAY || type.getKind() == TypeKind.TYPEVAR
        || type.getKind() == TypeKind.UNION);
  }

  private static String scalar(Object value) {
    return value.toString().replaceAll("\\s+", " ");
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25)
      throw new IllegalArgumentException("JDK25 source root and exact classpath required");
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
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalArgumentException("all reference operands must resolve");
      var trees = Trees.instance(task);
      var types = task.getTypes();
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri()).toRealPath();
        if (!source.startsWith(root)) throw new IllegalArgumentException("source outside root");
        new TreePathScanner<Void, Void>() {
          @Override public Void visitBinary(BinaryTree node, Void ignored) {
            if (node.getKind() != Tree.Kind.EQUAL_TO && node.getKind() != Tree.Kind.NOT_EQUAL_TO)
              return super.visitBinary(node, ignored);
            var left = trees.getTypeMirror(TreePath.getPath(unit, node.getLeftOperand()));
            var right = trees.getTypeMirror(TreePath.getPath(unit, node.getRightOperand()));
            if (!reference(left) || !reference(right)) return super.visitBinary(node, ignored);
            var a = left.getKind() == TypeKind.UNION ? null : types.asElement(left);
            var b = right.getKind() == TypeKind.UNION ? null : types.asElement(right);
            if ((a != null && a.getKind() == ElementKind.ENUM)
                || (b != null && b.getKind() == ElementKind.ENUM)) return super.visitBinary(node, ignored);
            TreePath method = getCurrentPath();
            while (method != null && !(method.getLeaf() instanceof MethodTree))
              method = method.getParentPath();
            long start = trees.getSourcePositions().getStartPosition(unit, node);
            long end = trees.getSourcePositions().getEndPosition(unit, node);
            var row = List.of("REFERENCE_IDENTITY", root.relativize(source).toString(),
                Long.toString(unit.getLineMap().getLineNumber(start)),
                Long.toString(unit.getLineMap().getColumnNumber(start)),
                Long.toString(unit.getLineMap().getLineNumber(end - 1)),
                Long.toString(unit.getLineMap().getColumnNumber(end - 1)),
                left.toString(), right.toString(), node.getKind().name(),
                scalar(node.getLeftOperand()), scalar(node.getRightOperand()),
                method == null ? "<initializer>" : ((MethodTree) method.getLeaf()).getName().toString());
            if (row.stream().anyMatch(s -> s.indexOf('\t') >= 0 || s.indexOf('\n') >= 0 || s.indexOf('\r') >= 0))
              throw new IllegalArgumentException("bounded scalar facts required");
            System.out.println(String.join("\t", row));
            return super.visitBinary(node, ignored);
          }
        }.scan(unit, null);
      }
    }
  }
}
