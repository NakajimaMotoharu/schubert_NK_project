import com.sun.source.tree.*;
import com.sun.source.util.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import javax.lang.model.element.*;

/** Isolated compiler-bound literal proposals. No original source, setting or oracle is written. */
final class SourceStringLiteralConstants {
  record Request(String file, int line, int column) {}
  record Occurrence(LiteralTree tree, ClassTree owner, TypeElement type, int start, int end, String value) {}
  record Edit(int start, int end, String replacement) {}
  record Constant(String owner, String name, String value) { String key() { return owner + "#" + name; } }
  static void require(boolean value) { if (!value) throw new IllegalArgumentException("typed literal contract refused"); }
  static String sha(String value) throws Exception {
    var digest = MessageDigest.getInstance("SHA-256");
    for (char c : value.toCharArray()) { digest.update((byte) (c >>> 8)); digest.update((byte) c); }
    return HexFormat.of().formatHex(digest.digest()); // Exact UTF-16 code units, including unpaired surrogates.
  }

  /** Header scanner only: no semantic rewrite and no brace guessing inside comments/annotations. */
  static int body(String raw, int start) {
    int parentheses = 0, brackets = 0;
    for (int i = start; i < raw.length(); i++) {
      char c = raw.charAt(i);
      if (c == '/' && i + 1 < raw.length() && raw.charAt(i + 1) == '/') {
        i = raw.indexOf('\n', i + 2); require(i >= 0); continue;
      }
      if (c == '/' && i + 1 < raw.length() && raw.charAt(i + 1) == '*') {
        i = raw.indexOf("*/", i + 2); require(i >= 0); i++; continue;
      }
      if (c == '\\' && i + 1 < raw.length() && raw.charAt(i + 1) == 'u') throw new IllegalArgumentException("unicode-translated header held");
      if (c == '"' || c == '\'') {
        require(!raw.startsWith("\"\"\"", i)); char quote = c; boolean closed = false;
        for (i++; i < raw.length(); i++) {
          if (raw.charAt(i) == '\\') { i++; continue; }
          if (raw.charAt(i) == quote) { closed = true; break; }
        }
        require(closed); continue;
      }
      if (c == '(') parentheses++;
      if (c == ')') parentheses--;
      if (c == '[') brackets++;
      if (c == ']') brackets--;
      require(parentheses >= 0 && brackets >= 0);
      if (c == '{' && parentheses == 0 && brackets == 0) return i + 1;
    }
    throw new IllegalArgumentException("no exact source body");
  }

  static List<Constant> propose(Path input, Path output, String cp, List<Request> requests) throws Exception {
    require(!Files.exists(output) && !output.startsWith(input) && !input.startsWith(output));
    Map<String, String> candidates = new TreeMap<>(); List<Constant> constants = new ArrayList<>(); Set<Request> handled = new HashSet<>();
    try (var model = SourcePrivateFieldRename.load(input, cp)) {
      for (var unit : model.units()) {
        Path file = Path.of(unit.getSourceFile().toUri()); String relative = input.relativize(file).toString(); String raw = Files.readString(file);
        List<Request> selected = requests.stream().filter(r -> r.file().equals(relative)).toList();
        List<Occurrence> occurrences = new ArrayList<>();
        new TreePathScanner<Void, Void>() {
          @Override public Void visitLiteral(LiteralTree node, Void unused) {
            if (!(node.getValue() instanceof String value)) return super.visitLiteral(node, unused);
            int first = (int) model.trees().getSourcePositions().getStartPosition(unit, node);
            int last = (int) model.trees().getSourcePositions().getEndPosition(unit, node);
            if (first < 0 || last <= first) return super.visitLiteral(node, unused);
            TreePath outer = null;
            for (TreePath p = getCurrentPath(); p != null; p = p.getParentPath()) if (p.getLeaf() instanceof ClassTree) outer = p;
            if (outer != null && model.trees().getElement(outer) instanceof TypeElement type)
              occurrences.add(new Occurrence(node, (ClassTree) outer.getLeaf(), type, first, last, value));
            return super.visitLiteral(node, unused);
          }
        }.scan(unit, null);
        Map<String, List<Occurrence>> groups = new LinkedHashMap<>();
        for (Request request : selected) {
          List<Occurrence> matches = occurrences.stream().filter(o -> unit.getLineMap().getLineNumber(o.start()) == request.line() && unit.getLineMap().getColumnNumber(o.start()) == request.column()).toList();
          require(matches.size() == 1 && handled.add(request)); Occurrence target = matches.getFirst();
          String key = target.type().getQualifiedName() + "\u0000" + target.value();
          require(!groups.containsKey(key));
          groups.put(key, occurrences.stream().filter(o -> o.type().equals(target.type()) && o.value().equals(target.value())).toList());
        }
        List<Edit> edits = new ArrayList<>(); Map<Integer, StringBuilder> additions = new TreeMap<>(); Set<String> reserved = new HashSet<>();
        for (List<Occurrence> group : groups.values()) {
          Occurrence first = group.getFirst();
          if (!Set.of(ElementKind.CLASS, ElementKind.RECORD).contains(first.type().getKind())) {
            System.out.println("HELD\t" + relative + "\tOWNER_KIND\t" + first.type().getKind()); continue;
          }
          int insertion = body(raw, (int) model.trees().getSourcePositions().getStartPosition(unit, first.owner()));
          if (group.stream().anyMatch(o -> o.start() < insertion || raw.startsWith("\"\"\"", o.start()))) {
            System.out.println("HELD\t" + relative + "\tHEADER_OR_TEXTBLOCK"); continue;
          }
          require(group.size() >= 4);
          String hint = first.value().replaceAll("[^A-Za-z0-9]+", "_").replaceAll("^_+|_+$", "");
          if (hint.length() > 36) hint = hint.substring(0, 36);
          String name = "LITERAL_" + (hint.isEmpty() ? "VALUE" : hint.toUpperCase(Locale.ROOT));
          Set<String> inherited = new HashSet<>(); model.task().getElements().getAllMembers(first.type()).forEach(e -> inherited.add(e.getSimpleName().toString()));
          int collisions = 0;
          while (raw.contains(name) || inherited.contains(name) || !reserved.add(name)) { require(collisions++ < 32); name += "_VALUE"; }
          Constant constant = new Constant(first.type().getQualifiedName().toString(), name, first.value()); constants.add(constant);
          String literal = raw.substring(first.start(), first.end());
          additions.computeIfAbsent(insertion, ignored -> new StringBuilder()).append("\n  private static final java.lang.String ").append(name).append(" = ").append(literal).append(";\n");
          for (Occurrence occurrence : group) edits.add(new Edit(occurrence.start(), occurrence.end(), name));
          System.out.println("CONSTANT\t" + relative + "\t" + constant.owner() + "\t" + name + "\t" + sha(first.value()) + "\t" + group.size());
        }
        additions.forEach((position, value) -> edits.add(new Edit(position, position, value.toString())));
        edits.sort(Comparator.comparingInt(Edit::start).reversed()); String candidate = raw; int limit = raw.length();
        for (Edit edit : edits) { require(edit.end() <= limit); candidate = candidate.substring(0, edit.start()) + edit.replacement() + candidate.substring(edit.end()); limit = edit.start(); }
        require(Files.readString(file).equals(raw)); candidates.put(relative, candidate);
      }
    }
    require(handled.size() == requests.size()); Files.createDirectory(output);
    for (var item : candidates.entrySet()) { Path target = output.resolve(item.getKey()); Files.createDirectories(target.getParent()); Files.writeString(target, item.getValue()); }
    return constants;
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 4 || Runtime.version().feature() != 25) throw new IllegalArgumentException("JDK25 source/classpath/request/output required");
    Path input = Path.of(args[0]).toRealPath(); Path output = IsolatedSourceOutput.candidate(input, Path.of(args[3]), true);
    List<Request> requests = new ArrayList<>();
    for (String line : Files.readAllLines(Path.of(args[2]))) {
      String[] fields = line.split("\t", -1); require(fields.length == 3 && !Path.of(fields[0]).isAbsolute() && !fields[0].contains(".."));
      requests.add(new Request(fields[0], Integer.parseInt(fields[1]), Integer.parseInt(fields[2])));
    }
    List<Constant> constants = propose(input, output, args[1], requests);
    // Verification is a separate mandatory step; this planner never grants an apply authority.
    System.out.println("PROPOSED_ONLY\t" + constants.size());
  }
}
