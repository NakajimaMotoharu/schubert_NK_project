package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;
import org.junit.jupiter.api.Test;

/** PT-OPS-API-HEALTH001..003: literal truth/ordered sampling oracle, not native admission. */
final class ApiReadinessPredicateTest {
  private static final String CONSUMER_GROUPS_STEP = "groups";
  private static final String STOP_STEP = "stop";
  private static final String OUTBOX_STEP = "outbox";
  private static final String CONSUMERS_STEP = "consumers";

  @Test
  void health001LiteralTruthTablesAndShortCircuitOrder() {
    // Last value is the independently enumerated expected result, never a production calculation.
    boolean[][] management = {
      {false, false, false, false}, {false, false, true, false},
      {false, true, false, false}, {false, true, true, false},
      {true, false, false, false}, {true, false, true, true},
      {true, true, false, false}, {true, true, true, false}
    };
    List<List<String>> order =
        List.of(
            List.of(CONSUMER_GROUPS_STEP),
            List.of(CONSUMER_GROUPS_STEP),
            List.of(CONSUMER_GROUPS_STEP),
            List.of(CONSUMER_GROUPS_STEP),
            List.of(CONSUMER_GROUPS_STEP, STOP_STEP, OUTBOX_STEP),
            List.of(CONSUMER_GROUPS_STEP, STOP_STEP, OUTBOX_STEP),
            List.of(CONSUMER_GROUPS_STEP, STOP_STEP),
            List.of(CONSUMER_GROUPS_STEP, STOP_STEP));
    for (int i = 0; i < management.length; i++) {
      boolean[] row = management[i];
      var calls = new ArrayList<String>();
      var predicate =
          ApiProcessMain.applicationReadiness(
              sample(calls, CONSUMER_GROUPS_STEP, row[0]),
              sample(calls, STOP_STEP, row[1]),
              sample(calls, OUTBOX_STEP, row[2]));
      assertEquals(List.of(), calls, "factory performs no sampling");
      assertEquals(row[3], predicate.getAsBoolean());
      assertEquals(order.get(i), calls);
    }
    boolean[][] runtime = {
      {false, false, false}, {false, true, false}, {true, false, false}, {true, true, true}
    };
    List<List<String>> runtimeOrder =
        List.of(
            List.of(CONSUMERS_STEP),
            List.of(CONSUMERS_STEP),
            List.of(CONSUMERS_STEP, OUTBOX_STEP),
            List.of(CONSUMERS_STEP, OUTBOX_STEP));
    for (int i = 0; i < runtime.length; i++) {
      boolean[] row = runtime[i];
      var calls = new ArrayList<String>();
      var predicate =
          ApiProcessMain.runtimeReadiness(
              sample(calls, CONSUMERS_STEP, row[0]), sample(calls, OUTBOX_STEP, row[1]));
      assertEquals(List.of(), calls);
      assertEquals(row[2], predicate.getAsBoolean());
      assertEquals(runtimeOrder.get(i), calls);
    }
  }

  @Test
  void health002EveryCallReadsCurrentStateWithoutLatchingSuccess() {
    var groups = new AtomicBoolean();
    var stopping = new AtomicBoolean();
    var outbox = new AtomicBoolean(true);
    var management = ApiProcessMain.applicationReadiness(groups::get, stopping::get, outbox::get);
    var runtime = ApiProcessMain.runtimeReadiness(groups::get, outbox::get);
    assertFalse(management.getAsBoolean());
    assertFalse(runtime.getAsBoolean());
    groups.set(true);
    assertTrue(management.getAsBoolean());
    assertTrue(runtime.getAsBoolean());
    outbox.set(false);
    assertFalse(management.getAsBoolean());
    assertFalse(runtime.getAsBoolean());
    outbox.set(true);
    stopping.set(true);
    assertFalse(management.getAsBoolean());
    assertTrue(
        runtime.getAsBoolean(), "lifetime independently owns stop; predicate does not invent it");
    groups.set(false);
    assertFalse(runtime.getAsBoolean());
  }

  @Test
  void health003NullAndExactFailureAreNeverConvertedToHealth() {
    BooleanSupplier yes = () -> true;
    BooleanSupplier no = () -> false;
    assertThrows(
        NullPointerException.class, () -> ApiProcessMain.applicationReadiness(null, no, yes));
    assertThrows(
        NullPointerException.class, () -> ApiProcessMain.applicationReadiness(yes, null, yes));
    assertThrows(
        NullPointerException.class, () -> ApiProcessMain.applicationReadiness(yes, no, null));
    assertThrows(NullPointerException.class, () -> ApiProcessMain.runtimeReadiness(null, yes));
    assertThrows(NullPointerException.class, () -> ApiProcessMain.runtimeReadiness(yes, null));
    for (Error failure :
        List.of(new AssertionError("synthetic failure"), new LinkageError("synthetic failure"))) {
      BooleanSupplier broken =
          () -> {
            throw failure;
          };
      BooleanSupplier forbidden =
          () -> {
            throw new AssertionError("later supplier must not execute");
          };
      assertSame(
          failure,
          assertThrows(
              Error.class,
              () ->
                  ApiProcessMain.applicationReadiness(broken, forbidden, forbidden)
                      .getAsBoolean()));
      assertSame(
          failure,
          assertThrows(
              Error.class,
              () -> ApiProcessMain.applicationReadiness(yes, broken, forbidden).getAsBoolean()));
      assertSame(
          failure,
          assertThrows(
              Error.class,
              () -> ApiProcessMain.applicationReadiness(yes, no, broken).getAsBoolean()));
      assertSame(
          failure,
          assertThrows(
              Error.class,
              () -> ApiProcessMain.runtimeReadiness(broken, forbidden).getAsBoolean()));
      assertSame(
          failure,
          assertThrows(
              Error.class, () -> ApiProcessMain.runtimeReadiness(yes, broken).getAsBoolean()));
    }
    var failure = new IllegalStateException("synthetic unavailable");
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class,
            () ->
                ApiProcessMain.runtimeReadiness(
                        yes,
                        () -> {
                          throw failure;
                        })
                    .getAsBoolean()));
  }

  private static BooleanSupplier sample(List<String> calls, String name, boolean value) {
    return () -> {
      calls.add(name);
      return value;
    };
  }
}
