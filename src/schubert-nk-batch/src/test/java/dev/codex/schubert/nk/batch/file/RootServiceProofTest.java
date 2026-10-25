package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** ROOTPROOF001..004/ROOTTICKET001: whole hand-written fields, no Production expected encoder. */
final class RootServiceProofTest {
  static final String GOLD =
      """
      NKSTART1
      service=API
      boot_id=31100027-3333-4333-8444-555555555555
      invocation_id=22222222222222222222222222222222
      pid=300
      start_ticks=200
      admission_fd=128
      admission_device=123
      admission_inode=456
      service_uid=200
      service_gid=201
      service_groups=200,201,202
      permit_epoch=31100027-4444-4333-8444-555555555555
      permit_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      release_sha256=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
      config_sha256=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      roots_sha256=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
      broker_invocation_id=55555555555555555555555555555555
      """;

  static RootStartupContext.Snapshot self(RootStartupContext.Service actor) {
    return new RootStartupContext.Snapshot(
        actor,
        "31100027-3333-4333-8444-555555555555",
        "2".repeat(32),
        300,
        200,
        9,
        "/system.slice/" + actor.unit());
  }

  static RootCurrentPermitPreflight.Observed issued() throws Exception {
    var epoch = StartupLaunchFilesTest.epoch();
    var permit =
        new StartupPermitRecords.Permit(
            epoch.boot(),
            epoch.epoch(),
            epoch.activation(),
            "5".repeat(32),
            "b".repeat(64),
            "c".repeat(64),
            "d".repeat(64),
            "e".repeat(64),
            "f".repeat(64));
    return new RootCurrentPermitPreflight.Observed(epoch, permit);
  }

  static final FixedServiceIdentity.Value ID =
      new FixedServiceIdentity.Value(200, 201, List.of(200L, 201L, 202L));
  static final StartupAdmissionFile.Admission A = new StartupAdmissionFile.Admission(128, 123, 456);

  @Test
  void entireApiWebFramesFromExplicitActualInputFields() throws Exception {
    for (var role : ServiceConfigFiles.Service.values()) {
      String expected = GOLD.replace("service=API", "service=" + role.name());
      if (role == ServiceConfigFiles.Service.WEB)
        expected = expected.replace("c".repeat(64), "d".repeat(64));
      var frame =
          RootServiceLauncher.proof(
              role,
              self(RootStartupContext.Service.valueOf(role.name())),
              A,
              ID,
              issued(),
              "e".repeat(64));
      assertArrayEquals(expected.getBytes(StandardCharsets.US_ASCII), frame.encode());
      assertEquals(17, frame.fields().size());
      assertFalse(frame.fields().containsKey("proof_fd"));
    }
  }

  @Test
  void mismatchedRoleRootsAndMissingInputNeverEmitProof() throws Exception {
    var observed = issued();
    var actual = self(RootStartupContext.Service.API);
    assertThrows(
        IOException.class,
        () ->
            RootServiceLauncher.proof(
                ServiceConfigFiles.Service.WEB, actual, A, ID, observed, "e".repeat(64)));
    assertThrows(
        IOException.class,
        () ->
            RootServiceLauncher.proof(
                ServiceConfigFiles.Service.API, actual, A, ID, observed, "0".repeat(64)));
    for (int absent = 0; absent < 6; absent++) {
      final int index = absent;
      assertThrows(
          NullPointerException.class,
          () ->
              RootServiceLauncher.proof(
                  index == 0 ? null : ServiceConfigFiles.Service.API,
                  index == 1 ? null : actual,
                  index == 2 ? null : A,
                  index == 3 ? null : ID,
                  index == 4 ? null : observed,
                  index == 5 ? null : "e".repeat(64)));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            RootServiceLauncher.proof(
                ServiceConfigFiles.Service.API,
                actual,
                new StartupAdmissionFile.Admission(127, 123, 456),
                ID,
                observed,
                "e".repeat(64)));
  }

  @Test
  void eachIndependentEpochBootAndActivationContradictionNeverEmitsProof() throws Exception {
    var observed = issued();
    var current = observed.current();
    var permit = observed.permit();
    var wrongBoot = UUID.fromString("31100027-7777-4333-8444-555555555555");
    var wrongEpoch = UUID.fromString("31100027-8888-4333-8444-555555555555");
    var wrongActivation =
        new dev.codex.schubert.nk.batch.repository.MaintenanceActivation(
            permit.activation().run(), UUID.fromString("31100027-9999-4333-8444-555555555555"));
    var actual = self(RootStartupContext.Service.API);
    var foreignSelf =
        new RootStartupContext.Snapshot(
            actual.service(),
            wrongBoot.toString(),
            actual.invocation(),
            actual.pid(),
            actual.startTicks(),
            actual.initStartTicks(),
            actual.controlGroup());
    assertThrows(
        IOException.class,
        () ->
            RootServiceLauncher.proof(
                ServiceConfigFiles.Service.API, foreignSelf, A, ID, observed, "e".repeat(64)));
    for (int field = 0; field < 3; field++) {
      var contradicted =
          new StartupPermitRecords.Permit(
              field == 0 ? wrongBoot : permit.boot(),
              field == 1 ? wrongEpoch : permit.epoch(),
              field == 2 ? wrongActivation : permit.activation(),
              permit.brokerInvocation(),
              permit.releaseDigest(),
              permit.apiConfigDigest(),
              permit.webConfigDigest(),
              permit.rootsDigest(),
              permit.prestartStepsDigest());
      var wrong = new RootCurrentPermitPreflight.Observed(current, contradicted);
      assertThrows(
          IOException.class,
          () ->
              RootServiceLauncher.proof(
                  ServiceConfigFiles.Service.API, actual, A, ID, wrong, "e".repeat(64)));
    }
  }

  @Test
  void ticketMustMatchActualServiceBootInvocationPidAndStart() throws Exception {
    var actual = self(RootStartupContext.Service.API);
    var launch =
        StartupLaunchRecord.consume(StartupLaunchRecordTest.bytes(StartupLaunchRecordTest.GOLD));
    RootStartupPending.verifySelf(launch, actual);
    for (String changed :
        List.of(
            StartupLaunchRecordTest.GOLD.replace("service=API", "service=WEB"),
            StartupLaunchRecordTest.GOLD.replace("3333-4333", "3334-4333"),
            StartupLaunchRecordTest.GOLD.replace("2".repeat(32), "3".repeat(32)),
            StartupLaunchRecordTest.GOLD.replace("pid=300", "pid=301"),
            StartupLaunchRecordTest.GOLD.replace("start_ticks=200", "start_ticks=201"))) {
      var wrong = StartupLaunchRecord.consume(StartupLaunchRecordTest.bytes(changed));
      assertThrows(IOException.class, () -> RootStartupPending.verifySelf(wrong, actual));
    }
    assertThrows(
        IOException.class,
        () -> RootStartupPending.verifySelf(launch, self(RootStartupContext.Service.MORNING)));
    assertThrows(NullPointerException.class, () -> RootStartupPending.verifySelf(null, actual));
    assertThrows(NullPointerException.class, () -> RootStartupPending.verifySelf(launch, null));
  }
}
