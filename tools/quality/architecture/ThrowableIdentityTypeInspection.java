import com.sun.source.tree.BinaryTree;
import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import javax.lang.model.type.TypeKind;
import javax.lang.model.type.TypeMirror;
import javax.lang.model.util.Types;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.FileObject;
import javax.tools.ForwardingJavaFileManager;
import javax.tools.JavaFileManager.Location;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

/** Read-only type inspection. Never generate a Product class or call any inspected method. */
public final class ThrowableIdentityTypeInspection {
  private ThrowableIdentityTypeInspection() {}

  private record Point(String id, String relative, Path source, long line, long column) {}

  private static String clean(String text) {
    return text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
  }

  private static String throwable(Types types, TypeMirror candidate, TypeMirror base) {
    if (candidate == null
        || candidate.getKind() == TypeKind.ERROR
        || candidate.getKind() == TypeKind.NONE) return "UNKNOWN";
    if (candidate.getKind().isPrimitive() || candidate.getKind() == TypeKind.NULL) return "NO";
    try {
      return types.isSubtype(types.erasure(candidate), types.erasure(base)) ? "YES" : "NO";
    } catch (IllegalArgumentException unsupported) {
      return "UNKNOWN";
    }
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 4)
      throw new IllegalArgumentException("root, frozen rows, classpath, empty processor path");
    Path root = Path.of(args[0]).toRealPath();
    Path empty = Path.of(args[3]);
    try (var files = Files.list(empty)) {
      if (files.findAny().isPresent())
        throw new IllegalArgumentException("empty processor path required");
    }
    List<Point> points = new ArrayList<>();
    Map<Path, List<Point>> byFile = new LinkedHashMap<>();
    Map<String, List<String>> results = new LinkedHashMap<>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 4 || !row[0].matches("PMD-[0-9]{5}"))
        throw new IllegalArgumentException("fixed diagnostic row");
      Path source = root.resolve(row[1]).normalize();
      if (!row[1].matches(
              "src/schubert-nk-(api|web|batch|bootstrap|protocol|storage)/src/main/java/.+\\.java")
          || !source.startsWith(root.resolve("src"))
          || Files.isSymbolicLink(source)
          || !Files.isRegularFile(source)
          || results.containsKey(row[0]))
        throw new IllegalArgumentException("unique public Main input");
      Point point =
          new Point(row[0], row[1], source, Long.parseLong(row[2]), Long.parseLong(row[3]));
      if (point.line() <= 0 || point.column() <= 0)
        throw new IllegalArgumentException("positive source position");
      points.add(point);
      byFile.computeIfAbsent(source, ignored -> new ArrayList<>()).add(point);
      results.put(point.id(), new ArrayList<>());
    }
    if (points.size() != 56 || byFile.size() != 36)
      throw new IllegalArgumentException("frozen56/36");
    var compiler = ToolProvider.getSystemJavaCompiler();
    if (compiler == null) throw new IllegalStateException("JDK compiler required");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (StandardJavaFileManager standard =
        compiler.getStandardFileManager(diagnostics, Locale.ROOT, StandardCharsets.UTF_8)) {
      // Borrowed view only; standard above owns the single physical close.
      var manager =
          new ForwardingJavaFileManager<StandardJavaFileManager>(standard) {
            @Override
            public JavaFileObject getJavaFileForOutput(
                Location location, String name, JavaFileObject.Kind kind, FileObject sibling)
                throws IOException {
              throw new IOException("class generation is forbidden in static type inspection");
            }
          };
      var task =
          (JavacTask)
              compiler.getTask(
                  null,
                  manager,
                  diagnostics,
                  List.of(
                      "--release",
                      "25",
                      "-proc:none",
                      "-implicit:none",
                      "-sourcepath",
                      empty.toString(),
                      "-processorpath",
                      empty.toString(),
                      "-classpath",
                      args[2]),
                  null,
                  standard.getJavaFileObjectsFromPaths(byFile.keySet()));
      List<CompilationUnitTree> units = new ArrayList<>();
      task.parse().forEach(units::add);
      task.analyze();
      long errors =
          diagnostics.getDiagnostics().stream()
              .filter(d -> d.getKind() == Diagnostic.Kind.ERROR)
              .count();
      System.out.println("DIAGNOSTIC_ERRORS\t" + errors);
      if (errors != 0) {
        for (var diagnostic : diagnostics.getDiagnostics())
          if (diagnostic.getKind() == Diagnostic.Kind.ERROR)
            System.err.println(
                "STATIC_DIAGNOSTIC\t" + diagnostic.getCode() + "\t" + diagnostic.getLineNumber());
        System.exit(2);
      }
      Trees trees = Trees.instance(task);
      Types types = task.getTypes();
      TypeMirror base = task.getElements().getTypeElement("java.lang.Throwable").asType();
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri()).toAbsolutePath().normalize();
        var requests = byFile.get(source);
        if (requests == null) throw new IllegalStateException("foreign compilation unit");
        new TreePathScanner<Void, Void>() {
          @Override
          public Void visitBinary(BinaryTree node, Void unused) {
            if (node.getKind() == Tree.Kind.EQUAL_TO || node.getKind() == Tree.Kind.NOT_EQUAL_TO) {
              long start = trees.getSourcePositions().getStartPosition(unit, node);
              long end = trees.getSourcePositions().getEndPosition(unit, node);
              if (start >= 0 && end > start) {
                for (var point : requests) {
                  long position = unit.getLineMap().getPosition(point.line(), point.column());
                  if (position < start || position >= end) continue;
                  TypeMirror left =
                      trees.getTypeMirror(new TreePath(getCurrentPath(), node.getLeftOperand()));
                  TypeMirror right =
                      trees.getTypeMirror(new TreePath(getCurrentPath(), node.getRightOperand()));
                  String method = "";
                  List<String> owners = new ArrayList<>();
                  for (TreePath p = getCurrentPath(); p != null; p = p.getParentPath()) {
                    if (method.isEmpty() && p.getLeaf() instanceof MethodTree m)
                      method = m.getName().toString();
                    if (p.getLeaf() instanceof ClassTree c && !c.getSimpleName().isEmpty())
                      owners.addFirst(c.getSimpleName().toString());
                  }
                  results
                      .get(point.id())
                      .add(
                          String.join(
                              "\t",
                              "TYPE",
                              point.id(),
                              point.relative(),
                              Long.toString(unit.getLineMap().getLineNumber(start)),
                              Long.toString(unit.getLineMap().getColumnNumber(start)),
                              node.getKind().name(),
                              clean(left == null ? "UNKNOWN" : left.toString()),
                              clean(right == null ? "UNKNOWN" : right.toString()),
                              throwable(types, left, base),
                              throwable(types, right, base),
                              String.join(".", owners),
                              method));
                }
              }
            }
            return super.visitBinary(node, unused);
          }
        }.scan(unit, null);
      }
    }
    System.out.println("STATIC_ONLY_NO_GENERATE\ttrue");
    for (var point : points) {
      var hits = results.get(point.id());
      if (hits.size() == 1) System.out.println(hits.getFirst());
      else System.out.println("UNRESOLVED\t" + point.id() + "\t" + hits.size());
    }
  }
}
