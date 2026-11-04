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

  private record Method(
      String owner, String name, int parameters, long start, long end,
      long startOffset, long endOffset) {}

  private static List<Method> parse(String source) throws Exception {
    return parse(source, false);
  }

  private static List<Method> parse(String source, boolean mainDeclarations) throws Exception {
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
            String name = node.getSimpleName().toString();
            if (mainDeclarations && name.isEmpty()) {
              long at = positions.getStartPosition(unit, node);
              if (at < 0) throw new IllegalArgumentException("bounded anonymous class required");
              name = "<anonymous@" + at + ">";
            }
            owners.addLast(name);
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
            if (mainDeclarations || test) {
              if (!mainDeclarations && node.getName().contentEquals("<init>"))
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
                      unit.getLineMap().getLineNumber(end - 1), start, end));
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

  private static void mainVectors() throws Exception {
    var declarations = parse(
        "package p; class C {\nC() {}\nvoid m() {}\nclass N { void n(int x) {} }\n}", true);
    if (declarations.size() != 3 || !declarations.getFirst().name().equals("<init>")
        || !declarations.getFirst().owner().equals("p.C"))
      throw new AssertionError("main constructor vector");
    var method = declarations.get(1);
    if (method.start() != 3 || method.end() != 3
        || method.startOffset() < 0 || method.endOffset() <= method.startOffset())
      throw new AssertionError("main literal line and offset vector");
    if (!declarations.getLast().owner().equals("p.C$N")
        || declarations.getLast().parameters() != 1)
      throw new AssertionError("main nested vector");
    var overloads = parse("class C { void m(int x) {} void m(String x) {} }", true);
    if (overloads.size() != 2 || overloads.getFirst().parameters() != 1
        || overloads.getLast().parameters() != 1
        || overloads.getFirst().endOffset() > overloads.getLast().startOffset())
      throw new AssertionError("same-line overload offset vector");
    var record = parse("record R(int x) { R { if (x < 0) throw new IllegalArgumentException(); } }", true);
    if (record.size() != 1 || !record.getFirst().name().equals("<init>"))
      throw new AssertionError("compact record constructor vector");
    if (parse("class C { void m() { Runnable r = () -> {}; } }", true).size() != 1)
      throw new AssertionError("lambda is not a declared method vector");
    var anonymous = parse("class C { Object x = new Object() { void m() {} }; }", true);
    if (anonymous.size() != 1 || !anonymous.getFirst().owner().startsWith("C$<anonymous@"))
      throw new AssertionError("anonymous syntactic owner vector");
    if (!parse("class C { String s=\"void fake() {}\"; /* void fake() {} */ int x=1; }", true).isEmpty())
      throw new AssertionError("fields and strings have no declared method vector");
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2 && args.length != 3)
      throw new IllegalArgumentException("root and exact path catalog, optional main mode required");
    boolean mainDeclarations = args.length == 3;
    if (mainDeclarations && !args[2].equals("--main-declarations"))
      throw new IllegalArgumentException("unknown declaration mode");
    vectors();
    if (mainDeclarations) mainVectors();
    var root = Path.of(args[0]).toRealPath();
    System.out.println("SELFTEST\t" + (mainDeclarations ? 15 : 7));
    for (String relative : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      // Refuse excluded basenames before target filesystem metadata or content access.
      String basename = Path.of(relative).getFileName().toString();
      if (List.of("SnapshotKeyCloseWitness.java", "pg9892_snapshot_key_close_witness.py",
              "RootFailedStartRecoveryTest.java", "RootFailedStartPairRecoveryTest.java")
          .contains(basename))
        throw new IllegalArgumentException("held source excluded by name");
      var path = root.resolve(relative).normalize();
      if (!relative.startsWith("src/schubert-nk-") || !relative.endsWith(".java")
          || !relative.contains(mainDeclarations ? "/src/main/java/" : "/src/test/java/")
          || !path.startsWith(root)
          || !path.toRealPath().equals(path))
        throw new IllegalArgumentException("exact canonical source path for selected mode required");
      for (Method method : parse(Files.readString(path, StandardCharsets.UTF_8), mainDeclarations))
        System.out.println(
            relative + "\t" + method.owner() + "\t" + method.name() + "\t"
                + method.parameters() + "\t" + method.start() + "\t" + method.end()
                + (mainDeclarations
                    ? "\t" + method.startOffset() + "\t" + method.endOffset() : ""));
    }
  }
}
