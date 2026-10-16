import com.sun.source.tree.*;
import com.sun.source.util.*;
import java.nio.file.*;
import java.util.*;
import javax.lang.model.element.*;

/** Full normalized compiler tree/bindings/ABI proof; only approved compile-time private constants normalize. */
final class SourceStringLiteralProof {
  record Expected(String hash, int uses) {}
  static void require(boolean value) { SourceStringLiteralConstants.require(value); }
  static String key(Element e) { return SourcePrivateFieldRename.owner(e) + "#" + e.getSimpleName(); }

  static Map<String, String> constants(SourcePrivateFieldRename.Model model, Map<String, Expected> expected, boolean after) {
    Map<String, String> result = new HashMap<>();
    for (var unit : model.units()) new TreePathScanner<Void, Void>() {
      @Override public Void visitVariable(VariableTree tree, Void unused) {
        Element e = model.trees().getElement(getCurrentPath());
        if (e != null && e.getKind() == ElementKind.FIELD && expected.containsKey(key(e))) {
          require(after && e.getModifiers().equals(Set.of(Modifier.PRIVATE, Modifier.STATIC, Modifier.FINAL))
              && tree.getModifiers().getAnnotations().isEmpty() && e instanceof VariableElement);
          Object constant = ((VariableElement) e).getConstantValue();
          require(constant instanceof String);
          try { require(SourceStringLiteralConstants.sha((String) constant).equals(expected.get(key(e)).hash())); }
          catch (Exception failure) { throw new IllegalArgumentException("constant identity refused", failure); }
          require(result.put(key(e), (String) constant) == null);
        }
        return super.visitVariable(tree, unused);
      }
    }.scan(unit, null);
    require(after ? result.keySet().equals(expected.keySet()) : result.isEmpty()); return result;
  }

  static String digest(SourcePrivateFieldRename.Model model, CompilationUnitTree unit, Map<String, String> constants, Map<String, Integer> uses) throws Exception {
    var result = new StringBuilder(); var types = new SourcePrivateFieldRename.TypeFingerprint();
    new TreePathScanner<Void, Void>() {
      void add(Object value) { String text = String.valueOf(value); result.append(text.length()).append(':').append(text).append(';'); }
      Element element() { return model.trees().getElement(getCurrentPath()); }
      String binding(Element e) { return SourcePrivateFieldRename.binding(e, Map.of(), types); }
      @Override public Void scan(Tree tree, Void unused) {
        if (tree == null) { add("null"); return null; }
        TreePath path = getCurrentPath() == null ? new TreePath(unit) : new TreePath(getCurrentPath(), tree);
        Element e = model.trees().getElement(path);
        if (tree instanceof VariableTree && e != null && constants.containsKey(key(e))) return null;
        if ((tree instanceof IdentifierTree || tree instanceof MemberSelectTree) && e != null && constants.containsKey(key(e))) {
          uses.merge(key(e), 1, Integer::sum);
          add(Tree.Kind.STRING_LITERAL); add(String.class.getName()); add(constants.get(key(e))); add("end"); return null;
        }
        add(tree.getKind()); var found = super.scan(tree, unused); add("end"); return found;
      }
      @Override public Void visitIdentifier(IdentifierTree tree, Void u) { add(tree.getName()); add(binding(element())); return super.visitIdentifier(tree, u); }
      @Override public Void visitMemberSelect(MemberSelectTree tree, Void u) { add(tree.getIdentifier()); add(binding(element())); return super.visitMemberSelect(tree, u); }
      @Override public Void visitVariable(VariableTree tree, Void u) { add(tree.getName()); add(binding(element())); return super.visitVariable(tree, u); }
      @Override public Void visitMethod(MethodTree tree, Void u) { add(tree.getName()); add(binding(element())); return super.visitMethod(tree, u); }
      @Override public Void visitClass(ClassTree tree, Void u) {
        add(tree.getSimpleName()); Element e = element(); add(binding(e));
        if (e instanceof TypeElement type) add(type.getEnclosedElements().stream().filter(m -> !constants.containsKey(key(m))).map(m -> binding(m) + ":" + m.getModifiers()).sorted().toList());
        return super.visitClass(tree, u);
      }
      @Override public Void visitLiteral(LiteralTree tree, Void u) { add(tree.getValue() == null ? "null-literal" : tree.getValue().getClass().getName()); add(tree.getValue()); return super.visitLiteral(tree, u); }
      @Override public Void visitModifiers(ModifiersTree tree, Void u) { add(tree.getFlags().stream().sorted().toList()); return super.visitModifiers(tree, u); }
      @Override public Void visitPrimitiveType(PrimitiveTypeTree tree, Void u) { add(tree.getPrimitiveTypeKind()); return super.visitPrimitiveType(tree, u); }
      @Override public Void visitTypeParameter(TypeParameterTree tree, Void u) { add(tree.getName()); return super.visitTypeParameter(tree, u); }
      @Override public Void visitLabeledStatement(LabeledStatementTree tree, Void u) { add(tree.getLabel()); return super.visitLabeledStatement(tree, u); }
      @Override public Void visitBreak(BreakTree tree, Void u) { add(tree.getLabel()); return super.visitBreak(tree, u); }
      @Override public Void visitContinue(ContinueTree tree, Void u) { add(tree.getLabel()); return super.visitContinue(tree, u); }
      @Override public Void visitMemberReference(MemberReferenceTree tree, Void u) { add(tree.getName()); add(tree.getMode()); add(binding(element())); return super.visitMemberReference(tree, u); }
      @Override public Void visitNewClass(NewClassTree tree, Void u) { add(binding(element())); return super.visitNewClass(tree, u); }
    }.scan(unit, null);
    return SourceStringLiteralConstants.sha(result.toString());
  }

  public static void main(String[] args) throws Exception {
    if (args.length != 4 || Runtime.version().feature() != 25) throw new IllegalArgumentException("JDK25 original/candidate/classpath/plan required");
    Path before = Path.of(args[0]).toRealPath(), after = IsolatedSourceOutput.candidate(before, Path.of(args[1]), false);
    Map<String, Expected> expected = new HashMap<>();
    for (String line : Files.readAllLines(Path.of(args[3]))) {
      if (!line.startsWith("CONSTANT\t")) continue;
      String[] row = line.split("\t", -1); require(row.length == 6 && row[4].matches("[a-f0-9]{64}") && Integer.parseInt(row[5]) >= 4);
      require(expected.put(row[2] + "#" + row[3], new Expected(row[4], Integer.parseInt(row[5]))) == null);
    }
    try (var original = SourcePrivateFieldRename.load(before, args[2]); var candidate = SourcePrivateFieldRename.load(after, args[2])) {
      constants(original, expected, false); Map<String, String> approved = constants(candidate, expected, true);
      Map<String, String> old = new TreeMap<>(), current = new TreeMap<>(); Map<String, Integer> uses = new HashMap<>();
      for (var unit : original.units()) old.put(before.relativize(Path.of(unit.getSourceFile().toUri())).toString(), digest(original, unit, Map.of(), new HashMap<>()));
      for (var unit : candidate.units()) current.put(after.relativize(Path.of(unit.getSourceFile().toUri())).toString(), digest(candidate, unit, approved, uses));
      require(old.equals(current));
      require(uses.keySet().equals(expected.keySet()) && uses.entrySet().stream().allMatch(e -> e.getValue().equals(expected.get(e.getKey()).uses())));
      System.out.println("FULL_SEMANTIC_ABI_VALUES_IDENTICAL\t" + old.size() + "\t" + expected.size());
    }
  }
}
