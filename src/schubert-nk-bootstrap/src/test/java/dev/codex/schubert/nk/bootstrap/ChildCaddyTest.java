package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SSC178: independently fixed Caddy unit/cgroup, never Artemis identity substitution. */
final class ChildCaddyTest {
  static final class Fixture extends ChildBrokerTest.Fixture {
    Fixture() {
      manager = ChildBrokerTest.UNIT.replace("artemis", "caddy");
      cgroup = "0::/system.slice/caddy.service\n";
    }

    @Override
    public byte[] caddyUnit() {
      return super.brokerUnit();
    }
  }

  @Test
  void caddy455009SameKernelIdentityAndGenerationTwice() throws Exception {
    var f = new Fixture();
    var actor =
        new ChildStartupContext(f)
            .verifyCaddy(ChildBrokerTest.BOOT, ChildBrokerTest.INV, ChildBrokerTest.FIXED);
    assertEquals(43, actor.pid());
    assertEquals(12345, actor.startTicks());
    assertEquals("0::/system.slice/caddy.service\n", actor.cgroup());
    assertEquals(2, f.owned.size());
    assertTrue(
        f.owned.stream().allMatch(bytes -> java.util.Arrays.equals(bytes, new byte[bytes.length])));
  }

  @Test
  void caddy455010ForeignUnitCapabilitiesAndManagerKernelDriftReject() {
    for (String field :
        List.of("unit", "cgroup", "caps", "groups", "nnp", "manager", "kernel", "uid")) {
      var f = new Fixture();
      switch (field) {
        case "unit" -> f.manager = ChildBrokerTest.UNIT;
        case "cgroup" -> f.cgroup = "0::/system.slice/artemis.service\n";
        case "caps" ->
            f.status = f.status.replace("CapEff:\t0000000000000000", "CapEff:\t0000000000000001");
        case "groups" -> f.status = f.status.replace("Groups:\t201", "Groups:\t201 202");
        case "nnp" -> f.status = f.status.replace("NoNewPrivs:\t1", "NoNewPrivs:\t0");
        case "manager" -> f.managerDrift = true;
        case "kernel" -> f.kernelDrift = true;
        case "uid" -> f.rootUid = 200;
        default -> throw new AssertionError();
      }
      assertThrows(
          IOException.class,
          () ->
              new ChildStartupContext(f)
                  .verifyCaddy(ChildBrokerTest.BOOT, ChildBrokerTest.INV, ChildBrokerTest.FIXED),
          field);
    }
    assertThrows(
        IOException.class,
        () ->
            new ChildStartupContext(new ChildBrokerTest.Fixture())
                .verifyCaddy(ChildBrokerTest.BOOT, ChildBrokerTest.INV, ChildBrokerTest.FIXED));
  }
}
