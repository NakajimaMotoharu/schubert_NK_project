import com.sun.source.tree.*;
import com.sun.source.util.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import javax.lang.model.element.*;
import javax.tools.*;

/** Symbol facts only: inline private final Object used exclusively as a monitor, never a waiver. */
final class SourcePrivateMonitorInventory {
  private record Block(long start, long end, long bodyStart, long bodyEnd,
      long expressionStart, long expressionEnd, String owner, String method) {}

  private static final class Field {
    final String path;
    final String owner;
    final String name;
    final long typeStart;
    final long typeEnd;
    final long initStart;
    final long initEnd;
    final List<Block> blocks = new ArrayList<>();
    int otherReads;
    Field(String path, String owner, String name, long typeStart, long typeEnd,
        long initStart, long initEnd) {
      this.path = path; this.owner = owner; this.name = name;
      this.typeStart = typeStart; this.typeEnd = typeEnd;
      this.initStart = initStart; this.initEnd = initEnd;
    }
  }

  private static Tree strip(Tree tree) {
    while (tree instanceof ParenthesizedTree p) tree = p.getExpression();
    return tree;
  }

  private static SynchronizedTree monitor(TreePath path) {
    Tree original = path.getLeaf();
    TreePath parent = path.getParentPath();
    while (parent != null && parent.getLeaf() instanceof ParenthesizedTree) parent = parent.getParentPath();
    return parent != null && parent.getLeaf() instanceof SynchronizedTree sync
        && strip(sync.getExpression()) == original ? sync : null;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25) throw new IllegalArgumentException("JDK25 fixed Main root/classpath required");
    Path root = Path.of(args[0]).toRealPath();
    List<Path> files;
    try (var paths = Files.walk(root)) {
      files = paths.filter(p -> p.toString().endsWith(".java")).sorted().toList();
    }
    if (files.isEmpty()) throw new IllegalArgumentException("nonempty Main inputs");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var compiler = ToolProvider.getSystemJavaCompiler();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics,
          List.of("--release", "25", "-proc:none", "-implicit:none", "-classpath", args[1]),
          null, manager.getJavaFileObjectsFromPaths(files));
      var units = new ArrayList<CompilationUnitTree>(); task.parse().forEach(units::add); task.analyze();
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) throw new IllegalArgumentException("every source symbol must resolve");
      Trees trees = Trees.instance(task); var elements = task.getElements();
      var positions = trees.getSourcePositions();
      Map<Element, Field> fields = new LinkedHashMap<>();
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri()).toRealPath();
        if (!source.startsWith(root)) throw new IllegalArgumentException("outside fixed source root");
        String relative = root.relativize(source).toString();
        new TreePathScanner<Void, Void>() {
          @Override public Void visitVariable(VariableTree node, Void unused) {
            Element symbol = trees.getElement(getCurrentPath());
            if (symbol instanceof VariableElement variable && variable.getKind() == ElementKind.FIELD
                && variable.getModifiers().containsAll(Set.of(Modifier.PRIVATE, Modifier.FINAL))
                && variable.asType().toString().equals("java.lang.Object")
                && node.getInitializer() instanceof NewClassTree init && init.getArguments().isEmpty()
                && init.getClassBody() == null) {
              Element constructor = trees.getElement(TreePath.getPath(unit, init));
              if (constructor instanceof ExecutableElement method
                  && method.getEnclosingElement().toString().equals("java.lang.Object")) {
                fields.put(variable, new Field(relative,
                    elements.getBinaryName((TypeElement) variable.getEnclosingElement()).toString(),
                    variable.getSimpleName().toString(), positions.getStartPosition(unit, node.getType()),
                    positions.getEndPosition(unit, node.getType()), positions.getStartPosition(unit, init.getIdentifier()),
                    positions.getEndPosition(unit, init.getIdentifier())));
              }
            }
            return super.visitVariable(node, unused);
          }
        }.scan(unit, null);
      }
      for (var unit : units) {
        new TreePathScanner<Void, Void>() {
          private void read(boolean stableReceiver) {
            Field field = fields.get(trees.getElement(getCurrentPath()));
            if (field == null) return;
            SynchronizedTree sync = monitor(getCurrentPath());
            if (!stableReceiver || sync == null) { field.otherReads++; return; }
            String owner = "<initializer>", method = "<initializer>";
            for (TreePath p = getCurrentPath(); p != null; p = p.getParentPath()) {
              if (method.equals("<initializer>") && p.getLeaf() instanceof MethodTree) {
                Element value = trees.getElement(p);
                if (value instanceof ExecutableElement executable) method = executable.toString();
              }
              if (p.getLeaf() instanceof ClassTree) {
                Element value = trees.getElement(p);
                if (value instanceof TypeElement type) { owner = elements.getBinaryName(type).toString(); break; }
              }
            }
            Tree expression = strip(sync.getExpression());
            field.blocks.add(new Block(positions.getStartPosition(unit, sync), positions.getEndPosition(unit, sync),
                positions.getStartPosition(unit, sync.getBlock()), positions.getEndPosition(unit, sync.getBlock()),
                positions.getStartPosition(unit, expression), positions.getEndPosition(unit, expression), owner, method));
          }
          @Override public Void visitIdentifier(IdentifierTree node, Void unused) {
            read(true); return super.visitIdentifier(node, unused);
          }
          @Override public Void visitMemberSelect(MemberSelectTree node, Void unused) {
            read(node.getExpression().toString().equals("this"));
            return super.visitMemberSelect(node, unused);
          }
        }.scan(unit, null);
      }
      for (var field : fields.values()) {
        boolean eligible = field.otherReads == 0 && !field.blocks.isEmpty();
        System.out.println("MONITOR_FIELD\t" + field.path + "\t" + field.owner + "\t" + field.name
            + "\t" + field.typeStart + "\t" + field.typeEnd + "\t" + field.initStart + "\t" + field.initEnd
            + "\t" + field.blocks.size() + "\t" + field.otherReads + "\t" + eligible);
        if (!eligible) continue;
        for (var block : field.blocks) {
          if (block.start < 0 || block.end <= block.start || block.bodyStart <= block.start
              || block.bodyEnd > block.end || block.expressionStart < block.start || block.expressionEnd > block.bodyStart) throw new IllegalArgumentException("bounded source spans required");
          System.out.println("MONITOR_BLOCK\t" + field.path + "\t" + field.owner + "\t" + field.name
              + "\t" + block.start + "\t" + block.end + "\t" + block.bodyStart + "\t" + block.bodyEnd
              + "\t" + block.expressionStart + "\t" + block.expressionEnd + "\t" + block.owner + "\t" + block.method);
        }
      }
    }
  }
}
