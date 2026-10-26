import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.lang.classfile.instruction.InvokeInstruction;
import java.lang.classfile.instruction.LineNumber;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;

/** Parse exact existing Test class bytes only. No target loading, reflection or invocation. */
public final class ExpectedConstructorBindings {
  private ExpectedConstructorBindings() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("snapshot and frozen file list required");
    Path root = Path.of(args[0]).toRealPath();
    int files = 0;
    int calls = 0;
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", -1);
      if (row.length != 2
          || !row[0].contains("/target/test-classes/")
          || !row[0].endsWith(".class")
          || !row[1].matches("[A-Za-z0-9_$]+\\.java"))
        throw new IllegalArgumentException("exact normal Test class and SourceFile required");
      Path file = root.resolve(row[0]).normalize();
      if (!file.startsWith(root)
          || Files.isSymbolicLink(file)
          || !file.toRealPath().startsWith(root))
        throw new IllegalArgumentException("regular snapshot class required");
      byte[] bytes = Files.readAllBytes(file);
      var model =
          ClassFile.of(
                  ClassFile.DebugElementsOption.PASS_DEBUG,
                  ClassFile.LineNumbersOption.PASS_LINE_NUMBERS)
              .parse(bytes);
      String type = model.thisClass().asInternalName();
      String suffix = row[0].split("/target/test-classes/", -1)[1];
      if (!suffix.equals(type + ".class")
          || !model
              .findAttribute(Attributes.sourceFile())
              .orElseThrow()
              .sourceFile()
              .stringValue()
              .equals(row[1])) throw new IllegalArgumentException("class/source identity mismatch");
      String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
      System.out.println("CLASS\t" + row[0] + "\t" + type + "\t" + row[1] + "\t" + digest);
      files++;
      for (var method : model.methods()) {
        if (method.code().isEmpty()) continue;
        int sourceLine = -1;
        for (var element : method.code().orElseThrow()) {
          if (element instanceof LineNumber number) sourceLine = number.line();
          if (element instanceof InvokeInstruction call && call.name().equalsString("<init>")) {
            System.out.println(
                "CTOR\t"
                    + row[0]
                    + "\t"
                    + method.methodName().stringValue()
                    + "\t"
                    + sourceLine
                    + "\t"
                    + call.owner().asInternalName()
                    + "\t"
                    + call.type().stringValue());
            calls++;
          }
        }
      }
    }
    System.out.println("SUMMARY\t" + files + "\t" + calls);
  }
}
