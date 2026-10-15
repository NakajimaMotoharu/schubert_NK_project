import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.LiteralTree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.LinkOption;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Parse-only mechanical proposals; a separate semantic compiler proves the complete candidate. */
final class SourceDeclarationExpansion {
  private record Edit(int start, int end, String value) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25)
      throw new IllegalArgumentException("JDK25 and distinct input/new output required");
    Path input = Path.of(args[0]).toRealPath();
    Path output = IsolatedSourceOutput.candidate(input, Path.of(args[1]), true);
    Files.createDirectory(output);
    List<Path> paths;
    try (var files = Files.walk(input)) {
      paths = files.filter(p -> p.toString().endsWith(".java")).sorted().toList();
    }
    if (paths.isEmpty()) throw new IllegalArgumentException("empty source scope");
    if (!paths.stream().allMatch(p -> Files.isRegularFile(p, LinkOption.NOFOLLOW_LINKS)))
      throw new IllegalArgumentException("regular source files only");
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics, List.of("--release", "25", "-proc:none"), null, manager.getJavaFileObjectsFromPaths(paths));
      var units = new ArrayList<CompilationUnitTree>();
      task.parse().forEach(units::add);
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalArgumentException("invalid original syntax");
      Trees trees = Trees.instance(task);
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri());
        String raw = Files.readString(source);
        var declarations = new HashMap<Integer, List<VariableTree>>();
        var parents = new HashMap<Integer, String>();
        var edits = new ArrayList<Edit>();
        int[] tabs = {0};
        new TreePathScanner<Void, Void>() {
          @Override
          public Void visitVariable(VariableTree tree, Void unused) {
            int start = Math.toIntExact(trees.getSourcePositions().getStartPosition(unit, tree));
            if (start >= 0) {
              declarations.computeIfAbsent(start, ignored -> new ArrayList<>()).add(tree);
              parents.put(start, getCurrentPath().getParentPath().getLeaf().getKind().name());
            }
            return super.visitVariable(tree, unused);
          }

          @Override
          public Void visitLiteral(LiteralTree tree, Void unused) {
            if (tree.getValue() instanceof String) {
              int start = Math.toIntExact(trees.getSourcePositions().getStartPosition(unit, tree));
              int end = Math.toIntExact(trees.getSourcePositions().getEndPosition(unit, tree));
              String literal = raw.substring(start, end);
              int count = (int) literal.chars().filter(c -> c == '\t').count();
              if (count != 0) {
                tabs[0] += count;
                edits.add(new Edit(start, end, literal.replace("\t", "\\t")));
              }
            }
            return super.visitLiteral(tree, unused);
          }
        }.scan(unit, null);
        int groups = 0;
        int variables = 0;
        int held = 0;
        for (var entry : declarations.entrySet()) {
          var group = entry.getValue();
          if (group.size() < 2) continue;
          int start = entry.getKey();
          int end = group.stream().mapToInt(v -> Math.toIntExact(trees.getSourcePositions().getEndPosition(unit, v))).max().orElseThrow();
          String old = raw.substring(start, end);
          String parent = parents.get(start);
          if (!List.of("CLASS", "INTERFACE", "ENUM", "RECORD", "BLOCK", "CASE").contains(parent)
              || old.contains("/*") || old.contains("//") || old.indexOf('\t') >= 0) {
            held++;
            continue;
          }
          var replacement = new StringBuilder();
          for (var variable : group) {
            if (!replacement.isEmpty()) replacement.append('\n');
            replacement.append(variable);
            if (!variable.toString().endsWith(";")) replacement.append(';');
          }
          edits.add(new Edit(start, end, replacement.toString()));
          groups++;
          variables += group.size();
        }
        edits.sort(Comparator.comparingInt(Edit::start).reversed());
        int limit = raw.length();
        String value = raw;
        for (var edit : edits) {
          if (edit.start() < 0 || edit.start() >= edit.end() || edit.end() > limit)
            throw new IllegalArgumentException("overlapping candidate edits refused");
          value = value.substring(0, edit.start()) + edit.value() + value.substring(edit.end());
          limit = edit.start();
        }
        Path relative = input.relativize(source);
        Path target = output.resolve(relative);
        Files.createDirectories(target.getParent());
        Files.writeString(target, value);
        if (!value.equals(raw) || held != 0)
          System.out.println("CANDIDATE\t" + relative + "\t" + groups + "\t" + variables + "\t" + tabs[0] + "\t" + held);
      }
    }
  }
}
