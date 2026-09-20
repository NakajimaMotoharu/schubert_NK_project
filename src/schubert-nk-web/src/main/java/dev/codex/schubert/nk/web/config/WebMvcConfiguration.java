package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.ErrorController;
import dev.codex.schubert.nk.web.controller.MenuController;
import dev.codex.schubert.nk.web.error.ProblemViewFactory;
import java.util.Objects;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.web.servlet.support.csrf.CsrfRequestDataValueProcessor;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.support.RequestDataValueProcessor;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.spring6.templateresolver.SpringResourceTemplateResolver;
import org.thymeleaf.spring6.view.ThymeleafViewResolver;
import org.thymeleaf.templatemode.TemplateMode;

/**
 * Explicit MVC/template composition, not the production bootstrap or all endpoint registration.
 * NK-WEB-001; FUN-002/SYS-006/TST-001..005; UI222/223; SS311/313/352;
 * PG-D-115/116/PT-WEB-142..157/SSC-047.
 */
@Configuration(proxyBeanMethods = false)
@EnableWebMvc
public class WebMvcConfiguration implements WebMvcConfigurer {
  @Bean
  public ProblemViewFactory problemViewFactory() {
    return new ProblemViewFactory();
  }

  @Bean
  public ErrorController errorController(ProblemViewFactory factory) {
    return new ErrorController(factory);
  }

  @Bean
  public MenuController menuController() {
    return new MenuController();
  }

  @Bean
  public SpringResourceTemplateResolver templateResolver(ApplicationContext context) {
    Objects.requireNonNull(context, "context");
    var resolver = new SpringResourceTemplateResolver();
    resolver.setApplicationContext(context);
    resolver.setPrefix("classpath:/templates/");
    resolver.setSuffix(".html");
    resolver.setTemplateMode(TemplateMode.HTML);
    resolver.setCharacterEncoding("UTF-8");
    resolver.setCacheable(true);
    resolver.setCheckExistence(true);
    return resolver;
  }

  @Bean
  public SpringTemplateEngine templateEngine(SpringResourceTemplateResolver resolver) {
    Objects.requireNonNull(resolver, "resolver");
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(resolver);
    engine.setEnableSpringELCompiler(false);
    return engine;
  }

  @Bean
  public ThymeleafViewResolver thymeleafViewResolver(SpringTemplateEngine engine) {
    Objects.requireNonNull(engine, "engine");
    var resolver = new ThymeleafViewResolver();
    resolver.setTemplateEngine(engine);
    resolver.setCharacterEncoding("UTF-8");
    resolver.setContentType("text/html;charset=UTF-8");
    resolver.setForceContentType(true);
    resolver.setViewNames(
        new String[] {
          "menu",
          "animation",
          "animation-list",
          "music",
          "music-sections",
          "error/error",
          "scenarios",
          "scenario-routes",
          "scenario-files",
          "scenario",
          "search"
        });
    resolver.setAlwaysProcessRedirectAndForward(false);
    resolver.setProducePartialOutputWhileProcessing(false);
    return resolver;
  }

  @Bean
  public RequestDataValueProcessor requestDataValueProcessor() {
    return new CsrfRequestDataValueProcessor();
  }

  @Override
  public void addResourceHandlers(ResourceHandlerRegistry registry) {
    Objects.requireNonNull(registry, "registry");
    // Resource lookup is not a public authorization grant; the security chain has an exact
    // allowlist.
    registry.addResourceHandler("/css/**").addResourceLocations("classpath:/static/css/");
    registry.addResourceHandler("/js/**").addResourceLocations("classpath:/static/js/");
  }
}
