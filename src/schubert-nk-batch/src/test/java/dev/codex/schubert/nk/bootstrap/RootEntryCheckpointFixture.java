package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.List;

/**
 * Same-package data-provider fixture only: no native export, agent attach, OS admission or CRC
 * credit.
 */
public final class RootEntryCheckpointFixture {
  private RootEntryCheckpointFixture() {}

  public static FixedNativeCoverageCheckpoint create(
      ServiceConfigFiles.Service service, List<String> events, IOException failure) {
    String invocation = "1234567890abcdef1234567890abcdef";
    String session = service.name() + "-" + invocation + "-root";
    String option =
        "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar="
            + "output=none,append=false,dumponexit=false,sessionid="
            + session;
    var profile =
        FixedNativeCoverageProfile.parse(
                service, FixedNativeCoverageProfile.Phase.ROOT, invocation, List.of(option))
            .orElseThrow();
    return new FixedNativeCoverageCheckpoint(
        profile,
        new FixedNativeCoverageCheckpoint.Agent() {
          public String version() {
            return "0.8.15.202606040825";
          }

          public String session() {
            return session;
          }

          public byte[] executionDataWithoutReset() {
            return new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7};
          }
        },
        (name, bytes) -> {
          assertEquals("1234567890abcdef1234567890abcdef.terminal.exec", name);
          assertArrayEquals(new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7}, bytes);
          events.add("terminal");
          if (failure != null) throw failure;
        });
  }
}
