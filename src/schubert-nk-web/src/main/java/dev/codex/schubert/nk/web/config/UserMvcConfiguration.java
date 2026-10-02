package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.UserAdminController;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit SCR015 composition, not ordinary ready. UI225/SS313; PG-D344/PT-USER-HTTP007. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class UserMvcConfiguration {
  @Bean
  public UserAdminController userAdminController(
      UserAdministrationWireClient client, ApiSessionInvalidHandler invalid) {
    return new UserAdminController(client, invalid);
  }
}
