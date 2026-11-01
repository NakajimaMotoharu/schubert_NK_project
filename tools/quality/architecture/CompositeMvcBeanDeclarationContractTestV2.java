package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.util.Arrays;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** SS311/313; MVC-COMPOSITE001. Public annotations only, no Context/bean/handler invocation. */
final class CompositeMvcBeanDeclarationContractTestV2 {
  @Test
  void compositeMvc001OnlyBusinessBeanDeclarationsAreCountedWithoutProxyFactories() {
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
    // BUG2232: official JaCoCo adds a synthetic non-business $jacocoInit method.
    assertEquals(0L, Arrays.stream(type.getDeclaredMethods())
        .filter(method -> method.isAnnotationPresent(Bean.class)).count());
  }
}
