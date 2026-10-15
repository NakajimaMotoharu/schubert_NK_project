import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.ImportTree;
import com.sun.source.tree.MemberReferenceTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.NewClassTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import javax.lang.model.element.Element;
import javax.lang.model.element.Modifier;
import javax.lang.model.element.TypeElement;
import javax.lang.model.util.Elements;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Public compiler semantic binding probe; emits proposals only, never rewrites source. */
final class SourceImportExpansion {
  private record Star(ImportTree tree, String prefix, boolean isStatic, Set<Element> members) {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("root and qualified classpath required");
    Path root = Path.of(args[0]).toRealPath();
    List<Path> paths;
    try (var files = Files.walk(root)) {
      paths = files.filter(p -> p.toString().endsWith(".java")).sorted().toList();
    }
    if (paths.isEmpty()) throw new IllegalArgumentException("empty Java scope");
    var compiler = ToolProvider.getSystemJavaCompiler();
    if (compiler == null || Runtime.version().feature() != 25)
      throw new IllegalStateException("actual JDK25 compiler required");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      JavacTask task =
          (JavacTask)
              compiler.getTask(
                  null,
                  manager,
                  diagnostics,
                  List.of("--release", "25", "-proc:none", "-implicit:none", "-Xlint:none", "-classpath", args[1]),
                  null,
                  manager.getJavaFileObjectsFromPaths(paths));
      var units = new ArrayList<CompilationUnitTree>();
      task.parse().forEach(units::add);
      task.analyze();
      long errors = diagnostics.getDiagnostics().stream().filter(d -> d.getKind() == Diagnostic.Kind.ERROR).count();
      if (errors != 0) {
        for (var d : diagnostics.getDiagnostics())
          if (d.getKind() == Diagnostic.Kind.ERROR)
            System.err.println(d.getCode() + ":" + d.getLineNumber());
        throw new IllegalStateException("unresolved semantic input: " + errors);
      }
      Trees trees = Trees.instance(task);
      Elements elements = task.getElements();
      units.sort(Comparator.comparing(u -> u.getSourceFile().toUri().toString()));
      for (var unit : units) {
        String relative = root.relativize(Path.of(unit.getSourceFile().toUri())).toString();
        if (relative.indexOf('\t') >= 0 || relative.indexOf('\n') >= 0)
          throw new IllegalArgumentException("unsafe source coordinate");
        var stars = new ArrayList<Star>();
        var additions = new HashMap<Star, Set<String>>();
        for (var item : unit.getImports()) {
          String qualified = item.getQualifiedIdentifier().toString();
          if (!qualified.endsWith(".*")) continue;
          String prefix = qualified.substring(0, qualified.length() - 2);
          var members = new HashSet<Element>();
          if (item.isStatic()) {
            TypeElement type = elements.getTypeElement(prefix);
            if (type == null) throw new IllegalStateException("unknown static wildcard owner");
            for (var member : elements.getAllMembers(type))
              if (member.getModifiers().contains(Modifier.STATIC)) members.add(member);
          }
          var star = new Star(item, prefix, item.isStatic(), members);
          stars.add(star);
          additions.put(star, new TreeSet<>());
        }
        var bindings = new StringBuilder();
        new TreePathScanner<Void, Void>() {
          private void binding(TreePath path) {
            Element e = trees.getElement(path);
            if (e == null) return;
            bindings.append(e.getKind()).append(':').append(e.getEnclosingElement()).append(':').append(e).append('\n');
          }

          @Override
          public Void visitImport(ImportTree tree, Void unused) {
            return null;
          }

          @Override
          public Void visitIdentifier(IdentifierTree tree, Void unused) {
            binding(getCurrentPath());
            Element element = trees.getElement(getCurrentPath());
            if (element != null && tree.getName().contentEquals(element.getSimpleName())) {
              for (Star star : stars) {
                if (star.isStatic() && star.members().contains(element)) {
                  additions.get(star).add("import static " + star.prefix() + "." + element.getSimpleName() + ";");
                } else if (!star.isStatic() && element instanceof TypeElement type) {
                  Element parent = type.getEnclosingElement();
                  String parentName = parent instanceof TypeElement t ? t.getQualifiedName().toString() : parent.toString();
                  if (parentName.equals(star.prefix()))
                    additions.get(star).add("import " + type.getQualifiedName() + ";");
                }
              }
            }
            return super.visitIdentifier(tree, unused);
          }

          @Override
          public Void visitMemberSelect(MemberSelectTree tree, Void unused) {
            binding(getCurrentPath());
            return super.visitMemberSelect(tree, unused);
          }

          @Override
          public Void visitMemberReference(MemberReferenceTree tree, Void unused) {
            binding(getCurrentPath());
            return super.visitMemberReference(tree, unused);
          }

          @Override
          public Void visitNewClass(NewClassTree tree, Void unused) {
            binding(getCurrentPath());
            return super.visitNewClass(tree, unused);
          }
        }.scan(unit, null);
        System.out.println("FILE\t" + relative);
        System.out.println("BINDINGS\t" + HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bindings.toString().getBytes(StandardCharsets.UTF_8))));
        String declarations = unit.getPackageAnnotations() + ":" + unit.getPackageName() + ":" + unit.getTypeDecls();
        System.out.println("DECLARATIONS\t" + HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(declarations.getBytes(StandardCharsets.UTF_8))));
        for (Star star : stars) {
          long start = trees.getSourcePositions().getStartPosition(unit, star.tree());
          long end = trees.getSourcePositions().getEndPosition(unit, star.tree());
          if (start < 0 || end <= start) throw new IllegalStateException("unknown import position");
          System.out.println("IMPORT\t" + start + "\t" + end + "\t" + String.join(" ", additions.get(star)));
        }
      }
    }
  }
}
