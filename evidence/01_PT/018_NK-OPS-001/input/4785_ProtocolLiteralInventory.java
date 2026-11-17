import com.sun.source.tree.*;
import com.sun.source.util.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import javax.tools.*;

/** Independent parse-only literal/field-initializer inventory, no production execution. */
public final class ProtocolLiteralInventory {
  private static String b(String value) {
    return Base64.getEncoder().encodeToString(value.getBytes(StandardCharsets.UTF_8));
  }
  public static void main(String[] args) throws Exception {
    JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
    try (StandardJavaFileManager manager = compiler.getStandardFileManager(null, null, StandardCharsets.UTF_8)) {
      JavacTask task = (JavacTask) compiler.getTask(null, manager, null, List.of("-proc:none"), null,
          manager.getJavaFileObjects(args));
      for (CompilationUnitTree unit : task.parse()) {
        new TreePathScanner<Void, Void>() {
          @Override public Void visitLiteral(LiteralTree t, Void p) {
            System.out.println("LITERAL\t" + t.getKind() + "\t" + b(String.valueOf(t.getValue())));
            return super.visitLiteral(t,p);
          }
          @Override public Void visitVariable(VariableTree t, Void p) {
            if (getCurrentPath().getParentPath().getLeaf() instanceof ClassTree && t.getInitializer()!=null)
              System.out.println("FIELD\t" + t.getName() + "\t" + b(t.getInitializer().toString()));
            return super.visitVariable(t,p);
          }
        }.scan(unit,null);
      }
    }
  }
}
