import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.ArrayDeque;

/** Resolve an uncreated output through existing ancestors before any directory/source write. */
final class IsolatedSourceOutput {
  private IsolatedSourceOutput() {}

  static Path candidate(Path original, Path proposed, boolean newOnly) throws IOException {
    Path input = original.toRealPath();
    Path lexical = proposed.toAbsolutePath().normalize();
    if (Files.isSymbolicLink(lexical)) throw new IllegalArgumentException("output symlink refused");
    var suffix = new ArrayDeque<Path>();
    Path ancestor = lexical;
    while (!Files.exists(ancestor, LinkOption.NOFOLLOW_LINKS)) {
      suffix.addFirst(ancestor.getFileName());
      ancestor = ancestor.getParent();
      if (ancestor == null) throw new IllegalArgumentException("output ancestor unavailable");
    }
    Path resolved = ancestor.toRealPath();
    for (Path name : suffix) resolved = resolved.resolve(name);
    resolved = resolved.normalize();
    if (resolved.startsWith(input) || input.startsWith(resolved))
      throw new IllegalArgumentException("canonical input/output overlap refused");
    if (newOnly && Files.exists(resolved, LinkOption.NOFOLLOW_LINKS))
      throw new IllegalArgumentException("new-only candidate output exists");
    if (!newOnly && !Files.isDirectory(resolved, LinkOption.NOFOLLOW_LINKS))
      throw new IllegalArgumentException("existing regular candidate directory required");
    return resolved;
  }
}
