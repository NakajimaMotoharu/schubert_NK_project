package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion.Outcome;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-BAT-MREC-RAW001..004; SS343 6.13/PG-D-1170, pure values with no runtime authority. */
final class MaintenanceRecordsRawContractTest {
  private static final String RECORD_HEAD =
      "NKDONE1\n"
          + "12345678-9abc-def0-8123-456789abcdef\n"
          + "2026-09-12T04:05:06.123456Z\n"
          + "fedcba98-7654-3210-8fed-cba987654321\n"
          + "2026-09-12T05:06:07.234567Z\n";

  @Test
  void raw001PrivateStaticCodecRejectsInstantiationAndRestoresAccessFlag() throws Exception {
    var constructor = MaintenanceRecords.class.getDeclaredConstructor();
    assertTrue(Modifier.isPrivate(constructor.getModifiers()));
    assertFalse(constructor.canAccess(null));
    try {
      assertTrue(constructor.trySetAccessible());
      var wrapped = assertThrows(InvocationTargetException.class, constructor::newInstance);
      var rejected = assertInstanceOf(AssertionError.class, wrapped.getCause());
      assertEquals("MaintenanceRecords is a static codec", rejected.getMessage());
      assertNull(rejected.getCause());
      assertEquals(0, rejected.getSuppressed().length);
    } finally {
      constructor.setAccessible(false);
    }
    assertFalse(constructor.canAccess(null));
  }

  @Test
  void raw002UnknownStatusHashAliasesRemainInvalidAndInputIsBorrowed() {
    // Independent Java String polynomial: 1*31+17=48; 48*31+79=1567.
    // These collide with the legal status strings 0 and 10, respectively, without equalling them.
    String[] aliases = {"\001\021", "0O"};
    int[] fixedHashes = {48, 1567};
    for (int i = 0; i < aliases.length; i++) {
      assertEquals(fixedHashes[i], aliases[i].hashCode());
      byte[] input = (RECORD_HEAD + aliases[i] + "\n").getBytes(StandardCharsets.US_ASCII);
      assertEquals(141, input.length);
      byte[] original = input.clone();
      var rejected =
          assertThrows(IOException.class, () -> MaintenanceRecords.readCompletion(input));
      assertEquals("maintenance record is invalid", rejected.getMessage());
      assertNull(rejected.getCause());
      assertEquals(0, rejected.getSuppressed().length);
      assertArrayEquals(original, input);
    }
  }

  @Test
  void raw003OutcomeOrderExitCodesAndValuesArrayOwnershipAreFixed() {
    Outcome[] first = Outcome.values();
    Outcome[] second = Outcome.values();
    assertArrayEquals(new Outcome[] {Outcome.SUCCESS, Outcome.WARNING}, first);
    assertNotSame(first, second);
    first[0] = Outcome.WARNING;
    assertSame(Outcome.SUCCESS, second[0]);
    assertArrayEquals(new Outcome[] {Outcome.SUCCESS, Outcome.WARNING}, Outcome.values());
    assertEquals(0, Outcome.SUCCESS.exitCode());
    assertEquals(10, Outcome.WARNING.exitCode());
  }

  @Test
  void raw004OutcomePublicNamesAreExactAndUnknownOrMissingNamesAreRejected() {
    assertSame(Outcome.SUCCESS, Outcome.valueOf("SUCCESS"));
    assertSame(Outcome.WARNING, Outcome.valueOf("WARNING"));
    assertThrows(NullPointerException.class, () -> Outcome.valueOf(null));
    for (String name : List.of("", "success", "WARNING ", " WARNING", "0", "10", "UNKNOWN"))
      assertThrows(IllegalArgumentException.class, () -> Outcome.valueOf(name));
  }
}
