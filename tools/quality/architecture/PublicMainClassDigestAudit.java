import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.lang.classfile.attribute.SourceFileAttribute;
import java.lang.constant.ClassDesc;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.zip.ZipFile;

/** Parse normal host Main class bytes only; never resolve, initialize or invoke a target class. */
public final class PublicMainClassDigestAudit {
  private PublicMainClassDigestAudit() {}

  private record Proof(String name, String source, String sha256) {}

  private static String sha(byte[] bytes) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }

  private static Proof inspect(String entry, byte[] bytes) throws Exception {
    if (!entry.matches("[A-Za-z0-9_/$-]+\\.class"))
      throw new IllegalArgumentException("canonical class entry required");
    var model = ClassFile.of().parse(bytes);
    if (model.majorVersion() != 69)
      throw new IllegalArgumentException("pinned Java25 class format required");
    String name = model.thisClass().asInternalName();
    String source =
        model.findAttribute(Attributes.sourceFile())
            .orElseThrow(() -> new IllegalArgumentException("SourceFile required"))
            .sourceFile()
            .stringValue();
    if (!entry.equals(name + ".class") || !source.matches("[A-Za-z0-9_$-]+\\.java"))
      throw new IllegalArgumentException("exact class identity and simple SourceFile required");
    return new Proof(name, source, sha(bytes));
  }

  private static void vectors() throws Exception {
    if (!sha("abc".getBytes(StandardCharsets.UTF_8))
        .equals("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"))
      throw new AssertionError("literal SHA256 vector");
    byte[] normal =
        ClassFile.of()
            .build(ClassDesc.of("p.T"), builder -> builder.with(SourceFileAttribute.of("T.java")));
    var proof = inspect("p/T.class", normal);
    if (!proof.name().equals("p/T") || !proof.source().equals("T.java"))
      throw new AssertionError("normal identity/SourceFile vector");
    byte[] info =
        ClassFile.of()
            .build(
                ClassDesc.ofDescriptor("Lp/package-info;"),
                builder -> builder.with(SourceFileAttribute.of("package-info.java")));
    if (!inspect("p/package-info.class", info).source().equals("package-info.java"))
      throw new AssertionError("legal package-info vector");
    try {
      inspect("p/Other.class", normal);
      throw new AssertionError("wrong entry accepted");
    } catch (IllegalArgumentException expected) {
      // Synthetic metadata only; no target code is defined or run.
    }
    try {
      inspect("p/T.class", ClassFile.of().build(ClassDesc.of("p.T"), builder -> {}));
      throw new AssertionError("missing SourceFile accepted");
    } catch (IllegalArgumentException expected) {
      // Reject before any proof is emitted.
    }
    try {
      inspect("../T.class", normal);
      throw new AssertionError("traversal entry accepted");
    } catch (IllegalArgumentException expected) {
      // Closed entry namespace.
    }
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("normal snapshot and pinned catalog required");
    vectors();
    var snapshot = Path.of(args[0]).toRealPath();
    var modules = Set.of("protocol", "storage", "bootstrap", "api", "web", "batch");
    System.out.println("SELFTEST\t6");
    for (String line : Files.readAllLines(Path.of(args[1]), StandardCharsets.UTF_8)) {
      String[] fields = line.split("\t", -1);
      if (fields.length != 2 || !modules.contains(fields[0]))
        throw new IllegalArgumentException("one pinned module/Jar pair required");
      String module = fields[0];
      var path = Path.of(fields[1]);
      if (!path.toRealPath().equals(path)
          || !path.startsWith(snapshot.resolve("src/schubert-nk-" + module + "/target"))
          || !path.getFileName().toString().endsWith(".jar"))
        throw new IllegalArgumentException("normal snapshot regular Jar only");
      try (var archive = new ZipFile(path.toFile())) {
        var entries =
            archive.stream().filter(entry -> entry.getName().endsWith(".class"))
                .map(entry -> entry.getName()).sorted().toList();
        if (entries.size() != Set.copyOf(entries).size())
          throw new IllegalArgumentException("no duplicate class entries");
        for (String entry : entries) {
          if (!entry.startsWith("dev/codex/schubert/nk/"))
            throw new IllegalArgumentException("normal project class namespace only");
          byte[] bytes;
          try (var input = archive.getInputStream(archive.getEntry(entry))) {
            bytes = input.readAllBytes();
          }
          var value = inspect(entry, bytes);
          System.out.println(
              String.join(
                  "\t", List.of(module, entry, value.name(), value.source(), value.sha256())));
        }
      }
    }
  }
}
