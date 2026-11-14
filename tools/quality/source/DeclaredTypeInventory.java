package dev.codex.schubert.quality;

import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** YKT2431 source-only AST inventory. Never calls analyze/generate or resolves business types. */
public final class DeclaredTypeInventory {
  private DeclaredTypeInventory() {}

  public static void main(String[] args) throws Exception {
    if (args.length < 2)
      throw new IllegalArgumentException("owned empty path and explicit Java sources required");
    Path empty = Path.of(args[0]);
    if (!Files.isDirectory(empty)) throw new IllegalArgumentException("empty path absent");
    try (var members = Files.list(empty)) {
      if (members.findAny().isPresent())
        throw new IllegalArgumentException("classpath must be empty");
    }
    for (int index = 1; index < args.length; index++)
      if (!args[index].endsWith(".java") || Files.isSymbolicLink(Path.of(args[index])))
        throw new IllegalArgumentException("regular explicit Java source required");
    var compiler = ToolProvider.getSystemJavaCompiler();
    if (compiler == null) throw new IllegalStateException("full JDK required");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var files =
        compiler.getStandardFileManager(diagnostics, Locale.ROOT, StandardCharsets.UTF_8)) {
      var input = files.getJavaFileObjectsFromStrings(Arrays.asList(args).subList(1, args.length));
      var options =
          List.of(
              "-proc:none",
              "-classpath",
              empty.toString(),
              "-sourcepath",
              empty.toString(),
              "-processorpath",
              empty.toString(),
              "--release",
              "25");
      var task = (JavacTask) compiler.getTask(null, files, diagnostics, options, null, input);
      var trees = Trees.instance(task);
      int units = 0;
      int[] types = {0};
      // Deliberately only parse. No task.analyze(), task.generate(), getElement() or type lookup.
      for (CompilationUnitTree unit : task.parse()) {
        units++;
        String source = Path.of(unit.getSourceFile().toUri()).toString();
        String pkg = unit.getPackageName() == null ? "" : unit.getPackageName().toString();
        new TreePathScanner<Void, Boolean>() {
          private final ArrayList<String> enclosing = new ArrayList<>();

          @Override
          public Void visitClass(ClassTree node, Boolean inheritedStable) {
            String name = node.getSimpleName().toString();
            Tree parent = getCurrentPath().getParentPath().getLeaf();
            boolean member = parent instanceof CompilationUnitTree || parent instanceof ClassTree;
            boolean stable = Boolean.TRUE.equals(inheritedStable) && member && !name.isEmpty();
            long line =
                unit.getLineMap()
                    .getLineNumber(trees.getSourcePositions().getStartPosition(unit, node));
            enclosing.add(name.isEmpty() ? "anonymous@" + line : name);
            try {
              if (node.getKind() == Tree.Kind.RECORD || node.getKind() == Tree.Kind.ENUM) {
                String qualified = (pkg.isEmpty() ? "" : pkg + ".") + String.join(".", enclosing);
                String binary =
                    stable ? (pkg.isEmpty() ? "" : pkg + ".") + String.join("$", enclosing) : "-";
                System.out.println(
                    "TYPE\t"
                        + source
                        + "\t"
                        + line
                        + "\t"
                        + node.getKind()
                        + "\t"
                        + qualified
                        + "\t"
                        + binary
                        + "\t"
                        + (stable ? "MEMBER" : "LOCAL_OR_ANONYMOUS_UNBOUND"));
                types[0]++;
              }
              return super.visitClass(node, stable);
            } finally {
              enclosing.removeLast();
            }
          }
        }.scan(unit, true);
      }
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalArgumentException("source syntax error; no inventory acceptance");
      System.out.println("TOTAL\t" + units + "\t" + types[0]);
    }
  }
}
