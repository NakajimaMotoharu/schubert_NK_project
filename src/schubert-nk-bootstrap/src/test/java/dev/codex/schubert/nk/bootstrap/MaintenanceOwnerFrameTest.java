package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SS343§6.17 literal vectors, never expected bytes made by Production encode. SSC119/COWNER. */
class MaintenanceOwnerFrameTest {
  private static final String FIXTURE_2026_09_27T15_00_00Z_23AE9E87 = "2026-09-27T15:00:00Z";
  private static final String FIXTURE_00000000_0000_0000_0000_000000000000_36B66471 =
      "00000000-0000-0000-0000-000000000000";
  private static final String GOLDEN =
      "NKMAINTOWNER1\nboot=11111111-1111-4111-8111-111111111111\n"
          + "run=22222222-2222-4222-8222-222222222222\n"
          + "activation=33333333-3333-4333-8333-333333333333\n"
          + "cutoff=2026-09-27T15:00:00Z\nepoch=44444444-4444-4444-8444-444444444444\n"
          + "morning_invocation=55555555555555555555555555555555\nmorning_pid=42\n"
          + "morning_start_ticks=12345\ncleanup_invocation=-\ncleanup_pid=-\n"
          + "cleanup_start_ticks=-\ndeadline_nanos=1800000000007\n";

  @Test
  void literalParentAndSingleInspectorTransitionAreIndependentClaims() {
    var value = consume(GOLDEN);
    assertArrayEquals(bytes(GOLDEN), value.encode());
    assertEquals(1_800_000_000_007L, value.deadlineNanos());
    assertEquals(42, value.morning().pid());
    assertEquals(12345, value.morning().startTicks());
    assertTrue(value.cleanup().isEmpty());
    var child = new MaintenanceOwnerFrame.Parent("6".repeat(32), 43, 23456);
    String expected =
        GOLDEN
            .replace("cleanup_invocation=-", "cleanup_invocation=66666666666666666666666666666666")
            .replace("cleanup_pid=-", "cleanup_pid=43")
            .replace("cleanup_start_ticks=-", "cleanup_start_ticks=23456");
    var inspector = value.forInspector(child);
    assertArrayEquals(bytes(expected), inspector.encode());
    assertEquals(inspector, consume(expected));
    assertThrows(IllegalArgumentException.class, () -> inspector.forInspector(child));
    assertThrows(NullPointerException.class, () -> value.forInspector(null));
    assertEquals("MaintenanceOwnerFrame[claims=<redacted>]", inspector.toString());
    assertEquals("MaintenanceParent[identity=<redacted>]", child.toString());
  }

  @Test
  void malformedAndCrossParentClaimsConsumeEveryInput() {
    for (String input :
        new String[] {
          "",
          GOLDEN + "unknown=1\n",
          GOLDEN + "x",
          GOLDEN.replace("NKMAINTOWNER1", "NKMAINTOWNER\u007f"),
          GOLDEN.replace("NKMAINTOWNER1", "NKMAINTOWNER2"),
          GOLDEN.replace("\n", "\r\n"),
          GOLDEN.substring(0, GOLDEN.length() - 1),
          GOLDEN.replace("boot=", "run="),
          GOLDEN.replace("morning_pid=42", "morning_pid=042"),
          GOLDEN.replace("morning_pid=42", "morning_pid=1"),
          GOLDEN.replace("morning_pid=42", "morning_pid=2147483648"),
          GOLDEN.replace("morning_start_ticks=12345", "morning_start_ticks=0"),
          GOLDEN.replace("morning_start_ticks=12345", "morning_start_ticks=9223372036854775808"),
          GOLDEN.replace("deadline_nanos=1800000000007", "deadline_nanos=0"),
          GOLDEN.replace("deadline_nanos=1800000000007", "deadline_nanos=-1"),
          GOLDEN.replace("cleanup_pid=-", "cleanup_pid=43"),
          GOLDEN.replace("cleanup_start_ticks=-", "cleanup_start_ticks=1"),
          GOLDEN.replace(
              "cleanup_invocation=-", "cleanup_invocation=66666666666666666666666666666666"),
          GOLDEN.replace("55555555555555555555555555555555", "0".repeat(32)),
          GOLDEN.replace("55555555555555555555555555555555", "A".repeat(32)),
          GOLDEN.replace(FIXTURE_2026_09_27T15_00_00Z_23AE9E87, "2026-09-27T15:00:00.0000001Z"),
          GOLDEN.replace(FIXTURE_2026_09_27T15_00_00Z_23AE9E87, "bad"),
          GOLDEN.replace(FIXTURE_2026_09_27T15_00_00Z_23AE9E87, "0000-01-01T00:00:00Z"),
          GOLDEN.replace(FIXTURE_2026_09_27T15_00_00Z_23AE9E87, "+10000-01-01T00:00:00Z"),
          GOLDEN.replace(
              "33333333-3333-4333-8333-333333333333", "22222222-2222-4222-8222-222222222222"),
          GOLDEN.replace(
              "11111111-1111-4111-8111-111111111111",
              FIXTURE_00000000_0000_0000_0000_000000000000_36B66471),
          GOLDEN.replace(
              "22222222-2222-4222-8222-222222222222",
              FIXTURE_00000000_0000_0000_0000_000000000000_36B66471),
          GOLDEN.replace(
              "33333333-3333-4333-8333-333333333333",
              FIXTURE_00000000_0000_0000_0000_000000000000_36B66471),
          GOLDEN.replace(
              "44444444-4444-4444-8444-444444444444",
              FIXTURE_00000000_0000_0000_0000_000000000000_36B66471),
          GOLDEN.replace("44444444-4444-4444-8444-444444444444", "wrong"),
          GOLDEN.replace("epoch=", "épöçh="),
          "x".repeat(1025)
        }) {
      byte[] owned = bytes(input);
      assertThrows(IllegalArgumentException.class, () -> MaintenanceOwnerFrame.consume(owned));
      assertArrayEquals(new byte[owned.length], owned);
    }
    var value = consume(GOLDEN);
    assertThrows(IllegalArgumentException.class, () -> value.forInspector(value.morning()));
    assertThrows(
        IllegalArgumentException.class,
        () -> value.forInspector(new MaintenanceOwnerFrame.Parent("5".repeat(32), 43, 8)));
    assertThrows(
        IllegalArgumentException.class,
        () -> value.forInspector(new MaintenanceOwnerFrame.Parent("6".repeat(32), 42, 8)));
    assertThrows(NullPointerException.class, () -> MaintenanceOwnerFrame.consume(null));
    assertThrows(NullPointerException.class, () -> new MaintenanceOwnerFrame.Parent(null, 42, 8));
    assertThrows(
        IllegalArgumentException.class, () -> new MaintenanceOwnerFrame.Parent("bad", 42, 8));
  }

  @Test
  void constructorNullsAreContractFailuresNotDefaultOwners() {
    var value = consume(GOLDEN);
    for (int index = 0; index < 7; index++) {
      int missing = index;
      assertThrows(
          NullPointerException.class,
          () ->
              new MaintenanceOwnerFrame(
                  missing == 0 ? null : value.boot(), missing == 1 ? null : value.run(),
                  missing == 2 ? null : value.activation(), missing == 3 ? null : value.cutoff(),
                  missing == 4 ? null : value.epoch(), missing == 5 ? null : value.morning(),
                  missing == 6 ? null : Optional.empty(), value.deadlineNanos()));
    }
  }

  @Test
  void guardTimeoutUsesDownwardIntegerSecondsAndNeverNormalizesFailure() throws Exception {
    MaintenanceOwnerFrame.Guard enough = () -> 9_999_999_999L;
    enough.check();
    assertEquals(5, enough.queryTimeoutSeconds());
    assertEquals(4, ((MaintenanceOwnerFrame.Guard) () -> 4_999_999_999L).queryTimeoutSeconds());
    assertEquals(1, ((MaintenanceOwnerFrame.Guard) () -> 1_000_000_000L).queryTimeoutSeconds());
    for (long invalid : new long[] {0, -1}) {
      var guard = (MaintenanceOwnerFrame.Guard) () -> invalid;
      assertThrows(java.io.IOException.class, guard::check);
      assertThrows(java.io.IOException.class, guard::queryTimeoutSeconds);
    }
    assertThrows(
        java.io.IOException.class,
        ((MaintenanceOwnerFrame.Guard) () -> 999_999_999L)::queryTimeoutSeconds);
    var expired =
        new MaintenanceOwnerFrame(
                consume(GOLDEN).boot(),
                consume(GOLDEN).run(),
                consume(GOLDEN).activation(),
                consume(GOLDEN).cutoff(),
                consume(GOLDEN).epoch(),
                consume(GOLDEN).morning(),
                Optional.empty(),
                1)
            .parentsGuard();
    assertThrows(java.io.IOException.class, expired::check);
    Thread.currentThread().interrupt();
    try {
      assertThrows(java.io.IOException.class, expired::check);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }

  private static MaintenanceOwnerFrame consume(String literal) {
    byte[] owned = bytes(literal);
    var result = MaintenanceOwnerFrame.consume(owned);
    assertArrayEquals(new byte[owned.length], owned);
    return result;
  }

  private static byte[] bytes(String literal) {
    return literal.getBytes(StandardCharsets.UTF_8);
  }
}
