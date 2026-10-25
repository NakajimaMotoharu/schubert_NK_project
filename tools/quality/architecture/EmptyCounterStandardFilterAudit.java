import java.nio.file.Files;
import java.nio.file.Path;
import java.util.BitSet;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.zip.ZipFile;
import org.jacoco.core.internal.analysis.filter.Filters;
import org.jacoco.core.internal.analysis.filter.IFilterContext;
import org.jacoco.core.internal.analysis.filter.IFilterOutput;
import org.jacoco.core.internal.analysis.filter.KotlinSMAP;
import org.jacoco.core.internal.analysis.filter.Replacements;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.AbstractInsnNode;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodNode;

/** Applies the pinned analyzer's standard filters to byte arrays, never target execution. */
public final class EmptyCounterStandardFilterAudit {
  private EmptyCounterStandardFilterAudit() {}

  private record Context(ClassNode node) implements IFilterContext {
    @Override
    public String getClassName() {
      return node.name;
    }

    @Override
    public String getSuperClassName() {
      return node.superName;
    }

    @Override
    public int getClassAccess() {
      return node.access;
    }

    @Override
    public String getSourceFileName() {
      return node.sourceFile;
    }

    @Override
    public KotlinSMAP getKotlinSMAP() {
      return null;
    }

    @Override
    public Set<String> getClassAttributes() {
      return node.recordComponents == null ? Set.of() : Set.of("Record");
    }

    @Override
    public Set<String> getClassAnnotations() {
      var result = new HashSet<String>();
      if (node.visibleAnnotations != null) node.visibleAnnotations.forEach(a -> result.add(a.desc));
      if (node.invisibleAnnotations != null)
        node.invisibleAnnotations.forEach(a -> result.add(a.desc));
      return Set.copyOf(result);
    }
  }

  private static final class Output implements IFilterOutput {
    private final MethodNode method;
    private final BitSet ignored = new BitSet();

    private Output(MethodNode method) {
      this.method = method;
    }

    @Override
    public void ignore(AbstractInsnNode from, AbstractInsnNode to) {
      int start = method.instructions.indexOf(from);
      int end = method.instructions.indexOf(to);
      if (start < 0 || end < start)
        throw new IllegalArgumentException("bounded original range required");
      ignored.set(start, end + 1);
    }

    @Override
    public void merge(AbstractInsnNode first, AbstractInsnNode second) {
      throw new IllegalStateException("unexpected merge, no applicability inference permitted");
    }

    @Override
    public void replaceBranches(AbstractInsnNode source, Replacements replacements) {
      throw new IllegalStateException("unexpected branch replacement");
    }
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 2)
      throw new IllegalArgumentException("Jar and whole-class catalogs required");
    Set<String> expected = Set.copyOf(Files.readAllLines(Path.of(args[1])));
    if (expected.size() != 31) throw new IllegalArgumentException("exact frozen31 scope");
    var seen = new HashSet<String>();
    int methodCount = 0;
    for (String line : Files.readAllLines(Path.of(args[0]))) {
      String[] fields = line.split("\t", -1);
      if (fields.length != 2) throw new IllegalArgumentException("module and Jar required");
      try (var archive = new ZipFile(Path.of(fields[1]).toFile())) {
        for (String key : expected.stream().sorted().toList()) {
          if (!key.startsWith(fields[0] + ":")) continue;
          String entry = key.substring(key.indexOf(':') + 1);
          byte[] bytes;
          try (var stream = archive.getInputStream(archive.getEntry(entry))) {
            bytes = stream.readAllBytes();
          }
          var node = new ClassNode(Opcodes.ASM9);
          new ClassReader(bytes).accept(node, 0);
          if (!(node.name + ".class").equals(entry) || !seen.add(key))
            throw new IllegalArgumentException("exact class identity");
          System.out.println("CLASS\t" + key + "\t" + node.superName + "\t" + node.access);
          for (var method : node.methods) {
            if (method.instructions.size() == 0) continue;
            var out = new Output(method);
            Filters.all().filter(method, new Context(node), out);
            int total = 0;
            int ignored = 0;
            for (int i = 0; i < method.instructions.size(); i++) {
              if (method.instructions.get(i).getOpcode() >= 0) {
                total++;
                if (out.ignored.get(i)) ignored++;
              }
            }
            System.out.println(
                String.join(
                    "\t",
                    List.of(
                        "METHOD",
                        key,
                        method.name,
                        method.desc,
                        Integer.toString(method.access),
                        Integer.toString(total),
                        Integer.toString(ignored))));
            methodCount++;
          }
        }
      }
    }
    if (!seen.equals(expected) || methodCount != 49)
      throw new IllegalStateException("all31/49 required");
    System.out.println("TOTAL\t31\t49");
  }
}
