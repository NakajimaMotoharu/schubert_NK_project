import java.lang.classfile.Annotation;
import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.lang.classfile.attribute.RuntimeVisibleAnnotationsAttribute;
import java.lang.classfile.attribute.SourceFileAttribute;
import java.lang.constant.ClassDesc;
import java.lang.constant.MethodTypeDesc;
import java.lang.reflect.AccessFlag;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;

/** Read normal host Test annotation metadata only; never resolve or initialize a target class. */
public final class PublicTestMethodMetadataAudit {
  private PublicTestMethodMetadataAudit() {}

  private record Method(String name, String descriptor, int parameters, String annotation) {}

  private static List<Method> methods(byte[] bytes) {
    var model = ClassFile.of().parse(bytes);
    if (model.majorVersion() != 69) throw new IllegalArgumentException("Java25 bytes required");
    var result = new ArrayList<Method>();
    var allowed =
        Set.of(
            "Lorg/junit/jupiter/api/Test;",
            "Lorg/junit/jupiter/api/RepeatedTest;",
            "Lorg/junit/jupiter/api/TestFactory;",
            "Lorg/junit/jupiter/api/TestTemplate;",
            "Lorg/junit/jupiter/params/ParameterizedTest;");
    for (var method : model.methods()) {
      var annotations = method.findAttribute(Attributes.runtimeVisibleAnnotations());
      if (annotations.isEmpty()) continue;
      for (var annotation : annotations.get().annotations()) {
        String type = annotation.className().stringValue();
        if (!allowed.contains(type)) continue;
        result.add(
            new Method(
                method.methodName().stringValue(),
                method.methodType().stringValue(),
                method.methodTypeSymbol().parameterCount(),
                type.substring(1, type.length() - 1).replace('/', '.')));
      }
    }
    return result;
  }

  private static byte[] vector(String annotation, String descriptor) {
    return ClassFile.of()
        .build(
            ClassDesc.of("p.T"),
            builder ->
                builder
                    .with(SourceFileAttribute.of("T.java"))
                    .withMethod(
                        "example",
                        MethodTypeDesc.ofDescriptor(descriptor),
                        AccessFlag.PUBLIC.mask() | AccessFlag.STATIC.mask(),
                        method ->
                            method
                                .with(
                                    RuntimeVisibleAnnotationsAttribute.of(
                                        Annotation.of(ClassDesc.of(annotation))))
                                .withCode(code -> code.return_())));
  }

  private static void vectors() {
    var plain = methods(vector("org.junit.jupiter.api.Test", "()V"));
    if (!plain.equals(List.of(new Method("example", "()V", 0, "org.junit.jupiter.api.Test"))))
      throw new AssertionError("ordinary annotation vector");
    var parameters = methods(vector("org.junit.jupiter.api.Test", "(ILjava/lang/String;)V"));
    if (parameters.size() != 1 || parameters.getFirst().parameters() != 2)
      throw new AssertionError("descriptor parameter count vector");
    if (!methods(vector("other.Test", "()V")).isEmpty())
      throw new AssertionError("foreign annotation vector");
    if (!methods(vector("org.junit.jupiter.api.RepeatedTest", "()V"))
        .getFirst()
        .annotation()
        .equals("org.junit.jupiter.api.RepeatedTest"))
      throw new AssertionError("repeated is distinct, never expanded vector");
    if (!methods(ClassFile.of().build(ClassDesc.of("p.Empty"), builder -> {})).isEmpty())
      throw new AssertionError("no method vector");
    if (!methods(vector("org.junit.jupiter.params.ParameterizedTest", "(I)V"))
        .getFirst()
        .annotation()
        .equals("org.junit.jupiter.params.ParameterizedTest"))
      throw new AssertionError("other Jupiter kind vector");
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("normal snapshot and catalog required");
    vectors();
    var snapshot = Path.of(args[0]).toRealPath();
    var modules = Set.of("api", "batch", "bootstrap", "protocol", "storage", "web");
    System.out.println("SELFTEST\t6");
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] fields = line.split("\t", -1);
      if (fields.length != 2 || !modules.contains(fields[0]))
        throw new IllegalArgumentException("one known module/canonical class path required");
      var path = Path.of(fields[1]);
      if (!path.toRealPath().equals(path)
          || !path.startsWith(
              snapshot.resolve("src/schubert-nk-" + fields[0] + "/target/test-classes"))
          || !path.getFileName().toString().endsWith(".class"))
        throw new IllegalArgumentException("normal host Test class only");
      byte[] bytes = Files.readAllBytes(path);
      var model = ClassFile.of().parse(bytes);
      String name = model.thisClass().asInternalName();
      String source =
          model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile().stringValue();
      if (!name.startsWith("dev/codex/schubert/nk/") || !source.matches("[A-Za-z0-9_$-]+\\.java"))
        throw new IllegalArgumentException("project class and simple SourceFile required");
      String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
      System.out.println("CLASS\t" + fields[0] + "\t" + name + "\t" + source + "\t" + digest);
      for (var method : methods(bytes))
        System.out.println(
            "TEST\t"
                + fields[0]
                + "\t"
                + name
                + "\t"
                + method.name()
                + "\t"
                + method.descriptor()
                + "\t"
                + method.parameters()
                + "\t"
                + method.annotation());
    }
  }
}
