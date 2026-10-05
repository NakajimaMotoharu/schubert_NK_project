package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Immutable, non-secret argv policy for the future same-PID root service launcher. The caller must
 * independently resolve and admit the fixed NSS identity, release/ELF/current permit, environment
 * allowlist and inherited descriptors before using the existing LinuxProcessExec boundary. This
 * class never executes a process or grants readiness. NK-OPS-001; SYS002/004,OPS009; UI212/251/253;
 * SS311/342§4.2/343; SSC086..089; PG369/PT-OPS-REXEC001..004; 471 D04/05.
 */
@NullMarked
public final class FixedServiceExecArguments {
  private static final List<String> WEB_JAVA =
      List.of(
          "-XX:MaxDirectMemorySize=128m",
          "-XX:MaxMetaspaceSize=192m",
          "-XX:ReservedCodeCacheSize=128m",
          "-Xms384m",
          "-Xmx768m",
          "-Xlog:gc*=info:stdout:time,uptime,level,tags",
          "-cp",
          "/opt/schubert-nk/current/web/web.jar:/opt/schubert-nk/current/web/lib/*",
          "dev.codex.schubert.nk.web.bootstrap.WebProcessMain");
  private static final List<String> API_JAVA =
      List.of(
          "-XX:MaxDirectMemorySize=256m",
          "-XX:MaxMetaspaceSize=256m",
          "-XX:ReservedCodeCacheSize=128m",
          "-Xms512m",
          "-Xmx1024m",
          "-Xlog:gc*=info:stdout:time,uptime,level,tags",
          "-cp",
          "/opt/schubert-nk/current/api/api.jar:/opt/schubert-nk/current/api/lib/*",
          "dev.codex.schubert.nk.api.bootstrap.ApiProcessMain");

  private final ServiceConfigFiles.Service service;
  private final FixedServiceIdentity.Value identity;

  public FixedServiceExecArguments(
      ServiceConfigFiles.Service service, FixedServiceIdentity.Value identity) {
    this.service = Objects.requireNonNull(service, "fixed service");
    this.identity = Objects.requireNonNull(identity, "admitted fixed NSS identity");
  }

  /** The first argv element is the held /usr/bin/setpriv ELF; no shell or arbitrary JVM option. */
  public List<String> arguments() {
    return arguments(java.util.Optional.empty());
  }

  /** SSC193: only the same service's closed ordinary PT profile; default vector stays identical. */
  public List<String> arguments(java.util.Optional<FixedNativeCoverageProfile> profile) {
    if (profile == null) throw new IllegalArgumentException("fixed PT profile required");
    profile.ifPresent(
        value -> {
          if (value.service() != service
              || value.phase() != FixedNativeCoverageProfile.Phase.ORDINARY)
            throw new IllegalArgumentException("fixed ordinary PT role required");
        });
    var argv = new ArrayList<String>();
    argv.addAll(
        List.of(
            "/usr/bin/setpriv",
            "--reuid=" + identity.uid(),
            "--regid=" + identity.gid(),
            "--groups=" + identity.groupArgument(),
            "--inh-caps=-all",
            "--ambient-caps=-all",
            "--bounding-set=-all",
            "--no-new-privs",
            "/usr/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-Dfile.encoding=UTF-8",
            "-Duser.timezone=UTC",
            "-XX:+ExitOnOutOfMemoryError"));
    profile.ifPresent(value -> argv.add(9, value.argument()));
    argv.addAll(
        switch (service) {
          case WEB -> WEB_JAVA;
          case API -> API_JAVA;
        });
    return List.copyOf(argv);
  }
}
