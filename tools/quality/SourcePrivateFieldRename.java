import com.sun.source.tree.BreakTree;
import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.ContinueTree;
import com.sun.source.tree.IdentifierTree;
import com.sun.source.tree.LabeledStatementTree;
import com.sun.source.tree.LiteralTree;
import com.sun.source.tree.MemberReferenceTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.ModifiersTree;
import com.sun.source.tree.NewClassTree;
import com.sun.source.tree.PrimitiveTypeTree;
import com.sun.source.tree.Tree;
import com.sun.source.tree.TypeParameterTree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreePathScanner;
import com.sun.source.util.Trees;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Pattern;
import javax.lang.model.element.Element;
import javax.lang.model.element.ElementKind;
import javax.lang.model.element.Modifier;
import javax.lang.model.element.TypeElement;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

/** Closed private-symbol rename and normalized complete semantic proof; not a runtime adapter. */
final class SourcePrivateFieldRename {
  record Request(String file, String owner, String name, int position) {
    String key() { return owner + "#" + name; }
  }
  record Change(Request request, String replacement) {}
  record Edit(int start, int end, String value) {}
  record Model(StandardJavaFileManager manager, JavacTask task, Trees trees, List<CompilationUnitTree> units) implements AutoCloseable {
    public void close() throws IOException { manager.close(); }
  }

  static void require(boolean value) {
    if (!value) throw new IllegalArgumentException("exact private source-symbol contract refused");
  }

  static Model load(Path root, String cp) throws IOException {
    List<Path> paths;
    try (var walk = Files.walk(root)) { paths = walk.filter(p -> p.toString().endsWith(".java")).sorted().toList(); }
    require(!paths.isEmpty());
    require(paths.stream().allMatch(p -> Files.isRegularFile(p, LinkOption.NOFOLLOW_LINKS)));
    var compiler = ToolProvider.getSystemJavaCompiler();
    var diagnostics = new DiagnosticCollector<JavaFileObject>();
    var manager = compiler.getStandardFileManager(diagnostics, null, StandardCharsets.UTF_8);
    var task = (JavacTask) compiler.getTask(null, manager, diagnostics, List.of("--release", "25", "-proc:none", "-implicit:none", "-classpath", cp), null, manager.getJavaFileObjectsFromPaths(paths));
    var units = new ArrayList<CompilationUnitTree>();
    task.parse().forEach(units::add); task.analyze();
    if (diagnostics.getDiagnostics().stream().anyMatch(d -> d.getKind() == Diagnostic.Kind.ERROR)) {
      manager.close(); throw new IllegalArgumentException("unresolved source symbols");
    }
    return new Model(manager, task, Trees.instance(task), units);
  }

  static String owner(Element element) {
    return element.getEnclosingElement() instanceof TypeElement t ? t.getQualifiedName().toString() : "";
  }

  static String name(Element element, Map<String, String> normalized) {
    String actual = element.getSimpleName().toString();
    return element.getKind() == ElementKind.FIELD ? normalized.getOrDefault(owner(element) + "#" + actual, actual) : actual;
  }

  static String binding(Element element, Map<String, String> normalized) {
    if (element == null) return "<none>";
    var parent = element.getEnclosingElement();
    String scope;
    if (parent instanceof TypeElement t) scope = t.getQualifiedName().toString();
    else if (parent != null && parent.getKind() == ElementKind.FIELD) scope = owner(parent) + "#" + name(parent, normalized);
    else scope = parent == null ? "<root>" : parent.getKind() + ":" + parent.toString();
    return element.getKind() + ":" + scope + ":" + name(element, normalized) + ":" + element.asType();
  }

  static String digest(Model model, CompilationUnitTree unit, Map<String, String> normalized) throws Exception {
    var result = new StringBuilder();
    new TreePathScanner<Void, Void>() {
      void add(Object value) { result.append(value).append('\u0000'); }
      Element element() { return model.trees().getElement(getCurrentPath()); }
      @Override public Void scan(Tree tree, Void v) {
        if (tree == null) { add("null"); return null; }
        add(tree.getKind()); var r = super.scan(tree, v); add("end"); return r;
      }
      @Override public Void visitIdentifier(IdentifierTree tree, Void v) {
        Element e = element(); add(e != null && e.getKind() == ElementKind.FIELD ? name(e, normalized) : tree.getName()); add(binding(e, normalized));
        return super.visitIdentifier(tree, v);
      }
      @Override public Void visitMemberSelect(MemberSelectTree tree, Void v) {
        Element e = element(); add(e != null && e.getKind() == ElementKind.FIELD ? name(e, normalized) : tree.getIdentifier()); add(binding(e, normalized));
        return super.visitMemberSelect(tree, v);
      }
      @Override public Void visitVariable(VariableTree tree, Void v) {
        Element e = element(); add(e != null && e.getKind() == ElementKind.FIELD ? name(e, normalized) : tree.getName()); add(binding(e, normalized));
        return super.visitVariable(tree, v);
      }
      @Override public Void visitMethod(MethodTree tree, Void v) { add(tree.getName()); add(binding(element(), normalized)); return super.visitMethod(tree, v); }
      @Override public Void visitClass(ClassTree tree, Void v) {
        add(tree.getSimpleName()); Element e = element(); add(binding(e, normalized));
        if (e instanceof TypeElement t) {
          var members = t.getEnclosedElements().stream().map(x -> binding(x, normalized) + ":" + x.getModifiers()).sorted().toList(); add(members);
        }
        return super.visitClass(tree, v);
      }
      @Override public Void visitLiteral(LiteralTree tree, Void v) { add(tree.getValue() == null ? "null-literal" : tree.getValue().getClass().getName()); add(tree.getValue()); return super.visitLiteral(tree, v); }
      @Override public Void visitModifiers(ModifiersTree tree, Void v) { add(tree.getFlags().stream().sorted().toList()); return super.visitModifiers(tree, v); }
      @Override public Void visitPrimitiveType(PrimitiveTypeTree tree, Void v) { add(tree.getPrimitiveTypeKind()); return super.visitPrimitiveType(tree, v); }
      @Override public Void visitTypeParameter(TypeParameterTree tree, Void v) { add(tree.getName()); return super.visitTypeParameter(tree, v); }
      @Override public Void visitLabeledStatement(LabeledStatementTree tree, Void v) { add(tree.getLabel()); return super.visitLabeledStatement(tree, v); }
      @Override public Void visitBreak(BreakTree tree, Void v) { add(tree.getLabel()); return super.visitBreak(tree, v); }
      @Override public Void visitContinue(ContinueTree tree, Void v) { add(tree.getLabel()); return super.visitContinue(tree, v); }
      @Override public Void visitMemberReference(MemberReferenceTree tree, Void v) { add(tree.getName()); add(tree.getMode()); add(binding(element(), normalized)); return super.visitMemberReference(tree, v); }
      @Override public Void visitNewClass(NewClassTree tree, Void v) { add(binding(element(), normalized)); return super.visitNewClass(tree, v); }
    }.scan(unit, null);
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(result.toString().getBytes(StandardCharsets.UTF_8)));
  }

  static int declarationPosition(Model m, CompilationUnitTree u, VariableTree tree, String raw) {
    long end = tree.getInitializer() == null ? m.trees().getSourcePositions().getEndPosition(u, tree) : m.trees().getSourcePositions().getStartPosition(u, tree.getInitializer());
    long start = m.trees().getSourcePositions().getEndPosition(u, tree.getType());
    require(start >= 0 && end >= start);
    var matcher = Pattern.compile("\\s*(" + Pattern.quote(tree.getName().toString()) + ")\\s*[=;]\\s*").matcher(raw.substring(Math.toIntExact(start), Math.toIntExact(end)));
    require(matcher.matches()); return Math.toIntExact(start) + matcher.start(1);
  }

  static boolean permittedAnnotations(Model model, Element e) {
    return model.task().getElements().getAllAnnotationMirrors(e).stream().allMatch(a -> a.getAnnotationType().toString().startsWith("org.jspecify.") || a.getAnnotationType().toString().startsWith("java.lang."));
  }

  public static void main(String[] args) throws Exception {
    require(args.length == 5 && Runtime.version().feature() == 25);
    boolean propose = args[0].equals("propose"); require(propose || args[0].equals("verify"));
    Path input = Path.of(args[1]).toRealPath();
    Path output = IsolatedSourceOutput.candidate(input, Path.of(args[4]), propose);
    var requests = new LinkedHashMap<String, Request>();
    for (String line : Files.readAllLines(Path.of(args[3]))) {
      var p = line.split("\t", -1); require(p.length == 4 && p[2].matches("[A-Za-z][A-Za-z0-9_]*"));
      var request = new Request(p[0], p[1], p[2], Integer.parseInt(p[3]));
      require(Path.of(p[0]).normalize().toString().equals(p[0]) && !Path.of(p[0]).isAbsolute() && !p[0].startsWith(".."));
      require(requests.put(request.key(), request) == null);
    }
    require(!requests.isEmpty());
    var changes = new LinkedHashMap<String, Change>();
    if (!propose) {
      require(Files.isRegularFile(output.resolve(".private-field-map.tsv"), LinkOption.NOFOLLOW_LINKS));
      for (String line : Files.readAllLines(output.resolve(".private-field-map.tsv"))) {
        var p = line.split("\t", -1); require(p.length == 5);
        var request = requests.get(p[1] + "#" + p[2]); require(request != null && request.file().equals(p[0]) && request.position() == Integer.parseInt(p[4]));
        require(changes.put(request.key(), new Change(request, p[3])) == null);
      }
      require(changes.keySet().equals(requests.keySet()));
    }
    var beforeHashes = new LinkedHashMap<String, String>();
    var originals = new LinkedHashMap<String, String>();
    try (var before = load(input, args[2])) {
      var types = before.task().getTypes(); var serializable = before.task().getElements().getTypeElement("java.io.Serializable").asType();
      for (var unit : before.units()) {
        String relative = input.relativize(Path.of(unit.getSourceFile().toUri())).toString();
        String raw = Files.readString(input.resolve(relative)); originals.put(relative, raw);
        var edits = new TreeMap<Integer, Edit>();
        var selected = new IdentityHashMap<Element, Change>();
        var reserved = new HashSet<String>();
        new TreePathScanner<Void, Void>() {
          @Override public Void visitVariable(VariableTree tree, Void v) {
            Element e = before.trees().getElement(getCurrentPath());
            if (e != null && e.getKind() == ElementKind.FIELD) {
              var request = requests.get(owner(e) + "#" + e.getSimpleName());
              if (request != null && request.file().equals(relative)) {
                require(e.getModifiers().contains(Modifier.PRIVATE));
                require(e.getEnclosingElement() instanceof TypeElement);
                var t = (TypeElement) e.getEnclosingElement();
                require(t.getKind() != ElementKind.RECORD && !types.isSubtype(types.erasure(t.asType()), types.erasure(serializable)) && !t.getQualifiedName().isEmpty());
                require(permittedAnnotations(before, e) && permittedAnnotations(before, t));
                var inheritedNames = before.task().getElements().getAllMembers(t).stream().map(x -> x.getSimpleName().toString()).collect(java.util.stream.Collectors.toSet());
                int position = declarationPosition(before, unit, tree, raw); require(position == request.position());
                String replacement;
                if (propose) {
                  boolean constant = e.getModifiers().containsAll(Set.of(Modifier.STATIC, Modifier.FINAL)) && request.name().matches("[A-Z][A-Z0-9_]*");
                  replacement = constant ? "RETAINED_" + request.name() : "retained" + Character.toUpperCase(request.name().charAt(0)) + request.name().substring(1);
                  int attempts = 0;
                  while (raw.contains(replacement) || reserved.contains(replacement) || inheritedNames.contains(replacement)) { require(attempts++ < 32); replacement += constant ? "_STATE" : "State"; }
                  var change = new Change(request, replacement); require(changes.put(request.key(), change) == null);
                } else {
                  replacement = changes.get(request.key()).replacement();
                  require(!raw.contains(replacement) && !reserved.contains(replacement) && !inheritedNames.contains(replacement));
                }
                reserved.add(replacement); var change = changes.get(request.key()); selected.put(e, change);
                require(edits.put(position, new Edit(position, position + request.name().length(), replacement)) == null);
              }
            }
            return super.visitVariable(tree, v);
          }
        }.scan(unit, null);
        new TreePathScanner<Void, Void>() {
          void reference(int start, int end, Element e) {
            var change = selected.get(e); if (change == null) return;
            require(start >= 0 && end > start && raw.substring(start, end).equals(change.request().name()));
            var edit = new Edit(start, end, change.replacement()); var prior = edits.putIfAbsent(start, edit); require(prior == null || prior.equals(edit));
          }
          @Override public Void visitIdentifier(IdentifierTree tree, Void v) { reference(Math.toIntExact(before.trees().getSourcePositions().getStartPosition(unit, tree)), Math.toIntExact(before.trees().getSourcePositions().getEndPosition(unit, tree)), before.trees().getElement(getCurrentPath())); return super.visitIdentifier(tree, v); }
          @Override public Void visitMemberSelect(MemberSelectTree tree, Void v) {
            var e = before.trees().getElement(getCurrentPath()); var change = selected.get(e);
            if (change != null) { int end = Math.toIntExact(before.trees().getSourcePositions().getEndPosition(unit, tree)); reference(end - change.request().name().length(), end, e); }
            return super.visitMemberSelect(tree, v);
          }
        }.scan(unit, null);
        beforeHashes.put(relative, digest(before, unit, Map.of()));
        if (propose) {
          String candidate = raw; int limit = raw.length();
          for (var edit : edits.descendingMap().values()) { require(edit.end() <= limit); candidate = candidate.substring(0, edit.start()) + edit.value() + candidate.substring(edit.end()); limit = edit.start(); }
          // Keep all candidate writes until every request has passed actual symbol validation.
          CANDIDATES.put(relative, candidate);
        }
      }
    }
    require(changes.keySet().equals(requests.keySet()));
    var normalized = new HashMap<String, String>();
    for (var change : changes.values()) require(normalized.put(change.request().owner() + "#" + change.replacement(), change.request().name()) == null);
    if (propose) {
      Files.createDirectories(output.getParent()); Files.createDirectory(output);
      for (var entry : CANDIDATES.entrySet()) { Path p = output.resolve(entry.getKey()); Files.createDirectories(p.getParent()); Files.writeString(p, entry.getValue()); }
    }
    var actualHashes = new LinkedHashMap<String, String>();
    var actualNewFields = new HashSet<String>();
    try (var after = load(output, args[2])) {
      for (var unit : after.units()) {
        String relative = output.relativize(Path.of(unit.getSourceFile().toUri())).toString();
        new TreePathScanner<Void, Void>() {
          @Override public Void visitVariable(VariableTree tree, Void unused) {
            Element e = after.trees().getElement(getCurrentPath());
            if (e != null && e.getKind() == ElementKind.FIELD) {
              String key = owner(e) + "#" + e.getSimpleName();
              require(!requests.containsKey(key));
              if (normalized.containsKey(key)) require(actualNewFields.add(key));
            }
            return super.visitVariable(tree, unused);
          }
        }.scan(unit, null);
        require(beforeHashes.containsKey(relative)); actualHashes.put(relative, digest(after, unit, normalized));
      }
    }
    require(actualNewFields.equals(normalized.keySet()) && beforeHashes.equals(actualHashes));
    for (var original : originals.entrySet()) require(Files.readString(input.resolve(original.getKey())).equals(original.getValue()));
    if (propose) {
      var mapping = new StringBuilder();
      for (var c : changes.values()) mapping.append(c.request().file()).append('\t').append(c.request().owner()).append('\t').append(c.request().name()).append('\t').append(c.replacement()).append('\t').append(c.request().position()).append('\n');
      Files.writeString(output.resolve(".private-field-map.tsv"), mapping);
    }
    for (var entry : beforeHashes.entrySet()) System.out.println("PROOF\t" + entry.getKey() + "\t" + entry.getValue() + "\t" + actualHashes.get(entry.getKey()));
    System.out.println("FIELDS\t" + changes.size());
  }

  private static final Map<String, String> CANDIDATES = new LinkedHashMap<>();
}
