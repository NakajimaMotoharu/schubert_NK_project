package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SSC196/PT-OPS-NC196001..004: literal roles/options/NSS, no production-derived oracle. */
final class TerminalNativeCoverageProfileTest {
  private static final String INV = "1234567890abcdef1234567890abcdef";
  private static final String PREFIX =
      "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=";
  private static final byte[] GOLDEN = {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1};

  @Test
  void nc196001TwoLiteralTerminalRolesCannotMasqueradeAsStartup() throws Exception {
    var roles =
        List.of(
            FixedNativeCoverageProfile.TerminalRole.INSPECTOR,
            FixedNativeCoverageProfile.TerminalRole.BOOTSTRAP);
    var labels = List.of("INSPECTOR", "BOOTSTRAP");
    var units =
        List.of("schubert-nk-inbox-inspector.service", "schubert-nk-bootstrap-admin.service");
    var dirs = List.of("ordinary-inspector196", "ordinary-bootstrap196");
    for (int i = 0; i < 2; i++) {
      String expected = PREFIX + labels.get(i) + "-" + INV + "-ordinary";
      var profile =
          FixedNativeCoverageProfile.parseTerminal(roles.get(i), INV, List.of(expected))
              .orElseThrow();
      assertEquals(expected, profile.argument());
      assertEquals(labels.get(i) + "-" + INV + "-ordinary", profile.sessionId());
      assertEquals(INV, profile.invocation());
      assertEquals(FixedNativeCoverageProfile.Phase.ORDINARY, profile.phase());
      assertEquals("0::/system.slice/" + units.get(i) + "\n", profile.cgroup());
      assertEquals(dirs.get(i), profile.directory());
      assertThrows(IllegalStateException.class, profile::service);
      assertThrows(IllegalStateException.class, profile::forOrdinary);
      assertTrue(FixedNativeCoverageProfile.parseTerminal(roles.get(i), null, List.of()).isEmpty());
      assertTrue(
          FixedNativeCoverageProfile.parseTerminal(
                  roles.get(i), "invalid", List.of("-javaagent:/host/agent.jar"))
              .isEmpty());
      assertTrue(
          FixedNativeCoverageCheckpoint.fromCurrentTerminalJvm(roles.get(i), null).isEmpty());
    }
  }

  @Test
  void nc196002NullUnknownDuplicateAndExpandedProfilesAreRejected() {
    var role = FixedNativeCoverageProfile.TerminalRole.INSPECTOR;
    String valid = PREFIX + "INSPECTOR-" + INV + "-ordinary";
    assertThrows(
        IllegalArgumentException.class,
        () -> FixedNativeCoverageProfile.parseTerminal(null, INV, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> FixedNativeCoverageProfile.parseTerminal(role, INV, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> FixedNativeCoverageProfile.parseTerminal(role, INV, Arrays.asList("-Xmx512m", null)));
    for (String bad :
        Arrays.asList(
            null, "", "0".repeat(32), "F".repeat(32), INV + "\n", "1".repeat(31), "1".repeat(33)))
      assertThrows(
          IllegalArgumentException.class,
          () -> FixedNativeCoverageProfile.parseTerminal(role, bad, List.of(valid)));
    for (String bad :
        List.of(
            valid.replace("INSPECTOR-", "BOOTSTRAP-"),
            valid.replace("INSPECTOR-", "API-"),
            valid.replace("-ordinary", "-root"),
            valid.replace(INV, "a".repeat(32)),
            valid.replace("output=none", "output=file"),
            valid.replace("append=false", "append=true"),
            valid.replace("dumponexit=false", "dumponexit=true"),
            valid.replace("jacoco-agent.jar", "other.jar"),
            valid + ",jmx=true",
            valid + " "))
      assertThrows(
          IllegalArgumentException.class,
          () -> FixedNativeCoverageProfile.parseTerminal(role, INV, List.of(bad)));
    assertThrows(
        IllegalArgumentException.class,
        () -> FixedNativeCoverageProfile.parseTerminal(role, INV, List.of(valid, valid)));
    assertThrows(
        IOException.class, () -> FixedNativeCoverageCheckpoint.fromCurrentTerminalJvm(null, INV));
  }

  @Test
  void nc196003ClosedNssMappingAndOldFourDirectoriesRemainExact() throws Exception {
    var f = new FixedServiceIdentityTest.Fixture();
    f.values.put(
        "passwd/schubert-inbox-inspector",
        "schubert-inbox-inspector:x:991:976::/nonexistent:/usr/sbin/nologin\n");
    f.values.put("group/schubert-inbox-inspector", "schubert-inbox-inspector:x:976:\n");
    var inspector =
        FixedNativeCoverageProfile.parseTerminal(
                FixedNativeCoverageProfile.TerminalRole.INSPECTOR,
                INV,
                List.of(PREFIX + "INSPECTOR-" + INV + "-ordinary"))
            .orElseThrow();
    assertEquals(
        new FixedServiceIdentity.Value(991, 976, List.of(976L, 982L, 986L)),
        inspector.identity(f.subject()));
    var bootstrap =
        FixedNativeCoverageProfile.parseTerminal(
                FixedNativeCoverageProfile.TerminalRole.BOOTSTRAP,
                INV,
                List.of(PREFIX + "BOOTSTRAP-" + INV + "-ordinary"))
            .orElseThrow();
    assertEquals(
        new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L)),
        bootstrap.identity(f.subject()));
    for (var service : ServiceConfigFiles.Service.values())
      for (var phase : FixedNativeCoverageProfile.Phase.values()) {
        String label = service == ServiceConfigFiles.Service.API ? "api" : "web";
        String prefix = phase == FixedNativeCoverageProfile.Phase.ROOT ? "root" : "ordinary";
        var profile =
            FixedNativeCoverageProfile.parse(
                    service,
                    phase,
                    INV,
                    List.of(PREFIX + label.toUpperCase(Locale.ROOT) + "-" + INV + "-" + prefix))
                .orElseThrow();
        assertEquals(prefix + "-" + label + "193", profile.directory());
        assertEquals("0::/system.slice/schubert-nk-" + label + ".service\n", profile.cgroup());
        assertEquals(
            service == ServiceConfigFiles.Service.API
                ? new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L))
                : new FixedServiceIdentity.Value(998, 980, List.of(980L, 982L, 986L)),
            profile.identity(f.subject()));
      }
  }

  @Test
  void nc196004TerminalExportIsNewOnceAndBeforeExecDoesNotTouchAgent() throws Exception {
    for (var role : FixedNativeCoverageProfile.TerminalRole.values()) {
      String label =
          role == FixedNativeCoverageProfile.TerminalRole.INSPECTOR ? "INSPECTOR" : "BOOTSTRAP";
      var profile =
          FixedNativeCoverageProfile.parseTerminal(
                  role, INV, List.of(PREFIX + label + "-" + INV + "-ordinary"))
              .orElseThrow();
      AtomicInteger reads = new AtomicInteger();
      var agent =
          new FixedNativeCoverageCheckpoint.Agent() {
            public String version() {
              return "0.8.15.202606040825";
            }

            public String session() {
              return label + "-" + INV + "-ordinary";
            }

            public byte[] executionDataWithoutReset() {
              reads.incrementAndGet();
              return GOLDEN.clone();
            }
          };
      var output = new LinkedHashMap<String, byte[]>();
      var checkpoint =
          new FixedNativeCoverageCheckpoint(
              profile,
              agent,
              (name, bytes) -> {
                assertNull(output.put(name, bytes.clone()));
                bytes[0] = 9;
              });
      assertThrows(
          IllegalArgumentException.class,
          () -> checkpoint.capture(FixedNativeCoverageCheckpoint.Point.BEFORE_EXEC));
      assertEquals(0, reads.get());
      checkpoint.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL);
      assertEquals(List.of(INV + ".terminal.exec"), List.copyOf(output.keySet()));
      assertArrayEquals(GOLDEN, output.get(INV + ".terminal.exec"));
      assertEquals(1, reads.get());
      assertThrows(
          IOException.class,
          () -> checkpoint.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL));
      assertThrows(IllegalStateException.class, checkpoint::ordinaryProfile);
      assertEquals(1, reads.get());
    }
  }
}
