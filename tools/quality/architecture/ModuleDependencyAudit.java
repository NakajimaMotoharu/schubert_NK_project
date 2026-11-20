import com.tngtech.archunit.ArchConfiguration;
import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.jar.JarFile;

/**
 * F02 / SS311 sections2-3,5.2,10 / PG-D516. Static bytecode only, not a service entry.
 * Input is six caller-authenticated original Jars or private handwritten canary Jars.
 * No target class is loaded/reflected/initialized/executed. No architecture rule is frozen.
 */
public final class ModuleDependencyAudit {
  private static final String INTERNAL = "dev.codex.schubert.nk.";
  private static final String WEB_REPLY_CLIENT = INTERNAL + "web.messaging.JmsRequestReplyClient";
  private static final Set<String> OBJECT_SERIALIZATION_TYPES =
      Set.of(
          "java.io.Externalizable",
          "java.io.InvalidClassException",
          "java.io.InvalidObjectException",
          "java.io.NotActiveException",
          "java.io.NotSerializableException",
          "java.io.ObjectInput",
          "java.io.ObjectInputFilter",
          "java.io.ObjectInputStream",
          "java.io.ObjectInputValidation",
          "java.io.ObjectOutput",
          "java.io.ObjectOutputStream",
          "java.io.ObjectStreamClass",
          "java.io.ObjectStreamConstants",
          "java.io.ObjectStreamException",
          "java.io.ObjectStreamField",
          "java.io.OptionalDataException",
          "java.io.Serial",
          "java.io.Serializable",
          "java.io.StreamCorruptedException",
          "java.io.WriteAbortedException");
  private static final Set<String> MODULES =
      Set.of("protocol", "storage", "bootstrap", "api", "web", "batch");
  private static final Set<String> FILE_IO_TYPES =
      Set.of(
          "java.io.File", "java.io.FileInputStream", "java.io.FileOutputStream",
          "java.io.FileReader", "java.io.FileWriter", "java.io.RandomAccessFile",
          "java.nio.channels.FileChannel", "java.nio.channels.AsynchronousFileChannel");
  private static final Map<String, Set<String>> ALLOWED =
      Map.of(
          "protocol", Set.of(),
          "storage", Set.of(),
          "bootstrap", Set.of("storage"),
          "api", Set.of("protocol", "storage", "bootstrap"),
          "web", Set.of("protocol", "storage", "bootstrap"),
          "batch", Set.of("storage", "bootstrap"));

  private ModuleDependencyAudit() {}

  public static void main(String[] args) throws IOException {
    if (args.length != MODULES.size()) throw new IllegalArgumentException("six explicit module Jars");
    Map<String, String> owners = new HashMap<>();
    Map<String, Integer> inputCounts = new TreeMap<>();
    List<JarFile> jars = new ArrayList<>();
    try {
      for (String arg : args) {
        int split = arg.indexOf('=');
        if (split <= 0) throw new IllegalArgumentException("module=path required");
        String module = arg.substring(0, split);
        if (!MODULES.contains(module) || inputCounts.containsKey(module))
          throw new IllegalArgumentException("unique approved module");
        JarFile jar = new JarFile(Path.of(arg.substring(split + 1)).toFile());
        jars.add(jar);
        int count = 0;
        var entries = jar.entries();
        while (entries.hasMoreElements()) {
          var entry = entries.nextElement();
          if (entry.isDirectory() || !entry.getName().endsWith(".class")) continue;
          String name = entry.getName();
          if (name.startsWith("META-INF/") || name.contains(".."))
            throw new IllegalArgumentException("ordinary exact class inventory only");
          name = name.substring(0, name.length() - 6).replace('/', '.');
          if (owners.putIfAbsent(name, module) != null)
            throw new IllegalArgumentException("duplicate physical class");
          count++;
        }
        if (count == 0) throw new IllegalArgumentException("nonempty physical module");
        inputCounts.put(module, count);
      }
      ArchConfiguration.get().setResolveMissingDependenciesFromClassPath(false);
      JavaClasses classes = new ClassFileImporter().importJars(jars);
      Set<String> actual = new HashSet<>();
      for (JavaClass type : classes) actual.add(type.getName());
      if (!actual.equals(owners.keySet()))
        throw new IllegalStateException("all input classes must be imported without omission");
      if (System.getProperty("nk.archunit.canary.initialized") != null)
        throw new IllegalStateException("target initializer was executed");

      Map<String, Set<String>> violations = new TreeMap<>();
      for (String rule : List.of("MODULE_EDGES", "FRAMEWORK_FENCES", "CONTROLLER_BOUNDARY", "REPOSITORY_DIRECTION", "INTERNAL_OWNER"))
        violations.put(rule, new TreeSet<>());
      int dependencies = 0;
      int calls = 0;
      for (JavaClass type : classes) {
        String origin = type.getName();
        String module = owners.get(origin);
        boolean controller = module.equals("web") && isController(type);
        boolean applicationOrDomain =
            (module.equals("api") || module.equals("web"))
                && (origin.startsWith(INTERNAL + module + ".application.")
                    || origin.startsWith(INTERNAL + module + ".domain."));
        boolean apiRepository = module.equals("api") && isApiRepository(type);
        for (var dependency : type.getDirectDependenciesFromSelf()) {
          dependencies++;
          String target = component(dependency.getTargetClass().getName());
          String targetModule = owners.get(target);
          String pair = origin + "\t" + target;
          if (targetModule != null
              && !targetModule.equals(module)
              && (!ALLOWED.get(module).contains(targetModule)
                  || (applicationOrDomain && targetModule.equals("storage")))) {
            violations.get("MODULE_EDGES").add(pair);
          }
          if (target.startsWith(INTERNAL) && targetModule == null)
            violations.get("INTERNAL_OWNER").add(pair);
          if (forbiddenFramework(module, target)) violations.get("FRAMEWORK_FENCES").add(pair);
          if (controller
              && (jdbc(target)
                  || jms(target)
                  || target.equals(WEB_REPLY_CLIENT)
                  || target.startsWith(WEB_REPLY_CLIENT + "$")
                  || "storage".equals(targetModule)))
            violations.get("CONTROLLER_BOUNDARY").add(pair);
          if (apiRepository && target.startsWith(INTERNAL + "api.application."))
            violations.get("REPOSITORY_DIRECTION").add(pair);
        }
        for (var access : type.getCodeUnitAccessesFromSelf()) {
          calls++;
          String target = access.getTargetOwner().getName();
          if (controller && filesystem(target))
            violations.get("CONTROLLER_BOUNDARY").add(origin + "\t" + target);
          if (module.equals("protocol") && protocolFilesystem(target))
            violations.get("FRAMEWORK_FENCES").add(origin + "\t" + target);
        }
      }
      System.out.println("ARCHUNIT\t1.4.2\t" + owners.size() + "\t" + actual.size());
      for (var entry : inputCounts.entrySet()) System.out.println("MODULE\t" + entry.getKey() + "\t" + entry.getValue());
      int failures = 0;
      for (var entry : violations.entrySet()) {
        System.out.println("RULE\t" + entry.getKey() + "\t" + entry.getValue().size());
        for (String detail : entry.getValue()) System.out.println("FINDING\t" + entry.getKey() + "\t" + detail);
        failures += entry.getValue().size();
      }
      System.out.println("INSPECTED\t" + dependencies + "\t" + calls);
      if (failures != 0) System.exit(1);
    } finally {
      for (int index = jars.size() - 1; index >= 0; index--) jars.get(index).close();
    }
  }

  private static String component(String name) {
    while (name.endsWith("[]")) name = name.substring(0, name.length() - 2);
    return name;
  }

  private static boolean jdbc(String target) {
    return target.startsWith("java.sql.")
        || target.startsWith("javax.sql.")
        || target.startsWith("org.springframework.jdbc.")
        || target.startsWith("org.postgresql.");
  }

  private static boolean isController(JavaClass type) {
    Set<JavaClass> visited = new HashSet<>();
    JavaClass enclosing = type;
    while (visited.add(enclosing)) {
      if (enclosing.getSimpleName().contains("Controller")
          || enclosing.isAnnotatedWith("org.springframework.stereotype.Controller")
          || enclosing.isAnnotatedWith("org.springframework.web.bind.annotation.RestController")) {
        return true;
      }
      var parent = enclosing.getEnclosingClass();
      if (parent.isEmpty()) {
        return false;
      }
      enclosing = parent.orElseThrow();
    }
    throw new IllegalArgumentException("cyclic enclosing class");
  }

  private static boolean isApiRepository(JavaClass type) {
    String name = type.getName();
    if (name.startsWith(INTERNAL + "api.persistence.")
        || name.startsWith(INTERNAL + "api.monitoring.persistence.")) {
      return true;
    }
    Set<JavaClass> visited = new HashSet<>();
    JavaClass enclosing = type;
    while (visited.add(enclosing)) {
      if (enclosing.getSimpleName().endsWith("Repository")
          || enclosing.isAnnotatedWith("org.springframework.stereotype.Repository")) {
        return true;
      }
      var parent = enclosing.getEnclosingClass();
      if (parent.isEmpty()) {
        return false;
      }
      enclosing = parent.orElseThrow();
    }
    throw new IllegalArgumentException("cyclic enclosing class");
  }

  private static boolean jms(String target) {
    return jmsApi(target) || target.startsWith("org.springframework.jms.");
  }

  private static boolean jmsApi(String target) {
    return target.startsWith("jakarta.jms.")
        || target.startsWith("javax.jms.")
        || target.startsWith("org.apache.activemq.artemis.");
  }

  private static boolean filesystem(String target) {
    return target.startsWith("java.nio.file.") || FILE_IO_TYPES.contains(target);
  }

  private static boolean protocolFilesystem(String target) {
    return FILE_IO_TYPES.contains(target)
        || target.equals("java.nio.file.Files")
        || target.equals("java.nio.file.FileSystems")
        || target.equals("java.nio.file.FileSystem")
        || target.equals("java.nio.file.FileStore")
        || target.equals("java.nio.file.spi.FileSystemProvider");
  }

  private static boolean javaSerialization(String target) {
    int enclosingTypeEnd = target.indexOf('$');
    return OBJECT_SERIALIZATION_TYPES.contains(
        enclosingTypeEnd < 0 ? target : target.substring(0, enclosingTypeEnd));
  }

  private static boolean forbiddenFramework(String module, String target) {
    if (module.equals("protocol") && javaSerialization(target)) return true;
    boolean spring = target.startsWith("org.springframework.");
    boolean mvc = target.startsWith("org.springframework.web.servlet.")
        || target.startsWith("org.springframework.web.bind.annotation.")
        || target.startsWith("org.springframework.http.server.")
        || target.startsWith("org.thymeleaf.")
        || target.startsWith("jakarta.servlet.") || target.startsWith("javax.servlet.");
    boolean server = target.startsWith("com.sun.net.httpserver.");
    boolean httpClient = target.startsWith("java.net.http.");
    return switch (module) {
      case "protocol", "storage" -> jdbc(target) || jmsApi(target) || spring || server || httpClient;
      case "bootstrap" -> jms(target) || mvc || server
          || target.startsWith("org.springframework.web.")
          || target.startsWith("org.springframework.http.")
          || httpClient;
      case "api" -> mvc;
      case "batch" -> mvc || server;
      case "web" -> false;
      default -> throw new IllegalArgumentException("fixed physical module");
    };
  }
}
