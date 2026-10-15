import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;
import javax.lang.model.element.ElementKind;
import javax.lang.model.element.TypeElement;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Actual field symbols and rename-risk facts only; never changes application source. */
final class SourceFieldNamingInventory {
  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25)
      throw new IllegalArgumentException("JDK25 source root and qualified classpath required");
    Path root = Path.of(args[0]).toRealPath();
    List<Path> files;
    try (var paths = Files.walk(root)) {
      files = paths.filter(p -> p.toString().endsWith(".java")).sorted().toList();
    }
    if (files.isEmpty()) throw new IllegalArgumentException("nonempty actual field scope required");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var compiler = ToolProvider.getSystemJavaCompiler();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics, List.of("--release", "25", "-proc:none", "-implicit:none", "-classpath", args[1]), null, manager.getJavaFileObjectsFromPaths(files));
      var units = new ArrayList<CompilationUnitTree>();
      task.parse().forEach(units::add);
      task.analyze();
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalArgumentException("actual field symbols must resolve without errors");
      var trees = Trees.instance(task);
      var types = task.getTypes();
      var serializable = task.getElements().getTypeElement("java.io.Serializable").asType();
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri());
        String relative = root.relativize(source).toString();
        String raw = Files.readString(source);
        new TreePathScanner<Void, Void>() {
          @Override
          public Void visitVariable(VariableTree tree, Void unused) {
            var element = trees.getElement(getCurrentPath());
            long start = trees.getSourcePositions().getStartPosition(unit, tree);
            long end = trees.getSourcePositions().getEndPosition(unit, tree);
            if (element != null && element.getKind() == ElementKind.FIELD && start >= 0 && end > start
                && element.getEnclosingElement() instanceof TypeElement owner) {
              long typeEnd = trees.getSourcePositions().getEndPosition(unit, tree.getType());
              long initializerStart = tree.getInitializer() == null ? end : trees.getSourcePositions().getStartPosition(unit, tree.getInitializer());
              long nameStart = -1;
              if (typeEnd >= start && initializerStart >= typeEnd) {
                var matcher = Pattern.compile("\\s*(" + Pattern.quote(tree.getName().toString()) + ")\\s*[=;]\\s*").matcher(raw.substring(Math.toIntExact(typeEnd), Math.toIntExact(initializerStart)));
                if (matcher.matches()) nameStart = typeEnd + matcher.start(1);
              }
              List<String> fields = List.of(
                  "FIELD", relative, owner.getQualifiedName().toString(), tree.getName().toString(),
                  element.getModifiers().toString(), Boolean.toString(owner.getKind() == ElementKind.RECORD),
                  Boolean.toString(types.isSubtype(types.erasure(owner.asType()), types.erasure(serializable))),
                  owner.getAnnotationMirrors().stream().map(a -> a.getAnnotationType().toString()).sorted().toList().toString(),
                  element.getAnnotationMirrors().stream().map(a -> a.getAnnotationType().toString()).sorted().toList().toString(),
                  Long.toString(unit.getLineMap().getLineNumber(start)), Long.toString(unit.getLineMap().getLineNumber(end)),
                  Long.toString(nameStart < 0 ? -1 : unit.getLineMap().getLineNumber(nameStart)),
                  Long.toString(nameStart), Long.toString(start), Long.toString(end));
              if (fields.stream().anyMatch(s -> s.indexOf('\t') >= 0 || s.indexOf('\n') >= 0 || s.indexOf('\r') >= 0))
                throw new IllegalArgumentException("bounded field metadata only");
              System.out.println(String.join("\t", fields));
            }
            return super.visitVariable(tree, unused);
          }
        }.scan(unit, null);
      }
    }
  }
}
