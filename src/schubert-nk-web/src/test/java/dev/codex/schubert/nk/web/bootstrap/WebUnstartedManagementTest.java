package dev.codex.schubert.nk.web.bootstrap;

import com.sun.net.httpserver.HttpServer;
import dev.codex.schubert.nk.api.file.OwnedRetentionProcess;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** SSC317/PT-NHOLD317001: unstarted stop return is UNKNOWN, not a release proof. */
final class WebUnstartedManagementTest {
  @Test
  void hold317001UnstartedManagementCannotUnwindTheOuterOwner() throws Exception {
    OwnedRetentionProcess.assertHeld(Driver.class, List.of());
  }

  public static final class Driver {
    public static void main(String[] arguments) throws IOException {
      OwnedRetentionProcess.deadline();
      var information =
          Map.of(
              "commit",
              "d".repeat(40),
              "app",
              "0.1.0",
              "config",
              "1",
              "schema",
              "025",
              "protocol",
              "001");
      try {
        ResourceScope.acquire(
            () -> WebManagementServer.bind(information, () -> true, 0, HttpServer::create),
            ServiceProcessResources.ownedRelease(WebManagementServer::close, true),
            owner -> Boolean.TRUE);
      } finally {
        System.out.println("OUTER_RELEASED");
      }
    }
  }
}
