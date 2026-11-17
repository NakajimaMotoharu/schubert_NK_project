import com.sun.source.tree.*;
import com.sun.source.util.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import javax.tools.*;

/** Parse-only source syntax inventory: no analyze/generate, no production class definition. */
public final class ProtocolDispatchSyntax {
  private static String b(String s) {
    return Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8));
  }
  public static void main(String[] args) throws Exception {
    JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
    try (StandardJavaFileManager files = compiler.getStandardFileManager(null, null, StandardCharsets.UTF_8)) {
      JavacTask task = (JavacTask) compiler.getTask(null, files, null, List.of("-proc:none"), null,
          files.getJavaFileObjects(args));
      Trees trees = Trees.instance(task);
      for (CompilationUnitTree unit : task.parse()) {
        String source = Files.readString(Path.of(unit.getSourceFile().toUri()));
        SourcePositions positions = trees.getSourcePositions();
        new TreePathScanner<Void, Void>() {
          long start(Tree t) { return positions.getStartPosition(unit, t); }
          long end(Tree t) { return positions.getEndPosition(unit, t); }
          String text(Tree t) { return source.substring((int) start(t), (int) end(t)); }
          void emit(Tree node, ExpressionTree selector, List<? extends CaseTree> cases) {
            Tree parent = getCurrentPath().getParentPath().getLeaf();
            Tree replace = parent instanceof ReturnTree || parent instanceof VariableTree ? parent : node;
            String variable = parent instanceof VariableTree v ? v.getType() + " " + v.getName() : "";
            System.out.println("SW\t"+b(unit.getSourceFile().getName())+"\t"+start(replace)+"\t"+end(replace)
                +"\t"+parent.getKind()+"\t"+b(variable)+"\t"+b(text(selector)));
            for (CaseTree c : cases) {
              List<? extends ExpressionTree> labels = c.getExpressions();
              String label = String.join("\n", labels.stream().map(Object::toString).toList());
              Tree body = c.getBody();
              System.out.println("CASE\t"+b(label)+"\t"+body.getKind()+"\t"+b(text(body)));
            }
            System.out.println("END");
          }
          @Override public Void visitSwitchExpression(SwitchExpressionTree t, Void p) {
            emit(t, t.getExpression(), t.getCases()); return super.visitSwitchExpression(t, p);
          }
          @Override public Void visitSwitch(SwitchTree t, Void p) {
            emit(t, t.getExpression(), t.getCases()); return super.visitSwitch(t, p);
          }
        }.scan(unit, null);
      }
    }
  }
}
