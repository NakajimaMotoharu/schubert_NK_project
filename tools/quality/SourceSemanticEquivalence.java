import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

/** Independent compiler universes; no alpha renaming, ignored declarations, or source writes. */
final class SourceSemanticEquivalence {
  public static void main(String[] args) throws Exception {
    SourcePrivateFieldRename.require(args.length == 3);
    Path before = Path.of(args[0]).toRealPath(), after = Path.of(args[1]).toRealPath();
    SourcePrivateFieldRename.require(!before.equals(after));
    var expected = new LinkedHashMap<String, String>(); var actual = new LinkedHashMap<String, String>();
    try (var model = SourcePrivateFieldRename.load(before, args[2])) {
      for (var unit : model.units()) expected.put(before.relativize(Path.of(unit.getSourceFile().toUri())).toString(), SourcePrivateFieldRename.digest(model, unit, Map.of()));
    }
    try (var model = SourcePrivateFieldRename.load(after, args[2])) {
      for (var unit : model.units()) actual.put(after.relativize(Path.of(unit.getSourceFile().toUri())).toString(), SourcePrivateFieldRename.digest(model, unit, Map.of()));
    }
    SourcePrivateFieldRename.require(!expected.isEmpty() && expected.equals(actual));
    for (var item : expected.entrySet()) System.out.println("PROOF\t" + item.getKey() + "\t" + item.getValue() + "\t" + actual.get(item.getKey()));
  }
}
