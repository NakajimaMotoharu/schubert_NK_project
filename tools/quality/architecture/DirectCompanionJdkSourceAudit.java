import com.sun.source.tree.*;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import java.io.StringWriter;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.SimpleJavaFileObject;
import javax.tools.ToolProvider;

/** 1902: independent JDK parse-only witness; analyze/generate/call are never invoked. */
public final class DirectCompanionJdkSourceAudit {
  private DirectCompanionJdkSourceAudit() {}

  private static boolean reference(
      CompilationUnitTree unit, String expectedPackage, String target) {
    if (unit.getPackageName() == null || !unit.getPackageName().toString().equals(expectedPackage))
      return false;
    String qualified = expectedPackage + "." + target;
    for (var imported : unit.getImports()) {
      String name = imported.getQualifiedIdentifier().toString();
      if (!imported.isStatic() && name.endsWith("." + target) && !name.equals(qualified))
        return false;
    }
    boolean[] shadow = {false};
    new TreeScanner<Void, Void>() {
      @Override
      public Void visitClass(ClassTree node, Void ignored) {
        if (node.getSimpleName().contentEquals(target)) shadow[0] = true;
        return super.visitClass(node, ignored);
      }

      @Override
      public Void visitVariable(VariableTree node, Void ignored) {
        if (node.getName().contentEquals(target)) shadow[0] = true;
        return super.visitVariable(node, ignored);
      }

      @Override
      public Void visitTypeParameter(TypeParameterTree node, Void ignored) {
        if (node.getName().contentEquals(target)) shadow[0] = true;
        return super.visitTypeParameter(node, ignored);
      }
    }.scan(unit, null);
    if (shadow[0]) return false;
    boolean[] matched = {false};
    new TreeScanner<Void, Boolean>() {
      private void type(Tree tree, boolean inherited) {
        if (tree == null) return;
        switch (tree.getKind()) {
          case IDENTIFIER -> {
            if (!inherited && tree.toString().equals(target)) matched[0] = true;
          }
          case MEMBER_SELECT -> {
            String name = tree.toString();
            if (name.equals(qualified)
                || name.startsWith(qualified + ".")
                || (!inherited && name.startsWith(target + "."))) matched[0] = true;
          }
          case PARAMETERIZED_TYPE -> {
            var parameterized = (ParameterizedTypeTree) tree;
            type(parameterized.getType(), inherited);
            parameterized.getTypeArguments().forEach(value -> type(value, inherited));
          }
          case ARRAY_TYPE -> type(((ArrayTypeTree) tree).getType(), inherited);
          case ANNOTATED_TYPE -> type(((AnnotatedTypeTree) tree).getUnderlyingType(), inherited);
          case EXTENDS_WILDCARD, SUPER_WILDCARD ->
              type(((WildcardTree) tree).getBound(), inherited);
          case UNION_TYPE ->
              ((UnionTypeTree) tree).getTypeAlternatives().forEach(value -> type(value, inherited));
          case INTERSECTION_TYPE ->
              ((IntersectionTypeTree) tree).getBounds().forEach(value -> type(value, inherited));
          default -> {
            /* No expression-name or string/comment inference. */
          }
        }
      }

      @Override
      public Void visitClass(ClassTree node, Boolean inherited) {
        boolean nested =
            inherited
                || node.getExtendsClause() != null
                || !node.getImplementsClause().isEmpty()
                || node.getSimpleName().isEmpty();
        type(node.getExtendsClause(), nested);
        node.getImplementsClause().forEach(value -> type(value, nested));
        return super.visitClass(node, nested);
      }

      @Override
      public Void visitVariable(VariableTree node, Boolean inherited) {
        type(node.getType(), inherited);
        return super.visitVariable(node, inherited);
      }

      @Override
      public Void visitMethod(MethodTree node, Boolean inherited) {
        type(node.getReturnType(), inherited);
        node.getThrows().forEach(value -> type(value, inherited));
        return super.visitMethod(node, inherited);
      }

      @Override
      public Void visitNewClass(NewClassTree node, Boolean inherited) {
        type(node.getIdentifier(), inherited);
        node.getTypeArguments().forEach(value -> type(value, inherited));
        return super.visitNewClass(node, inherited);
      }

      @Override
      public Void visitNewArray(NewArrayTree node, Boolean inherited) {
        type(node.getType(), inherited);
        return super.visitNewArray(node, inherited);
      }

      @Override
      public Void visitTypeCast(TypeCastTree node, Boolean inherited) {
        type(node.getType(), inherited);
        return super.visitTypeCast(node, inherited);
      }

      @Override
      public Void visitInstanceOf(InstanceOfTree node, Boolean inherited) {
        type(node.getType(), inherited);
        return super.visitInstanceOf(node, inherited);
      }

      @Override
      public Void visitMemberSelect(MemberSelectTree node, Boolean inherited) {
        if (node.getIdentifier().contentEquals("class")) type(node.getExpression(), inherited);
        return super.visitMemberSelect(node, inherited);
      }

      @Override
      public Void visitMethodInvocation(MethodInvocationTree node, Boolean inherited) {
        node.getTypeArguments().forEach(value -> type(value, inherited));
        return super.visitMethodInvocation(node, inherited);
      }

      @Override
      public Void visitTypeParameter(TypeParameterTree node, Boolean inherited) {
        node.getBounds().forEach(value -> type(value, inherited));
        return super.visitTypeParameter(node, inherited);
      }
    }.scan(unit, false);
    return matched[0];
  }

  private static void selfTest() throws Exception {
    String[][] vectors = {
      {"package p; class ThingTest { Object x=new Thing(); }", "true"},
      {"package p; class ThingTest { Thing x; }", "true"},
      {"package p; class ThingTest { Object x=Thing.class; }", "true"},
      {"package p; class ThingTest { other.Thing x; }", "false"},
      {"package p; /* Thing */ class ThingTest { String x=\"Thing\"; }", "false"},
      {"package p; class ThingTest { class Thing {} Thing x; }", "false"},
      {"package p; class ThingTest { void x(int Thing) {} }", "false"},
      {"package p; class ThingTest<Thing> { Thing x; }", "false"},
      {"package p; import other.Thing; class ThingTest { Thing x; }", "false"},
      {"package other; class ThingTest { Thing x; }", "false"},
      {"package p; class ThingTest { p.Thing x; }", "true"},
      {"package p; class ThingTest extends Base { Thing x; }", "false"},
      {"package p; class ThingTest { Object x=new Base(){ Thing y; }; }", "false"}
    };
    for (int index = 0; index < vectors.length; index++) {
      var compiler = ToolProvider.getSystemJavaCompiler();
      var diagnostic = new DiagnosticCollector<JavaFileObject>();
      String text = vectors[index][0];
      var source =
          new SimpleJavaFileObject(
              URI.create("string:///ThingTest.java"), JavaFileObject.Kind.SOURCE) {
            @Override
            public CharSequence getCharContent(boolean ignored) {
              return text;
            }
          };
      try (var manager =
          compiler.getStandardFileManager(diagnostic, null, StandardCharsets.UTF_8)) {
        var task =
            (JavacTask)
                compiler.getTask(
                    new StringWriter(),
                    manager,
                    diagnostic,
                    List.of("-proc:none", "--release", "25"),
                    null,
                    List.of(source));
        var unit = task.parse().iterator().next();
        if (!diagnostic.getDiagnostics().isEmpty()
            || reference(unit, "p", "Thing") != Boolean.parseBoolean(vectors[index][1])) {
          throw new IllegalStateException("independent parse fixture mismatch at index " + index);
        }
      }
    }
    System.out.println("SELFTEST\t" + vectors.length);
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 3)
      throw new IllegalArgumentException("root, catalog, empty classpath required");
    selfTest();
    Path root = Path.of(args[0]).toRealPath();
    var targets = new HashMap<String, String[]>();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] fields = line.split("\t", -1);
      if (fields.length != 3 || fields[0].contains("..") || !fields[0].startsWith("src/")) {
        throw new IllegalArgumentException("bounded source row required");
      }
      Path path = root.resolve(fields[0]);
      if (!path.toRealPath().equals(path)
          || Files.isSymbolicLink(path)
          || targets.put(path.toUri().toString(), fields) != null) {
        throw new IllegalArgumentException("unique canonical public source required");
      }
    }
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostic = new DiagnosticCollector<JavaFileObject>();
    try (var manager = compiler.getStandardFileManager(diagnostic, null, StandardCharsets.UTF_8)) {
      var paths = targets.values().stream().map(row -> root.resolve(row[0])).toList();
      var task =
          (JavacTask)
              compiler.getTask(
                  new StringWriter(),
                  manager,
                  diagnostic,
                  List.of(
                      "-proc:none",
                      "--release",
                      "25",
                      "-classpath",
                      args[2],
                      "-sourcepath",
                      args[2]),
                  null,
                  manager.getJavaFileObjectsFromPaths(paths));
      for (var unit : task.parse()) {
        String[] target = targets.get(unit.getSourceFile().toUri().toString());
        if (target == null) throw new IllegalStateException("unrequested source parsed");
        System.out.println(target[0] + "\t" + reference(unit, target[1], target[2]));
      }
      if (!diagnostic.getDiagnostics().isEmpty())
        throw new IllegalStateException("source parse diagnostic");
    }
  }
}
