import com.sun.source.tree.BlockTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.Tree;
import com.sun.source.tree.TryTree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.SourcePositions;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Parse-only structural facts; never resolves/initializes/invokes a Production class. */
public final class SourceJdbcOwnershipInventory {
  private SourceJdbcOwnershipInventory() {}

  private static String encoded(String value) {
    return Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8));
  }

  public static void main(String[] paths) throws Exception {
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task =
          (JavacTask)
              compiler.getTask(
                  null,
                  manager,
                  diagnostics,
                  List.of("-proc:none", "-implicit:none", "--release", "25"),
                  null,
                  manager.getJavaFileObjects(paths));
      var units = task.parse();
      var positions = Trees.instance(task).getSourcePositions();
      for (var unit : units) {
        new Inventory(unit, positions).scan(unit, null);
      }
      if (diagnostics.getDiagnostics().stream()
          .anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) {
        throw new IllegalArgumentException("all supplied source files must parse completely");
      }
    }
  }

  private static final class Inventory extends TreePathScanner<Void, Void> {
    private final CompilationUnitTree unit;
    private final SourcePositions positions;
    private final String path;
    private final String source;
    private String method = "";

    Inventory(CompilationUnitTree unit, SourcePositions positions) throws Exception {
      this.unit = unit;
      this.positions = positions;
      var file = Path.of(unit.getSourceFile().toUri());
      path = file.toAbsolutePath().normalize().toString();
      source = Files.readString(file, StandardCharsets.UTF_8);
    }

    private String text(Tree tree) {
      if (tree == null) return "";
      long begin = positions.getStartPosition(unit, tree);
      long end = positions.getEndPosition(unit, tree);
      if (begin < 0 || end < begin || end > source.length()) {
        throw new IllegalArgumentException("exact source positions required");
      }
      return source.substring(Math.toIntExact(begin), Math.toIntExact(end));
    }

    @Override
    public Void visitMethod(MethodTree node, Void unused) {
      String previous = method;
      method = node.getName().toString();
      try {
        return super.visitMethod(node, unused);
      } finally {
        method = previous;
      }
    }

    @Override
    public Void visitBlock(BlockTree node, Void unused) {
      var statements = node.getStatements();
      for (int i = 0; i < statements.size(); i++) {
        if (!(statements.get(i) instanceof VariableTree resource)
            || !(resource.getInitializer() instanceof MethodInvocationTree call)
            || !(call.getMethodSelect() instanceof MemberSelectTree select)) continue;
        String operation = select.getIdentifier().toString();
        if (!(operation.equals("prepareStatement") || operation.equals("executeQuery"))) continue;
        VariableTree primary =
            i + 1 < statements.size() && statements.get(i + 1) instanceof VariableTree variable
                ? variable
                : null;
        int next = i + 2;
        var declarations = new ArrayList<String>();
        while (next < statements.size()
            && statements.get(next) instanceof VariableTree declaration
            && declaration.getInitializer() == null) {
          declarations.add(text(declaration));
          next++;
        }
        TryTree scope =
            next < statements.size() && statements.get(next) instanceof TryTree attempt
                ? attempt
                : null;
        boolean immediate =
            primary != null
                && primary.getType().toString().equals("Throwable")
                && primary.getInitializer() != null
                && primary.getInitializer().getKind() == Tree.Kind.NULL_LITERAL
                && scope != null
                && scope.getResources().isEmpty()
                && scope.getFinallyBlock() != null;
        String catches =
            scope == null
                ? ""
                : String.join("\n", scope.getCatches().stream().map(this::text).toList());
        long start = positions.getStartPosition(unit, resource);
        long end = positions.getEndPosition(unit, resource);
        String[] values = {
          path,
          method,
          resource.getName().toString(),
          Long.toString(unit.getLineMap().getLineNumber(start)),
          Long.toString(unit.getLineMap().getLineNumber(end)),
          text(resource),
          primary == null ? "" : primary.getName().toString(),
          text(primary),
          scope == null ? "" : text(scope.getBlock()),
          catches,
          scope == null ? "" : text(scope.getFinallyBlock()),
          Boolean.toString(immediate),
          operation,
          String.join("\n", declarations)
        };
        System.out.println(
            String.join(
                "\t",
                java.util.Arrays.stream(values)
                    .map(SourceJdbcOwnershipInventory::encoded)
                    .toList()));
      }
      return super.visitBlock(node, unused);
    }
  }
}
