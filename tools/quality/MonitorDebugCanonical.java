import java.lang.classfile.ClassFile;
import java.lang.classfile.ClassTransform;
import java.lang.constant.ClassDesc;
import java.lang.constant.ConstantDescs;
import java.lang.constant.MethodTypeDesc;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;

/** Analysis-only debug comparison. Raw Main bytes/CRC are never rewritten or substituted. */
final class MonitorDebugCanonical {
  private static final ClassFile CANONICAL =
      ClassFile.of(
          ClassFile.DebugElementsOption.DROP_DEBUG,
          ClassFile.LineNumbersOption.DROP_LINE_NUMBERS,
          ClassFile.ConstantPoolSharingOption.NEW_POOL);

  static byte[] normalize(byte[] bytes) {
    return CANONICAL.transformClass(CANONICAL.parse(bytes), ClassTransform.ACCEPT_ALL);
  }

  private static byte[] fixture(int line, int literal, int access) {
    return ClassFile.of()
        .build(
            ClassDesc.of("FixedDebugControl"),
            builder ->
                builder.withMethodBody(
                    "value",
                    MethodTypeDesc.of(ConstantDescs.CD_int),
                    access | ClassFile.ACC_STATIC,
                    code -> code.lineNumber(line).loadConstant(literal).ireturn()));
  }

  static void controls() {
    byte[] original = fixture(10, 7, ClassFile.ACC_PUBLIC);
    byte[] line = fixture(20, 7, ClassFile.ACC_PUBLIC);
    byte[] value = fixture(10, 8, ClassFile.ACC_PUBLIC);
    byte[] access = fixture(10, 7, ClassFile.ACC_PRIVATE);
    if (Arrays.equals(original, line)
        || !Arrays.equals(normalize(original), normalize(line))
        || Arrays.equals(normalize(original), normalize(value))
        || Arrays.equals(normalize(original), normalize(access)))
      throw new AssertionError("debug-only accepted, literal and access changes rejected");
  }

  private static String sha(byte[] bytes) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }

  public static void main(String[] arguments) throws Exception {
    if (Runtime.version().feature() != 25) throw new IllegalStateException("JDK25 required");
    controls();
    if (arguments.length == 0) {
      System.out.println("CONTROLS3_PASS");
      return;
    }
    if (arguments.length != 2) throw new IllegalArgumentException("two exact physical class files");
    byte[] before = Files.readAllBytes(Path.of(arguments[0]));
    byte[] after = Files.readAllBytes(Path.of(arguments[1]));
    byte[] left = normalize(before), right = normalize(after);
    System.out.println(sha(left) + "\t" + sha(right) + "\t" + Arrays.equals(left, right));
  }
}
