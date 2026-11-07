import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.ExpressionTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.NewArrayTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Parse explicit Test source only; no analyze, generate, processors or Product class loading. */
public final class TestProxyLoaderAstCheck {
  private TestProxyLoaderAstCheck() {}

  public static void main(String[] args) throws Exception {
    Path root = Path.of(args[0]).toAbsolutePath();
    var names = new java.util.ArrayList<String>();
    for (int i = 1; i < args.length; i++) {
      String name = args[i];
      if (!name.startsWith("src/") || !name.contains("/src/test/java/")
          || name.contains("RootFailedStart") || name.contains("SnapshotKeyCloseWitness")) {
        throw new IllegalArgumentException("outside explicit Test source");
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
        Map<String, String> imports = new HashMap<>();
        for (var item : unit.getImports()) {
          if (!item.isStatic()) {
            String type = item.getQualifiedIdentifier().toString();
            imports.put(type.substring(type.lastIndexOf('.') + 1), type);
          }
        }
        Set<String> classes = new HashSet<>();
        new TreePathScanner<Void, Void>() {
          @Override public Void visitClass(ClassTree node, Void unused) {
            classes.add(node.getSimpleName().toString());
            return super.visitClass(node, unused);
          }
        }.scan(unit, null);
        new TreePathScanner<Void, Void>() {
          @Override public Void visitMethodInvocation(MethodInvocationTree node, Void unused) {
            if ("Proxy.newProxyInstance".equals(node.getMethodSelect().toString())
                && "java.lang.reflect.Proxy".equals(imports.get("Proxy"))
                && node.getArguments().size() == 3) {
              ExpressionTree first = node.getArguments().get(0);
              ExpressionTree second = node.getArguments().get(1);
              if (first instanceof MethodInvocationTree getter
                  && getter.getArguments().isEmpty()
                  && getter.getMethodSelect() instanceof MemberSelectTree member
                  && member.getIdentifier().contentEquals("getClassLoader")
                  && second instanceof NewArrayTree array
                  && array.getType().toString().equals("Class<?>")
                  && array.getInitializers() != null && array.getInitializers().size() == 1) {
                String receiver = member.getExpression().toString();
                String iface = array.getInitializers().get(0).toString();
                String kind = "UNPROVEN";
                String resolved = "UNPROVEN";
                if (receiver.equals("type") && iface.equals("type")) {
                  TreePath parent = getCurrentPath();
                  while (parent != null && !(parent.getLeaf() instanceof MethodTree)) {
                    parent = parent.getParentPath();
                  }
                  if (parent != null && parent.getLeaf() instanceof MethodTree method
                      && method.getParameters().stream().anyMatch(v ->
                          v.getName().contentEquals("type")
                              && v.getType().toString().matches("Class<[A-Za-z][A-Za-z0-9]*>"))) {
                    kind = "CLASS_PARAMETER_SAME_INTERFACE_ARRAY";
                    resolved = "Class<T> type";
                  }
                } else if (receiver.endsWith(".class") && iface.endsWith(".class")) {
                  String owner = receiver.substring(0, receiver.length() - 6);
                  String target = iface.substring(0, iface.length() - 6);
                  String base = target.split("\\.")[0];
                  String imported = imports.get(base);
                  if (imported != null && (owner.equals(target) || classes.contains(owner))) {
                    kind = owner.equals(target) ? "INTERFACE_DEFINING_LOADER"
                        : "OWN_TEST_DEFINING_LOADER";
                    resolved = imported + target.substring(base.length());
                  }
                }
                long offset = trees.getSourcePositions().getStartPosition(unit, first);
                long line = unit.getLineMap().getLineNumber(offset);
                System.out.println(path + "\t" + line + "\t" + first + "\t" + iface
                    + "\t" + resolved + "\t" + kind);
              }
            }
            return super.visitMethodInvocation(node, unused);
          }
        }.scan(unit, null);
      }
      if (diagnostics.getDiagnostics().stream().anyMatch(d ->
          d.getKind() == Diagnostic.Kind.ERROR)) throw new IllegalStateException("parse errors");
    }
  }
}
