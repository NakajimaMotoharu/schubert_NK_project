package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS343 SSC137; PT-OPS-ROOTSELF-001..003. */
final class RootStartupPendingTest {
  private static final UUID BOOT = UUID.fromString("46600001-3333-4333-8444-555555555555");
  private static final String INVOCATION = "1234567890abcdef1234567890abcdef";

  private static StartupLaunchRecord launch(ServiceConfigFiles.Service service) {
    return new StartupLaunchRecord(
        service,
        BOOT,
        UUID.fromString("46600002-3333-4333-8444-555555555555"),
        "a".repeat(64),
        "b".repeat(64),
        new MaintenanceOwnerFrame.Parent(INVOCATION, 300, 700));
  }

  private static RootStartupContext.Snapshot self(
      RootStartupContext.Service service, String boot, String invocation, long pid, long ticks) {
    return new RootStartupContext.Snapshot(
        service, boot, invocation, pid, ticks, 1, "/system.slice/" + service.unit());
  }

  @Test
  void exactBothServicesMatchOnlyTheRecordedChildGeneration() {
    for (var service : ServiceConfigFiles.Service.values()) {
      var processService = RootStartupContext.Service.valueOf(service.name());
      var record = launch(service);
      assertDoesNotThrow(
          () ->
              RootStartupPending.verifySelf(
                  record, self(processService, BOOT.toString(), INVOCATION, 300, 700)));
    }
  }

  @Test
  void eachIndependentForeignIdentityAndOtherServiceIsRejected() {
    for (var service : ServiceConfigFiles.Service.values()) {
      var own = RootStartupContext.Service.valueOf(service.name());
      var other =
          own == RootStartupContext.Service.API
              ? RootStartupContext.Service.WEB
              : RootStartupContext.Service.API;
      var record = launch(service);
      var invalid =
          List.of(
              self(other, BOOT.toString(), INVOCATION, 300, 700),
              self(own, "46600003-3333-4333-8444-555555555555", INVOCATION, 300, 700),
              self(own, BOOT.toString(), "fedcba0987654321fedcba0987654321", 300, 700),
              self(own, BOOT.toString(), INVOCATION, 301, 700),
              self(own, BOOT.toString(), INVOCATION, 300, 701));
      for (var wrong : invalid)
        assertThrows(IOException.class, () -> RootStartupPending.verifySelf(record, wrong));
      for (var role : RootStartupContext.Service.values()) {
        if (role == RootStartupContext.Service.API || role == RootStartupContext.Service.WEB)
          continue;
        assertThrows(
            IOException.class,
            () ->
                RootStartupPending.verifySelf(
                    record, self(role, BOOT.toString(), INVOCATION, 300, 700)));
      }
    }
  }

  @Test
  void absentBoundaryObjectsFailBeforeAnyNativeAuthority() {
    var valid = self(RootStartupContext.Service.API, BOOT.toString(), INVOCATION, 300, 700);
    assertThrows(NullPointerException.class, () -> RootStartupPending.verifySelf(null, valid));
    assertThrows(
        NullPointerException.class,
        () -> RootStartupPending.verifySelf(launch(ServiceConfigFiles.Service.API), null));
  }
}
