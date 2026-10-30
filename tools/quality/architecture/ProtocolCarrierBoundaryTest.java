package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-2789: independent literal value/collection contracts; no I/O or product bootstrap. */
public final class ProtocolCarrierBoundaryTest {
  @Test
  void textRedactionAndPrimitiveBoundaries() {
    FieldValue.Text text = new FieldValue.Text("secret-example");
    assertEquals("Text[redacted,length=14]", text.toString());
    assertEquals("secret-example", text.value());
    assertEquals("Text[redacted,length=0]", new FieldValue.Text("").toString());
    assertEquals("Text[redacted,length=2]", new FieldValue.Text("音楽").toString());
    assertEquals("value", assertThrows(NullPointerException.class, () -> new FieldValue.Text(null)).getMessage());
    assertEquals(Long.MIN_VALUE, new FieldValue.Numeric(Long.MIN_VALUE).value());
    assertEquals(Long.MAX_VALUE, new FieldValue.Numeric(Long.MAX_VALUE).value());
    assertTrue(new FieldValue.Flag(true).value());
    assertFalse(new FieldValue.Flag(false).value());
    assertArrayEquals(new FieldValue.Unset[] {FieldValue.Unset.INSTANCE}, FieldValue.Unset.values());
    assertSame(FieldValue.Unset.INSTANCE, FieldValue.Unset.valueOf("INSTANCE"));
  }

  @Test
  void emptyAndAbsentHaveExplicitUnsetContract() {
    FieldValueSet empty = FieldValueSet.empty();
    assertEquals(0, empty.size());
    assertEquals(List.of(), new ArrayList<>(empty.names()));
    assertSame(FieldValue.Unset.INSTANCE, empty.getOrUnset("missing"));
    assertEquals("FieldValueSet[names=[]]", empty.toString());
    assertEquals(0, empty.hashCode());
    assertEquals("name", assertThrows(NullPointerException.class, () -> empty.getOrUnset(null)).getMessage());
  }

  @Test
  void immutableOrderedDefensiveCopy() {
    LinkedHashMap<String, FieldValue> input = new LinkedHashMap<>();
    FieldValue.Numeric first = new FieldValue.Numeric(42);
    input.put("first", first);
    input.put("second", new FieldValue.Flag(false));
    FieldValueSet set = new FieldValueSet(input);
    input.clear();
    input.put("changed", new FieldValue.Numeric(0));
    assertEquals(2, set.size());
    assertEquals(List.of("first", "second"), new ArrayList<>(set.names()));
    assertSame(first, set.getOrUnset("first"));
    assertSame(FieldValue.Unset.INSTANCE, set.getOrUnset("changed"));
    assertEquals("FieldValueSet[names=[first, second]]", set.toString());
    assertThrows(UnsupportedOperationException.class, () -> set.names().remove("first"));
    assertThrows(UnsupportedOperationException.class, () -> set.names().add("extra"));
    assertEquals(List.of("first", "second"), new ArrayList<>(set.names()));
  }

  @Test
  void invalidMapsAndNullEntriesAreRejected() {
    assertEquals("source", assertThrows(NullPointerException.class, () -> new FieldValueSet(null)).getMessage());
    LinkedHashMap<String, FieldValue> nullKey = new LinkedHashMap<>();
    nullKey.put(null, FieldValue.Unset.INSTANCE);
    assertEquals("field name", assertThrows(NullPointerException.class, () -> new FieldValueSet(nullKey)).getMessage());
    LinkedHashMap<String, FieldValue> nullValue = new LinkedHashMap<>();
    nullValue.put("known", null);
    assertEquals("field value", assertThrows(NullPointerException.class, () -> new FieldValueSet(nullValue)).getMessage());
    for (String invalid : List.of("", " ", "\t\n", "\u3000")) {
      assertEquals("field value name must not be blank", assertThrows(LayoutValidationException.class,
          () -> new FieldValueSet(Map.of(invalid, FieldValue.Unset.INSTANCE))).getMessage());
    }
  }

  @Test
  void equalityAndHashFollowIndependentMapContract() {
    FieldValueSet value = new FieldValueSet(Map.of("x", new FieldValue.Numeric(42)));
    FieldValueSet equal = new FieldValueSet(Map.of("x", new FieldValue.Numeric(42)));
    FieldValueSet different = new FieldValueSet(Map.of("x", new FieldValue.Numeric(43)));
    assertTrue(value.equals(value));
    assertTrue(value.equals(equal));
    assertTrue(equal.equals(value));
    assertFalse(value.equals(different));
    assertFalse(value.equals(null));
    assertFalse(value.equals("wrong type"));
    // Map entry hash is key hash XOR value hash: ASCII x=120, Long.hashCode(42)=42.
    assertEquals(82, value.hashCode());
    assertEquals(82, equal.hashCode());
    assertEquals(83, different.hashCode());
  }

  @Test
  void independentReadersObserveSameImmutableSnapshot() throws Exception {
    FieldValueSet set = new FieldValueSet(Map.of("x", new FieldValue.Numeric(42)));
    var pool = Executors.newFixedThreadPool(2);
    try {
      List<Callable<String>> calls = List.of(
          () -> set.toString(), () -> set.toString(), () -> set.toString(), () -> set.toString());
      for (var future : pool.invokeAll(calls, 5, TimeUnit.SECONDS)) {
        assertEquals("FieldValueSet[names=[x]]", future.get(1, TimeUnit.SECONDS));
      }
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(5, TimeUnit.SECONDS));
    }
  }
}
