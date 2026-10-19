import com.sun.source.tree.ReturnTree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.LinkedHashMap;
import javax.lang.model.element.ElementKind;
import javax.lang.model.element.Modifier;
import javax.lang.model.element.TypeElement;
import javax.lang.model.util.ElementFilter;

/** Read-only compiler symbols, not a rename permission, serialization change or runtime adapter. */
final class FieldAccessorContractProbe {
  static void require(boolean okay) {
    if (!okay) throw new IllegalArgumentException("exact field/accessor source contract required");
  }

  public static void main(String[] arguments) throws Exception {
    if (arguments.length == 3 && arguments[0].equals("--diagnose")) {
      diagnose(Path.of(arguments[1]).toRealPath(), arguments[2]);
      return;
    }
    require(arguments.length == 3 && Runtime.version().feature() == 25);
    Path root = Path.of(arguments[0]).toRealPath();
    var requests = new LinkedHashMap<String, String>();
    for (String line : Files.readAllLines(Path.of(arguments[2]))) {
      String[] parts = line.split("\t", -1);
      require(parts.length == 3 && parts[1].matches("[1-9][0-9]*") && parts[2].matches("[A-Za-z][A-Za-z0-9_]*"));
      require(requests.put(line, parts[2]) == null);
    }
    require(!requests.isEmpty());
    var matched = new HashSet<String>();
    try (var model = SourcePrivateFieldRename.load(root, arguments[1])) {
      var types = model.task().getTypes();
      var elements = model.task().getElements();
      var serializable = elements.getTypeElement("java.io.Serializable").asType();
      var throwable = elements.getTypeElement("java.lang.Throwable").asType();
      for (var unit : model.units()) {
        String file = root.relativize(Path.of(unit.getSourceFile().toUri())).toString();
        new TreePathScanner<Void, Void>() {
          @Override
          public Void visitVariable(VariableTree tree, Void unused) {
            var field = model.trees().getElement(getCurrentPath());
            if (field != null && field.getKind() == ElementKind.FIELD) {
              long offset = model.trees().getSourcePositions().getStartPosition(unit, tree);
              long line = unit.getLineMap().getLineNumber(offset);
              String key = file + "\t" + line + "\t" + field.getSimpleName();
              if (requests.containsKey(key)) {
                require(matched.add(key) && field.getModifiers().contains(Modifier.PRIVATE));
                var owner = (TypeElement) field.getEnclosingElement();
                var getters = ElementFilter.methodsIn(owner.getEnclosedElements()).stream()
                    .filter(method -> method.getSimpleName().equals(field.getSimpleName())
                        && method.getParameters().isEmpty()
                        && types.isSameType(method.getReturnType(), field.asType())).toList();
                require(getters.size() == 1);
                var getter = getters.getFirst();
                var getterTree = model.trees().getTree(getter);
                require(getterTree != null);
                var body = getterTree.getBody();
                require(body != null && body.getStatements().size() == 1
                    && body.getStatements().getFirst() instanceof ReturnTree);
                var returned = ((ReturnTree) body.getStatements().getFirst()).getExpression();
                require(field.equals(model.trees().getElement(TreePath.getPath(unit, returned))));
                boolean serial = types.isSubtype(types.erasure(owner.asType()), types.erasure(serializable));
                boolean failure = types.isSubtype(types.erasure(owner.asType()), types.erasure(throwable));
                String category = owner.getKind() == ElementKind.ENUM ? "ENUM"
                    : failure ? "THROWABLE" : serial ? "SERIALIZABLE_CLASS" : "NON_SERIALIZABLE_CLASS";
                boolean serializedField = serial && owner.getKind() != ElementKind.ENUM
                    && !field.getModifiers().contains(Modifier.STATIC)
                    && !field.getModifiers().contains(Modifier.TRANSIENT);
                System.out.println("FIELD\t" + key + "\t" + owner.getQualifiedName() + "\t"
                    + category + "\t" + serial + "\t" + serializedField + "\t"
                    + getter.getModifiers().contains(Modifier.PUBLIC));
              }
            }
            return super.visitVariable(tree, unused);
          }
        }.scan(unit, null);
      }
    }
    require(matched.equals(requests.keySet()));
    System.out.println("COUNT\t" + matched.size());
  }

  /** Failure diagnostics only; does not waive or change the original source-symbol loader. */
  private static void diagnose(Path root, String classpath) throws Exception {
    var compiler = javax.tools.ToolProvider.getSystemJavaCompiler();
    require(compiler != null && Runtime.version().feature() == 25);
    var diagnostics = new javax.tools.DiagnosticCollector<javax.tools.JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, java.nio.charset.StandardCharsets.UTF_8)) {
      java.util.List<Path> sources;
      try (var files = Files.walk(root)) {
        sources = files.filter(p -> p.toString().endsWith(".java")).sorted().toList();
      }
      var task = (com.sun.source.util.JavacTask) compiler.getTask(null, manager, diagnostics,
          java.util.List.of("--release", "25", "-proc:none", "-implicit:none", "-classpath", classpath),
          null, manager.getJavaFileObjectsFromPaths(sources));
      task.parse();
      task.analyze();
      int errors = 0;
      for (var diagnostic : diagnostics.getDiagnostics()) {
        if (diagnostic.getKind() != javax.tools.Diagnostic.Kind.ERROR) continue;
        errors++;
        if (errors <= 20) {
          String file = diagnostic.getSource() == null ? "<options>"
              : root.relativize(Path.of(diagnostic.getSource().toUri())).toString();
          String message = diagnostic.getMessage(java.util.Locale.ROOT).replace('\n', ' ').replace('\r', ' ');
          if (message.length() > 300) message = message.substring(0, 300);
          System.out.println("DIAGNOSTIC\t" + diagnostic.getCode() + "\t" + file + "\t"
              + diagnostic.getLineNumber() + "\t" + message);
        }
      }
      System.out.println("DIAGNOSTIC_ERRORS\t" + errors);
      require(errors == 0);
    }
  }
}
