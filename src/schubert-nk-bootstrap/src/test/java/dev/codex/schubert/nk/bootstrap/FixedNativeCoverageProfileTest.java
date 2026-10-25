package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** Independent literal option/role/phase/invocation matrix; no production-generated expected. */
final class FixedNativeCoverageProfileTest {
  private static final String INV = "1234567890abcdef1234567890abcdef";
  private static final String PREFIX =
      "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid=";

  @Test
  void nc193001DefaultAndUnrelatedHostAgentDoNotActivateOrReadInvocation() {
    for (var service : ServiceConfigFiles.Service.values())
      for (var phase : FixedNativeCoverageProfile.Phase.values()) {
        assertTrue(FixedNativeCoverageProfile.parse(service, phase, null, List.of()).isEmpty());
        assertTrue(
            FixedNativeCoverageProfile.parse(
                    service, phase, "invalid", List.of("-Xmx512m", "-javaagent:/host/jacoco.jar"))
                .isEmpty());
      }
  }

  @Test
  void nc193002FourLiteralProfilesAndRootToOrdinaryPreserveSameRoleAndInvocation() {
    var services = List.of(ServiceConfigFiles.Service.API, ServiceConfigFiles.Service.WEB);
    var labels = List.of("API", "WEB");
    var phases =
        List.of(FixedNativeCoverageProfile.Phase.ROOT, FixedNativeCoverageProfile.Phase.ORDINARY);
    var suffixes = List.of("root", "ordinary");
    for (int s = 0; s < 2; s++)
      for (int p = 0; p < 2; p++) {
        String expected = PREFIX + labels.get(s) + "-" + INV + "-" + suffixes.get(p);
        var actual =
            FixedNativeCoverageProfile.parse(services.get(s), phases.get(p), INV, List.of(expected))
                .orElseThrow();
        assertEquals(expected, actual.argument());
        assertEquals(labels.get(s) + "-" + INV + "-" + suffixes.get(p), actual.sessionId());
        assertEquals(services.get(s), actual.service());
        assertEquals(phases.get(p), actual.phase());
        assertEquals(INV, actual.invocation());
        var ordinary = actual.forOrdinary();
        assertEquals(PREFIX + labels.get(s) + "-" + INV + "-ordinary", ordinary.argument());
        assertEquals(services.get(s), ordinary.service());
        assertEquals(FixedNativeCoverageProfile.Phase.ORDINARY, ordinary.phase());
        assertEquals(INV, ordinary.invocation());
      }
  }

  @Test
  void nc193003MissingNullCollectionElementsAndUnknownInvocationAreRejectedWithoutNpe() {
    String option = PREFIX + "API-" + INV + "-root";
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FixedNativeCoverageProfile.parse(
                null, FixedNativeCoverageProfile.Phase.ROOT, INV, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FixedNativeCoverageProfile.parse(ServiceConfigFiles.Service.API, null, INV, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FixedNativeCoverageProfile.parse(
                ServiceConfigFiles.Service.API, FixedNativeCoverageProfile.Phase.ROOT, INV, null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FixedNativeCoverageProfile.parse(
                ServiceConfigFiles.Service.API,
                FixedNativeCoverageProfile.Phase.ROOT,
                INV,
                Arrays.asList("-Xmx512m", null)));
    for (String invalid :
        Arrays.asList(
            null, "", "0".repeat(32), "F".repeat(32), "1".repeat(31), "1".repeat(33), INV + "\n"))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              FixedNativeCoverageProfile.parse(
                  ServiceConfigFiles.Service.API,
                  FixedNativeCoverageProfile.Phase.ROOT,
                  invalid,
                  List.of(option)));
  }

  @Test
  void nc193004ReservedUnknownDuplicateRolePhasePathAndOptionExpansionAreRejected() {
    String valid = PREFIX + "API-" + INV + "-root";
    for (String wrong :
        List.of(
            valid.replace("API-", "WEB-"),
            valid.replace("-root", "-ordinary"),
            valid.replace(INV, "a".repeat(32)),
            valid.replace("jacoco-agent.jar", "other.jar"),
            valid.replace("output=none", "output=file"),
            valid.replace("append=false", "append=true"),
            valid.replace("dumponexit=false", "dumponexit=true"),
            valid + ",jmx=true",
            valid + " ",
            "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar"))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              FixedNativeCoverageProfile.parse(
                  ServiceConfigFiles.Service.API,
                  FixedNativeCoverageProfile.Phase.ROOT,
                  INV,
                  List.of(wrong)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FixedNativeCoverageProfile.parse(
                ServiceConfigFiles.Service.API,
                FixedNativeCoverageProfile.Phase.ROOT,
                INV,
                List.of(valid, valid)));
  }

  @Test
  void nc193005AgentPinAndImmutableOptionsAreIndependentFixedConstants() {
    assertEquals("/opt/pgpt-tools-pg390/jacoco-agent.jar", FixedNativeCoverageProfile.AGENT_PATH);
    assertEquals(
        "fb5b0036a0899ea97edfa0fc2c7985b55f3f7c5695028163e5e60d4f3cf6075d",
        FixedNativeCoverageProfile.AGENT_SHA256);
    var inputs = new java.util.ArrayList<String>();
    inputs.add(PREFIX + "API-" + INV + "-root");
    var actual =
        FixedNativeCoverageProfile.parse(
                ServiceConfigFiles.Service.API, FixedNativeCoverageProfile.Phase.ROOT, INV, inputs)
            .orElseThrow();
    inputs.clear();
    assertEquals(PREFIX + "API-" + INV + "-root", actual.argument());
  }
}
