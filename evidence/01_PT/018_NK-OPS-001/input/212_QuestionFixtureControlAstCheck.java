import com.sun.source.tree.AssignmentTree;
import com.sun.source.tree.BlockTree;
import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.CompoundAssignmentTree;
import com.sun.source.tree.ExpressionTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.LiteralTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.NewClassTree;
import com.sun.source.tree.Tree;
import com.sun.source.tree.TryTree;
import com.sun.source.tree.UnaryTree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import javax.lang.model.element.Modifier;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Fixed Question Test source, parse-only; emits structural metadata without values or execution. */
public final class QuestionFixtureControlAstCheck {
  private static final Set<String> FIELDS = Set.of("failReceipt", "verifyNoTransaction", "afterReply",
      "code", "state", "summary", "answer", "owner", "count", "total", "replyId", "responder");
  private QuestionFixtureControlAstCheck() {}

  public static void main(String[] args) throws Exception {
    Path root = Path.of(args[0]).toAbsolutePath();
    String name = args[1];
    if (!name.equals("src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/QuestionControllerTest.java")) {
      throw new IllegalArgumentException("only fixed Test input");
    }
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
      var task = (JavacTask) compiler.getTask(null, files, diagnostics,
          List.of("-proc:none", "--release", "25"), null,
          files.getJavaFileObjects(root.resolve(name).toFile()));
      var units = task.parse();
      var trees = Trees.instance(task);
      for (CompilationUnitTree unit : units) {
        new TreePathScanner<Void, Void>() {
          private String owner() {
            List<String> names = new ArrayList<>();
            for (TreePath p = getCurrentPath(); p != null; p = p.getParentPath()) {
              if (p.getLeaf() instanceof ClassTree cl && !cl.getSimpleName().isEmpty()) {
                names.add(cl.getSimpleName().toString());
              }
            }
            Collections.reverse(names);
            return String.join(".", names);
          }
          private String method() {
            for (TreePath p = getCurrentPath(); p != null; p = p.getParentPath()) {
              if (p.getLeaf() instanceof MethodTree m) return m.getName().toString();
            }
            return "<field>";
          }
          private long line(Tree node, boolean end) {
            long offset = end ? trees.getSourcePositions().getEndPosition(unit, node) - 1
                : trees.getSourcePositions().getStartPosition(unit, node);
            return unit.getLineMap().getLineNumber(offset);
          }
          private String[] field(ExpressionTree expression) {
            if (expression instanceof MemberSelectTree m && m.getExpression().toString().equals("f")
                && FIELDS.contains(m.getIdentifier().toString())) {
              return new String[] {"f", m.getIdentifier().toString()};
            }
            if (expression instanceof IdentifierTree id && owner().equals("QuestionControllerTest.Fixture")
                && FIELDS.contains(id.getName().toString())) {
              return new String[] {"this", id.getName().toString()};
            }
            return null;
          }
          @Override public Void visitMethod(MethodTree node, Void unused) {
            System.out.println("METHOD\t" + owner() + "\t" + node.getName() + "\t"
                + line(node, false) + "\t" + line(node, true));
            return super.visitMethod(node, unused);
          }
          @Override public Void visitVariable(VariableTree node, Void unused) {
            if (node.getModifiers().getFlags().contains(Modifier.VOLATILE)) {
              System.out.println("FIELD\t" + owner() + "\t" + node.getName() + "\t"
                  + node.getType() + "\t" + line(node, false));
            }
            if (node.getName().contentEquals("f") && node.getInitializer() instanceof NewClassTree init
                && init.getIdentifier().toString().equals("Fixture")) {
              Tree scope = null;
              for (TreePath p = getCurrentPath().getParentPath(); p != null; p = p.getParentPath()) {
                if (p.getLeaf() instanceof TryTree tr && tr.getResources().contains(node)) {
                  scope = tr.getBlock(); break;
                }
                if (p.getLeaf() instanceof BlockTree) { scope = p.getLeaf(); break; }
              }
              if (scope == null) throw new IllegalStateException("unknown local owner scope");
              System.out.println("LOCAL_F\t" + owner() + "\t" + method() + "\t"
                  + line(node, false) + "\t" + line(scope, false) + "\t" + line(scope, true));
            }
            return super.visitVariable(node, unused);
          }
          @Override public Void visitAssignment(AssignmentTree node, Void unused) {
            String[] field = field(node.getVariable());
            if (field != null) {
              String rhs = node.getExpression() instanceof LiteralTree literal
                  && literal.getValue() instanceof Boolean ? literal.getValue().toString() : "OTHER";
              System.out.println("WRITE\t" + owner() + "\t" + method() + "\t" + field[0]
                  + "\t" + field[1] + "\t" + line(node, false) + "\t" + rhs);
            }
            return super.visitAssignment(node, unused);
          }
          @Override public Void visitCompoundAssignment(CompoundAssignmentTree node, Void unused) {
            if (field(node.getVariable()) != null) {
              System.out.println("RMW\t" + owner() + "\t" + method() + "\t" + line(node, false));
            }
            return super.visitCompoundAssignment(node, unused);
          }
          @Override public Void visitUnary(UnaryTree node, Void unused) {
            if (Set.of(Tree.Kind.PREFIX_INCREMENT, Tree.Kind.PREFIX_DECREMENT,
                Tree.Kind.POSTFIX_INCREMENT, Tree.Kind.POSTFIX_DECREMENT).contains(node.getKind())
                && field(node.getExpression()) != null) {
              System.out.println("RMW\t" + owner() + "\t" + method() + "\t" + line(node, false));
            }
            return super.visitUnary(node, unused);
          }
          @Override public Void visitMethodInvocation(MethodInvocationTree node, Void unused) {
            String call = node.getMethodSelect().toString();
            if (Set.of("f.accepting", "f.acceptanceMvc", "pool.submit").contains(call)) {
              System.out.println("CALL\t" + owner() + "\t" + method() + "\t" + call
                  + "\t" + line(node, false));
            }
            if ((call.equals("job.get") || call.equals("future.get")) && node.getArguments().isEmpty()) {
              System.out.println("UNBOUNDED_GET\t" + owner() + "\t" + method() + "\t"
                  + call + "\t" + line(node, false));
            }
            return super.visitMethodInvocation(node, unused);
          }
        }.scan(unit, null);
      }
      if (diagnostics.getDiagnostics().stream().anyMatch(d ->
          d.getKind() == Diagnostic.Kind.ERROR)) throw new IllegalStateException("parse errors");
    }
  }
}
