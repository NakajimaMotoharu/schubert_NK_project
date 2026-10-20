import com.sun.source.tree.CatchTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.ThrowTree;
import com.sun.source.tree.TryTree;
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
import javax.lang.model.type.TypeMirror;
import javax.lang.model.util.Types;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Main-only syntax/type facts; a proposed removal is not a PG decision or test PASS. */
final class SourcePureRethrowInventory {
  private static Element symbol(Trees trees, CompilationUnitTree unit, com.sun.source.tree.Tree tree) {
    TreePath path = TreePath.getPath(unit, tree);
    return path == null ? null : trees.getElement(path);
  }

  private static List<TypeMirror> alternatives(Trees trees, CompilationUnitTree unit, CatchTree node) {
    List<? extends com.sun.source.tree.Tree> nodes = node.getParameter().getType() instanceof UnionTypeTree union
        ? union.getTypeAlternatives() : List.of(node.getParameter().getType());
    var result = new ArrayList<TypeMirror>();
    for (var alternative : nodes) {
      TypeMirror mirror = trees.getTypeMirror(TreePath.getPath(unit, alternative));
      if (mirror == null) throw new IllegalArgumentException("every catch type must resolve");
      result.add(mirror);
    }
    return result;
  }

  private static boolean pure(Trees trees, CompilationUnitTree unit, CatchTree node) {
    var statements = node.getBlock().getStatements();
    Element parameter = symbol(trees, unit, node.getParameter());
    return parameter != null && statements.size() == 1
        && statements.getFirst() instanceof ThrowTree thrown
        && thrown.getExpression() instanceof IdentifierTree
        && parameter.equals(symbol(trees, unit, thrown.getExpression()));
  }

  private static boolean roots(List<TypeMirror> types) {
    return !types.isEmpty() && types.stream().allMatch(type ->
        type.toString().equals("java.lang.RuntimeException") || type.toString().equals("java.lang.Error"));
  }

  private static boolean later(Trees trees, Types types, CompilationUnitTree unit, TryTree owner, int index) {
    var current = alternatives(trees, unit, owner.getCatches().get(index));
    for (int next = index + 1; next < owner.getCatches().size(); next++) {
      for (var following : alternatives(trees, unit, owner.getCatches().get(next))) {
        if (current.stream().anyMatch(type -> types.isSubtype(type, following))) return true;
      }
    }
    return false;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25) {
      throw new IllegalArgumentException("fixed JDK25 source root and classpath required");
    }
    Path root = Path.of(args[0]).toRealPath();
    List<Path> files;
    try (var paths = Files.walk(root)) {
      files = paths.filter(path -> path.toString().endsWith(".java")).sorted().toList();
    }
    if (files.isEmpty()) throw new IllegalArgumentException("nonempty Main-only source root");
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
        throw new IllegalArgumentException("all Main catch types must resolve without errors");
      }
      Trees trees = Trees.instance(task);
      Types types = task.getTypes();
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri()).toRealPath();
        if (!source.startsWith(root)) throw new IllegalArgumentException("source escaped fixed Main root");
        String relative = root.relativize(source).toString();
        new TreePathScanner<Void, Void>() {
          @Override
          public Void visitCatch(CatchTree node, Void unused) {
            if (!(getCurrentPath().getParentPath().getLeaf() instanceof TryTree owner)) {
              throw new IllegalArgumentException("each source catch has one concrete Try parent");
            }
            int index = owner.getCatches().indexOf(node);
            if (index < 0) throw new IllegalArgumentException("exact catch identity");
            var caught = alternatives(trees, unit, node);
            boolean single = pure(trees, unit, node);
            boolean exactRoots = roots(caught);
            boolean following = later(trees, types, unit, owner, index);
            int eligible = 0;
            for (int i = 0; i < owner.getCatches().size(); i++) {
              var candidate = owner.getCatches().get(i);
              if (pure(trees, unit, candidate) && roots(alternatives(trees, unit, candidate))
                  && !later(trees, types, unit, owner, i)) eligible++;
            }
            boolean resources = !owner.getResources().isEmpty();
            boolean cleanup = owner.getFinallyBlock() != null;
            boolean residual = resources || cleanup || owner.getCatches().size() > eligible;
            var positions = trees.getSourcePositions();
            long a = positions.getStartPosition(unit, node);
            long b = positions.getEndPosition(unit, node);
            long p = positions.getStartPosition(unit, node.getParameter());
            long q = positions.getEndPosition(unit, node.getParameter());
            long c = positions.getStartPosition(unit, node.getBlock());
            long d = positions.getEndPosition(unit, node.getBlock());
            long t = positions.getStartPosition(unit, owner);
            long u = positions.getEndPosition(unit, owner);
            if (!(t >= 0 && t <= a && a <= p && p < q && q <= c && c < d && d == b && b <= u)) {
              throw new IllegalArgumentException("exact bounded UTF16 source tree extents");
            }
            String method = "<initializer>";
            for (TreePath path = getCurrentPath(); path != null; path = path.getParentPath()) {
              if (path.getLeaf() instanceof MethodTree enclosing) {
                Element element = trees.getElement(path);
                method = element == null ? enclosing.getName().toString() : element.getEnclosingElement() + "#" + element;
                break;
              }
            }
            List<String> fields = List.of("PURE_RETHROW", relative, method,
                String.join("|", caught.stream().map(Object::toString).toList()),
                Long.toString(unit.getLineMap().getLineNumber(p)), Long.toString(unit.getLineMap().getLineNumber(q - 1)),
                Long.toString(a), Long.toString(b), Long.toString(p), Long.toString(q),
                Long.toString(c), Long.toString(d), Long.toString(t), Long.toString(u),
                Boolean.toString(single), Boolean.toString(exactRoots), Boolean.toString(following),
                Boolean.toString(residual), Boolean.toString(single && exactRoots && !following && residual),
                Integer.toString(index), Integer.toString(owner.getCatches().size()), Integer.toString(eligible),
                Boolean.toString(resources), Boolean.toString(cleanup));
            if (fields.stream().anyMatch(s -> s.indexOf('\t') >= 0 || s.indexOf('\n') >= 0 || s.indexOf('\r') >= 0)) {
              throw new IllegalArgumentException("bounded scalar metadata only");
            }
            System.out.println(String.join("\t", fields));
            return super.visitCatch(node, unused);
          }
        }.scan(unit, null);
      }
    }
  }
}
