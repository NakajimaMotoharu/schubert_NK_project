package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-MSTOP-OBS-001 / SS343 SSC126; manual observation fields, never stop authority. */
final class MaintenanceObservedValuesContractTest {
  @Test
  void observed001FixedPropertyOrderPreservesColdAndShuffledLiveLiterals() {
    String cold =
        "Id=caddy.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\n"
            + "Job=\nMainPID=0\nControlPID=0\nSlice=system.slice\nDelegate=no\n"
            + "ControlGroup=\nInvocationID=\nStateChangeTimestampMonotonic=0\n";
    List<String> expectedCold =
        List.of("caddy.service", "loaded", "inactive", "dead", "", "0", "0",
            "system.slice", "no", "", "", "0");
    assertEquals(expectedCold,
        MaintenanceStopSnapshot.parse(MaintenanceUnit.CADDY,
            cold.getBytes(StandardCharsets.US_ASCII)).observedValues());

    String shuffled =
        "StateChangeTimestampMonotonic=18446744073709551615\n"
            + "InvocationID=0123456789abcdef0123456789abcdef\n"
            + "ControlGroup=/system.slice/caddy.service\nDelegate=no\nSlice=system.slice\n"
            + "ControlPID=7\nMainPID=23\nJob=17\nSubState=running\nActiveState=active\n"
            + "LoadState=loaded\nId=caddy.service\n";
    List<String> expectedLive =
        List.of("caddy.service", "loaded", "active", "running", "17", "23", "7",
            "system.slice", "no", "/system.slice/caddy.service",
            "0123456789abcdef0123456789abcdef", "18446744073709551615");
    assertEquals(expectedLive,
        MaintenanceStopSnapshot.parse(MaintenanceUnit.CADDY,
            shuffled.getBytes(StandardCharsets.US_ASCII)).observedValues());
  }
}
