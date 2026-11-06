package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-STATE-BYTE001..006; OPS009/UI251/SS341343. No command/state acquisition. */
final class UnitStateParserBytePortTest {
  private static final String API_ID = "Id=schubert-nk-api.service";
  private static final String WEB_ID = "Id=schubert-nk-web.service";
  private static final String LOAD = "LoadState=loaded";
  private static final String ACTIVE = "ActiveState=inactive";
  private static final String SUB = "SubState=dead";
  private static final String JOB = "Job=";
  private static final String MAIN = "MainPID=0";
  private static final String CONTROL = "ControlPID=0";
  private static final String DIAGNOSTIC = "application stop check failed";

  private static List<String> lines(boolean web) {
    return new ArrayList<>(List.of(web ? WEB_ID : API_ID, LOAD, ACTIVE, SUB, JOB, MAIN, CONTROL));
  }

  private static byte[] bytes(List<String> lines) {
    return (String.join("\n", lines) + "\n").getBytes(StandardCharsets.US_ASCII);
  }

  private static void rejected(byte[] input, StopGateFailure reason) {
    var original = input.clone();
    var failure =
        assertThrows(
            StopGateException.class,
            () -> UnitStateParser.requireStopped(ApplicationUnit.API, input));
    assertEquals(reason, failure.reason());
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertArrayEquals(original, input);
  }

  @Test
  void exactSevenFieldsForBothUnitsInRotatedAndReversedOrders() {
    for (boolean web : List.of(false, true)) {
      var values = lines(web);
      for (int rotation = 0; rotation < 7; rotation++) {
        Collections.rotate(values, 1);
        var input = bytes(values);
        var original = input.clone();
        UnitStateParser.requireStopped(web ? ApplicationUnit.WEB : ApplicationUnit.API, input);
        assertArrayEquals(original, input);
        Collections.reverse(values);
        UnitStateParser.requireStopped(
            web ? ApplicationUnit.WEB : ApplicationUnit.API, bytes(values));
        Collections.reverse(values);
      }
    }
  }

  @Test
  void byteLengthAsciiAndNullBoundariesRejectWithoutChangingInput() {
    assertThrows(
        NullPointerException.class,
        () -> UnitStateParser.requireStopped(null, bytes(lines(false))));
    assertThrows(
        NullPointerException.class,
        () -> UnitStateParser.requireStopped(ApplicationUnit.API, null));
    rejected(new byte[0], StopGateFailure.MALFORMED_STATE);
    var maximum = new byte[1024];
    java.util.Arrays.fill(maximum, (byte) ' ');
    rejected(maximum, StopGateFailure.MALFORMED_STATE);
    rejected(new byte[1025], StopGateFailure.MALFORMED_STATE);
    for (int illegal : new int[] {0, 13, 31, 127, 128, 255}) {
      var input = bytes(lines(false));
      input[3] = (byte) illegal;
      rejected(input, StopGateFailure.MALFORMED_STATE);
    }
    for (int legalButWrong : new int[] {32, 126}) {
      var input = bytes(lines(false));
      input[3] = (byte) legalButWrong;
      rejected(input, StopGateFailure.MALFORMED_STATE);
    }
  }

  @Test
  void framingEqualsUniquenessKeysAndIdentityAreStrict() {
    var normal = bytes(lines(false));
    rejected(java.util.Arrays.copyOf(normal, normal.length - 1), StopGateFailure.MALFORMED_STATE);
    var missing = lines(false);
    missing.remove(6);
    rejected(bytes(missing), StopGateFailure.MALFORMED_STATE);
    var extra = lines(false);
    extra.add("Extra=x");
    rejected(bytes(extra), StopGateFailure.MALFORMED_STATE);
    for (String bad :
        List.of("NoEquals", "=value", "Id=two=equals", LOAD, "Unknown=value", WEB_ID)) {
      var values = lines(false);
      values.set(0, bad);
      rejected(bytes(values), StopGateFailure.MALFORMED_STATE);
    }
    var duplicate = lines(false);
    duplicate.set(6, MAIN);
    rejected(bytes(duplicate), StopGateFailure.MALFORMED_STATE);
  }

  @Test
  void eachNonStoppedValueIsRejectedWithFixedReason() {
    var bad =
        List.of(
            "LoadState=not-found",
            "ActiveState=active",
            "SubState=running",
            "Job=9/start",
            "MainPID=1",
            "ControlPID=1");
    for (int index = 0; index < bad.size(); index++) {
      var values = lines(false);
      values.set(index + 1, bad.get(index));
      rejected(bytes(values), StopGateFailure.NOT_STOPPED);
    }
    var values = lines(false);
    values.set(1, "LoadState=masked");
    rejected(bytes(values), StopGateFailure.NOT_STOPPED);
  }

  @Test
  void failedProjectionDoesNotPoisonSubsequentIndependentBytes() {
    var wrong = lines(false);
    wrong.set(4, "Job=PUBLIC-DISPLAY-MARKER");
    rejected(bytes(wrong), StopGateFailure.NOT_STOPPED);
    var accepted = bytes(lines(false));
    var original = accepted.clone();
    UnitStateParser.requireStopped(ApplicationUnit.API, accepted);
    UnitStateParser.requireStopped(ApplicationUnit.API, accepted);
    assertArrayEquals(original, accepted);
  }

  @Test
  void independentMemoryProjectionsDoNotShareIntermediateState() throws Exception {
    var results = new ArrayList<Future<String>>();
    try (var executor = Executors.newFixedThreadPool(2)) {
      for (int index = 0; index < 32; index++) {
        boolean web = index % 2 == 0;
        results.add(
            executor.submit(
                () -> {
                  var input = bytes(lines(web));
                  UnitStateParser.requireStopped(
                      web ? ApplicationUnit.WEB : ApplicationUnit.API, input);
                  return new String(input, StandardCharsets.US_ASCII).split("\n")[0];
                }));
      }
      for (int index = 0; index < 32; index++)
        assertEquals(
            index % 2 == 0 ? WEB_ID : API_ID, results.get(index).get(10, TimeUnit.SECONDS));
    }
  }
}
