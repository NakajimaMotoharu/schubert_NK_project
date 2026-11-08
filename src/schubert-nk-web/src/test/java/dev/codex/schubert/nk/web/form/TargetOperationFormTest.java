package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** UI236 independent ID12+UUID36 golden; UI224/SS313314; PG-D368/PT-TARGET001..008. */
class TargetOperationFormTest {
  private static final String CANCEL_OPERATION = "CANCEL";
  private static final String OPERATION_FIELD = "operation";
  private static final String CONFIRM_FIELD = "confirm";
  private static final String OPERATION_TOKEN_FIELD = "operation_token";
  private static final String DELETE_OPERATION = "DELETE";
  private static final String TOKEN = "12345678-1234-4234-8234-123456789abc";

  private record Bound(
      Object owner,
      BooleanSupplier valid,
      Supplier<Map<String, String>> issues,
      Supplier<Map<String, Object>> values,
      Supplier<PayloadData> request) {}

  private static Bound bind(String operation, long id, Map<String, List<String>> fields) {
    if (operation.equals(CANCEL_OPERATION)) {
      var form = CancelForm.bind(id, fields);
      return new Bound(form, form::isValid, form::getIssues, form::displayValues, form::toRequest);
    }
    var form = QuestionDeleteForm.bind(id, fields);
    return new Bound(form, form::isValid, form::getIssues, form::displayValues, form::toRequest);
  }

  private static Map<String, List<String>> fields(String operation, String id) {
    var result = new LinkedHashMap<String, List<String>>();
    result.put(OPERATION_FIELD, List.of(operation));
    result.put("id", List.of(id));
    result.put(CONFIRM_FIELD, List.of("true"));
    result.put(OPERATION_TOKEN_FIELD, List.of(TOKEN));
    return result;
  }

  @Test
  void target001BothIndependentFortyEightByteGolden() {
    for (String operation : List.of(CANCEL_OPERATION, DELETE_OPERATION)) {
      var f = bind(operation, 42, fields(operation, "42"));
      assertTrue(f.valid.getAsBoolean());
      assertTrue(f.issues.get().isEmpty());
      var request = f.request.get();
      var layout = new LayoutId(operation.equals(CANCEL_OPERATION) ? "NTCREQ01" : "QDLREQ01");
      var encoded =
          PayloadCodec.standard()
              .encode(new PayloadValues(layout, request.fields(), List.of()), false);
      assertArrayEquals(
          ("000000000042" + TOKEN).getBytes(StandardCharsets.US_ASCII), encoded.copyData());
      assertEquals(TOKEN, f.values.get().get(OPERATION_TOKEN_FIELD));
      assertEquals(42L, f.values.get().get("id"));
      assertEquals(operation, f.values.get().get(OPERATION_FIELD));
      assertEquals(true, f.values.get().get(CONFIRM_FIELD));
      assertFalse(f.owner.toString().contains(TOKEN));
    }
  }

  @Test
  void target002PositiveN12BoundariesAndCanonicalTargetEquality() {
    for (String operation : List.of(CANCEL_OPERATION, DELETE_OPERATION)) {
      for (String id : List.of("1", "000000000001", "999999999999")) {
        long value = Long.parseLong(id);
        assertTrue(bind(operation, value, fields(operation, id)).valid.getAsBoolean());
      }
      for (String id :
          List.of("", "0", "000", "-1", "1000000000000", "42 ", " 42", "４２", "1.0", "+42", "43")) {
        var f = bind(operation, 42, fields(operation, id));
        assertFalse(f.valid.getAsBoolean());
        assertTrue(f.issues.get().containsKey("id"));
        assertThrows(IllegalStateException.class, f.request::get);
      }
      assertFalse(bind(operation, -1, fields(operation, "1")).valid.getAsBoolean());
      assertFalse(bind(operation, 1000000000000L, fields(operation, "1")).valid.getAsBoolean());
    }
  }

  @Test
  void target003EachRequiredFieldMissingNullEmptyMultipleAndNullElement() {
    for (String operation : List.of(CANCEL_OPERATION, DELETE_OPERATION)) {
      for (String key : List.of(OPERATION_FIELD, "id", CONFIRM_FIELD, OPERATION_TOKEN_FIELD)) {
        for (int variant = 0; variant < 5; variant++) {
          var p = fields(operation, "42");
          switch (variant) {
            case 0 -> p.remove(key);
            case 1 -> p.put(key, null);
            case 2 -> p.put(key, List.of());
            case 3 -> p.put(key, List.of("a", "a"));
            default -> p.put(key, Arrays.asList((String) null));
          }
          var f = bind(operation, 42, p);
          assertFalse(f.valid.getAsBoolean());
          assertTrue(f.issues.get().containsKey(key));
          assertThrows(IllegalStateException.class, f.request::get);
        }
      }
    }
  }

  @Test
  void target004ClosedOperationConfirmationAndCanonicalUuid() {
    for (String operation : List.of(CANCEL_OPERATION, DELETE_OPERATION)) {
      for (String value :
          List.of(
              "",
              "UNKNOWN",
              "cancel",
              DELETE_OPERATION.equals(operation) ? CANCEL_OPERATION : DELETE_OPERATION)) {
        var p = fields(operation, "42");
        p.put(OPERATION_FIELD, List.of(value));
        assertTrue(bind(operation, 42, p).issues.get().containsKey(OPERATION_FIELD));
      }
      for (String value : List.of("", "false", "on", "TRUE", " true")) {
        var p = fields(operation, "42");
        p.put(CONFIRM_FIELD, List.of(value));
        assertTrue(bind(operation, 42, p).issues.get().containsKey(CONFIRM_FIELD));
      }
      for (String value :
          List.of("", "bad", TOKEN.toUpperCase(Locale.ROOT), " " + TOKEN, TOKEN + " ")) {
        var p = fields(operation, "42");
        p.put(OPERATION_TOKEN_FIELD, List.of(value));
        assertTrue(bind(operation, 42, p).issues.get().containsKey(OPERATION_TOKEN_FIELD));
      }
    }
  }

  @Test
  void target005ClosedFieldsAndOnlyCsrfTransportAllowance() {
    for (String operation : List.of(CANCEL_OPERATION, DELETE_OPERATION)) {
      var p = fields(operation, "42");
      p.put("_csrf", List.of("synthetic"));
      assertTrue(bind(operation, 42, p).valid.getAsBoolean());
      p.put("owner", List.of("admin"));
      assertTrue(bind(operation, 42, p).issues.get().containsKey("form"));
      p.remove("owner");
      p.put(null, List.of("unexpected"));
      assertTrue(bind(operation, 42, p).issues.get().containsKey("form"));
    }
  }

  @Test
  void target006TopLevelNullAndUnsupportedInternalSelector() {
    assertThrows(NullPointerException.class, () -> CancelForm.bind(42, null));
    assertThrows(NullPointerException.class, () -> QuestionDeleteForm.bind(42, null));
    assertThrows(NullPointerException.class, () -> TargetOperationInput.bind(null, 42, Map.of()));
    assertThrows(
        IllegalArgumentException.class, () -> TargetOperationInput.bind("ROLE", 42, Map.of()));
  }

  @Test
  void target007ClosedImmutableSnapshotsDoNotRetainMutableInput() {
    for (String operation : List.of(CANCEL_OPERATION, DELETE_OPERATION)) {
      var p = fields(operation, "42");
      var f = bind(operation, 42, p);
      p.clear();
      assertTrue(f.valid.getAsBoolean());
      assertEquals(TOKEN, f.values.get().get(OPERATION_TOKEN_FIELD));
      assertThrows(UnsupportedOperationException.class, () -> f.values.get().clear());
      assertThrows(UnsupportedOperationException.class, () -> f.issues.get().put("id", "bad"));
    }
  }

  @Test
  void target008OneHundredParallelBindHasNoSharedMutableState() throws Exception {
    var futures = new ArrayList<Future<?>>();
    var executor = Executors.newFixedThreadPool(8);
    try {
      for (int n = 0; n < 100; n++) {
        String operation = n % 2 == 0 ? CANCEL_OPERATION : DELETE_OPERATION;
        futures.add(
            executor.submit(
                () -> {
                  var f = bind(operation, 42, fields(operation, "42"));
                  assertTrue(f.valid.getAsBoolean());
                  assertEquals(TOKEN, f.values.get().get(OPERATION_TOKEN_FIELD));
                }));
      }
      for (var future : futures) future.get(5, TimeUnit.SECONDS);
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
