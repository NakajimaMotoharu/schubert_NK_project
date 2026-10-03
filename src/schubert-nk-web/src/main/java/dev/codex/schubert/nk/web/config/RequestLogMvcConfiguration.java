package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.logging.WebRequestRouteInterceptor;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/** Explicit request logging assembly; SS312351/SSC172/PG-D354/REQ004016. */
@Configuration(proxyBeanMethods = false)
@NullMarked
public class RequestLogMvcConfiguration implements WebMvcConfigurer {
  @Override
  public void addInterceptors(InterceptorRegistry registry) {
    Objects.requireNonNull(registry, "registry").addInterceptor(new WebRequestRouteInterceptor());
  }
}
