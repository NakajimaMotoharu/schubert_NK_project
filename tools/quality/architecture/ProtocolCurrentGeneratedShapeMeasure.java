import java.lang.classfile.ClassFile;
import java.lang.classfile.Attributes;
import java.lang.reflect.AccessFlag;
import java.nio.file.Path;
import java.util.List;
import java.util.jar.JarFile;
import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.tools.ExecFileLoader;

/** Describe standard-filtered compiler helpers and their real probes; never synthesize coverage. */
public final class ProtocolCurrentGeneratedShapeMeasure {
  private ProtocolCurrentGeneratedShapeMeasure() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("current exec and exact protocol jar required");
    var exec = new ExecFileLoader();
    exec.load(Path.of(args[0]).toFile());
    if (exec.getSessionInfoStore().getInfos().size() != 1
        || !exec.getSessionInfoStore()
            .getInfos()
            .getFirst()
            .getId()
            .equals("PG10188-PROTOCOL-CURRENT-SOURCE")) {
      throw new IllegalStateException("one current actual protocol session required");
    }
    var builder = new CoverageBuilder();
    new Analyzer(exec.getExecutionDataStore(), builder).analyzeAll(Path.of(args[1]).toFile());
    int observed = 0;
    try (var jar = new JarFile(args[1])) {
      for (String name :
          List.of(
              "dev/codex/schubert/nk/protocol/codec/PayloadCodec$1",
              "dev/codex/schubert/nk/protocol/file/MediaDescriptorValidator$1",
              "dev/codex/schubert/nk/protocol/layout/FieldDefinition$1",
              "dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog$1")) {
        byte[] bytes;
        try (var stream = jar.getInputStream(jar.getJarEntry(name + ".class"))) {
          bytes = stream.readAllBytes();
        }
        var model = ClassFile.of().parse(bytes);
        String simple = name.substring(name.lastIndexOf('/') + 1);
        String source = simple.substring(0, simple.indexOf('$')) + ".java";
        if (!model.thisClass().asInternalName().equals(name)
            || !model.flags().has(AccessFlag.SYNTHETIC)
            || model.fields().isEmpty()
            || model.fields().stream()
                .anyMatch(f -> !f.fieldName().stringValue().startsWith("$SwitchMap$")
                    || !f.fieldType().stringValue().equals("[I")
                    || !f.flags().has(AccessFlag.STATIC) || !f.flags().has(AccessFlag.FINAL)
                    || !f.flags().has(AccessFlag.SYNTHETIC))
            || !model.findAttribute(Attributes.sourceFile()).orElseThrow().sourceFile().stringValue().equals(source)
            || model.methods().size() != 1
            || !model.methods().getFirst().methodName().stringValue().equals("<clinit>")
            || !model.methods().getFirst().flags().has(AccessFlag.STATIC)
            || model.methods().getFirst().code().isEmpty()) {
          throw new IllegalStateException("exact compiler switch-map shape required");
        }
        var coverage =
            builder.getClasses().stream()
                .filter(c -> c.getName().equals(name))
                .findFirst()
                .orElseThrow();
        if (coverage.getLineCounter().getTotalCount() != 0
            || coverage.getMethodCounter().getTotalCount() != 0
            || coverage.getClassCounter().getTotalCount() != 0
            || coverage.getBranchCounter().getTotalCount() != 0) {
          throw new IllegalStateException("standard-filtered empty counter shape required");
        }
        var actual = exec.getExecutionDataStore().get(coverage.getId());
        if (actual == null || !actual.getName().equals(name))
          throw new IllegalStateException("current actual CRC/probes required");
        int hit = 0;
        for (boolean probe : actual.getProbes()) if (probe) hit++;
        System.out.println(
            "GENERATED\t"
                + name
                + "\t"
                + Long.toUnsignedString(coverage.getId(), 16)
                + "\t"
                + model.fields().size()
                + "\t"
                + hit
                + "\t"
                + (actual.getProbes().length - hit));
        observed++;
      }
    }
    if (observed != 4)
      throw new IllegalStateException("all four filtered compiler helpers required");
  }
}
