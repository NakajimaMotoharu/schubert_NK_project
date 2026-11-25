import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.TreeSet;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

final class ApprovedSourceReferences {
  public static void main(String[] args) throws Exception {
    Path root = Path.of(args[0]);
    List<Path> inputs = Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)
        .stream().map(root::resolve).toList();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var compiler = ToolProvider.getSystemJavaCompiler();
    try (var files = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      JavacTask task = (JavacTask) compiler.getTask(null, files, diagnostics,
          List.of("-proc:none"), null, files.getJavaFileObjectsFromPaths(inputs));
      int parsed = 0;
      for (CompilationUnitTree unit : task.parse()) {
        parsed++;
        String source = root.relativize(Path.of(unit.getSourceFile().toUri())).toString();
        String pkg = unit.getPackageName().toString();
        List<String> result = new ArrayList<>();
        result.add("SOURCE\t" + source + "\t" + pkg);
        unit.getImports().forEach(value ->
            result.add("IMPORT\t" + source + "\t" + value.getQualifiedIdentifier()));
        References references = new References();
        references.scan(unit, null);
        references.simple.forEach(name -> result.add("SIMPLE\t" + source + "\t" + name));
        references.qualified.forEach(name -> result.add("QUALIFIED\t" + source + "\t" + name));
        result.forEach(System.out::println);
      }
      if (parsed != inputs.size() || diagnostics.getDiagnostics().stream()
          .anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) {
        throw new IllegalStateException("explicit source parse did not complete");
      }
    }
  }

  private static final class References extends TreeScanner<Void, Void> {
    final TreeSet<String> simple = new TreeSet<>();
    final TreeSet<String> qualified = new TreeSet<>();

    @Override
    public Void visitIdentifier(IdentifierTree node, Void unused) {
      simple.add(node.getName().toString());
      return super.visitIdentifier(node, unused);
    }

    @Override
    public Void visitMemberSelect(MemberSelectTree node, Void unused) {
      String candidate = node.toString();
      if (candidate.matches("dev\\.codex\\.schubert\\.nk(?:\\.[A-Za-z_$][A-Za-z0-9_$]*)+")) {
        qualified.add(candidate);
      }
      return super.visitMemberSelect(node, unused);
    }
  }
}
