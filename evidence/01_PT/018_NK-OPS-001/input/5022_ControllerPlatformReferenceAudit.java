import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.ImportTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.SourcePositions;
import com.sun.source.util.TreeScanner;
import com.sun.source.util.Trees;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.ToolProvider;

/** F02 / SYS-005 / SS311 §5.2: explicit source references only. */
final class ControllerPlatformReferenceAudit {
  private static final String PACKAGE = "dev.codex.schubert.nk.web.controller";
  private static final List<String> DATABASE =
      List.of("java.sql.", "javax.sql.", "org.springframework.jdbc.", "com.zaxxer.hikari.");
  private static final List<String> MESSAGING =
      List.of("jakarta.jms.", "javax.jms.", "org.springframework.jms.", "org.apache.artemis.");
  private static final List<String> FILESYSTEM =
      List.of(
          "java.nio.file.",
          "java.nio.channels.FileChannel",
          "java.nio.channels.AsynchronousFileChannel",
          "dev.codex.schubert.nk.storage.");
  private static final Set<String> FILE_TYPES =
      Set.of(
          "File",
          "FileDescriptor",
          "FileInputStream",
          "FileOutputStream",
          "FileReader",
          "FileWriter",
          "RandomAccessFile");

  public static void main(String[] args) throws Exception {
    if (args.length == 0)
      throw new IllegalArgumentException("explicit controller sources required");
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    try (var files = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8)) {
      var task =
          (JavacTask)
              compiler.getTask(
                  null,
                  files,
                  diagnostics,
                  List.of("-proc:none", "--release", "25"),
                  null,
                  files.getJavaFileObjectsFromStrings(Arrays.asList(args)));
      SourcePositions positions = Trees.instance(task).getSourcePositions();
      int seen = 0;
      for (CompilationUnitTree source : task.parse()) {
        if (!source.getPackageName().toString().equals(PACKAGE))
          throw new IllegalArgumentException("expected controller package");
        var audit = new Audit(source, positions);
        audit.scan(source, null);
        audit.write();
        seen++;
      }
      if (seen != args.length
          || diagnostics.getDiagnostics().stream()
              .anyMatch(diagnostic -> diagnostic.getKind() == Diagnostic.Kind.ERROR))
        throw new IllegalStateException("full source parse failed");
    }
  }

  private static final class Audit extends TreeScanner<Void, Void> {
    private final CompilationUnitTree source;
    private final SourcePositions positions;
    private final Set<String> findings = new TreeSet<>();
    private int imports;
    private int qualifiedSelections;

    Audit(CompilationUnitTree source, SourcePositions positions) {
      this.source = source;
      this.positions = positions;
    }

    @Override
    public Void visitImport(ImportTree tree, Void unused) {
      imports++;
      classify(tree.getQualifiedIdentifier().toString(), positions.getStartPosition(source, tree));
      return null;
    }

    @Override
    public Void visitMemberSelect(MemberSelectTree tree, Void unused) {
      qualifiedSelections++;
      classify(tree.toString(), positions.getStartPosition(source, tree));
      return super.visitMemberSelect(tree, unused);
    }

    private void classify(String reference, long position) {
      String group = classifyPlatform(reference);
      if (group != null) findings.add(group + "\t" + source.getLineMap().getLineNumber(position));
    }

    private void write() {
      String path = source.getSourceFile().toUri().getPath();
      String name = path.substring(path.lastIndexOf('/') + 1);
      System.out.printf(
          "CONTROLLER\t%s\t%d\t%d\t%d%n", name, imports, qualifiedSelections, findings.size());
      for (String finding : findings) System.out.println("REFERENCE\t" + name + "\t" + finding);
    }
  }

  private static String classifyPlatform(String reference) {
    if (DATABASE.stream().anyMatch(reference::startsWith)) return "JDBC";
    if (MESSAGING.stream().anyMatch(reference::startsWith)) return "JMS";
    if (FILESYSTEM.stream().anyMatch(reference::startsWith)) return "FILESYSTEM";
    if (!reference.startsWith("java.io.")) return null;
    String ioName = reference.substring("java.io.".length()).split("\\.", 2)[0];
    return FILE_TYPES.contains(ioName) || ioName.equals("*") ? "FILESYSTEM" : null;
  }
}
