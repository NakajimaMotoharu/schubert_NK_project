package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.platform.StopGateException;
import dev.codex.schubert.nk.batch.platform.StopGateFailure;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.lang.reflect.Modifier;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/PG339; PT-OPS-MMAIN001-005. */
final class MorningProcessMainTest {
  @Test
  void mmain001AdmissionSuccessStillCannotClaimMorningSuccess() {
    var calls = new AtomicInteger();
    assertEquals(30, MorningProcessMain.run(new String[0], calls::incrementAndGet));
    assertEquals(1, calls.get());
  }

  @Test
  void mmain002ArgumentsCannotSelectRunOrOverrideGate() {
    var calls = new AtomicInteger();
    assertEquals(
        70, MorningProcessMain.run(new String[] {"--run-id=ignored"}, calls::incrementAndGet));
    assertEquals(70, MorningProcessMain.run(new String[] {""}, calls::incrementAndGet));
    assertEquals(0, calls.get());
  }

  @Test
  void mmain003KnownIoAndStopFailureAreFixedNonSuccess() throws Exception {
    assertEquals(
        30,
        MorningProcessMain.run(
            new String[0],
            () -> {
              throw new IOException("PRIVATE");
            }));
    // A fixed known stop exception is already sanitized by the stop-policy boundary.
    Constructor<StopGateException> factory =
        StopGateException.class.getDeclaredConstructor(StopGateFailure.class);
    factory.setAccessible(true);
    StopGateException known = factory.newInstance(StopGateFailure.COMMAND_FAILURE);
    assertEquals(
        30,
        MorningProcessMain.run(
            new String[0],
            () -> {
              throw known;
            }));
  }

  @Test
  void mmain004UnknownIdentityAndNullContractAreNotNormalized() {
    var unknown = new IllegalStateException("programming failure");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningProcessMain.run(
                    new String[0],
                    () -> {
                      throw unknown;
                    })));
    assertThrows(NullPointerException.class, () -> MorningProcessMain.run(null, () -> {}));
    assertThrows(NullPointerException.class, () -> MorningProcessMain.run(new String[0], null));
  }

  @Test
  void mmain005NoPublicConstructorForAlternativeLauncher() throws Exception {
    Constructor<MorningProcessMain> constructor = MorningProcessMain.class.getDeclaredConstructor();
    assertTrue(Modifier.isPrivate(constructor.getModifiers()));
    assertTrue(
        Modifier.isPublic(
            MorningProcessMain.class.getMethod("main", String[].class).getModifiers()));
  }
}
