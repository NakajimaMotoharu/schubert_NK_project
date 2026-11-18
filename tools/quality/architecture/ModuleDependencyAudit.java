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
        for (var dependency : type.getDirectDependenciesFromSelf()) {
          dependencies++;
          String target = component(dependency.getTargetClass().getName());
          String targetModule = owners.get(target);
          String pair = origin + "\t" + target;
          if (targetModule != null && !targetModule.equals(module) && !ALLOWED.get(module).contains(targetModule))
            violations.get("MODULE_EDGES").add(pair);
          if (target.startsWith(INTERNAL) && targetModule == null)
            violations.get("INTERNAL_OWNER").add(pair);
          if (forbiddenFramework(module, target)) violations.get("FRAMEWORK_FENCES").add(pair);
          if (controller && (jdbc(target) || jms(target) || "storage".equals(targetModule)))
            violations.get("CONTROLLER_BOUNDARY").add(pair);
        }
        for (var access : type.getCodeUnitAccessesFromSelf()) {
          calls++;
          String target = access.getTargetOwner().getName();
          if (controller && filesystem(target))
            violations.get("CONTROLLER_BOUNDARY").add(origin + "\t" + target);
          if (module.equals("api") && origin.startsWith(INTERNAL + "api.persistence.")
              && target.startsWith(INTERNAL + "api.application."))
            violations.get("REPOSITORY_DIRECTION").add(origin + "\t" + target);
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
        || target.startsWith("org.springframework.jdbc.");
  }

  private static boolean isController(JavaClass type) {
    return type.getSimpleName().contains("Controller")
        || type.isAnnotatedWith("org.springframework.stereotype.Controller")
        || type.isAnnotatedWith("org.springframework.web.bind.annotation.RestController");
  }

  private static boolean jms(String target) {
    return jmsApi(target) || target.startsWith("org.springframework.jms.");
  }

  private static boolean jmsApi(String target) {
    return target.startsWith("jakarta.jms.") || target.startsWith("javax.jms.");
  }

  private static boolean filesystem(String target) {
    return target.startsWith("java.nio.file.") || FILE_IO_TYPES.contains(target);
  }

  private static boolean forbiddenFramework(String module, String target) {
    boolean spring = target.startsWith("org.springframework.");
    boolean mvc = target.startsWith("org.springframework.web.servlet.")
        || target.startsWith("org.springframework.web.bind.annotation.")
        || target.startsWith("org.springframework.http.server.")
        || target.startsWith("org.thymeleaf.")
        || target.startsWith("jakarta.servlet.") || target.startsWith("javax.servlet.");
    boolean server = target.startsWith("com.sun.net.httpserver.");
    return switch (module) {
      case "protocol", "storage" -> jdbc(target) || jmsApi(target) || spring;
      case "bootstrap" -> jms(target) || mvc || server
          || target.startsWith("org.springframework.web.")
          || target.startsWith("org.springframework.http.")
          || target.startsWith("java.net.http.");
      case "api" -> mvc;
      case "batch" -> mvc || server;
      case "web" -> false;
      default -> throw new IllegalArgumentException("fixed physical module");
    };
  }
}
