import com.sun.source.tree.BinaryTree;
import com.sun.source.tree.AssignmentTree;
import com.sun.source.tree.CompoundAssignmentTree;
import com.sun.source.tree.ClassTree;
import com.sun.source.tree.LambdaExpressionTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.IfTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePath;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import javax.lang.model.element.Element;
import javax.lang.model.element.ExecutableElement;
import javax.lang.model.element.VariableElement;
import javax.lang.model.type.TypeMirror;
import javax.lang.model.util.Types;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** Narrow facts, not blanket equality/catch-rule exemptions. */
final class SourceSuppressionIdentityInventory {
  private static Element symbol(Trees trees, CompilationUnitTree unit, Tree tree) {
    TreePath path = TreePath.getPath(unit, tree);
    return path == null ? null : trees.getElement(path);
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || Runtime.version().feature() != 25) {
      throw new IllegalArgumentException("JDK25 source root and qualified classpath required");
    }
    Path root = Path.of(args[0]).toRealPath();
    List<Path> files;
    try (var paths = Files.walk(root)) {
      files = paths.filter(p -> p.toString().endsWith(".java")).sorted().toList();
    }
    if (files.isEmpty()) throw new IllegalArgumentException("nonempty source required");
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var compiler = ToolProvider.getSystemJavaCompiler();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task = (JavacTask) compiler.getTask(null, manager, diagnostics,
          List.of("--release", "25", "-proc:none", "-implicit:none", "-classpath", args[1]),
          null, manager.getJavaFileObjectsFromPaths(files));
      var units = new ArrayList<CompilationUnitTree>();
      task.parse().forEach(units::add);
      task.analyze();
      if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) {
        throw new IllegalArgumentException("all actual identity symbols must resolve");
      }
      Trees trees = Trees.instance(task);
      Types types = task.getTypes();
      TypeMirror throwable = task.getElements().getTypeElement("java.lang.Throwable").asType();
      for (var unit : units) {
        Path source = Path.of(unit.getSourceFile().toUri()).toRealPath();
        if (!source.startsWith(root)) throw new IllegalArgumentException("source outside root");
        new TreePathScanner<Void, Void>() {
          @Override public Void visitBinary(BinaryTree node, Void unused) {
            if (node.getKind() != Tree.Kind.NOT_EQUAL_TO) return super.visitBinary(node, unused);
            var left = node.getLeftOperand();
            var right = node.getRightOperand();
            Element a = symbol(trees, unit, left), b = symbol(trees, unit, right);
            if (!(a instanceof VariableElement) || !(b instanceof VariableElement)
                || a.getKind().isField() || b.getKind().isField() || a.equals(b)
                || !types.isSubtype(a.asType(), throwable)
                || !types.isSubtype(b.asType(), throwable)) return super.visitBinary(node, unused);
            TreePath parent = getCurrentPath().getParentPath();
            while (parent != null && !(parent.getLeaf() instanceof IfTree)
                && !(parent.getLeaf() instanceof MethodTree)) parent = parent.getParentPath();
            if (parent == null || !(parent.getLeaf() instanceof IfTree guard)) return super.visitBinary(node, unused);
            // Reject a comparison merely appearing in the body or a negative OR:
            // only a direct/parenthesized positive conjunct can guard the call.
            Tree cursor = node;
            for (TreePath p = getCurrentPath().getParentPath(); p != parent; p = p.getParentPath()) {
              Tree.Kind kind = p.getLeaf().getKind();
              if (kind != Tree.Kind.PARENTHESIZED && kind != Tree.Kind.CONDITIONAL_AND) return super.visitBinary(node, unused);
              cursor = p.getLeaf();
            }
            if (cursor != guard.getCondition()) return super.visitBinary(node, unused);
            boolean[] match = {false}, reassigned = {false};
            var verifier = new TreePathScanner<Void, Void>() {
              @Override public Void visitClass(ClassTree tree, Void u) { return null; }
              @Override public Void visitLambdaExpression(LambdaExpressionTree tree, Void u) { return null; }
              @Override public Void visitAssignment(AssignmentTree assignment, Void u) {
                Element target = symbol(trees, unit, assignment.getVariable());
                if (a.equals(target) || b.equals(target)) reassigned[0] = true;
                return super.visitAssignment(assignment, u);
              }
              @Override public Void visitCompoundAssignment(CompoundAssignmentTree assignment, Void u) {
                Element target = symbol(trees, unit, assignment.getVariable());
                if (a.equals(target) || b.equals(target)) reassigned[0] = true;
                return super.visitCompoundAssignment(assignment, u);
              }
              @Override public Void visitMethodInvocation(MethodInvocationTree call, Void u) {
                if (call.getMethodSelect() instanceof MemberSelectTree select
                    && select.getIdentifier().contentEquals("addSuppressed") && call.getArguments().size() == 1) {
                  Element receiver = symbol(trees, unit, select.getExpression());
                  Element argument = symbol(trees, unit, call.getArguments().getFirst());
                  Element invoked = symbol(trees, unit, select);
                  if (((a.equals(receiver) && b.equals(argument)) || (b.equals(receiver) && a.equals(argument)))
                      && invoked instanceof ExecutableElement method
                      && method.getEnclosingElement().toString().equals("java.lang.Throwable")) match[0] = true;
                }
                return super.visitMethodInvocation(call, u);
              }
            };
            verifier.scan(new TreePath(parent, guard.getCondition()), null);
            verifier.scan(new TreePath(parent, guard.getThenStatement()), null);
            if (match[0] && !reassigned[0]) {
              long start = trees.getSourcePositions().getStartPosition(unit, node);
              long end = trees.getSourcePositions().getEndPosition(unit, node);
              List<String> row = List.of("SELF_SUPPRESSION_GUARD", root.relativize(source).toString(),
                  Long.toString(unit.getLineMap().getLineNumber(start)), Long.toString(unit.getLineMap().getColumnNumber(start)),
                  Long.toString(unit.getLineMap().getLineNumber(end - 1)), Long.toString(unit.getLineMap().getColumnNumber(end - 1)),
                  a.asType().toString(), b.asType().toString(), a.toString(), b.toString());
              if (row.stream().anyMatch(s -> s.indexOf('\t') >= 0 || s.indexOf('\n') >= 0 || s.indexOf('\r') >= 0)) throw new IllegalArgumentException("scalar facts required");
              System.out.println(String.join("\t", row));
            }
            return super.visitBinary(node, unused);
          }
        }.scan(unit, null);
      }
    }
  }
}
