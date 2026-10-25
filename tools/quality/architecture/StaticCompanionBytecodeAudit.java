import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import java.util.TreeSet;
import java.util.function.Consumer;
import org.objectweb.asm.*;

/** 1904: bytes only. Neither source test, business class nor generated fixture is loaded/run. */
public final class StaticCompanionBytecodeAudit {
  private StaticCompanionBytecodeAudit() {}

  private record Proof(
      String className,
      String sourceFile,
      Set<String> kinds,
      Set<String> owners,
      boolean matched) {}

  private static boolean family(String owner, String target) {
    return owner.equals(target) || owner.startsWith(target + "$");
  }

  private static Proof probe(byte[] bytes, String expectedSource, String target) {
    var reader = new ClassReader(bytes);
    String[] source = {"NONE"};
    var kinds = new TreeSet<String>();
    var owners = new TreeSet<String>();
    reader.accept(
        new ClassVisitor(Opcodes.ASM9) {
          private void owner(String candidate, String kind) {
            if (family(candidate, target)) {
              kinds.add(kind);
              owners.add(candidate);
            }
          }

          private void literal(Object value, String kind) {
            if (value instanceof Handle handle) owner(handle.getOwner(), kind + "_HANDLE");
            if (value instanceof Type type) {
              if (type.getSort() == Type.ARRAY) type = type.getElementType();
              if (type.getSort() == Type.OBJECT) owner(type.getInternalName(), kind + "_TYPE");
            }
          }

          @Override
          public void visitSource(String name, String debug) {
            if (name != null) source[0] = name;
          }

          @Override
          public MethodVisitor visitMethod(
              int access, String name, String descriptor, String signature, String[] exceptions) {
            return new MethodVisitor(Opcodes.ASM9) {
              @Override
              public void visitMethodInsn(
                  int opcode, String declaringOwner, String member, String desc, boolean itf) {
                owner(declaringOwner, "METHOD");
              }

              @Override
              public void visitFieldInsn(
                  int opcode, String declaringOwner, String member, String desc) {
                owner(declaringOwner, "FIELD");
              }

              @Override
              public void visitTypeInsn(int opcode, String type) {
                if (type.startsWith("[")) literal(Type.getType(type), "INSTRUCTION");
                else owner(type, "TYPE");
              }

              @Override
              public void visitLdcInsn(Object value) {
                literal(value, "LDC");
              }

              @Override
              public void visitInvokeDynamicInsn(
                  String name, String descriptor, Handle bootstrap, Object... arguments) {
                literal(bootstrap, "BOOTSTRAP");
                for (Object argument : arguments) literal(argument, "BOOTSTRAP_ARGUMENT");
              }
            };
          }
        },
        ClassReader.SKIP_FRAMES);
    String className = reader.getClassName();
    String expectedPackage = target.substring(0, target.lastIndexOf('/') + 1);
    String actualPackage = className.substring(0, className.lastIndexOf('/') + 1);
    boolean matched =
        source[0].equals(expectedSource)
            && actualPackage.equals(expectedPackage)
            && !kinds.isEmpty();
    return new Proof(className, source[0], Set.copyOf(kinds), Set.copyOf(owners), matched);
  }

  private static byte[] fixture(String source, Consumer<MethodVisitor> body) {
    var writer = new ClassWriter(0);
    writer.visit(Opcodes.V25, Opcodes.ACC_PUBLIC, "p/Fixture", null, "java/lang/Object", null);
    writer.visitSource(source, null);
    var method =
        writer.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, "marker", "()V", null, null);
    method.visitCode();
    body.accept(method);
    method.visitInsn(Opcodes.RETURN);
    method.visitMaxs(4, 0);
    method.visitEnd();
    writer.visitEnd();
    return writer.toByteArray();
  }

  private static void selfTest() {
    String target = "p/Target";
    byte[][] vectors = {
      fixture(
          "Fixture.java", m -> m.visitMethodInsn(Opcodes.INVOKESTATIC, target, "go", "()V", false)),
      fixture(
          "Fixture.java",
          m -> m.visitMethodInsn(Opcodes.INVOKESTATIC, target + "Other", "go", "()V", false)),
      fixture(
          "Fixture.java",
          m -> {
            m.visitFieldInsn(Opcodes.GETSTATIC, target, "number", "I");
            m.visitInsn(Opcodes.POP);
          }),
      fixture(
          "Fixture.java",
          m -> {
            m.visitTypeInsn(Opcodes.NEW, target);
            m.visitInsn(Opcodes.POP);
          }),
      fixture(
          "Fixture.java",
          m -> {
            m.visitLdcInsn(Type.getObjectType(target));
            m.visitInsn(Opcodes.POP);
          }),
      fixture(
          "Fixture.java",
          m -> {
            m.visitLdcInsn(target);
            m.visitInsn(Opcodes.POP);
          }),
      fixture(
          "Fixture.java",
          m -> {
            m.visitLdcInsn(new Handle(Opcodes.H_INVOKESTATIC, target, "go", "()V", false));
            m.visitInsn(Opcodes.POP);
          }),
      fixture(
          "Fixture.java",
          m -> m.visitMethodInsn(Opcodes.INVOKESTATIC, target + "$Nested", "go", "()V", false)),
      fixture(
          "Fixture.java",
          m -> m.visitMethodInsn(Opcodes.INVOKESTATIC, "other/Target", "go", "()V", false)),
      fixture(
          "Other.java", m -> m.visitMethodInsn(Opcodes.INVOKESTATIC, target, "go", "()V", false))
    };
    boolean[] expected = {true, false, true, true, true, false, true, true, false, false};
    for (int index = 0; index < vectors.length; index++) {
      if (probe(vectors[index], "Fixture.java", target).matched() != expected[index]) {
        throw new IllegalStateException("bytecode fixture mismatch at index " + index);
      }
    }
    System.out.println("SELFTEST\t" + vectors.length);
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("fresh class root and catalog required");
    selfTest();
    Path root = Path.of(args[0]).toRealPath();
    for (String line : Files.readAllLines(Path.of(args[1]))) {
      String[] fields = line.split("\t", -1);
      if (fields.length != 3
          || fields[0].startsWith("/")
          || fields[0].contains("..")
          || !fields[0].matches("[A-Za-z0-9_/$.-]+\\.class")
          || !fields[1].matches("[A-Za-z0-9_$]+\\.java")
          || !fields[2].matches("[A-Za-z0-9_/$]+")) {
        throw new IllegalArgumentException("closed class/source/target metadata row required");
      }
      Path path = root.resolve(fields[0]);
      if (!path.toRealPath().equals(path) || Files.isSymbolicLink(path)) {
        throw new IllegalArgumentException("regular fresh class artifact required");
      }
      Proof proof = probe(Files.readAllBytes(path), fields[1], fields[2]);
      System.out.println(
          fields[0]
              + "\t"
              + proof.matched()
              + "\t"
              + String.join(",", new TreeSet<>(proof.kinds()))
              + "\t"
              + proof.sourceFile()
              + "\t"
              + proof.className()
              + "\t"
              + String.join(",", new TreeSet<>(proof.owners())));
    }
  }
}
