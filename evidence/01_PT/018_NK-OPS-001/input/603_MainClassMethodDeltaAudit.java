import java.lang.classfile.Attributes;
import java.lang.classfile.ClassFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import java.util.zip.ZipFile;

/** SDK data reader only; never define, initialize or invoke a target class. */
public final class MainClassMethodDeltaAudit {
  private MainClassMethodDeltaAudit() {}

  private static final Set<String> HELD =
      Set.of(
          "api:dev/codex/schubert/nk/api/error/TemporaryInfrastructureException.class",
          "web:dev/codex/schubert/nk/web/bootstrap/WebStartupException.class");

  public static void main(String[] args) throws Exception {
    if (args.length != 3) throw new IllegalArgumentException("snapshot/jars/delta required");
    var snapshot = Path.of(args[0]).toRealPath();
    var selected = new HashSet<>(Files.readAllLines(Path.of(args[2])));
    if (selected.size() != 42 || selected.stream().anyMatch(HELD::contains))
      throw new IllegalArgumentException("exact non-held delta required");
    var modules = Set.of("protocol", "storage", "bootstrap", "api", "web", "batch");
    var observedModules = new HashSet<String>();
    var observed = new HashSet<String>();
    var parsedKeys = new HashSet<String>();
    int held = 0;
    int reused = 0;
    for (String line : Files.readAllLines(Path.of(args[1]))) {
      String[] input = line.split("\t", -1);
      if (input.length != 2 || !modules.contains(input[0]) || !observedModules.add(input[0]))
        throw new IllegalArgumentException("exact unique module catalog required");
      var jar = Path.of(input[1]);
      if (!jar.toRealPath().equals(jar)
          || !jar.startsWith(snapshot.resolve("src/schubert-nk-" + input[0] + "/target"))
          || !jar.getFileName().toString().endsWith(".jar"))
        throw new IllegalArgumentException("fixed normal compiler Jar only");
      try (var archive = new ZipFile(jar.toFile())) {
        for (var entry :
            archive.stream()
                .filter(e -> e.getName().endsWith(".class"))
                .sorted(java.util.Comparator.comparing(java.util.zip.ZipEntry::getName))
                .toList()) {
          String key = input[0] + ":" + entry.getName();
          if (!observed.add(key)
              || !entry.getName().matches("dev/codex/schubert/nk/[A-Za-z0-9_/$-]+\\.class"))
            throw new IllegalArgumentException("unique exact namespace required");
          // Both guards precede getInputStream/read/parse, including for explicit HOLDs.
          if (HELD.contains(key)) {
            System.out.println("HOLD\t" + key);
            held++;
            continue;
          }
          if (!selected.contains(key)) {
            reused++;
            continue;
          }
          byte[] bytes;
          try (var stream = archive.getInputStream(entry)) {
            bytes = stream.readAllBytes();
          }
          var model = ClassFile.of().parse(bytes);
          if (model.majorVersion() != 69
              || !(model.thisClass().asInternalName() + ".class").equals(entry.getName()))
            throw new IllegalArgumentException("exact Java25 identity required");
          String source =
              model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile().stringValue();
          if (!source.matches("[A-Za-z0-9_$-]+\\.java"))
            throw new IllegalArgumentException("simple SourceFile required");
          System.out.println(
              "CLASS\t"
                  + key
                  + "\t"
                  + model.flags().flagsMask()
                  + "\t"
                  + source
                  + "\t"
                  + model.fields().size()
                  + "\t"
                  + model.methods().size());
          for (var method : model.methods()) {
            var code = method.findAttribute(Attributes.code());
            System.out.println(
                "METHOD\t"
                    + key
                    + "\t"
                    + method.methodName().stringValue()
                    + "\t"
                    + method.methodType().stringValue()
                    + "\t"
                    + method.flags().flagsMask()
                    + "\t"
                    + code.isPresent()
                    + "\t"
                    + code.map(c -> c.codeLength()).orElse(0));
          }
          parsedKeys.add(key);
        }
      }
    }
    if (!observedModules.equals(modules)
        || observed.size() != 1845
        || !parsedKeys.equals(selected)
        || held != 2
        || reused != 1801)
      throw new IllegalStateException("complete current names with exact delta/reuse/HOLD required");
    System.out.println("TOTAL\t" + parsedKeys.size() + "\t" + held + "\t" + reused);
  }
}
