import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Label;
import org.objectweb.asm.Opcodes;

/**
 * Reads class files as data only; preserves instructions/frames/handlers/members, never loads
 * Tests.
 */
public final class TestClassDebugOnlyMeasure {
  private TestClassDebugOnlyMeasure() {}

  private static byte[] normalized(byte[] raw) {
    var writer = new ClassWriter(0);
    new ClassReader(raw).accept(writer, ClassReader.SKIP_DEBUG);
    return writer.toByteArray();
  }

  private static String digest(byte[] raw) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(raw));
  }

  private static String source(byte[] raw) {
    String[] found = {null};
    new ClassReader(raw)
        .accept(
            new ClassVisitor(Opcodes.ASM9) {
              @Override
              public void visitSource(String name, String debug) {
                found[0] = name;
              }
            },
            ClassReader.SKIP_CODE | ClassReader.SKIP_FRAMES);
    return found[0];
  }

  private static byte[] fixture(String method, int line, int value, int field, int flags) {
    var writer = new ClassWriter(0);
    writer.visit(Opcodes.V25, flags, "metadata/Fixture", null, "java/lang/Object", null);
    writer.visitSource("Fixture.java", null);
    writer
        .visitField(
            Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC | Opcodes.ACC_FINAL, "VALUE", "I", null, field)
        .visitEnd();
    var body =
        writer.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, method, "()I", null, null);
    body.visitCode();
    var label = new Label();
    body.visitLabel(label);
    body.visitLineNumber(line, label);
    body.visitIntInsn(Opcodes.BIPUSH, value);
    body.visitInsn(Opcodes.IRETURN);
    body.visitMaxs(1, 0);
    body.visitEnd();
    writer.visitEnd();
    return writer.toByteArray();
  }

  private static void selftest() {
    byte[] base = fixture("m", 1, 7, 5, Opcodes.ACC_PUBLIC);
    byte[] debug = fixture("m", 2, 7, 5, Opcodes.ACC_PUBLIC);
    if (Arrays.equals(base, debug) || !Arrays.equals(normalized(base), normalized(debug)))
      throw new IllegalStateException("literal debug-only vector");
    for (byte[] changed :
        new byte[][] {
          fixture("m", 1, 8, 5, Opcodes.ACC_PUBLIC),
          fixture("n", 1, 7, 5, Opcodes.ACC_PUBLIC),
          fixture("m", 1, 7, 6, Opcodes.ACC_PUBLIC),
          fixture("m", 1, 7, 5, Opcodes.ACC_PUBLIC | Opcodes.ACC_FINAL)
        }) {
      if (Arrays.equals(normalized(base), normalized(changed)))
        throw new IllegalStateException("instruction/name/constant/access mutation must differ");
    }
    System.out.println("METADATA_VECTORS\t5");
  }

  private static Map<String, byte[]> classes(Path root) throws Exception {
    var result = new TreeMap<String, byte[]>();
    for (String module : new String[] {"api", "batch", "bootstrap", "protocol", "storage", "web"}) {
      Path base = root.resolve("src/schubert-nk-" + module + "/target/test-classes");
      if (!Files.isDirectory(base))
        throw new IllegalArgumentException("exact test-classes directory");
      try (var paths = Files.walk(base)) {
        for (var file : paths.filter(p -> p.toString().endsWith(".class")).sorted().toList()) {
          if (Files.isSymbolicLink(file))
            throw new IllegalArgumentException("regular class data only");
          byte[] raw = Files.readAllBytes(file);
          String relative = base.relativize(file).toString();
          if (!relative.equals(new ClassReader(raw).getClassName() + ".class"))
            throw new IllegalStateException("physical class identity mismatch");
          if (result.put(module + "/" + relative, raw) != null)
            throw new IllegalStateException("duplicate physical Test class");
        }
      }
    }
    return result;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("two fixed normal snapshots");
    selftest();
    var before = classes(Path.of(args[0]));
    var after = classes(Path.of(args[1]));
    if (!before.keySet().equals(after.keySet()) || before.size() != 1922)
      throw new IllegalStateException("exact complete1922 physical Test classes");
    int identical = 0;
    int debugOnly = 0;
    int different = 0;
    for (var entry : before.entrySet()) {
      byte[] old = entry.getValue();
      byte[] next = after.get(entry.getKey());
      byte[] canonical = normalized(old);
      boolean same =
          Arrays.equals(canonical, normalized(next)) && Objects.equals(source(old), source(next));
      String status;
      if (!same) {
        different++;
        status = "NON_DEBUG_DIFFERENCE";
      } else if (Arrays.equals(old, next)) {
        identical++;
        status = "BYTE_IDENTICAL";
      } else {
        debugOnly++;
        status = "DEBUG_ONLY";
      }
      System.out.println(
          "CLASS\t"
              + entry.getKey()
              + "\t"
              + status
              + "\t"
              + digest(old)
              + "\t"
              + digest(next)
              + "\t"
              + digest(canonical));
    }
    System.out.println("SUMMARY\t" + identical + "\t" + debugOnly + "\t" + different);
    if (different != 0)
      throw new IllegalStateException("non-debug class difference requires investigation");
  }
}
