package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.UserAdminController;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Full User composition, never also import legacy UserMvcConfiguration. SSC177/PG-D366/081. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class UserBusinessMvcConfiguration {
  @Bean
  public UserAdminController userAdminController(
      UserAdministrationWireClient client,
      ApiSessionInvalidHandler invalid,
      SessionOperationTokenLifecycle tokens) {
    return new UserAdminController(client, invalid, tokens);
  }
}
