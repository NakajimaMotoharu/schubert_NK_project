package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.nio.file.Path;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

final class GateOutputRootValueTest {
  @Test
  @DisplayName("PT-CHR-OUTPUT-ROOT-001 destination without parent never reaches the output port")
  void destinationWithoutParentDoesNotInvokeOutputPort() {
    var noParent = Path.of("").toAbsolutePath().getRoot();
    assertNotNull(noParent);

    var io =
        new GateCli.JsonOutput() {
          @Override
          public void createParent(Path parent) {
            fail("parent acquisition must not be attempted");
          }

          @Override
          public void writeTemporary(Path temporary, Object value) {
            fail("temporary output must not be attempted");
          }

          @Override
          public void publish(Path temporary, Path output) {
            fail("publish must not be attempted");
          }

          @Override
          public void deleteTemporary(Path temporary) {
            fail("cleanup must not be attempted for unclaimed output");
          }
        };

    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> GateCli.writeJson(noParent, "fixture", io));
    assertEquals("output must name a file below a directory", failure.getMessage());
  }
}
