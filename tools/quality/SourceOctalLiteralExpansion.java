import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.LiteralTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.JavaFileObject;
import javax.tools.DiagnosticCollector;
import javax.tools.ToolProvider;

/** Explicit hexadecimal spelling only; original Java integer type and exact bit value are invariant. */
final class SourceOctalLiteralExpansion {
  record Edit(int start, int end, String replacement) {}
  static void require(boolean value) { if (!value) throw new IllegalArgumentException("exact integer-token contract refused"); }
  public static void main(String[] args) throws Exception {
    require(args.length == 2 && Runtime.version().feature() == 25);
    Path input = Path.of(args[0]).toRealPath();
    Path output = IsolatedSourceOutput.candidate(input, Path.of(args[1]), true);
    List<Path> sources;
    try (var walk = Files.walk(input)) { sources = walk.filter(p -> p.toString().endsWith(".java")).sorted().toList(); }
    require(!sources.isEmpty() && sources.stream().allMatch(p -> Files.isRegularFile(p, LinkOption.NOFOLLOW_LINKS)));
    var compiler = ToolProvider.getSystemJavaCompiler(); var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics, List.of("--release", "25", "-proc:none"), null, manager.getJavaFileObjectsFromPaths(sources));
      var units = new ArrayList<CompilationUnitTree>(); task.parse().forEach(units::add);
      require(diagnostics.getDiagnostics().stream().noneMatch(d -> d.getKind() == Diagnostic.Kind.ERROR));
      Trees trees = Trees.instance(task); var candidates = new java.util.LinkedHashMap<String, String>(); int total = 0;
      for (var unit : units) {
        Path file = Path.of(unit.getSourceFile().toUri()); String raw = Files.readString(file); String relative = input.relativize(file).toString();
        var edits = new ArrayList<Edit>();
        new TreePathScanner<Void, Void>() {
          @Override public Void visitLiteral(LiteralTree literal, Void unused) {
            Object value = literal.getValue();
            if (value instanceof Integer || value instanceof Long) {
              int start = Math.toIntExact(trees.getSourcePositions().getStartPosition(unit, literal));
              int end = Math.toIntExact(trees.getSourcePositions().getEndPosition(unit, literal)); require(start >= 0 && end > start);
              String token = raw.substring(start, end);
              if (token.matches("0[0-7_]+[lL]?")) {
                boolean wide = value instanceof Long; require(wide == token.matches(".*[lL]"));
                String digits = token.replace("_", "").replaceAll("[lL]$", "");
                BigInteger octal = new BigInteger(digits, 8); require(octal.bitLength() <= (wide ? 64 : 32));
                String hex;
                if (wide) { long n = (Long) value; require(octal.longValue() == n); hex = "0x" + Long.toHexString(n) + "L"; }
                else { int n = (Integer) value; require(octal.intValue() == n); hex = "0x" + Integer.toHexString(n); }
                edits.add(new Edit(start, end, hex));
                System.out.println("LITERAL\t" + relative + "\t" + start + "\t" + end + "\t" + token + "\t" + hex + "\t" + (wide ? "LONG" : "INT") + "\t" + value);
              }
            }
            return super.visitLiteral(literal, unused);
          }
        }.scan(unit, null);
        total += edits.size(); String candidate = raw; int limit = raw.length(); edits.sort(Comparator.comparingInt(Edit::start).reversed());
        for (var edit : edits) { require(edit.end() <= limit); candidate = candidate.substring(0, edit.start()) + edit.replacement() + candidate.substring(edit.end()); limit = edit.start(); }
        require(Files.readString(file).equals(raw)); candidates.put(relative, candidate);
      }
      Files.createDirectory(output);
      for (var item : candidates.entrySet()) { Path target = output.resolve(item.getKey()); Files.createDirectories(target.getParent()); Files.writeString(target, item.getValue()); }
      System.out.println("OCTAL\t" + total);
    }
  }
}
