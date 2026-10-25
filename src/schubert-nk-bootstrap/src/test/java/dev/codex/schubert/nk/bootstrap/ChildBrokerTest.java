package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * SSC125 BROKERSTART001/002, literal manager/kernel/NSS vectors, never synthetic startup authority.
 */
final class ChildBrokerTest {
  static final UUID BOOT = UUID.fromString("11111111-1111-4111-8111-111111111111");
  static final String INV = "7".repeat(32);
  static final FixedServiceIdentity.Value FIXED =
      new FixedServiceIdentity.Value(200, 201, List.of(201L));
  static final String UNIT =
      "Id=artemis.service\nLoadState=loaded\nActiveState=active\nSubState=running\n"
          + "MainPID=43\nInvocationID="
          + INV
          + "\nControlGroup=/system.slice/artemis.service\n";
  static final String STATUS =
      "Uid:\t200 200 200 200\nGid:\t201 201 201 201\nGroups:\t201\n"
          + "CapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\n"
          + "CapBnd:\t0000000000000000\nCapAmb:\t0000000000000000\nNoNewPrivs:\t1\n";

  static byte[] bytes(String s) {
    return s.getBytes(StandardCharsets.US_ASCII);
  }

  static class Fixture implements ChildStartupContext.Io {
    String manager = UNIT;
    String status = STATUS;
    String boot = BOOT + "\n";
    String cgroup = "0::/system.slice/artemis.service\n";
    String state = "S";
    long rootUid = 0;
    boolean managerDrift;
    boolean kernelDrift;
    boolean uidDrift;
    int reads;
    int ticks;
    int kernelReads;
    int statusReads;
    final List<byte[]> owned = new ArrayList<>();

    public long pid() {
      return 44;
    }

    public long uid() {
      return rootUid;
    }

    public String filesystem() {
      return "proc";
    }

    public byte[] boot() {
      kernelReads++;
      return bytes(boot);
    }

    public byte[] stat(long pid) {
      kernelReads++;
      assertEquals(43, pid);
      return bytes(
          "43 (vendor java) "
              + state
              + " "
              + "0 ".repeat(18)
              + (kernelDrift && ticks++ > 0 ? 12346 : 12345)
              + "\n");
    }

    public byte[] status(long pid) {
      kernelReads++;
      statusReads++;
      return bytes(
          uidDrift && statusReads > 1
              ? status.replace("200 200 200 200", "202 202 202 202")
              : status);
    }

    public byte[] cgroup(long pid) {
      kernelReads++;
      return bytes(cgroup);
    }

    public byte[] brokerUnit() {
      byte[] b =
          bytes(managerDrift && reads++ > 0 ? manager.replace(INV, "8".repeat(32)) : manager);
      owned.add(b);
      return b;
    }
  }

  @Test
  void common925004SecondCaptureUidChangeStillRejectsWithInnerUidContract() {
    var broker = new Fixture();
    broker.uidDrift = true;
    assertThrows(
        IOException.class, () -> new ChildStartupContext(broker).verifyBroker(BOOT, INV, FIXED));
    assertEquals(2, broker.statusReads);
    assertTrue(
        broker.owned.stream().allMatch(value -> Arrays.equals(value, new byte[value.length])));
    var caddy = new ChildCaddyTest.Fixture();
    caddy.uidDrift = true;
    assertThrows(
        IOException.class, () -> new ChildStartupContext(caddy).verifyCaddy(BOOT, INV, FIXED));
    assertEquals(2, caddy.statusReads);
    assertTrue(
        caddy.owned.stream().allMatch(value -> Arrays.equals(value, new byte[value.length])));
  }

  @Test
  void common922002MalformedInvocationRejectsBeforeBrokerOrCaddyObservation() {
    for (String invocation :
        List.of(
            "",
            "0".repeat(32),
            "A".repeat(32),
            "7".repeat(31),
            "11111111-1111-4111-8111-111111111111")) {
      var broker = new Fixture();
      assertThrows(
          IOException.class,
          () -> new ChildStartupContext(broker).verifyBroker(BOOT, invocation, FIXED));
      assertTrue(broker.owned.isEmpty(), "No manager observation for invalid broker invocation");
      assertEquals(0, broker.kernelReads);
      var caddy = new ChildCaddyTest.Fixture();
      assertThrows(
          IOException.class,
          () -> new ChildStartupContext(caddy).verifyCaddy(BOOT, invocation, FIXED));
      assertTrue(caddy.owned.isEmpty(), "No manager observation for invalid caddy invocation");
      assertEquals(0, caddy.kernelReads);
    }
  }

  @Test
  void rootReadsActualFixedBrokerTwiceWithoutConfusingRootAndBrokerUid() throws Exception {
    var f = new Fixture();
    var actual = new ChildStartupContext(f).verifyBroker(BOOT, INV, FIXED);
    assertEquals(43, actual.pid());
    assertEquals(12345, actual.startTicks());
    assertEquals(200, actual.uid());
    assertEquals(201, actual.gid());
    assertEquals(List.of(201L), actual.groups());
    assertTrue(actual.zeroCapabilities());
    assertTrue(actual.noNewPrivileges());
    assertEquals("ChildStartupContext.Observed[REDACTED]", actual.toString());
    assertEquals(2, f.owned.size());
    for (byte[] b : f.owned) assertArrayEquals(new byte[b.length], b);
    var nss = new FixedServiceIdentityTest.Fixture();
    nss.values.put(
        "passwd/schubert-artemis", "schubert-artemis:x:200:201::/nonexistent:/usr/sbin/nologin\n");
    nss.values.put("group/schubert-artemis", "schubert-artemis:x:201:\n");
    assertEquals(FIXED, nss.subject().resolveArtemis());
    assertEquals(
        List.of(
            List.of("/usr/bin/getent", "passwd", "schubert-artemis"),
            List.of("/usr/bin/getent", "group", "schubert-artemis")),
        nss.commands);
  }

  @Test
  void independentDaemonManagerKernelAndOwnerMismatchesReject() {
    for (var change :
        List.of(
            Map.entry("Id=artemis.service", "Id=other.service"),
            Map.entry("LoadState=loaded", "LoadState=not-found"),
            Map.entry("ActiveState=active", "ActiveState=activating"),
            Map.entry("SubState=running", "SubState=start"),
            Map.entry("MainPID=43", "MainPID=1"),
            Map.entry(INV, "8".repeat(32)),
            Map.entry("ControlGroup=/system.slice/artemis.service", "ControlGroup=/other"),
            Map.entry("Id=artemis.service\n", "Id=artemis.service\nId=artemis.service\n"),
            Map.entry("Id=artemis.service\n", "Unknown=x\n"),
            Map.entry("Id=artemis.service\n", "badline\n"))) {
      var f = new Fixture();
      f.manager = UNIT.replace(change.getKey(), change.getValue());
      assertThrows(
          IOException.class,
          () -> new ChildStartupContext(f).verifyBroker(BOOT, INV, FIXED),
          change.toString());
    }
    for (var change :
        List.of(
            Map.entry("200 200 200 200", "202 202 202 202"),
            Map.entry("201 201 201 201", "202 202 202 202"),
            Map.entry("Groups:\t201", "Groups:\t201 202"),
            Map.entry("CapBnd:\t0000000000000000", "CapBnd:\t0000000000000001"),
            Map.entry("NoNewPrivs:\t1", "NoNewPrivs:\t0"))) {
      var f = new Fixture();
      f.status = STATUS.replace(change.getKey(), change.getValue());
      assertThrows(
          IOException.class, () -> new ChildStartupContext(f).verifyBroker(BOOT, INV, FIXED));
    }
    for (String fault :
        List.of("root", "boot", "cgroup", "zombie", "managerDrift", "kernelDrift")) {
      var f = new Fixture();
      switch (fault) {
        case "root" -> f.rootUid = 200;
        case "boot" -> f.boot = "22222222-2222-4222-8222-222222222222\n";
        case "cgroup" -> f.cgroup = "0::/other\n";
        case "zombie" -> f.state = "Z";
        case "managerDrift" -> f.managerDrift = true;
        case "kernelDrift" -> f.kernelDrift = true;
        default -> fail("closed fixture");
      }
      assertThrows(
          IOException.class,
          () -> new ChildStartupContext(f).verifyBroker(BOOT, INV, FIXED),
          fault);
    }
    var c = new ChildStartupContext(new Fixture());
    assertThrows(IOException.class, () -> c.verifyBroker(BOOT, "0".repeat(32), FIXED));
    assertThrows(NullPointerException.class, () -> c.verifyBroker(null, INV, FIXED));
    assertThrows(NullPointerException.class, () -> c.verifyBroker(BOOT, null, FIXED));
    assertThrows(NullPointerException.class, () -> c.verifyBroker(BOOT, INV, null));
    Thread.currentThread().interrupt();
    try {
      assertThrows(IOException.class, () -> c.verifyBroker(BOOT, INV, FIXED));
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void brokerstart003InterruptAfterSecondManagerReadDeniesAndErasesBothBuffers() {
    var fixture =
        new Fixture() {
          int readsForInterruption;

          @Override
          public byte[] brokerUnit() {
            byte[] result = super.brokerUnit();
            if (++readsForInterruption == 2) Thread.currentThread().interrupt();
            return result;
          }
        };
    try {
      var error =
          assertThrows(
              IOException.class,
              () -> new ChildStartupContext(fixture).verifyBroker(BOOT, INV, FIXED));
      assertEquals("child startup context unavailable", error.getMessage());
      assertNull(error.getCause());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(2, fixture.owned.size());
      for (byte[] buffer : fixture.owned) assertArrayEquals(new byte[buffer.length], buffer);
    } finally {
      Thread.interrupted();
    }
  }
}
