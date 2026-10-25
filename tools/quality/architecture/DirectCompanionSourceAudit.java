import com.github.javaparser.JavaParser;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.EnumDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.body.RecordDeclaration;
import com.github.javaparser.ast.body.TypeDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.ObjectCreationExpr;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.type.TypeParameter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/** G13.07/1902: source text only; never resolves, loads, compiles, or invokes target classes. */
public final class DirectCompanionSourceAudit {
  private DirectCompanionSourceAudit() {}

  private static String classify(String source, String expectedPackage, String target) {
    var configuration =
        new ParserConfiguration()
            .setLanguageLevel(ParserConfiguration.LanguageLevel.JAVA_25)
            .setCharacterEncoding(StandardCharsets.UTF_8);
    var parsed = new JavaParser(configuration).parse(source);
    if (!parsed.isSuccessful() || parsed.getResult().isEmpty()) return "PARSE_UNRESOLVED";
    CompilationUnit unit = parsed.getResult().orElseThrow();
    if (unit.getPackageDeclaration().isEmpty()
        || !unit.getPackageDeclaration().orElseThrow().getNameAsString().equals(expectedPackage)) {
      return "PACKAGE_MISMATCH";
    }
    String qualified = expectedPackage + "." + target;
    for (var imported : unit.getImports()) {
      if (!imported.isStatic()
          && !imported.isAsterisk()
          && imported.getName().getIdentifier().equals(target)
          && !imported.getNameAsString().equals(qualified)) return "CONFLICTING_IMPORT";
    }
    for (Node node : unit.findAll(Node.class)) {
      if (node instanceof TypeDeclaration<?> type && type.getNameAsString().equals(target)) {
        return "SHADOWED_TYPE";
      }
      if (node instanceof TypeParameter type && type.getNameAsString().equals(target)) {
        return "SHADOWED_TYPE_PARAMETER";
      }
      if (node instanceof VariableDeclarator variable
          && variable.getNameAsString().equals(target)) {
        return "SHADOWED_IDENTIFIER";
      }
      if (node instanceof Parameter parameter && parameter.getNameAsString().equals(target)) {
        return "SHADOWED_IDENTIFIER";
      }
    }
    boolean ambiguous = false;
    for (var type : unit.findAll(ClassOrInterfaceType.class)) {
      String name = type.getNameWithScope();
      if (name.equals(qualified)) return "REFERENCED_TARGET";
      if (name.equals(target)) {
        if (inheritedScopeUnknown(type)) ambiguous = true;
        else return "REFERENCED_TARGET";
      }
    }
    return ambiguous ? "INHERITANCE_UNRESOLVED" : "NO_TYPED_TARGET_REFERENCE";
  }

  private static boolean inheritedScopeUnknown(Node type) {
    Node child = type;
    var parent = child.getParentNode();
    while (parent.isPresent()) {
      Node node = parent.orElseThrow();
      if (node instanceof ClassOrInterfaceDeclaration declaration
          && (!declaration.getExtendedTypes().isEmpty()
              || !declaration.getImplementedTypes().isEmpty())) return true;
      if (node instanceof EnumDeclaration declaration
          && !declaration.getImplementedTypes().isEmpty()) return true;
      if (node instanceof RecordDeclaration declaration
          && !declaration.getImplementedTypes().isEmpty()) return true;
      if (node instanceof ObjectCreationExpr creation
          && creation.getAnonymousClassBody().isPresent()
          && child != creation.getType()) return true;
      child = node;
      parent = node.getParentNode();
    }
    return false;
  }

  private static void selfTest() {
    String[][] vectors = {
      {"package p; class ThingTest { Object x=new Thing(); }", "REFERENCED_TARGET"},
      {"package p; class ThingTest { Thing x; }", "REFERENCED_TARGET"},
      {"package p; class ThingTest { Object x=Thing.class; }", "REFERENCED_TARGET"},
      {"package p; class ThingTest { other.Thing x; }", "NO_TYPED_TARGET_REFERENCE"},
      {
        "package p; /* Thing */ class ThingTest { String x=\"Thing\"; }",
        "NO_TYPED_TARGET_REFERENCE"
      },
      {"package p; class ThingTest { class Thing {} Thing x; }", "SHADOWED_TYPE"},
      {"package p; class ThingTest { void x(int Thing) {} }", "SHADOWED_IDENTIFIER"},
      {"package p; class ThingTest<Thing> { Thing x; }", "SHADOWED_TYPE_PARAMETER"},
      {"package p; import other.Thing; class ThingTest { Thing x; }", "CONFLICTING_IMPORT"},
      {"package other; class ThingTest { Thing x; }", "PACKAGE_MISMATCH"},
      {"package p; class ThingTest {", "PARSE_UNRESOLVED"},
      {"package p; class ThingTest { p.Thing x; }", "REFERENCED_TARGET"},
      {"package p; class ThingTest { Object x=Thing.values(); }", "NO_TYPED_TARGET_REFERENCE"},
      {"package p; class ThingTest extends Base { Thing x; }", "INHERITANCE_UNRESOLVED"},
      {"package p; class ThingTest { Object x=new Base(){ Thing y; }; }", "INHERITANCE_UNRESOLVED"},
      {"package p; import p.Thing; class ThingTest { Thing x; }", "REFERENCED_TARGET"}
    };
    for (int index = 0; index < vectors.length; index++) {
      if (!classify(vectors[index][0], "p", "Thing").equals(vectors[index][1])) {
        throw new IllegalStateException("static parser fixture mismatch at index " + index);
      }
    }
    System.out.println("SELFTEST\t" + vectors.length);
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("root and bounded source catalog required");
    selfTest();
    Path root = Path.of(args[0]).toRealPath();
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] fields = line.split("\t", -1);
      if (fields.length != 3
          || !fields[0].matches("src/schubert-nk-[a-z]+/src/test/java/[A-Za-z0-9_/$.-]+\\.java")
          || fields[0].contains("..")
          || !fields[1].matches("[A-Za-z_$][A-Za-z0-9_$.]*")
          || !fields[2].matches("[A-Za-z_$][A-Za-z0-9_$]*")) {
        throw new IllegalArgumentException("closed public source catalog row required");
      }
      Path path = root.resolve(fields[0]);
      if (!path.toRealPath().equals(path) || Files.isSymbolicLink(path)) {
        throw new IllegalArgumentException("regular canonical public source required");
      }
      String result =
          classify(Files.readString(path, StandardCharsets.UTF_8), fields[1], fields[2]);
      System.out.println(fields[0] + "\t" + result);
    }
  }
}
