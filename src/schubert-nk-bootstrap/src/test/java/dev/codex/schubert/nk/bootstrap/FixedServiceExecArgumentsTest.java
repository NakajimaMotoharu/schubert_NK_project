package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SS342§4.2 independent literal argv golden; PT-OPS-REXEC001..004. */
final class FixedServiceExecArgumentsTest {
  private static final FixedServiceIdentity.Value WEB_IDENTITY =
      new FixedServiceIdentity.Value(998, 980, List.of(980L, 982L, 986L));
  private static final FixedServiceIdentity.Value API_IDENTITY =
      new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L));

  private static List<String> expectedWebVector() {
    return List.of(
        "/usr/bin/setpriv",
        "--reuid=998",
        "--regid=980",
        "--groups=980,982,986",
        "--inh-caps=-all",
        "--ambient-caps=-all",
        "--bounding-set=-all",
        "--no-new-privs",
        "/usr/bin/java",
        "--enable-native-access=ALL-UNNAMED",
        "-Dfile.encoding=UTF-8",
        "-Duser.timezone=UTC",
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxDirectMemorySize=128m",
        "-XX:MaxMetaspaceSize=192m",
        "-XX:ReservedCodeCacheSize=128m",
        "-Xms384m",
        "-Xmx768m",
        "-Xlog:gc*=info:stdout:time,uptime,level,tags",
        "-cp",
        "/opt/schubert-nk/current/web/web.jar:/opt/schubert-nk/current/web/lib/*",
        "dev.codex.schubert.nk.web.bootstrap.WebProcessMain");
  }

  private static List<String> expectedApiVector() {
    return List.of(
        "/usr/bin/setpriv",
        "--reuid=999",
        "--regid=981",
        "--groups=980,981,982,986",
        "--inh-caps=-all",
        "--ambient-caps=-all",
        "--bounding-set=-all",
        "--no-new-privs",
        "/usr/bin/java",
        "--enable-native-access=ALL-UNNAMED",
        "-Dfile.encoding=UTF-8",
        "-Duser.timezone=UTC",
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:MaxDirectMemorySize=256m",
        "-XX:MaxMetaspaceSize=256m",
        "-XX:ReservedCodeCacheSize=128m",
        "-Xms512m",
        "-Xmx1024m",
        "-Xlog:gc*=info:stdout:time,uptime,level,tags",
        "-cp",
        "/opt/schubert-nk/current/api/api.jar:/opt/schubert-nk/current/api/lib/*",
        "dev.codex.schubert.nk.api.bootstrap.ApiProcessMain");
  }

  @Test
  void rexec001WebFixedSetprivAndJavaVectorMatchesDesign() {
    var actual =
        new FixedServiceExecArguments(ServiceConfigFiles.Service.WEB, WEB_IDENTITY).arguments();
    assertEquals(expectedWebVector(), actual);
    assertFalse(actual.toString().contains("--init-groups"));
    assertFalse(actual.toString().contains("/bin/sh"));
  }

  @Test
  void rexec002ApiFixedSetprivAndJavaVectorMatchesDesign() {
    var actual =
        new FixedServiceExecArguments(ServiceConfigFiles.Service.API, API_IDENTITY).arguments();
    assertEquals(expectedApiVector(), actual);
    assertFalse(actual.toString().contains("--init-groups"));
    assertFalse(actual.toString().contains("/bin/sh"));
  }

  @Test
  void rexec003NullAndIdentityInvariantRejectBeforeVector() {
    assertThrows(
        NullPointerException.class, () -> new FixedServiceExecArguments(null, WEB_IDENTITY));
    assertThrows(
        NullPointerException.class,
        () -> new FixedServiceExecArguments(ServiceConfigFiles.Service.WEB, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FixedServiceIdentity.Value(0, 980, List.of(980L)));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FixedServiceIdentity.Value(998, 980, List.of(982L)));
  }

  @Test
  void rexec004RepeatedAndConcurrentVectorsAreImmutable() throws Exception {
    var command = new FixedServiceExecArguments(ServiceConfigFiles.Service.WEB, WEB_IDENTITY);
    var first = command.arguments();
    assertThrows(UnsupportedOperationException.class, () -> first.add("UNTRUSTED"));
    var workers = Executors.newFixedThreadPool(4);
    try {
      var futures = new ArrayList<java.util.concurrent.Future<Boolean>>();
      for (int i = 0; i < 40; i++) {
        futures.add(workers.submit(() -> expectedWebVector().equals(command.arguments())));
      }
      for (var future : futures) assertTrue(future.get(5, TimeUnit.SECONDS).booleanValue());
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS), "owned argv workers terminate");
    }
  }

  @Test
  void rexec193FixedOrdinaryAgentIsTheOnlyAdditionalArgument() {
    String inv = "1234567890abcdef1234567890abcdef";
    String prefix =
        "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=";
    for (var service : ServiceConfigFiles.Service.values()) {
      var command =
          new FixedServiceExecArguments(
              service, service == ServiceConfigFiles.Service.API ? API_IDENTITY : WEB_IDENTITY);
      String option = prefix + service.name() + "-" + inv + "-ordinary";
      var profile =
          FixedNativeCoverageProfile.parse(
              service, FixedNativeCoverageProfile.Phase.ORDINARY, inv, List.of(option));
      var actual = command.arguments(profile);
      assertEquals(option, actual.get(9));
      var withoutAgent = new ArrayList<>(actual);
      withoutAgent.remove(9);
      assertEquals(
          service == ServiceConfigFiles.Service.API ? expectedApiVector() : expectedWebVector(),
          withoutAgent);
      assertThrows(UnsupportedOperationException.class, () -> actual.add("unexpected"));
      var rootProfile =
          FixedNativeCoverageProfile.parse(
              service,
              FixedNativeCoverageProfile.Phase.ROOT,
              inv,
              List.of(prefix + service.name() + "-" + inv + "-root"));
      assertThrows(IllegalArgumentException.class, () -> command.arguments(rootProfile));
      var other =
          service == ServiceConfigFiles.Service.API
              ? ServiceConfigFiles.Service.WEB
              : ServiceConfigFiles.Service.API;
      var otherProfile =
          FixedNativeCoverageProfile.parse(
              other,
              FixedNativeCoverageProfile.Phase.ORDINARY,
              inv,
              List.of(prefix + other.name() + "-" + inv + "-ordinary"));
      assertThrows(IllegalArgumentException.class, () -> command.arguments(otherProfile));
      assertThrows(IllegalArgumentException.class, () -> command.arguments(null));
    }
  }
}
