package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import jakarta.servlet.Filter;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.function.Supplier;
import org.apache.catalina.LifecycleException;
import org.apache.catalina.LifecycleState;
import org.apache.catalina.core.StandardHost;
import org.apache.catalina.startup.Tomcat;
import org.apache.tomcat.util.descriptor.web.FilterDef;
import org.apache.tomcat.util.descriptor.web.FilterMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.DispatcherServlet;

/**
 * Loopback-only production Servlet/MVC composition. Credential, DataSource, JMS and security
 * dependencies are supplied by the later WebApplication bootstrap, never invented here. NK-WEB-002;
 * SYS-001/006/AUT-001; UI222/226/252; SS311/313/314/342/352/362; PG220/PT-SCR109..111.
 */
public final class WebHttpServer implements AutoCloseable {
  private final Tomcat tomcat;
  private final int port;
  private final Object lifecycleLock = new Object();
  private boolean closed;

  private WebHttpServer(Tomcat tomcat) {
    this.tomcat = tomcat;
    this.port = tomcat.getConnector().getLocalPort();
  }

  /**
   * Starts the real MVC server on 127.0.0.1; the supplied filter owns HTTP admission for every
   * dispatcher type. Port zero is permitted for isolated PT only.
   */
  public static WebHttpServer start(
      Path runtimeDirectory, int port, Filter security, Class<?>... featureConfigurations)
      throws LifecycleException {
    return startWithFactory(runtimeDirectory, port, security, Tomcat::new, featureConfigurations);
  }

  /** Package-local lifecycle seam: PT can verify failed bind/start and failed cleanup. */
  static WebHttpServer startWithFactory(
      Path runtimeDirectory,
      int port,
      Filter security,
      Supplier<Tomcat> tomcatFactory,
      Class<?>... featureConfigurations)
      throws LifecycleException {
    Objects.requireNonNull(runtimeDirectory, "runtimeDirectory");
    Objects.requireNonNull(security, "security");
    Objects.requireNonNull(tomcatFactory, "tomcatFactory");
    Objects.requireNonNull(featureConfigurations, "featureConfigurations");
    validateConfiguration(runtimeDirectory, port, featureConfigurations);
    var tomcat = Objects.requireNonNull(tomcatFactory.get(), "tomcatFactory result");
    try {
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
      var mvc = new AnnotationConfigWebApplicationContext();
      mvc.register(WebMvcConfiguration.class);
      if (featureConfigurations.length > 0) mvc.register(featureConfigurations);
      var servlet = Tomcat.addServlet(context, "nk-mvc", new DispatcherServlet(mvc));
      servlet.setLoadOnStartup(1);
      servlet.setAsyncSupported(true);
      context.addServletMapping("/", "nk-mvc");
      tomcat.start();
      if (context.getState() != LifecycleState.STARTED) {
        throw new LifecycleException("Web MVC startup failed");
      }
      return new WebHttpServer(tomcat);
    } catch (LifecycleException | RuntimeException failure) {
      try {
        tomcat.destroy();
      } catch (LifecycleException cleanup) {
        failure.addSuppressed(cleanup);
      }
      throw failure;
    }
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

  public int port() {
    synchronized (lifecycleLock) {
      if (closed) throw new IllegalStateException("Web HTTP server is closed");
      return port;
    }
  }

  @Override
  public void close() throws LifecycleException {
    synchronized (lifecycleLock) {
      if (closed) return;
      closed = true;
      try {
        tomcat.stop();
      } finally {
        tomcat.destroy();
      }
    }
  }
}
