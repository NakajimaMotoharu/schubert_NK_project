package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** SS311/313; MVC-COMPOSITE001. Public annotations only, no Context/bean/handler invocation. */
final class CompositeMvcDeclarationContractTest {
  @Test
  void compositeMvc001OnlyScenarioAndLogCompositionIsDeclaredWithoutProxyBeanMethods() {
    assertNotNull(new ScenarioLogMvcConfiguration());
    var type = ScenarioLogMvcConfiguration.class;
    var configuration = type.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = type.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertEquals(2, imports.value().length);
    assertEquals(Set.of(ScenarioMvcConfiguration.class, LogMvcConfiguration.class),
        Set.of(imports.value()));
    assertEquals(0, type.getDeclaredMethods().length);
  }
}
