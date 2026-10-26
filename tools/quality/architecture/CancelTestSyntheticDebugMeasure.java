import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Label;
import org.objectweb.asm.Opcodes;

/** Only classfile metadata; strict non-debug equality, never loads a product/Test class. */
public final class CancelTestSyntheticDebugMeasure {
  private CancelTestSyntheticDebugMeasure() {}

  private static byte[] normalized(byte[] raw) {
    var writer = new ClassWriter(0);
    new ClassReader(raw).accept(writer, ClassReader.SKIP_DEBUG);
    return writer.toByteArray();
  }

  private static byte[] fixture(String name, int line, int opcode, int field, int flags) {
    var writer = new ClassWriter(0);
    writer.visit(Opcodes.V25, flags, "metadata/Fixture", null, "java/lang/Object", null);
    writer.visitSource("Fixture.java", null);
    writer.visitField(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC | Opcodes.ACC_FINAL,
        "V", "I", null, field).visitEnd();
    var method = writer.visitMethod(Opcodes.ACC_STATIC, name, "()I", null, null);
    method.visitCode();
    var label = new Label();
    method.visitLabel(label);
    method.visitLineNumber(line, label);
    method.visitIntInsn(Opcodes.BIPUSH, opcode);
    method.visitInsn(Opcodes.IRETURN);
    method.visitMaxs(1, 0);
    method.visitEnd();
    writer.visitEnd();
    return writer.toByteArray();
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("two exact synthetic Test class files");
    byte[] base = fixture("m", 1, 7, 5, Opcodes.ACC_PUBLIC);
    byte[] debug = fixture("m", 2, 7, 5, Opcodes.ACC_PUBLIC);
    if (Arrays.equals(base,debug) || !Arrays.equals(normalized(base),normalized(debug)))
      throw new IllegalStateException("literal debug vector");
    for (byte[] altered : new byte[][] {fixture("m",1,8,5,Opcodes.ACC_PUBLIC),
        fixture("n",1,7,5,Opcodes.ACC_PUBLIC),fixture("m",1,7,6,Opcodes.ACC_PUBLIC),
        fixture("m",1,7,5,Opcodes.ACC_PUBLIC | Opcodes.ACC_FINAL)})
      if (Arrays.equals(normalized(base),normalized(altered)))
        throw new IllegalStateException("instruction/name/field/flag mutation accepted");
    byte[][] values = {Files.readAllBytes(Path.of(args[0])),Files.readAllBytes(Path.of(args[1]))};
    for (byte[] raw : values) {
      var model = ClassFile.of().parse(raw);
      if (!model.thisClass().asInternalName().equals("dev/codex/schubert/nk/protocol/codec/PayloadCodecTest$1")
          || !model.flags().has(java.lang.reflect.AccessFlag.SYNTHETIC)
          || !model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile().stringValue().equals("PayloadCodecTest.java"))
        throw new IllegalStateException("fixed generated Test source identity required");
    }
    if (Arrays.equals(values[0],values[1]) || !Arrays.equals(normalized(values[0]),normalized(values[1])))
      throw new IllegalStateException("strict debug-only difference required");
    System.out.println("METADATA_VECTORS\t5");
    System.out.println("DEBUG_ONLY\t" + HexFormat.of().formatHex(
        MessageDigest.getInstance("SHA-256").digest(normalized(values[0]))));
  }
}
