import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.jar.JarFile;
import org.jacoco.core.instr.Instrumenter;
import org.jacoco.core.internal.data.CRC64;
import org.jacoco.core.runtime.OfflineInstrumentationAccessGenerator;
import org.jacoco.core.tools.ExecFileLoader;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.AbstractInsnNode;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.FieldInsnNode;
import org.objectweb.asm.tree.InsnNode;
import org.objectweb.asm.tree.IntInsnNode;
import org.objectweb.asm.tree.JumpInsnNode;
import org.objectweb.asm.tree.LabelNode;
import org.objectweb.asm.tree.LdcInsnNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.MethodNode;
import org.objectweb.asm.tree.TryCatchBlockNode;
import org.objectweb.asm.tree.VarInsnNode;

/**
 * Static byte-array/old-probe reader only. Never defines, initializes or invokes target classes.
 */
public final class ProtocolSwitchMapApplicabilityReviewV2 {
  private ProtocolSwitchMapApplicabilityReviewV2() {}

  private static void require(boolean condition, String message) {
    if (!condition) throw new IllegalStateException(message);
  }

  private static ClassNode parse(byte[] bytes) {
    var node = new ClassNode(Opcodes.ASM9);
    new ClassReader(bytes).accept(node, 0);
    return node;
  }

  private static int integer(AbstractInsnNode node) {
    int opcode = node.getOpcode();
    if (opcode >= Opcodes.ICONST_M1 && opcode <= Opcodes.ICONST_5) return opcode - Opcodes.ICONST_0;
    if (node instanceof IntInsnNode value && (opcode == Opcodes.BIPUSH || opcode == Opcodes.SIPUSH))
      return value.operand;
    if (node instanceof LdcInsnNode value && value.cst instanceof Integer number) return number;
    throw new IllegalStateException("explicit integer probe index required");
  }

  private static AbstractInsnNode previousCode(AbstractInsnNode node) {
    var previous = node.getPrevious();
    while (previous != null && previous.getOpcode() < 0) previous = previous.getPrevious();
    if (previous == null) throw new IllegalStateException("probe stack prefix missing");
    return previous;
  }

  private static LabelNode join(MethodNode method, TryCatchBlockNode handler) {
    int handlerIndex = method.instructions.indexOf(handler.handler);
    for (var node = handler.end.getNext();
        node != null && method.instructions.indexOf(node) < handlerIndex;
        node = node.getNext()) {
      if (node instanceof JumpInsnNode jump && jump.getOpcode() == Opcodes.GOTO) {
        require(method.instructions.indexOf(jump.label) > handlerIndex, "forward handler join");
        return jump.label;
      }
    }
    throw new IllegalStateException("explicit compiler handler join missing");
  }

  private static List<AbstractInsnNode> body(MethodNode method, TryCatchBlockNode handler) {
    var result = new ArrayList<AbstractInsnNode>();
    var end = join(method, handler);
    for (var node = handler.handler.getNext(); node != end; node = node.getNext()) {
      require(node != null, "bounded handler region");
      if (node.getOpcode() >= 0) result.add(node);
    }
    return result;
  }

  private static void emptyCatch(List<AbstractInsnNode> body) {
    require(
        body.size() == 1
            && body.getFirst() instanceof VarInsnNode store
            && store.getOpcode() == Opcodes.ASTORE,
        "compiler handler must only discard its exception into a local slot");
  }

  private static Map<Integer, AbstractInsnNode> probes(MethodNode method) {
    var result = new LinkedHashMap<Integer, AbstractInsnNode>();
    for (var node : method.instructions) {
      if (node.getOpcode() != Opcodes.BASTORE) continue;
      var one = previousCode(node);
      var index = previousCode(one);
      var array = previousCode(index);
      require(integer(one) == 1, "probe writes true only");
      require(
          array instanceof VarInsnNode v && v.getOpcode() == Opcodes.ALOAD, "probe array local");
      int id = integer(index);
      require(id >= 0 && result.put(id, node) == null, "unique nonnegative probe index");
    }
    return result;
  }

  private static void selftest() {
    require(integer(new InsnNode(Opcodes.ICONST_0)) == 0, "constant zero");
    require(integer(new IntInsnNode(Opcodes.BIPUSH, 16)) == 16, "constant sixteen");
    require(integer(new LdcInsnNode(7)) == 7, "ldc integer");
    try {
      integer(new InsnNode(Opcodes.ACONST_NULL));
      throw new AssertionError("noninteger accepted");
    } catch (IllegalStateException expected) {
      // Metadata fixture, not a target exception or product execution.
    }
    emptyCatch(List.of(new VarInsnNode(Opcodes.ASTORE, 0)));
    try {
      emptyCatch(List.of(new VarInsnNode(Opcodes.ASTORE, 0), new InsnNode(Opcodes.RETURN)));
      throw new AssertionError("nonempty handler accepted");
    } catch (IllegalStateException expected) {
      // A changed body must not inherit the compiler-only classification.
    }
    System.out.println("TOOL_SELFTEST\t6");
  }

  public static void main(String[] args) throws Exception {
    require(args.length == 2, "historical exec and exact current protocol jar required");
    selftest();
    var loader = new ExecFileLoader();
    loader.load(Path.of(args[0]).toFile());
    var sessions = loader.getSessionInfoStore().getInfos();
    require(
        sessions.size() == 1 && sessions.getFirst().getId().equals("PG9722-PROTOCOL-FULL-MODULE"),
        "one historical session, not current-source execution");
    var enums = new LinkedHashMap<String, ClassNode>();
    int totalHits = 0;
    int totalMisses = 0;
    try (var jar = new JarFile(args[1])) {
      for (var name :
          List.of(
              "dev/codex/schubert/nk/protocol/codec/PayloadCodec$1",
              "dev/codex/schubert/nk/protocol/file/MediaDescriptorValidator$1",
              "dev/codex/schubert/nk/protocol/layout/FieldDefinition$1",
              "dev/codex/schubert/nk/protocol/layout/LayoutFieldCatalog$1")) {
        byte[] bytes;
        try (var input = jar.getInputStream(jar.getJarEntry(name + ".class"))) {
          bytes = input.readAllBytes();
        }
        var original = parse(bytes);
        require(
            original.name.equals(name) && (original.access & Opcodes.ACC_SYNTHETIC) != 0,
            "exact synthetic class");
        require(
            !original.fields.isEmpty()
                && original.fields.stream()
                    .allMatch(
                        f ->
                            f.name.startsWith("$SwitchMap$")
                                && f.desc.equals("[I")
                                && (f.access & (Opcodes.ACC_STATIC | Opcodes.ACC_FINAL))
                                    == (Opcodes.ACC_STATIC | Opcodes.ACC_FINAL)),
            "switch-map arrays only");
        require(
            original.methods.size() == 1 && original.methods.getFirst().name.equals("<clinit>"),
            "one original clinit, never a source business method");
        var code = original.methods.getFirst();
        require(
            code.tryCatchBlocks.stream().allMatch(t -> "java/lang/NoSuchFieldError".equals(t.type)),
            "only missing-field compatibility handlers");
        var raw = loader.getExecutionDataStore().get(CRC64.classId(bytes));
        require(raw != null && raw.getName().equals(name), "historical CRC identity");
        var observed = raw.getProbes().clone();
        var transformed =
            new Instrumenter(new OfflineInstrumentationAccessGenerator())
                .instrument(bytes.clone(), name);
        var instrumented =
            parse(transformed).methods.stream()
                .filter(m -> m.name.equals("<clinit>"))
                .findFirst()
                .orElseThrow();
        var writes = probes(instrumented);
        require(
            writes.size() == observed.length
                && writes
                    .keySet()
                    .equals(
                        new HashSet<>(
                            java.util.stream.IntStream.range(0, observed.length).boxed().toList())),
            "all real probe indices, no insertion or omission");
        require(
            instrumented.tryCatchBlocks.size() == code.tryCatchBlocks.size(),
            "same handler inventory");
        var handlerIds = new TreeSet<Integer>();
        for (int number = 0; number < code.tryCatchBlocks.size(); number++) {
          var handler = code.tryCatchBlocks.get(number);
          emptyCatch(body(code, handler));
          var reference = new ArrayList<FieldInsnNode>();
          for (AbstractInsnNode node = handler.start; node != handler.end; node = node.getNext()) {
            if (node instanceof FieldInsnNode field
                && field.getOpcode() == Opcodes.GETSTATIC
                && !field.owner.equals(name)) reference.add(field);
          }
          require(reference.size() == 1, "one enum constant assignment per handler");
          var field = reference.getFirst();
          if (!enums.containsKey(field.owner)) {
            try (var input = jar.getInputStream(jar.getJarEntry(field.owner + ".class"))) {
              enums.put(field.owner, parse(input.readAllBytes()));
            }
          }
          var enumeration = enums.get(field.owner);
          require(
              enumeration.superName.equals("java/lang/Enum")
                  && (enumeration.access & Opcodes.ACC_ENUM) != 0,
              "actual enum definition in this artifact");
          require(
              field.desc.equals("L" + field.owner + ";")
                  && enumeration.fields.stream()
                      .anyMatch(
                          f ->
                              f.name.equals(field.name)
                                  && f.desc.equals(field.desc)
                                  && (f.access
                                          & (Opcodes.ACC_ENUM
                                              | Opcodes.ACC_STATIC
                                              | Opcodes.ACC_PUBLIC))
                                      == (Opcodes.ACC_ENUM
                                          | Opcodes.ACC_STATIC
                                          | Opcodes.ACC_PUBLIC)),
              "referenced enum field exists with exact descriptor and public static enum flags");
          var corresponding = instrumented.tryCatchBlocks.get(number);
          var region = body(instrumented, corresponding);
          var ids =
              writes.entrySet().stream()
                  .filter(e -> region.contains(e.getValue()))
                  .map(Map.Entry::getKey)
                  .toList();
          require(
              ids.size() == 1 && handlerIds.add(ids.getFirst()),
              "one distinct compatibility-handler probe");
          System.out.println(
              "HANDLER\t"
                  + name
                  + "\t"
                  + number
                  + "\t"
                  + ids.getFirst()
                  + "\t"
                  + field.owner
                  + "\t"
                  + field.name
                  + "\t"
                  + field.desc
                  + "\t"
                  + code.instructions.indexOf(handler.handler));
        }
        var misses = new TreeSet<Integer>();
        for (int id = 0; id < observed.length; id++) if (!observed[id]) misses.add(id);
        require(
            misses.equals(handlerIds),
            "every and only missed probe is in an empty compatibility handler");
        var allowedEnums = Set.copyOf(enums.keySet());
        for (var node : code.instructions) {
          if (node instanceof MethodInsnNode call)
            require(
                allowedEnums.contains(call.owner)
                    && (call.name.equals("values") && call.desc.equals("()[L" + call.owner + ";")
                        || call.name.equals("ordinal") && call.desc.equals("()I")),
                "enum metadata calls only");
        }
        int hit = observed.length - misses.size();
        totalHits += hit;
        totalMisses += misses.size();
        System.out.println(
            "CLASS\t"
                + name
                + "\t"
                + Long.toUnsignedString(raw.getId(), 16)
                + "\t"
                + observed.length
                + "\t"
                + hit
                + "\t"
                + misses.size()
                + "\t"
                + code.tryCatchBlocks.size());
      }
      for (var entry : enums.entrySet()) {
        var node = entry.getValue();
        require(
            node.methods.stream()
                .anyMatch(
                    m ->
                        m.name.equals("values")
                            && m.desc.equals("()[L" + node.name + ";")
                            && (m.access & Opcodes.ACC_STATIC) != 0),
            "enum values method present before assignments");
        System.out.println(
            "ENUM\t"
                + entry.getKey()
                + "\t"
                + node.fields.stream()
                    .filter(f -> (f.access & Opcodes.ACC_ENUM) != 0)
                    .map(f -> f.name)
                    .sorted()
                    .toList());
      }
    }
    require(totalHits == 25 && totalMisses == 16, "original measurements unchanged");
    System.out.println("TOTAL\t25\t16\tNO_TARGET_EXECUTION\tNO_COVERAGE_PROMOTION");
  }
}
