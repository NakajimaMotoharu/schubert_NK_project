import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.jar.JarFile;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.Handle;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

/** Read-only exact descriptors including invokedynamic handles; not unreachable/coverage credit. */
public final class Pg2584MorningFactoryReferences {
  private Pg2584MorningFactoryReferences() {}

  private static final String PREFIX = "dev/codex/schubert/nk/batch/file/";
  private static final List<String> TARGETS =
      List.of(
          PREFIX + "MorningControlScope",
          PREFIX + "MorningBackupStage",
          PREFIX + "MorningStartupLaunchOwner");
  private static final Map<String, List<String>> REFERENCES = new HashMap<>();
  private static final Map<String, Integer> DECLARATIONS = new HashMap<>();

  private static void reference(String owner, String name, String descriptor, String caller) {
    if (TARGETS.contains(owner))
      REFERENCES
          .computeIfAbsent(owner + "#" + name + descriptor, ignored -> new ArrayList<>())
          .add(caller);
  }

  public static void main(String[] args) throws Exception {
    if (args == null || args.length != 6)
      throw new IllegalArgumentException("six fixed Main Jars required");
    int classes = 0;
    for (String name : args) {
      try (var jar = new JarFile(Path.of(name).toFile())) {
        var entries = jar.entries();
        while (entries.hasMoreElements()) {
          var entry = entries.nextElement();
          if (!entry.getName().endsWith(".class")) continue;
          classes++;
          try (var input = jar.getInputStream(entry)) {
            new ClassReader(input)
                .accept(
                    new ClassVisitor(Opcodes.ASM9) {
                      private String type;

                      @Override
                      public void visit(
                          int version,
                          int access,
                          String owner,
                          String signature,
                          String parent,
                          String[] interfaces) {
                        type = owner;
                      }

                      @Override
                      public MethodVisitor visitMethod(
                          int access,
                          String method,
                          String descriptor,
                          String signature,
                          String[] exceptions) {
                        String caller = type + "#" + method + descriptor;
                        if (TARGETS.contains(type)) DECLARATIONS.put(caller, access);
                        return new MethodVisitor(Opcodes.ASM9) {
                          @Override
                          public void visitMethodInsn(
                              int opcode,
                              String owner,
                              String name,
                              String desc,
                              boolean isInterface) {
                            reference(owner, name, desc, caller);
                          }

                          @Override
                          public void visitInvokeDynamicInsn(
                              String name, String desc, Handle bootstrap, Object... arguments) {
                            reference(
                                bootstrap.getOwner(),
                                bootstrap.getName(),
                                bootstrap.getDesc(),
                                caller);
                            for (Object argument : arguments)
                              if (argument instanceof Handle handle)
                                reference(
                                    handle.getOwner(), handle.getName(), handle.getDesc(), caller);
                          }
                        };
                      }
                    },
                    ClassReader.SKIP_DEBUG | ClassReader.SKIP_FRAMES);
          }
        }
      }
    }
    if (classes != 1643) throw new IllegalStateException("whole current Main inventory required");
    System.out.println(
        "MainClasses=" + classes + " reflectionAndSourceAndTestAuditPending=true coverageCredit=0");
    DECLARATIONS.entrySet().stream()
        .sorted(Comparator.comparing(Map.Entry::getKey))
        .forEach(
            entry -> {
              String method = entry.getKey();
              if (method.contains("#lambda$") || method.contains("#<")) return;
              var refs =
                  REFERENCES.getOrDefault(method, List.of()).stream().distinct().sorted().toList();
              System.out.println(
                  "METHOD "
                      + method
                      + " access="
                      + entry.getValue()
                      + " directOrHandleCallers="
                      + refs.size());
              refs.forEach(caller -> System.out.println("CALLER " + caller));
            });
  }
}
