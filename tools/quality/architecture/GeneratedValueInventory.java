import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Set;
import java.util.jar.JarFile;
import org.objectweb.asm.ClassReader;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.Type;
import org.objectweb.asm.tree.AbstractInsnNode;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.FieldInsnNode;
import org.objectweb.asm.tree.InvokeDynamicInsnNode;
import org.objectweb.asm.tree.LineNumberNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.MethodNode;
import org.objectweb.asm.tree.VarInsnNode;

/** Read class bytes only. Target Jars are never classpath entries or loaded/initialized. */
public final class GeneratedValueInventory {
  private static final Set<String> ROLES =
      Set.of("protocol", "storage", "bootstrap", "api", "web", "batch", "canary");

  private GeneratedValueInventory() {}

  private static void row(String... fields) {
    for (String field : fields) {
      if (field.indexOf('\t') >= 0 || field.indexOf('\n') >= 0 || field.indexOf('\r') >= 0)
        throw new IllegalArgumentException("bounded symbolic metadata only");
    }
    System.out.println(String.join("\t", fields));
  }

  private static String shape(ClassNode owner, MethodNode method, boolean record) {
    if (record) {
      for (AbstractInsnNode instruction : method.instructions) {
        if (instruction instanceof InvokeDynamicInsnNode dynamic
            && dynamic.bsm.getOwner().equals("java/lang/runtime/ObjectMethods")
            && dynamic.bsm.getName().equals("bootstrap"))
          return "JDK_OBJECTMETHODS_BOOTSTRAP";
      }
      if (owner.recordComponents != null) {
        for (var component : owner.recordComponents) {
          if (!component.name.equals(method.name)
              || !method.desc.equals("()" + component.descriptor)) continue;
          var instructions = new java.util.ArrayList<AbstractInsnNode>();
          for (AbstractInsnNode instruction : method.instructions)
            if (instruction.getOpcode() >= 0) instructions.add(instruction);
          if (instructions.size() == 3
              && instructions.get(0) instanceof VarInsnNode load
              && load.getOpcode() == Opcodes.ALOAD && load.var == 0
              && instructions.get(1) instanceof FieldInsnNode field
              && field.getOpcode() == Opcodes.GETFIELD && field.owner.equals(owner.name)
              && field.name.equals(component.name) && field.desc.equals(component.descriptor)
              && instructions.get(2).getOpcode() == Type.getType(component.descriptor).getOpcode(Opcodes.IRETURN))
            return "FIELD_ACCESSOR_SHAPE_SOURCE_REVIEW_REQUIRED";
        }
      }
    } else if (method.name.equals("values") && method.desc.equals("()[L" + owner.name + ";")) {
      return "ENUM_VALUES_FACTORY";
    } else if (method.name.equals("valueOf")
        && method.desc.equals("(Ljava/lang/String;)L" + owner.name + ";")) {
      return "ENUM_VALUEOF_FACTORY";
    }
    return "ORDINARY_OR_OVERRIDDEN";
  }

  public static void main(String[] args) throws Exception {
    if (Runtime.version().feature() != 25 || args.length == 0)
      throw new IllegalArgumentException("JDK25 and explicit role=Jar entries required");
    Set<String> roles = new HashSet<>();
    Set<String> identities = new HashSet<>();
    int physical = 0;
    int generatedTypes = 0;
    for (String argument : args) {
      int split = argument.indexOf('=');
      if (split <= 0) throw new IllegalArgumentException("literal role and Jar required");
      String role = argument.substring(0, split);
      if (!ROLES.contains(role) || !roles.add(role))
        throw new IllegalArgumentException("unique declared role required");
      try (var jar = new JarFile(Path.of(argument.substring(split + 1)).toFile(), false)) {
        for (var entry : jar.stream().filter(e -> e.getName().endsWith(".class"))
            .sorted(java.util.Comparator.comparing(java.util.jar.JarEntry::getName)).toList()) {
          if (entry.getSize() <= 0 || entry.getSize() > 8 * 1024 * 1024)
            throw new IllegalArgumentException("bounded original class bytes only");
          byte[] bytes;
          try (var input = jar.getInputStream(entry)) { bytes = input.readAllBytes(); }
          var type = new ClassNode(Opcodes.ASM9);
          new ClassReader(bytes).accept(type, ClassReader.SKIP_FRAMES);
          if (!entry.getName().equals(type.name + ".class")
              || !identities.add(role + ":" + type.name))
            throw new IllegalArgumentException("exact class entry/role identity required");
          physical++;
          boolean record = "java/lang/Record".equals(type.superName);
          boolean enumeration = (type.access & Opcodes.ACC_ENUM) != 0;
          if (!record && !enumeration) continue;
          generatedTypes++;
          String sha = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
          row("TYPE", role, type.name, record ? "RECORD" : "ENUM", sha,
              type.sourceFile == null ? "SOURCE_METADATA_MISSING" : type.sourceFile,
              Integer.toString(type.access));
          if (record && type.recordComponents != null)
            for (var component : type.recordComponents)
              row("COMPONENT", role, type.name, component.name, component.descriptor);
          for (var method : type.methods) {
            int first = Integer.MAX_VALUE;
            int last = -1;
            for (AbstractInsnNode instruction : method.instructions)
              if (instruction instanceof LineNumberNode line) {
                first = Math.min(first, line.line);
                last = Math.max(last, line.line);
              }
            row("METHOD", role, type.name, method.name, method.desc,
                Integer.toString(method.access), shape(type, method, record),
                Integer.toString(last < 0 ? -1 : first), Integer.toString(last));
            if (List.of("<clinit>", "<init>").contains(method.name))
              for (AbstractInsnNode instruction : method.instructions) {
                if (instruction instanceof MethodInsnNode call)
                  row("INITCALL", role, type.name, method.name, call.owner, call.name, call.desc);
                else if (instruction instanceof FieldInsnNode field && field.getOpcode() == Opcodes.GETSTATIC)
                  row("INITFIELD", role, type.name, method.name, field.owner, field.name, field.desc);
                else if (instruction instanceof InvokeDynamicInsnNode dynamic)
                  row("INITDYNAMIC", role, type.name, method.name,
                      dynamic.bsm.getOwner(), dynamic.bsm.getName(), dynamic.desc);
              }
          }
        }
      }
    }
    row("RESULT", Integer.toString(physical), Integer.toString(generatedTypes));
  }
}
