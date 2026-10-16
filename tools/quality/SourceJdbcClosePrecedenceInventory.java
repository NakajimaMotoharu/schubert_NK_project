import com.sun.source.tree.*;
import com.sun.source.util.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import javax.lang.model.element.*;
import javax.lang.model.type.DeclaredType;
import javax.tools.*;

/** Exact typed SSC063/199 direct-close shape only; no quality-gate exemption. */
final class SourceJdbcClosePrecedenceInventory {
  private static final Set<String> CAUGHT =
      Set.of("java.sql.SQLException", "java.lang.RuntimeException", "java.lang.Error");

  private static Tree strip(Tree t) {
    while (t instanceof ParenthesizedTree p) t = p.getExpression();
    return t;
  }

  private static Element element(Trees trees, CompilationUnitTree unit, Tree tree) {
    TreePath path = TreePath.getPath(unit, strip(tree));
    return path == null ? null : trees.getElement(path);
  }

  private static StatementTree only(BlockTree b) {
    return b != null && b.getStatements().size() == 1 ? b.getStatements().getFirst() : null;
  }

  private static boolean throwableType(VariableElement variable) {
    return variable.asType() instanceof DeclaredType declared
        && declared.asElement() instanceof TypeElement type
        && type.getQualifiedName().contentEquals("java.lang.Throwable");
  }

  private static boolean caught(Trees trees, CompilationUnitTree unit, CatchTree c) {
    if (!(c.getParameter().getType() instanceof UnionTypeTree union)) return false;
    Set<String> names = new HashSet<>();
    for (Tree alternative : union.getTypeAlternatives()) {
      var type = trees.getTypeMirror(TreePath.getPath(unit, alternative));
      if (type == null || !names.add(type.toString())) return false;
    }
    return names.equals(CAUGHT);
  }

  private static String fact(Trees trees, CompilationUnitTree unit, TryTree parent) {
    BlockTree fin = parent.getFinallyBlock();
    StatementTree inner = only(fin);
    if (inner == null) return null;
    Element guarded = null;
    if (inner instanceof IfTree guard && guard.getElseStatement() == null) {
      Tree condition = strip(guard.getCondition());
      if (!(condition instanceof BinaryTree b) || b.getKind() != Tree.Kind.NOT_EQUAL_TO) return null;
      if (strip(b.getRightOperand()).getKind() != Tree.Kind.NULL_LITERAL) return null;
      guarded = element(trees, unit, b.getLeftOperand());
      if (!(guard.getThenStatement() instanceof BlockTree block)) return null;
      inner = only(block);
    }
    if (!(inner instanceof TryTree close) || !close.getResources().isEmpty()
        || close.getFinallyBlock() != null || close.getCatches().size() != 1) return null;
    StatementTree closing = only(close.getBlock());
    if (!(closing instanceof ExpressionStatementTree statement)
        || !(statement.getExpression() instanceof MethodInvocationTree invocation)
        || !(invocation.getMethodSelect() instanceof MemberSelectTree receiver)
        || !invocation.getArguments().isEmpty()) return null;
    Element closeSymbol = element(trees, unit, receiver);
    if (!(closeSymbol instanceof ExecutableElement method)
        || !method.getSimpleName().contentEquals("close")
        || !Set.of("java.sql.Statement", "java.sql.ResultSet").contains(method.getEnclosingElement().toString())
        || method.getModifiers().contains(Modifier.STATIC)) return null;
    Element resource = element(trees, unit, receiver.getExpression());
    if (resource == null || (guarded != null && !resource.equals(guarded))) return null;
    CatchTree secondary = close.getCatches().getFirst();
    if (!caught(trees, unit, secondary)) return null;
    Element secondaryParameter = element(trees, unit, secondary.getParameter());
    StatementTree handling = only(secondary.getBlock());
    if (!(handling instanceof IfTree decision) || decision.getElseStatement() != null) return null;
    Tree condition = strip(decision.getCondition());
    if (!(condition instanceof MethodInvocationTree call) || call.getArguments().size() != 2) return null;
    Element target = element(trees, unit, call.getMethodSelect());
    if (!(target instanceof ExecutableElement helper)
        || !helper.getEnclosingElement().toString().equals("dev.codex.schubert.nk.batch.repository.JdbcResourceFailures")
        || !helper.getSimpleName().contentEquals("replace") || !helper.getModifiers().contains(Modifier.STATIC)
        || !helper.getReturnType().toString().equals("boolean")
        || !helper.getParameters().stream().allMatch(SourceJdbcClosePrecedenceInventory::throwableType)) return null;
    StatementTree then = decision.getThenStatement();
    if (then instanceof BlockTree block) then = only(block);
    if (!(then instanceof ThrowTree thrown)
        || !secondaryParameter.equals(element(trees, unit, thrown.getExpression()))
        || !secondaryParameter.equals(element(trees, unit, call.getArguments().get(1)))) return null;
    Element primary = element(trees, unit, call.getArguments().getFirst());
    if (!(primary instanceof VariableElement variable) || primary.getKind() != ElementKind.LOCAL_VARIABLE
        || !throwableType(variable)) return null;
    Tree declaration = trees.getTree(variable);
    if (!(declaration instanceof VariableTree local) || local.getInitializer() == null
        || local.getInitializer().getKind() != Tree.Kind.NULL_LITERAL) return null;
    if (parent.getCatches().size() != 1) return null;
    CatchTree original = parent.getCatches().getFirst();
    if (!caught(trees, unit, original) || original.getBlock().getStatements().size() != 2) return null;
    var statements = original.getBlock().getStatements();
    if (!(statements.getFirst() instanceof ExpressionStatementTree assignmentStatement)
        || !(assignmentStatement.getExpression() instanceof AssignmentTree assignment)
        || !(statements.getLast() instanceof ThrowTree originalThrow)) return null;
    Element originalParameter = element(trees, unit, original.getParameter());
    if (!primary.equals(element(trees, unit, assignment.getVariable()))
        || !originalParameter.equals(element(trees, unit, assignment.getExpression()))
        || !originalParameter.equals(element(trees, unit, originalThrow.getExpression()))) return null;
    long start = trees.getSourcePositions().getStartPosition(unit, fin);
    long end = trees.getSourcePositions().getEndPosition(unit, fin);
    return unit.getLineMap().getLineNumber(start) + "\t" + unit.getLineMap().getLineNumber(end - 1)
        + "\t" + method.getEnclosingElement() + "\t" + primary.getSimpleName() + "\t" + secondaryParameter.getSimpleName();
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25) throw new IllegalArgumentException("JDK25 root/classpath required");
    Path root = Path.of(args[0]).toRealPath();
    List<Path> files;
    try (var paths = Files.walk(root)) {
      files = paths.filter(p -> p.toString().endsWith(".java")).sorted().toList();
    }
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var compiler = ToolProvider.getSystemJavaCompiler();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics,
          List.of("--release", "25", "-proc:none", "-implicit:none", "-classpath", args[1]), null, manager.getJavaFileObjectsFromPaths(files));
      var units = new ArrayList<CompilationUnitTree>(); task.parse().forEach(units::add); task.analyze();
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) throw new IllegalArgumentException("all actual symbols must resolve");
      Trees trees = Trees.instance(task);
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri()).toRealPath();
        if (!source.startsWith(root)) throw new IllegalArgumentException("source outside root");
        new TreePathScanner<Void, Void>() {
          @Override public Void visitTry(TryTree node, Void unused) {
            String row = fact(trees, unit, node);
            if (row != null) System.out.println("JDBC_CLOSE\t" + root.relativize(source) + "\t" + row);
            return super.visitTry(node, unused);
          }
        }.scan(unit, null);
      }
    }
  }
}
