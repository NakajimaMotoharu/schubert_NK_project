import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.ImportTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Syntax-only inventory for explicit NK references. Never attributes, loads or generates Main. */
final class SourceModuleReferenceAudit {
  private static final String NK_PREFIX = "dev.codex.schubert.nk.";

  private record Source(String module, Path path) {}

  private record Parsed(Source source, CompilationUnitTree tree) {}

  public static void main(String[] arguments) throws IOException {
    if (arguments.length != 1) {
      throw new IllegalArgumentException("one manifest of module and source path");
    }
    var inventory = new HashMap<Path, Source>();
    for (String line : Files.readAllLines(Path.of(arguments[0]))) {
      var fields = line.split("\t", -1);
      if (fields.length != 2) {
        throw new IllegalArgumentException("expected two fields");
      }
      Path path = Path.of(fields[1]).toAbsolutePath().normalize();
      if (inventory.putIfAbsent(path, new Source(fields[0], path)) != null) {
        throw new IllegalArgumentException("duplicate source path");
      }
    }
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
      var syntaxTask =
          (JavacTask)
              compiler.getTask(
                  null,
                  files,
                  diagnostics,
                  List.of("--release", "25", "-proc:none"),
                  null,
                  files.getJavaFileObjectsFromPaths(inventory.keySet()));
      List<Parsed> parsed = new ArrayList<>();
      for (var unit : syntaxTask.parse()) {
        Path path = Path.of(unit.getSourceFile().toUri());
        parsed.add(new Parsed(inventory.get(path), unit));
      }
      if (parsed.size() != inventory.size()
          || diagnostics.getDiagnostics().stream()
              .anyMatch(diagnostic -> diagnostic.getKind() == Diagnostic.Kind.ERROR)) {
        throw new IllegalArgumentException("incomplete or invalid source AST");
      }
      report(parsed);
    }
  }

  private static void report(List<Parsed> parsed) {
    Map<String, String> types = new HashMap<>();
    Map<String, TreeSet<String>> packages = new HashMap<>();
    var output = new TreeSet<String>();
    for (var current : parsed) {
      String module = current.source().module();
      var unit = current.tree();
      String pkg = unit.getPackageName().toString();
      packages.computeIfAbsent(pkg, ignored -> new TreeSet<>()).add(module);
      for (var declaration : unit.getTypeDecls()) {
        if (declaration instanceof ClassTree type) {
          String name = pkg + "." + type.getSimpleName();
          if (types.putIfAbsent(name, module) != null) {
            throw new IllegalArgumentException("duplicate declaration " + name);
          }
          output.add(String.join("\t", "TYPE", module, name));
        }
      }
    }
    for (var current : parsed) {
      output.add(
          String.join("\t", "FILE", current.source().module(), current.source().path().toString()));
      new ReferenceScanner(current.source(), types, packages, output).scan(current.tree(), null);
    }
    output.forEach(System.out::println);
  }

  private static final class ReferenceScanner extends TreeScanner<Void, Void> {
    private final Source source;
    private final Map<String, String> types;
    private final Map<String, TreeSet<String>> packages;
    private final TreeSet<String> output;

    private ReferenceScanner(
        Source source,
        Map<String, String> types,
        Map<String, TreeSet<String>> packages,
        TreeSet<String> output) {
      this.source = source;
      this.types = types;
      this.packages = packages;
      this.output = output;
    }

    @Override
    public Void visitImport(ImportTree tree, Void unused) {
      reference(
          tree.isStatic() ? "static-import" : "import", tree.getQualifiedIdentifier().toString());
      return null;
    }

    @Override
    public Void visitMemberSelect(MemberSelectTree tree, Void unused) {
      reference("source-qualified-name", tree.toString());
      return super.visitMemberSelect(tree, unused);
    }

    private void reference(String kind, String name) {
      if (!name.startsWith(NK_PREFIX)) {
        return;
      }
      int right = name.length();
      while (right > NK_PREFIX.length()) {
        String prefix = name.substring(0, right);
        String owner = types.get(prefix);
        if (owner != null) {
          result("REF", kind, owner, prefix);
          return;
        }
        right = name.lastIndexOf('.', right - 1);
      }
      if (kind.equals("source-qualified-name")) {
        return;
      }
      if (name.endsWith(".*")) {
        var owners = packages.get(name.substring(0, name.length() - 2));
        if (owners != null && owners.size() == 1) {
          result("REF", kind, owners.first(), name);
          return;
        }
      }
      result("UNRESOLVED", kind, "?", name);
    }

    private void result(String kind, String syntax, String destination, String name) {
      output.add(
          String.join(
              "\t", kind, source.module(), destination, syntax, name, source.path().toString()));
    }
  }
}
