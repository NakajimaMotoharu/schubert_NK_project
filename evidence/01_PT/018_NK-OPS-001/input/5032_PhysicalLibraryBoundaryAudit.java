import com.tngtech.archunit.ArchConfiguration;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.TreeMap;
import java.util.TreeSet;

/** F02 restricted physical library audit, SS311 §3. Source classification stays external. */
final class PhysicalLibraryBoundaryAudit {
  private static final String INTERNAL = "dev.codex.schubert.nk.";
  private static final List<String> MODULES = List.of("protocol", "storage", "bootstrap");

  public static void main(String[] args) throws Exception {
    if (args.length != MODULES.size()) throw new IllegalArgumentException("three exact libraries");
    var roots = new java.util.ArrayList<Path>();
    var owners = new HashMap<String, String>();
    var inventory = new TreeMap<String, Long>();
    for (int i = 0; i < MODULES.size(); i++) {
      String module = MODULES.get(i);
      Path root = Path.of(args[i]);
      roots.add(root);
      try (var files = Files.walk(root)) {
        var classes = files.filter(p -> p.getFileName().toString().endsWith(".class")).toList();
        if (classes.isEmpty()) throw new IllegalStateException("empty physical inventory");
        for (Path file : classes) {
          String entry = root.relativize(file).toString();
          if (Files.isSymbolicLink(file) || !Files.isRegularFile(file))
            throw new IllegalArgumentException("unexpected physical artifact");
          String type = entry.substring(0, entry.length() - 6).replace('/', '.');
          if (!type.startsWith(INTERNAL) || owners.putIfAbsent(type, module) != null)
            throw new IllegalArgumentException("unknown or duplicate physical type");
        }
        inventory.put(module, (long) classes.size());
      }
    }

    ArchConfiguration.get().setResolveMissingDependenciesFromClassPath(false);
    var parsed = new ClassFileImporter().importPaths(roots);
    var allNames = new HashSet<String>();
    var directions = new TreeMap<String, Integer>();
    var violations = new TreeSet<String>();
    int references = 0;
    int accesses = 0;
    for (var type : parsed) {
      String source = type.getName();
      allNames.add(source);
      String sourceModule = owners.get(source);
      if (sourceModule == null) throw new IllegalStateException("unexpected imported type");
      accesses += type.getCodeUnitAccessesFromSelf().size();
      for (var dep : type.getDirectDependenciesFromSelf()) {
        references++;
        String target = dep.getTargetClass().getName();
        while (target.endsWith("[]")) target = target.substring(0, target.length() - 2);
        String targetModule = owners.get(target);
        if (target.startsWith(INTERNAL) && targetModule == null)
          violations.add("UNKNOWN_INTERNAL\t" + source + "\t" + target);
        if (targetModule != null && !sourceModule.equals(targetModule)) {
          directions.merge(sourceModule + "->" + targetModule, 1, Integer::sum);
          if (!sourceModule.equals("bootstrap") || !targetModule.equals("storage"))
            violations.add("FORBIDDEN_EDGE\t" + source + "\t" + target);
        }
        if (forbiddenFramework(sourceModule, target))
          violations.add("FRAMEWORK_FENCE\t" + source + "\t" + target);
      }
    }

    if (!allNames.equals(owners.keySet()))
      throw new IllegalStateException("physical import coverage mismatch");
    inventory.forEach((m, n) -> System.out.println("MODULE\t" + m + "\t" + n));
    directions.forEach((pair, n) -> System.out.println("EDGE\t" + pair + "\t" + n));
    violations.forEach(v -> System.out.println("FINDING\t" + v));
    System.out.printf(
        "TOTAL\t%d\t%d\t%d\t%d%n", allNames.size(), references, accesses, violations.size());
    if (!violations.isEmpty()) System.exit(1);
  }

  private static boolean forbiddenFramework(String module, String target) {
    boolean mq =
        target.startsWith("javax.jms.")
            || target.startsWith("jakarta.jms.")
            || target.startsWith("org.apache.artemis.")
            || target.startsWith("org.springframework.jms.");
    boolean jdbc = target.startsWith("java.sql.") || target.startsWith("javax.sql.");
    boolean web =
        target.startsWith("org.springframework.web.servlet.")
            || target.startsWith("jakarta.servlet.")
            || target.startsWith("javax.servlet.")
            || target.startsWith("org.thymeleaf.")
            || target.startsWith("com.sun.net.httpserver.");
    if (module.equals("bootstrap")) return mq || web;
    return mq || jdbc || web || target.startsWith("org.springframework.");
  }
}
