import com.sun.source.tree.AnnotatedTypeTree;
import com.sun.source.tree.ExpressionTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.NewClassTree;
import com.sun.source.tree.ParameterizedTypeTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.TreeScanner;
import com.sun.source.util.Trees;
import java.io.StringWriter;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.SimpleJavaFileObject;
import javax.tools.ToolProvider;

/** Syntax data only. No analyze, generate, processor, target class load or invocation. */
public final class RemainingAssertionExpectedSyntaxInventory {
  private RemainingAssertionExpectedSyntaxInventory() {}

  private record Row(
      String path,
      String method,
      long line,
      String assertion,
      String kind,
      Set<String> expected,
      Set<String> actual,
      Set<String> constructors,
      String expressionHash) {
    int shared() {
      var overlap = new TreeSet<>(expected);
      overlap.retainAll(actual);
      return overlap.size();
    }

    String tsv() {
      return String.join(
          "\t",
          path,
          method,
          Long.toString(line),
          assertion,
          kind,
          String.join(";", expected),
          String.join(";", actual),
          String.join(";", constructors),
          Integer.toString(shared()),
          expressionHash);
    }
  }

  private static String selector(ExpressionTree tree) {
    if (tree instanceof IdentifierTree id) return id.getName().toString();
    if (tree instanceof MemberSelectTree member)
      return selector(member.getExpression()) + "." + member.getIdentifier();
    if (tree instanceof MethodInvocationTree call) return selector(call.getMethodSelect()) + "()";
    if (tree instanceof NewClassTree) return "NEW";
    return "EXPR";
  }

  private static String method(ExpressionTree tree) {
    if (tree instanceof IdentifierTree id) return id.getName().toString();
    if (tree instanceof MemberSelectTree member) return member.getIdentifier().toString();
    return "";
  }

  private static Set<String> calls(ExpressionTree tree) {
    var values = new TreeSet<String>();
    new TreeScanner<Void, Void>() {
      @Override
      public Void visitMethodInvocation(MethodInvocationTree node, Void unused) {
        values.add(selector(node.getMethodSelect()));
        return super.visitMethodInvocation(node, unused);
      }
    }.scan(tree, null);
    return values;
  }

  private static Set<String> constructors(ExpressionTree tree) {
    var values = new TreeSet<String>();
    new TreeScanner<Void, Void>() {
      @Override
      public Void visitNewClass(NewClassTree node, Void unused) {
        values.add(typeName(node.getIdentifier()));
        return super.visitNewClass(node, unused);
      }
    }.scan(tree, null);
    return values;
  }

  private static String typeName(Tree tree) {
    if (tree instanceof ParameterizedTypeTree type) return typeName(type.getType());
    if (tree instanceof AnnotatedTypeTree type) return typeName(type.getUnderlyingType());
    if (tree instanceof ExpressionTree expression) return selector(expression);
    return tree.getKind().name();
  }

  private static List<Row> parse(String path, String text) throws Exception {
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var file =
        new SimpleJavaFileObject(URI.create("memory:///Input.java"), JavaFileObject.Kind.SOURCE) {
          @Override
          public CharSequence getCharContent(boolean ignore) {
            return text;
          }
        };
    var compiler = ToolProvider.getSystemJavaCompiler();
    try (var manager =
        compiler.getStandardFileManager(
            diagnostics, java.util.Locale.ROOT, StandardCharsets.UTF_8)) {
      var task =
          (JavacTask)
              compiler.getTask(
                  new StringWriter(),
                  manager,
                  diagnostics,
                  List.of("--release", "25", "-proc:none"),
                  null,
                  List.of(file));
      var units = task.parse();
      var positions = Trees.instance(task).getSourcePositions();
      List<Row> rows = new ArrayList<>();
      for (var unit : units)
        new TreePathScanner<Void, Void>() {
          private String current = "<initializer>";

          @Override
          public Void visitMethod(MethodTree node, Void unused) {
            String previous = current;
            current = node.getName().toString();
            super.visitMethod(node, unused);
            current = previous;
            return null;
          }

          @Override
          public Void visitMethodInvocation(MethodInvocationTree node, Void unused) {
            String name = method(node.getMethodSelect());
            if (Set.of("assertEquals", "assertArrayEquals", "assertSame", "assertNotEquals")
                    .contains(name)
                && node.getArguments().size() >= 2) {
              var expected = node.getArguments().getFirst();
              var actual = node.getArguments().get(1);
              long start = positions.getStartPosition(unit, expected);
              long end = positions.getEndPosition(unit, expected);
              if (start < 0 || end <= start || end > text.length())
                throw new IllegalStateException("source span");
              String hash;
              try {
                hash =
                    HexFormat.of()
                        .formatHex(
                            MessageDigest.getInstance("SHA-256")
                                .digest(
                                    text.substring((int) start, (int) end)
                                        .getBytes(StandardCharsets.UTF_8)));
              } catch (java.security.NoSuchAlgorithmException failure) {
                throw new IllegalStateException(failure);
              }
              rows.add(
                  new Row(
                      path,
                      current,
                      unit.getLineMap().getLineNumber(start),
                      name,
                      expected.getKind().name(),
                      calls(expected),
                      calls(actual),
                      constructors(expected),
                      hash));
            }
            return super.visitMethodInvocation(node, unused);
          }
        }.scan(unit, null);
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalStateException("syntax diagnostic; no source text output");
      return rows;
    }
  }

  private static void selftest() throws Exception {
    var rows =
        parse(
            "metadata-vector",
            "class F { void t() { assertEquals(7,f()); assertEquals(f(),g());"
                + "assertEquals(f(),f()); assertArrayEquals(v,g()); assertEquals(new V(7),g());"
                + "assertEquals(Codec.standard().encode(x),g()); }}");
    if (rows.size() != 6
        || !rows.get(0).kind().equals("INT_LITERAL")
        || !rows.get(0).expected().isEmpty()
        || !rows.get(1).expected().equals(Set.of("f"))
        || rows.get(1).shared() != 0
        || rows.get(2).shared() != 1
        || !rows.get(3).kind().equals("IDENTIFIER")
        || !rows.get(3).expected().isEmpty()
        || !rows.get(4).constructors().equals(Set.of("V"))
        || !rows.get(5).expected().equals(Set.of("Codec.standard().encode", "Codec.standard")))
      throw new IllegalStateException("six independent syntax vectors");
    System.out.println("METADATA_VECTORS\t6");
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("fixed snapshot and exact source list");
    selftest();
    Path root = Path.of(args[0]).toRealPath();
    var paths = Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8);
    if (paths.size() != 789 || new TreeSet<>(paths).size() != 789)
      throw new IllegalArgumentException("789 sources");
    int count = 0;
    for (String relative : paths) {
      if (!relative.matches(
          "src/schubert-nk-(api|web|batch|bootstrap)/src/test/java/[A-Za-z0-9_$/]+\\.java"))
        throw new IllegalArgumentException("closed source scope");
      Path file = root.resolve(relative);
      if (Files.isSymbolicLink(file) || !file.toRealPath().startsWith(root))
        throw new IllegalStateException("regular source");
      var rows = parse(relative, Files.readString(file, StandardCharsets.UTF_8));
      for (var row : rows) {
        System.out.println(row.tsv());
        count++;
      }
    }
    System.out.println("SUMMARY\t" + paths.size() + "\t" + count);
  }
}
