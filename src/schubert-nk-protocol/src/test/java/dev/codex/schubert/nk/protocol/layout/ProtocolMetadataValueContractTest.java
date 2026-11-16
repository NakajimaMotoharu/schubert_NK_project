package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** UI232235/SS321322351354/451; independent metadata/value literals, no backend operations. */
class ProtocolMetadataValueContractTest {
  private static final String REQUEST_LAYOUT = "LGNREQ01";
  private static final String REPLY_LAYOUT = "LGNRSP01";
  private static final String LAYOUT_REJECTED = "layout rejected";

  @Test
  void metaValue001AllClosedEnumFactoriesAndCallerOwnedArrays() {
    enumContract(FieldArea::values, FieldArea::valueOf, "HEADER", "DATA", "RECORD");
    enumContract(Padding::values, Padding::valueOf, "SPACE_RIGHT", "ZERO_LEFT", "NONE");
    enumContract(
        Presence::values, Presence::valueOf, "MANDATORY", "CONDITIONAL", "OPTIONAL", "FIXED");
    enumContract(WireType::values, WireType::valueOf, "TEXT", "NUMERIC", "BOOLEAN");
    enumContract(
        BrokerTopology::values,
        BrokerTopology::valueOf,
        "SYNC_REQUEST",
        "SYNC_REPLY_WEB",
        "ASYNC_WORK",
        "WEB_LOG",
        "DEAD_LETTER",
        "EXPIRY");
    enumContract(FieldValue.Unset::values, FieldValue.Unset::valueOf, "INSTANCE");
  }

  @Test
  void metaValue002FieldValuesRetainIndependentHashAndRedactionContracts() {
    FieldValue.Text text = new FieldValue.Text("alpha");
    assertEquals("alpha", text.value());
    assertEquals(92909918, text.hashCode());
    assertEquals("Text[redacted,length=5]", text.toString());
    valueKey(text, new FieldValue.Text("alpha"));
    assertFalse(text.equals(new FieldValue.Text("beta")));
    assertThrows(NullPointerException.class, () -> new FieldValue.Text(null));
    FieldValue.Numeric number = new FieldValue.Numeric(42);
    assertEquals(42, number.value());
    assertEquals(42, number.hashCode());
    assertEquals("Numeric[value=42]", number.toString());
    valueKey(number, new FieldValue.Numeric(42));
    assertFalse(number.equals(new FieldValue.Numeric(43)));
    FieldValue.Flag yes = new FieldValue.Flag(true);
    FieldValue.Flag no = new FieldValue.Flag(false);
    assertTrue(yes.value());
    assertFalse(no.value());
    assertEquals(1231, yes.hashCode());
    assertEquals(1237, no.hashCode());
    assertEquals("Flag[value=true]", yes.toString());
    assertEquals("Flag[value=false]", no.toString());
    valueKey(yes, new FieldValue.Flag(true));
    assertFalse(yes.equals(no));
    FieldValue.Numeric minimum = new FieldValue.Numeric(Long.MIN_VALUE);
    FieldValue.Numeric maximum = new FieldValue.Numeric(Long.MAX_VALUE);
    assertEquals(Long.MIN_VALUE, minimum.value());
    assertEquals(Long.MAX_VALUE, maximum.value());
    assertEquals(Integer.MIN_VALUE, minimum.hashCode());
    assertEquals(Integer.MIN_VALUE, maximum.hashCode());
    Map<FieldValue.Numeric, String> collisions = new HashMap<>();
    collisions.put(minimum, "minimum");
    collisions.put(maximum, "maximum");
    assertEquals(2, collisions.size());
    assertEquals("minimum", collisions.get(new FieldValue.Numeric(Long.MIN_VALUE)));
    assertEquals("maximum", collisions.get(new FieldValue.Numeric(Long.MAX_VALUE)));
  }

  @Test
  void metaValue003HttpAndElapsedNumbersEnforceAsciiAndIndependentBoundaries() {
    for (int input : new int[] {100, 200, 599}) {
      HttpStatusCode status = new HttpStatusCode(input);
      assertEquals(input, status.value());
      assertEquals(input, status.hashCode());
      valueKey(status, new HttpStatusCode(input));
    }
    assertEquals("HttpStatusCode[value=200]", new HttpStatusCode(200).toString());
    assertEquals("200", HttpStatusCode.parse("200").wireValue());
    assertFalse(new HttpStatusCode(200).equals(new HttpStatusCode(201)));
    for (int input : new int[] {Integer.MIN_VALUE, -1, 0, 99, 600, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> new HttpStatusCode(input));
    }
    for (String input :
        List.of("", " 200", "200 ", "+200", "-200", "２００", "20", "2000", "099", "600")) {
      assertThrows(IllegalArgumentException.class, () -> HttpStatusCode.parse(input));
    }
    assertThrows(NullPointerException.class, () -> HttpStatusCode.parse(null));
    for (int input : new int[] {0, 17, 999999999}) {
      ElapsedMilliseconds elapsed = new ElapsedMilliseconds(input);
      assertEquals(input, elapsed.value());
      assertEquals(input, elapsed.hashCode());
      valueKey(elapsed, new ElapsedMilliseconds(input));
    }
    assertEquals("ElapsedMilliseconds[value=17]", new ElapsedMilliseconds(17).toString());
    assertEquals("0", ElapsedMilliseconds.parse("000000000").wireValue());
    assertEquals("17", ElapsedMilliseconds.parse("17").wireValue());
    assertEquals("999999999", ElapsedMilliseconds.parse("999999999").wireValue());
    assertFalse(new ElapsedMilliseconds(17).equals(new ElapsedMilliseconds(18)));
    for (int input : new int[] {Integer.MIN_VALUE, -1, 1000000000, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> new ElapsedMilliseconds(input));
    }
    for (String input : List.of("", " ", "+1", "-1", "1.0", "１", "1000000000", "17 ")) {
      assertThrows(IllegalArgumentException.class, () -> ElapsedMilliseconds.parse(input));
    }
    assertThrows(NullPointerException.class, () -> ElapsedMilliseconds.parse(null));
    Map<Object, String> typed = new HashMap<>();
    typed.put(new HttpStatusCode(200), "status");
    typed.put(new ElapsedMilliseconds(200), "elapsed");
    assertEquals(2, typed.size());
    assertEquals("status", typed.get(new HttpStatusCode(200)));
    assertEquals("elapsed", typed.get(new ElapsedMilliseconds(200)));
  }

  @Test
  void metaValue004LayoutOrderingUsesTheActualComparableBridgeAndPreservesCauses() {
    LayoutId first = new LayoutId(REQUEST_LAYOUT);
    LayoutId last = new LayoutId(REPLY_LAYOUT);
    assertEquals(REQUEST_LAYOUT, first.value());
    assertEquals(REQUEST_LAYOUT, first.toString());
    assertEquals(208788652, first.hashCode());
    assertEquals(209204765, last.hashCode());
    valueKey(first, new LayoutId(REQUEST_LAYOUT));
    assertFalse(first.equals(last));
    TreeSet<LayoutId> sorted = new TreeSet<>();
    sorted.add(last);
    sorted.add(first);
    sorted.add(new LayoutId(REQUEST_LAYOUT));
    assertEquals(
        List.of(REQUEST_LAYOUT, REPLY_LAYOUT), sorted.stream().map(LayoutId::value).toList());
    assertThrows(NullPointerException.class, () -> first.compareTo(null));
    assertThrows(NullPointerException.class, () -> new LayoutId(null));
    for (String input :
        List.of("", "LGNREQ0", "LGNREQ001", "lgnreq01", "LGNREQ0 ", "ＬGNREQ01", "LGNREQ0\n")) {
      assertThrows(LayoutValidationException.class, () -> new LayoutId(input));
    }
    RuntimeException cause = new IllegalArgumentException("public fixture cause");
    LayoutValidationException withCause = new LayoutValidationException(LAYOUT_REJECTED, cause);
    assertEquals(LAYOUT_REJECTED, withCause.getMessage());
    assertSame(cause, withCause.getCause());
    assertEquals(LAYOUT_REJECTED, new LayoutValidationException(LAYOUT_REJECTED).getMessage());
    assertNull(new LayoutValidationException(LAYOUT_REJECTED).getCause());
  }

  private static void valueKey(Object original, Object equal) {
    assertEquals(original, equal);
    assertNotSame(original, equal);
    assertFalse(original.equals(null));
    assertFalse(original.equals("unrelated-type"));
    Map<Object, String> values = new HashMap<>();
    values.put(original, "retained");
    assertEquals("retained", values.get(equal));
  }

  private static <E extends Enum<E>> void enumContract(
      Supplier<E[]> factory, Function<String, E> lookup, String... names) {
    E[] values = factory.get();
    assertEquals(names.length, values.length);
    assertEquals(List.of(names), Arrays.stream(values).map(Enum::name).toList());
    for (int index = 0; index < names.length; index++) {
      E value = lookup.apply(names[index]);
      assertSame(values[index], value);
      assertEquals(names[index], value.name());
      assertEquals(names[index], value.toString());
      assertEquals(index, value.ordinal());
    }
    for (String bad :
        List.of("", "unknown", names[0].toLowerCase(java.util.Locale.ROOT), names[0] + " ")) {
      assertThrows(IllegalArgumentException.class, () -> lookup.apply(bad));
    }
    assertThrows(NullPointerException.class, () -> lookup.apply(null));
    E original = values[0];
    values[0] = null;
    assertNotSame(values, factory.get());
    assertSame(original, factory.get()[0]);
  }
}
