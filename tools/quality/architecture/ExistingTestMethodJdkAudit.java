import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import com.sun.source.util.Trees;
import java.io.StringWriter;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.SimpleJavaFileObject;
import javax.tools.ToolProvider;

/** G13 method declaration witness only; never analyze, generate or execute target code. */
public final class ExistingTestMethodJdkAudit {
  private ExistingTestMethodJdkAudit() {}

  private record Method(String owner, String name, int parameters, long start, long end) {}

  private static List<Method> parse(String source) throws Exception {
    var compiler = ToolProvider.getSystemJavaCompiler();
    if (compiler == null) throw new IllegalStateException("JDK compiler required");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var input =
        new SimpleJavaFileObject(URI.create("string:///Audit.java"), JavaFileObject.Kind.SOURCE) {
          @Override
          public CharSequence getCharContent(boolean ignoreEncodingErrors) {
            return source;
          }
        };
    try (var manager =
        compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task =
          (JavacTask)
              compiler.getTask(
                  new StringWriter(),
                  manager,
                  diagnostics,
                  List.of("--release", "25", "-proc:none"),
                  null,
                  List.of(input));
      var units = task.parse();
      var positions = Trees.instance(task).getSourcePositions();
      var result = new ArrayList<Method>();
      for (CompilationUnitTree unit : units) {
        String prefix = unit.getPackageName() == null ? "" : unit.getPackageName() + ".";
        new TreeScanner<Void, Void>() {
          private final ArrayDeque<String> owners = new ArrayDeque<>();

          @Override
          public Void visitClass(ClassTree node, Void ignored) {
            owners.addLast(node.getSimpleName().toString());
            try {
              return super.visitClass(node, ignored);
            } finally {
              owners.removeLast();
            }
          }

          @Override
          public Void visitMethod(MethodTree node, Void ignored) {
            boolean test =
                node.getModifiers().getAnnotations().stream()
                    .map(annotation -> annotation.getAnnotationType().toString())
                    .anyMatch(name -> name.equals("Test") || name.equals("org.junit.jupiter.api.Test"));
            if (test) {
              if (node.getName().contentEquals("<init>"))
                throw new IllegalArgumentException("test method, not constructor required");
              long start = positions.getStartPosition(unit, node);
              long end = positions.getEndPosition(unit, node);
              if (owners.isEmpty() || start < 0 || end <= start)
                throw new IllegalArgumentException("bounded method positions required");
              result.add(
                  new Method(
                      prefix + String.join("$", owners),
                      node.getName().toString(),
                      node.getParameters().size(),
                      unit.getLineMap().getLineNumber(start),
                      unit.getLineMap().getLineNumber(end - 1)));
            }
            return super.visitMethod(node, ignored);
          }
        }.scan(unit, null);
      }
      if (diagnostics.getDiagnostics().stream()
          .anyMatch(item -> item.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalArgumentException("complete valid Java syntax required");
      return result;
    }
  }

  private static void vectors() throws Exception {
    var one = parse("package p; class T { @Test void a() {} }");
    if (one.size() != 1 || !one.getFirst().owner().equals("p.T")
        || !one.getFirst().name().equals("a") || one.getFirst().parameters() != 0)
      throw new AssertionError("plain annotation vector");
    if (!parse("class T { String s=\"@Test void fake() {}\"; /* @Test void x() {} */ }").isEmpty())
      throw new AssertionError("string/comment vector");
    if (parse("class T { @org.junit.jupiter.api.Test void a() {} }").size() != 1)
      throw new AssertionError("qualified annotation vector");
    if (!parse("class T { @other.Test void a() {} void helper() {} }").isEmpty())
      throw new AssertionError("foreign annotation/helper vector");
    var nested = parse("class T { @Test void a() {} class N { @Test void a(int x) {} } }");
    if (nested.size() != 2 || !nested.getLast().owner().equals("T$N")
        || nested.getLast().parameters() != 1)
      throw new AssertionError("nested/parameter vector");
    try {
      parse("class T { @Test T() {} }");
      throw new AssertionError("constructor vector");
    } catch (IllegalArgumentException expected) {
      // Deliberately unsupported constructor; not a target test failure.
    }
    try {
      parse("class T { @Test void a( {");
      throw new AssertionError("incomplete syntax vector");
    } catch (IllegalArgumentException expected) {
      // Input rejected; compiler never analyzes or generates any target class.
    }
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("root and exact path catalog required");
    vectors();
    var root = Path.of(args[0]).toRealPath();
    System.out.println("SELFTEST\t7");
    for (String relative : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      var path = root.resolve(relative).normalize();
      if (!relative.startsWith("src/schubert-nk-") || !relative.endsWith(".java")
          || !relative.contains("/src/test/java/") || !path.startsWith(root)
          || !path.toRealPath().equals(path))
        throw new IllegalArgumentException("exact canonical Test source path required");
      for (Method method : parse(Files.readString(path, StandardCharsets.UTF_8)))
        System.out.println(
            relative + "\t" + method.owner() + "\t" + method.name() + "\t"
                + method.parameters() + "\t" + method.start() + "\t" + method.end());
    }
  }
}
