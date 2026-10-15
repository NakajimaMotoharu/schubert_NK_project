package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.AnimationController;
import dev.codex.schubert.nk.web.messaging.AnimationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit SCR008/009 composition, not full bootstrap. FUN006/UI223/SS311,313/PG207/PT-SCR060. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class AnimationMvcConfiguration {
  @Bean
  public AnimationController animationController(
      AnimationWireClient client, ApiSessionInvalidHandler invalid) {
    return new AnimationController(client, invalid);
  }
}
