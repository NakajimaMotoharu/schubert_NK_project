package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import org.junit.jupiter.api.Test;

/** SS343/SSC164: missing root UID port cannot admit a different service's Root. */
final class UnsupportedRootIdentityTest {
  @Test
  void rootIdentityPort001AbsentUidProviderRejectsOtherwiseValidSamePeerService() throws Exception {
    var fixture = new RootStartupContextTest.LaunchFixture();
    // Delegate the independent literal proc/Unit fixture, but omit UID proof.
    var context =
        new RootStartupContext(
            new RootStartupContext.Io() {
              public long effectiveUid() {
                return fixture.effectiveUid();
              }

              public long pid() {
                return fixture.pid();
              }

              public String procFilesystem() throws IOException {
                return fixture.procFilesystem();
              }

              public String initExecutable() throws IOException {
                return fixture.initExecutable();
              }

              public byte[] boot() throws IOException {
                return fixture.boot();
              }

              public byte[] stat(long pid) throws IOException {
                return fixture.stat(pid);
              }

              public byte[] cgroup(long pid) throws IOException {
                return fixture.cgroup(pid);
              }

              public byte[] unit(RootStartupContext.Service service) throws IOException {
                return fixture.unit(service);
              }

              public String invocation() {
                return fixture.invocation();
              }
            });
    var morning = context.capture(RootStartupContext.Service.MORNING);
    var failure =
        assertThrows(
            IOException.class,
            () -> context.captureServiceRoot(morning, RootStartupContext.Service.API));
    assertEquals("startup context unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(1, fixture.targetReads, "UID refusal precedes successful second Unit proof");
    assertEquals(42, morning.pid(), "the authenticating Morning fixture is unchanged");
  }
}
