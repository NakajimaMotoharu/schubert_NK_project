import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.EnhancedForLoopTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.MemberReferenceTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.NewClassTree;
import com.sun.source.tree.Tree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Fixed explicit Test set, source-only structural wait inventory; never load or execute Tests. */
public final class TestWaitCandidateAstCheck {
  private TestWaitCandidateAstCheck() {}
  private static String safe(Tree tree) {
    if (tree instanceof IdentifierTree id) return id.getName().toString();
    if (tree instanceof MemberSelectTree m) return safe(m.getExpression()) + "." + m.getIdentifier();
    return "EXPR";
  }
  public static void main(String[] args) throws Exception {
    Path root = Path.of(args[0]).toAbsolutePath();
    List<String> names = new ArrayList<>();
    for (int i = 1; i < args.length; i++) {
      String name = args[i];
      if (!name.startsWith("src/") || !name.contains("/src/test/java/")
          || name.contains("RootFailedStart") || name.contains("SnapshotKeyCloseWitness")
          || name.contains("pg9892_")) throw new IllegalArgumentException("not explicit Test data");
      names.add(root.resolve(name).toString());
    }
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var files = compiler.getStandardFileManager(diagnostics, null, null)) {
      var task = (JavacTask) compiler.getTask(null, files, diagnostics,
          List.of("-proc:none", "--release", "25"), null, files.getJavaFileObjectsFromStrings(names));
      var units = task.parse();
      var trees = Trees.instance(task);
      for (CompilationUnitTree unit : units) {
        String path = root.relativize(Path.of(unit.getSourceFile().toUri())).toString();
        System.out.println("FILE\t" + path);
        for (var item : unit.getImports()) {
          if (!item.isStatic()) System.out.println("IMPORT\t" + path + "\t" + item.getQualifiedIdentifier());
        }
        new TreePathScanner<Void, Void>() {
          private String owner() {
            List<String> names = new ArrayList<>();
            for (TreePath p = getCurrentPath(); p != null; p = p.getParentPath()) {
              if (p.getLeaf() instanceof ClassTree cl && !cl.getSimpleName().isEmpty()) names.add(cl.getSimpleName().toString());
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
          private long line(Tree node) { return unit.getLineMap().getLineNumber(trees.getSourcePositions().getStartPosition(unit, node)); }
          @Override public Void visitVariable(VariableTree node, Void unused) {
            String init = "NONE";
            if (node.getInitializer() instanceof NewClassTree n) init = "NEW:" + n.getIdentifier();
            else if (node.getInitializer() instanceof MethodInvocationTree call) init = "CALL:" + safe(call.getMethodSelect());
            else if (node.getInitializer() instanceof IdentifierTree id) init = "ALIAS:" + id.getName();
            TreePath parent = getCurrentPath().getParentPath();
            if (parent != null && parent.getLeaf() instanceof EnhancedForLoopTree loop && loop.getVariable() == node) init = "ITER:" + safe(loop.getExpression());
            System.out.println("VAR\t" + path + "\t" + owner() + "\t" + method() + "\t"
                + node.getName() + "\t" + node.getType() + "\t" + init + "\t" + line(node));
            return super.visitVariable(node, unused);
          }
          @Override public Void visitMethodInvocation(MethodInvocationTree node, Void unused) {
            Tree select = node.getMethodSelect();
            String name = select instanceof MemberSelectTree m ? m.getIdentifier().toString() : safe(select);
            if (name.equals("get") || name.equals("join")) {
              String receiver = select instanceof MemberSelectTree m ? safe(m.getExpression()) : "IMPLICIT";
              long nameOffset = trees.getSourcePositions().getEndPosition(unit, select) - name.length();
              System.out.println("CALL\t" + path + "\t" + owner() + "\t" + method() + "\t"
                  + receiver + "\t" + name + "\t" + node.getArguments().size() + "\t"
                  + unit.getLineMap().getLineNumber(nameOffset) + "\t" + unit.getLineMap().getColumnNumber(nameOffset));
            }
            return super.visitMethodInvocation(node, unused);
          }
          @Override public Void visitMemberReference(MemberReferenceTree node, Void unused) {
            String name = node.getName().toString();
            if (name.equals("get") || name.equals("join")) {
              long nameOffset = trees.getSourcePositions().getEndPosition(unit, node) - name.length();
              System.out.println("REF\t" + path + "\t" + owner() + "\t" + method() + "\t"
                  + safe(node.getQualifierExpression()) + "\t" + name + "\tREFERENCE\t"
                  + unit.getLineMap().getLineNumber(nameOffset) + "\t" + unit.getLineMap().getColumnNumber(nameOffset));
            }
            return super.visitMemberReference(node, unused);
          }
        }.scan(unit, null);
      }
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) throw new IllegalStateException("parse errors");
    }
  }
}
