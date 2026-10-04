package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.LogoutController;
import dev.codex.schubert.nk.web.security.LocalLogoutHandler;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit Logout HTTP registration; UI226/SS313314/PG-D363/RERUN007. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
public class LogoutMvcConfiguration {
  @Bean
  public LogoutController logoutController(LocalLogoutHandler handler) {
    return new LogoutController(handler);
  }
}
