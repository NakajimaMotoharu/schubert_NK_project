package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.NoSuchFileException;
import java.util.List;
import org.junit.jupiter.api.Test;

/** ROOTGEN-1741-001..004 / OPS009/UI251/SS343353354/SSC164; literal data, no owner grant. */
final class RootGenerationCounterexampleTest {
  private static RootStartupContext.Snapshot copy(
      RootStartupContext.Snapshot s,
      RootStartupContext.Service service,
      String boot,
      long pid,
      long ticks,
      long init,
      String group) {
    return new RootStartupContext.Snapshot(service, boot, s.invocation(), pid, ticks, init, group);
  }

  @Test
  void rootgen1741001ApiAndWebGenerationControlsAreDataNotNewRootAdmission() throws Exception {
    for (var service : List.of(RootStartupContext.Service.API, RootStartupContext.Service.WEB)) {
      var f = new RootStartupContextTest.LaunchFixture();
      f.target = service;
      f.targetUnit = f.targetUnit.replace("schubert-nk-api.service", service.unit());
      f.targetGroup = "0::/system.slice/" + service.unit() + "\n";
      var root = f.context();
      var morning = root.capture(RootStartupContext.Service.MORNING);
      var child = root.captureServiceRoot(morning, service);
      assertEquals(200, child.pid());
      assertEquals(999, child.startTicks());
      assertEquals("/system.slice/" + service.unit(), child.controlGroup());
      f.rootUid = 999;
      root.recheckServiceGeneration(morning, child);
      assertFalse(root.serviceGenerationExited(morning, child));
      assertThrows(IOException.class, () -> root.captureServiceRoot(morning, service));
    }
  }

  @Test
  void rootgen1741002ForeignCapturedTerminalClaimsRejectBeforeMissingProc() throws Exception {
    var f = new RootStartupContextTest.LaunchFixture();
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    var c = root.captureServiceRoot(morning, RootStartupContext.Service.API);
    f.targetStat = "<MISSING>";
    var invalid =
        List.of(
            copy(
                c,
                RootStartupContext.Service.MORNING,
                c.boot(),
                c.pid(),
                c.startTicks(),
                c.initStartTicks(),
                c.controlGroup()),
            copy(
                c,
                c.service(),
                "foreign-boot",
                c.pid(),
                c.startTicks(),
                c.initStartTicks(),
                c.controlGroup()),
            copy(c, c.service(), c.boot(), 1, c.startTicks(), c.initStartTicks(), c.controlGroup()),
            copy(
                c,
                c.service(),
                c.boot(),
                morning.pid(),
                c.startTicks(),
                c.initStartTicks(),
                c.controlGroup()),
            copy(
                c,
                c.service(),
                c.boot(),
                c.pid(),
                c.startTicks(),
                c.initStartTicks(),
                "/system.slice/foreign.service"));
    for (var candidate : invalid)
      assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, candidate));
    assertThrows(IOException.class, () -> root.serviceGenerationExited(c, c));
    assertTrue(root.serviceGenerationExited(morning, c));
  }

  @Test
  void rootgen1741003RecheckRejectsForeignBootInitAndSamePidNewTicks() throws Exception {
    var f = new RootStartupContextTest.LaunchFixture();
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    var c = root.captureServiceRoot(morning, RootStartupContext.Service.API);
    for (var candidate :
        List.of(
            copy(
                c,
                c.service(),
                "foreign-boot",
                c.pid(),
                c.startTicks(),
                c.initStartTicks(),
                c.controlGroup()),
            copy(
                c,
                c.service(),
                c.boot(),
                c.pid(),
                c.startTicks(),
                c.initStartTicks() + 1,
                c.controlGroup()),
            copy(
                c,
                c.service(),
                c.boot(),
                c.pid(),
                c.startTicks() + 1,
                c.initStartTicks(),
                c.controlGroup()),
            copy(
                c,
                RootStartupContext.Service.MORNING,
                c.boot(),
                c.pid(),
                c.startTicks(),
                c.initStartTicks(),
                c.controlGroup())))
      assertThrows(IOException.class, () -> root.recheckServiceGeneration(morning, candidate));
    assertThrows(IOException.class, () -> root.recheckServiceGeneration(c, c));
    root.recheckServiceGeneration(morning, c);
  }

  @Test
  void rootgen1741004TwoReadDisappearanceRacesNeverCertifyUnstablePid() throws Exception {
    for (boolean firstMissing : new boolean[] {false, true}) {
      var f =
          new RootStartupContextTest.LaunchFixture() {
            boolean armed;
            int probes;

            @Override
            public byte[] stat(long value) throws IOException {
              if (value != 200 || !armed) return super.stat(value);
              boolean missing = ++probes == 1 ? firstMissing : !firstMissing;
              if (missing) throw new NoSuchFileException("PUBLIC_FIXED_PROC");
              return RootStartupContextTest.bytes(RootStartupContextTest.stat(200, "999"));
            }
          };
      var root = f.context();
      var morning = root.capture(RootStartupContext.Service.MORNING);
      var c = root.captureServiceRoot(morning, RootStartupContext.Service.API);
      f.armed = true;
      if (firstMissing)
        assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, c));
      else assertFalse(root.serviceGenerationExited(morning, c));
      assertEquals(2, f.probes);
    }
  }

  @Test
  void rootgen1741005AuthorityDriftAfterParentRecheckCannotAdmitChild() throws Exception {
    for (String fault : List.of("uid", "fs", "exe", "boot", "init")) {
      var f =
          new RootStartupContextTest.LaunchFixture() {
            boolean armed;
            final java.util.Map<String, Integer> counts = new java.util.HashMap<>();

            boolean drift(String name) {
              // A parent recheck comprises two complete self observations. Only
              // the next target observation changes the selected kernel fact.
              return armed && counts.merge(name, 1, Integer::sum) == 3 && name.equals(fault);
            }

            @Override
            public long effectiveUid() {
              return drift("uid") ? 1000 : super.effectiveUid();
            }

            @Override
            public String procFilesystem() throws IOException {
              return drift("fs") ? "tmpfs" : super.procFilesystem();
            }

            @Override
            public String initExecutable() throws IOException {
              return drift("exe") ? "/usr/bin/foreign" : super.initExecutable();
            }

            @Override
            public byte[] boot() throws IOException {
              return drift("boot")
                  ? RootStartupContextTest.bytes("22222222-2222-2222-2222-222222222222\n")
                  : super.boot();
            }

            @Override
            public byte[] stat(long pid) throws IOException {
              return pid == 1 && drift("init")
                  ? RootStartupContextTest.bytes(RootStartupContextTest.stat(1, "99999"))
                  : super.stat(pid);
            }
          };
      var root = f.context();
      var morning = root.capture(RootStartupContext.Service.MORNING);
      f.armed = true;
      assertThrows(
          IOException.class,
          () -> root.captureServiceRoot(morning, RootStartupContext.Service.API));
      assertEquals(3, f.counts.get(fault));
      assertEquals(0, f.targetReads);
    }
  }

  @Test
  void rootgen1741006PidMinimumInvocationZeroAndChangingTicksReject() throws Exception {
    for (String field : List.of("pid", "invocation")) {
      var f = new RootStartupContextTest.LaunchFixture();
      var root = f.context();
      var morning = root.capture(RootStartupContext.Service.MORNING);
      f.targetUnit =
          field.equals("pid")
              ? f.targetUnit.replace("MainPID=200", "MainPID=1")
              : f.targetUnit.replace("2".repeat(32), "0".repeat(32));
      assertThrows(
          IOException.class,
          () -> root.captureServiceRoot(morning, RootStartupContext.Service.API));
    }
    var f =
        new RootStartupContextTest.LaunchFixture() {
          int targetStats;

          @Override
          public byte[] stat(long pid) throws IOException {
            if (pid == 200)
              return RootStartupContextTest.bytes(
                  RootStartupContextTest.stat(200, ++targetStats == 1 ? "999" : "1000"));
            return super.stat(pid);
          }
        };
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    assertThrows(
        IOException.class, () -> root.captureServiceRoot(morning, RootStartupContext.Service.API));
    assertEquals(2, f.targetStats);
  }

  @Test
  void rootgen1741007WrongDeadlineRoleCannotBorrowOtherUnitBudget() throws Exception {
    var f = new RootStartupContextTest.LaunchFixture();
    var root = f.context();
    var morning = root.capture(RootStartupContext.Service.MORNING);
    var child = root.captureServiceRoot(morning, RootStartupContext.Service.API);
    assertThrows(IOException.class, () -> root.maintenanceDeadline(child, Long.MAX_VALUE));
    assertThrows(IOException.class, () -> root.serviceRootDeadline(morning, Long.MAX_VALUE));
  }

  @Test
  void rootgen1741008KernelStatusDelIsNotAllowedAscii() {
    var invalid = RootStartupContextTest.bytes("Uid: 0 0 0 0\nName: java" + ((char) 127) + "\n");
    assertThrows(IOException.class, () -> RootStartupContext.rootUid(invalid));
    assertEquals(127, invalid[invalid.length - 2]);
  }
}
