package dev.codex.schubert.nk.api.maintenance;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

/** BUG1107/YKT876: project syntax only; never load/start host vendor Units. */
final class UnitSyntaxFixture {
  private UnitSyntaxFixture() {}

  static Map<String, String> environment(Path directory) throws IOException {
    // These systemd implicit dependency targets have no production behavior in
    // the syntax fixture. Keep the project's own dependency/ordering directives.
    for (String target : List.of("sysinit", "basic", "shutdown")) {
      Files.writeString(
          directory.resolve(target + ".target"),
          "[Unit]\nDescription=Independent PT dependency stub\nDefaultDependencies=no\n");
    }
    // No trailing colon: it expands to the host's unrelated default Unit paths.
    // The verifier's complete stdout/stderr still forms the test oracle.
    return Map.of("SYSTEMD_UNIT_PATH", directory.toString(), "LC_ALL", "C");
  }
}
