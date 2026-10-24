package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.web.config.RequestLogMvcConfiguration;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.logging.HttpRequestLoggingValve;
import dev.codex.schubert.nk.web.logging.WebRequestLogProducer;
import dev.codex.schubert.nk.web.monitoring.HttpMetricValve;
import jakarta.servlet.Filter;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.apache.catalina.LifecycleException;
import org.apache.catalina.LifecycleState;
import org.apache.catalina.core.StandardHost;
import org.apache.catalina.startup.Tomcat;
import org.apache.tomcat.util.descriptor.web.FilterDef;
import org.apache.tomcat.util.descriptor.web.FilterMap;
import org.jspecify.annotations.Nullable;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.DispatcherServlet;

/**
 * Loopback-only production Servlet/MVC composition. Credential, DataSource, JMS and security
 * dependencies are supplied by the later WebApplication bootstrap, never invented here. NK-WEB-002;
 * SYS-001/006/AUT-001; UI222/226/252; SS311/313/314/342/352/362; PG220/PT-SCR109..111.
 */
public final class WebHttpServer implements AutoCloseable {
  private final Tomcat tomcat;
  private final AnnotationConfigWebApplicationContext mvc;
  private final Object lifecycleLock = new Object();
  private boolean closed;
  private boolean stopped;
  private boolean destroyed;
  private boolean started;

  private WebHttpServer(Supplier<Tomcat> tomcatFactory) {
    this.mvc = new AnnotationConfigWebApplicationContext();
    // SSC312/PG-D461/PT-HTTP-OWN003: unrefreshed MVC/lock/owner before acquisition.
    this.tomcat = Objects.requireNonNull(tomcatFactory.get(), "tomcatFactory result");
  }

  /**
   * Starts the real MVC server on 127.0.0.1; the supplied filter owns HTTP admission for every
   * dispatcher type. Port zero is permitted for isolated PT only.
   */
  public static WebHttpServer start(
      Path runtimeDirectory, int port, Filter security, Class<?>... featureConfigurations)
      throws LifecycleException {
    return start(runtimeDirectory, port, security, Map.of(), featureConfigurations);
  }

  /** Registers caller-owned application ports before any feature controller is instantiated. */
  public static WebHttpServer start(
      Path runtimeDirectory,
      int port,
      Filter security,
      Map<Class<?>, ?> dependencies,
      Class<?>... featureConfigurations)
      throws LifecycleException {
    return startWithFactory(
        runtimeDirectory, port, security, dependencies, Tomcat::new, featureConfigurations);
  }

  /** Package-local lifecycle seam: PT can verify failed bind/start and failed cleanup. */
  static WebHttpServer startWithFactory(
      Path runtimeDirectory,
      int port,
      Filter security,
      Supplier<Tomcat> tomcatFactory,
      Class<?>... featureConfigurations)
      throws LifecycleException {
    return startWithFactory(
        runtimeDirectory, port, security, Map.of(), tomcatFactory, featureConfigurations);
  }

  /** Native owner captures even a partially started container before any vendor mutation. */
  static WebHttpServer startOwned(
      Path runtimeDirectory,
      int port,
      Filter security,
      Map<Class<?>, ?> dependencies,
      Consumer<WebHttpServer> owner,
      Class<?>... featureConfigurations)
      throws LifecycleException {
    Objects.requireNonNull(owner, "HTTP owner");
    return startWithOwner(
        runtimeDirectory, port, security, dependencies, Tomcat::new, owner, featureConfigurations);
  }

  static WebHttpServer startWithOwner(
      Path runtimeDirectory,
      int port,
      Filter security,
      Map<Class<?>, ?> dependencies,
      Supplier<Tomcat> tomcatFactory,
      @Nullable Consumer<WebHttpServer> owner,
      Class<?>... featureConfigurations)
      throws LifecycleException {
    Objects.requireNonNull(runtimeDirectory, "runtimeDirectory");
    Objects.requireNonNull(security, "security");
    Objects.requireNonNull(tomcatFactory, "tomcatFactory");
    Objects.requireNonNull(featureConfigurations, "featureConfigurations");
    validateConfiguration(runtimeDirectory, port, featureConfigurations);
    Map<Class<?>, ?> registeredDependencies = checkedDependencies(dependencies);
    if (registeredDependencies.containsKey(HttpMetricValve.class)
        && !registeredDependencies.containsKey(WebRequestLogProducer.class))
      throw new IllegalArgumentException("HTTP metric observer requires request trace");
    var result = new WebHttpServer(tomcatFactory);
    var tomcat = result.tomcat;
    var mvc = result.mvc;
    try {
      if (owner != null) owner.accept(result);
      tomcat.setBaseDir(runtimeDirectory.toString());
      tomcat.setPort(port);
      tomcat.setSilent(true);
      tomcat.setAddDefaultWebXmlToWebapp(false);
      ((StandardHost) tomcat.getHost()).setErrorReportValveClass(null);
      var context = tomcat.addContext("", runtimeDirectory.toString());
      context.setParentClassLoader(WebHttpServer.class.getClassLoader());
      if (!tomcat.getConnector().setProperty("address", "127.0.0.1")) {
        throw new IllegalStateException("Web loopback binding is unavailable");
      }
      var definition = new FilterDef();
      definition.setFilterName("nk-security");
      definition.setFilter(security);
      definition.setAsyncSupported("true");
      context.addFilterDef(definition);
      var mapping = new FilterMap();
      mapping.setFilterName("nk-security");
      mapping.addURLPattern("/*");
      for (var dispatch : List.of("REQUEST", "ERROR", "ASYNC", "FORWARD")) {
        mapping.setDispatcher(dispatch);
      }
      context.addFilterMap(mapping);
      mvc.addBeanFactoryPostProcessor(
          factory ->
              registeredDependencies.forEach(
                  (type, instance) -> factory.registerSingleton(type.getName(), instance)));
      mvc.register(WebMvcConfiguration.class);
      // SSC172: this observer never creates/owns DB, JMS, key or authentication dependencies.
      Object requestLog = registeredDependencies.get(WebRequestLogProducer.class);
      if (requestLog != null) {
        context
            .getPipeline()
            .addValve(new HttpRequestLoggingValve((WebRequestLogProducer) requestLog));
        mvc.register(RequestLogMvcConfiguration.class);
      }
      Object metricObserver = registeredDependencies.get(HttpMetricValve.class);
      if (metricObserver != null) {
        context.getPipeline().addValve((HttpMetricValve) metricObserver);
      }
      Object admission = registeredDependencies.get(WebHttpAdmission.class);
      if (admission != null) {
        context.getPipeline().addValve(new WebHttpAdmissionValve((WebHttpAdmission) admission));
      }
      if (featureConfigurations.length > 0) mvc.register(featureConfigurations);
      var servlet = Tomcat.addServlet(context, "nk-mvc", new DispatcherServlet(mvc));
      servlet.setLoadOnStartup(1);
      servlet.setAsyncSupported(true);
      context.addServletMapping("/", "nk-mvc");
      tomcat.start();
      if (context.getState() != LifecycleState.STARTED) {
        throw new LifecycleException("Web MVC startup failed");
      }
      synchronized (result.lifecycleLock) {
        result.started = true;
      }
      return result;
    } catch (LifecycleException | RuntimeException | Error failure) {
      // Native partial owner keeps the exact phase and all borrowed dependencies until confirmed.
      if (owner == null) {
        try {
          tomcat.destroy();
        } catch (LifecycleException | RuntimeException | Error cleanup) {
          if (failure != cleanup) failure.addSuppressed(cleanup);
        }
      }
      throw failure;
    }
  }

  static WebHttpServer startWithFactory(
      Path runtimeDirectory,
      int port,
      Filter security,
      Map<Class<?>, ?> dependencies,
      Supplier<Tomcat> tomcatFactory,
      Class<?>... featureConfigurations)
      throws LifecycleException {
    return startWithOwner(
        runtimeDirectory, port, security, dependencies, tomcatFactory, null, featureConfigurations);
  }

  static void validateConfiguration(Path runtimeDirectory, int port, Class<?>[] configurations) {
    Objects.requireNonNull(runtimeDirectory, "runtimeDirectory");
    Objects.requireNonNull(configurations, "featureConfigurations");
    if (!Files.isDirectory(runtimeDirectory, LinkOption.NOFOLLOW_LINKS)
        || port < 0
        || port > 65535
        || Arrays.stream(configurations).anyMatch(Objects::isNull)) {
      throw new IllegalArgumentException("invalid Web HTTP startup configuration");
    }
  }

  static Map<Class<?>, ?> checkedDependencies(Map<Class<?>, ?> dependencies) {
    Objects.requireNonNull(dependencies, "dependencies");
    for (var entry : dependencies.entrySet()) {
      Class<?> type = Objects.requireNonNull(entry.getKey(), "dependency type");
      Object value = Objects.requireNonNull(entry.getValue(), "dependency value");
      if (!type.isInstance(value)) {
        throw new IllegalArgumentException("Web MVC dependency type does not match its value");
      }
    }
    return Map.copyOf(dependencies);
  }

  public int port() {
    synchronized (lifecycleLock) {
      if (closed || !started) throw new IllegalStateException("Web HTTP server is unavailable");
      return tomcat.getConnector().getLocalPort();
    }
  }

  /**
   * Actual bound MVC mappings, not a static annotation inventory; Tomcat still owns the context.
   */
  public java.util.Set<String> mappedPaths() {
    synchronized (lifecycleLock) {
      if (closed || !started) throw new IllegalStateException("Web HTTP server is unavailable");
      var mappings =
          mvc.getBean(
              org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping
                  .class);
      var paths = new java.util.HashSet<String>();
      mappings.getHandlerMethods().keySet().forEach(info -> paths.addAll(info.getPatternValues()));
      return java.util.Set.copyOf(paths);
    }
  }

  @Override
  public void close() throws LifecycleException {
    synchronized (lifecycleLock) {
      if (destroyed) return;
      closed = true;
      if (!stopped) {
        tomcat.stop();
        stopped = true;
      }
      tomcat.destroy();
      destroyed = true;
    }
  }
}
