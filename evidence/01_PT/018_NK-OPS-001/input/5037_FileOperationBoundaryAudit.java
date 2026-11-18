import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.LambdaExpressionTree;
import com.sun.source.tree.MemberReferenceTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** SSC-461 parse-only invocation inventory for already admitted source inputs. */
final class FileOperationBoundaryAudit {
  private static final Set<String> NAMES =
      Set.of(
          "atDirectory",
          "atPartHandle",
          "atReadyHandle",
          "atExistingEntryHandle",
          "createPrivatePart",
          "createPrivateEntry",
          "createPart",
          "atPart",
          "atReady",
          "openDate");
  private static final Set<String> JDBC_METHODS =
      Set.of(
          "prepareStatement",
          "prepareCall",
          "executeQuery",
          "executeUpdate",
          "getConnection",
          "getNextException",
          "commit",
          "rollback");

  public static void main(String[] paths) throws Exception {
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task =
          (JavacTask)
              compiler.getTask(
                  null,
                  manager,
                  diagnostics,
                  List.of("--release", "25", "-proc:none"),
                  null,
                  manager.getJavaFileObjectsFromStrings(List.of(paths)));
      var positions = Trees.instance(task).getSourcePositions();
      int files = 0;
      for (CompilationUnitTree file : task.parse()) {
        String label = Path.of(file.getSourceFile().toUri()).getFileName().toString();
        new TreeScanner<Void, Void>() {
          @Override
          public Void visitMethodInvocation(MethodInvocationTree call, Void unused) {
            if (call.getMethodSelect() instanceof MemberSelectTree method
                && NAMES.contains(method.getIdentifier().toString())) {
              if (call.getArguments().isEmpty()) throw new IllegalStateException("no callback");
              Tree callback = call.getArguments().getLast();
              var names = new TreeSet<String>();
              new TreeScanner<Void, Void>() {
                @Override
                public Void visitMethodInvocation(MethodInvocationTree item, Void ignored) {
                  String selected =
                      item.getMethodSelect() instanceof MemberSelectTree select
                          ? select.getIdentifier().toString()
                          : item.getMethodSelect().toString();
                  names.add(selected);
                  return super.visitMethodInvocation(item, ignored);
                }

                @Override
                public Void visitMemberReference(MemberReferenceTree item, Void ignored) {
                  names.add(item.getName().toString());
                  return super.visitMemberReference(item, ignored);
                }
              }.scan(callback, null);
              String kind =
                  callback instanceof LambdaExpressionTree ? "LAMBDA" : callback.getKind().name();
              boolean directJdbc = names.stream().anyMatch(JDBC_METHODS::contains);
              long row = file.getLineMap().getLineNumber(positions.getStartPosition(file, call));
              System.out.printf(
                  "CALL\t%s\t%d\t%s\t%s\t%s\t%s%n",
                  label, row, method.getIdentifier(), kind, directJdbc, String.join(",", names));
            }
            return super.visitMethodInvocation(call, unused);
          }
        }.scan(file, null);
        files++;
      }
      if (files != paths.length
          || diagnostics.getDiagnostics().stream()
              .anyMatch(x -> x.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalStateException("exact input syntax was not accepted");
      System.out.printf("PARSED\t%d%n", files);
    }
  }
}
