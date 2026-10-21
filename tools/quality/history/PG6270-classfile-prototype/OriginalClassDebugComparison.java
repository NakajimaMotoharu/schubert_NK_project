import java.lang.classfile.ClassFile;
import java.lang.classfile.ClassTransform;
import java.lang.classfile.CodeTransform;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Objects;
import java.util.zip.ZipFile;

/** Rejected PG6270 draft, not a gate: default verifier lacks application hierarchy resources.
 * Preserved for development failure history. Qualified comparison uses exact LineNumberTable
 * masking in classfile_line_numbers.py, not this debug-rebuilding prototype. */
public final class OriginalClassDebugComparison {
  private OriginalClassDebugComparison() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 3) throw new IllegalArgumentException("two jars and one class member required");
    byte[] before = member(Path.of(args[0]), args[2]);
    byte[] after = member(Path.of(args[1]), args[2]);
    var parser = ClassFile.of(ClassFile.DebugElementsOption.DROP_DEBUG,
        ClassFile.LineNumbersOption.DROP_LINE_NUMBERS);
    if (!parser.verify(before).isEmpty() || !parser.verify(after).isEmpty())
      throw new IllegalArgumentException("original classes must verify structurally");
    var copyBodies = ClassTransform.transformingMethodBodies(CodeTransform.ACCEPT_ALL);
    byte[] normalizedBefore = parser.transformClass(parser.parse(before), copyBodies);
    byte[] normalizedAfter = parser.transformClass(parser.parse(after), copyBodies);
    System.out.println("{\"rawEqual\":" + Arrays.equals(before, after)
        + ",\"debugNormalizedEqual\":" + Arrays.equals(normalizedBefore, normalizedAfter)
        + ",\"beforeSha256\":\"" + digest(before) + "\",\"afterSha256\":\"" + digest(after)
        + "\",\"normalizedBeforeSha256\":\"" + digest(normalizedBefore)
        + "\",\"normalizedAfterSha256\":\"" + digest(normalizedAfter)
        + "\",\"productionClassesExecuted\":0}");
  }

  private static byte[] member(Path jar, String name) throws Exception {
    try (var zip = new ZipFile(jar.toFile())) {
      var entry = Objects.requireNonNull(zip.getEntry(name), "original class member");
      try (var input = zip.getInputStream(entry)) { return input.readAllBytes(); }
    }
  }

  private static String digest(byte[] bytes) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }
}
