package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.foreign.Arena;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.ValueLayout;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Literal sd-bus ABI arguments and independently allocated C reply vectors; MANAGER817007..012. */
final class LinuxSystemdSessionTest {
  private static final String BUS_NEW = "sd_bus_new";
  private static final String MESSAGE_NEW_METHOD_CALL = "sd_bus_message_new_method_call";
  private static final String BUS_CALL = "sd_bus_call";
  private static final String GET_PROPERTY_STRING = "sd_bus_get_property_string";
  private static final String GET_PROPERTY = "sd_bus_get_property";
  private static final String LIBC_FREE = "free";
  private static final String BUS_RELEASE_EVENT = "bus";
  private static final String REQUEST_RELEASE_EVENT = "request";
  private static final String REPLY_RELEASE_EVENT = "reply";
  private static final String SYNTHETIC_FAILURE_MESSAGE = "synthetic";
  private static final String MESSAGE_UNREF = "sd_bus_message_unref";
  private static final String BUS_CLOSE_UNREF = "sd_bus_close_unref";
  private static final String LOADED_STATE = "loaded";
  private static final String BUS_PROCESS = "sd_bus_process";
  private static final String UNIQUE_BUS_NAME = ":1.7";
  private static final String MESSAGE_READ_BASIC = "sd_bus_message_read_basic";
  private static final String GET_PROPERTY_TRIVIAL = "sd_bus_get_property_trivial";
  private static final String AMD64_ARCH = "amd64";
  private static final String LINUX_OS = "Linux";
  private static final String UID_KEY = "uid";
  private static final String MODE_KEY = "mode";
  private static final List<String> OUTPUT_CALLS =
      List.of(BUS_NEW, MESSAGE_NEW_METHOD_CALL, BUS_CALL, GET_PROPERTY_STRING, GET_PROPERTY);

  private static int outputIndex(String symbol) {
    return switch (symbol) {
      case BUS_NEW -> 0;
      case MESSAGE_NEW_METHOD_CALL -> 1;
      case BUS_CALL -> 4;
      default -> 6;
    };
  }

  private static void outputRoute(LinuxSystemdSession session, String target) throws IOException {
    session.start(() -> 5000000);
    session.owner(4999999);
    if (target.equals(GET_PROPERTY_STRING))
      session.read(
          SystemManagerObservation.Service.API, SystemManagerObservation.Property.ID, 4999998);
    if (target.equals(GET_PROPERTY))
      session.read(
          SystemManagerObservation.Service.API,
          SystemManagerObservation.Property.INVOCATION,
          4999998);
  }

  private static void failWith(Throwable failure) throws IOException {
    if (failure instanceof IOException io) throw io;
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static String released(Calls literal, String symbol, Object[] arguments) {
    if (symbol.equals(LIBC_FREE)) return LIBC_FREE;
    long pointer = Calls.segment(arguments[0]).address();
    if (pointer == literal.bus.address()) return BUS_RELEASE_EVENT;
    if (pointer == literal.creds.address()) return REQUEST_RELEASE_EVENT;
    if (pointer == literal.message.address()) return REPLY_RELEASE_EVENT;
    throw new AssertionError("foreign independent pointer");
  }

  /** PT-OPS-FFMOWN001: C may write the output and then fail; no guessed free/retry. */
  @Test
  void ffmown001WriteThenUnknownKeepsOutputAndArenaWithoutRetry() throws Exception {
    for (String target : OUTPUT_CALLS)
      for (Throwable failure :
          List.of(
              new IOException(SYNTHETIC_FAILURE_MESSAGE),
              new IllegalStateException(SYNTHETIC_FAILURE_MESSAGE),
              new LinkageError(SYNTHETIC_FAILURE_MESSAGE))) {
        try (var data = Arena.ofConfined();
            var owned = Arena.ofConfined()) {
          var literal = new Calls(data);
          var out = new ArrayList<MemorySegment>();
          LinuxSystemdSession.Calls calls =
              (symbol, arguments) -> {
                if (symbol.equals(target)) out.add(Calls.segment(arguments[outputIndex(symbol)]));
                Object value = literal.call(symbol, arguments);
                if (symbol.equals(target)) failWith(failure);
                return value;
              };
          var session = new LinuxSystemdSession(calls, owned);
          Class<? extends Throwable> expected =
              failure instanceof IOException ? IOException.class : failure.getClass();
          Throwable actual = assertThrows(expected, () -> outputRoute(session, target));
          if (!(failure instanceof IOException)) assertSame(failure, actual);
          assertEquals(1, out.size());
          assertNotEquals(0, out.getFirst().get(ValueLayout.ADDRESS, 0).address());
          assertTrue(owned.scope().isAlive());
          assertFalse(session.closed());
          int before = literal.events.size();
          assertThrows(IOException.class, session::close);
          assertThrows(IOException.class, () -> session.owner(5000000));
          assertEquals(before, literal.events.size());
          assertEquals(0, literal.events.stream().filter(LIBC_FREE::equals).count());
          assertEquals(
              target.equals(BUS_CALL) ? 1 : target.startsWith(GET_PROPERTY) ? 6 : 0,
              literal.events.stream().filter(MESSAGE_UNREF::equals).count());
          assertFalse(literal.events.contains(BUS_CLOSE_UNREF));
        }
      }
  }

  /** PT-OPS-FFMOWN002: only three private result buffers, normal reuse and literal close order. */
  @Test
  void ffmown002ThreeOutputSlotsReuseAndLegacyReplyRequestFreeBusOrder() throws Exception {
    try (var data = Arena.ofConfined()) {
      var literal = new Calls(data);
      var addresses = new HashSet<Long>();
      var closes = new ArrayList<String>();
      LinuxSystemdSession.Calls calls =
          (symbol, arguments) -> {
            if (OUTPUT_CALLS.contains(symbol))
              addresses.add(Calls.segment(arguments[outputIndex(symbol)]).address());
            if (symbol.equals(LIBC_FREE) || symbol.endsWith("_unref"))
              closes.add(released(literal, symbol, arguments));
            return literal.call(symbol, arguments);
          };
      var owned = Arena.ofConfined();
      var session = new LinuxSystemdSession(calls, owned);
      session.start(() -> 5000000);
      int beforeRestart = literal.events.size();
      assertThrows(IOException.class, () -> session.start(() -> 5000000));
      assertEquals(beforeRestart, literal.events.size());
      for (int round = 0; round < 2; round++) {
        assertEquals(1, session.owner(4999999).pid());
        assertEquals(
            LOADED_STATE,
            session.read(
                SystemManagerObservation.Service.API,
                SystemManagerObservation.Property.ID,
                4999998));
        assertEquals(
            "00112233445566778899aabbccddeeff",
            session.read(
                SystemManagerObservation.Service.API,
                SystemManagerObservation.Property.INVOCATION,
                4999998));
        assertEquals(1, session.owner(4999999).pid());
      }
      session.close();
      assertEquals(3, addresses.size());
      var oneRound =
          List.of(
              REPLY_RELEASE_EVENT,
              REQUEST_RELEASE_EVENT,
              REPLY_RELEASE_EVENT,
              REQUEST_RELEASE_EVENT,
              REPLY_RELEASE_EVENT,
              REQUEST_RELEASE_EVENT,
              LIBC_FREE,
              REPLY_RELEASE_EVENT,
              REPLY_RELEASE_EVENT,
              REQUEST_RELEASE_EVENT,
              REPLY_RELEASE_EVENT,
              REQUEST_RELEASE_EVENT,
              REPLY_RELEASE_EVENT,
              REQUEST_RELEASE_EVENT);
      var expected = new ArrayList<>(oneRound);
      expected.addAll(oneRound);
      expected.add(BUS_RELEASE_EVENT);
      assertEquals(expected, closes);
      assertTrue(session.closed());
      assertFalse(owned.scope().isAlive());
    }
  }

  /** PT-OPS-FFMOWN003: a returned error status still gives a known output to release. */
  @Test
  void ffmown003NegativeAndWrongStatusesReleaseKnownOutputsInOriginalOrder() throws Exception {
    var beforeProperty =
        List.of(
            REPLY_RELEASE_EVENT,
            REQUEST_RELEASE_EVENT,
            REPLY_RELEASE_EVENT,
            REQUEST_RELEASE_EVENT,
            REPLY_RELEASE_EVENT,
            REQUEST_RELEASE_EVENT);
    for (String target : OUTPUT_CALLS)
      for (Object bad : List.of(-5, "invalid status")) {
        try (var data = Arena.ofConfined()) {
          var literal = new Calls(data);
          var closes = new ArrayList<String>();
          LinuxSystemdSession.Calls calls =
              (symbol, arguments) -> {
                if (symbol.equals(LIBC_FREE) || symbol.endsWith("_unref"))
                  closes.add(released(literal, symbol, arguments));
                Object value = literal.call(symbol, arguments);
                return symbol.equals(target) ? bad : value;
              };
          var owned = Arena.ofConfined();
          var session = new LinuxSystemdSession(calls, owned);
          assertThrows(IOException.class, () -> outputRoute(session, target));
          session.close();
          List<String> expected =
              switch (target) {
                case BUS_NEW -> List.of(BUS_RELEASE_EVENT);
                case MESSAGE_NEW_METHOD_CALL -> List.of(REQUEST_RELEASE_EVENT, BUS_RELEASE_EVENT);
                case BUS_CALL ->
                    List.of(REPLY_RELEASE_EVENT, REQUEST_RELEASE_EVENT, BUS_RELEASE_EVENT);
                default -> {
                  var sequence = new ArrayList<>(beforeProperty);
                  sequence.add(
                      target.equals(GET_PROPERTY_STRING) ? LIBC_FREE : REPLY_RELEASE_EVENT);
                  sequence.add(BUS_RELEASE_EVENT);
                  yield sequence;
                }
              };
          assertEquals(expected, closes);
          assertTrue(session.closed());
          assertFalse(owned.scope().isAlive());
        }
      }
  }

  /** PT-OPS-FFMOWN004: unknown reply close still drains the distinct known request once. */
  @Test
  void ffmown004UnknownReplyReleaseDrainsKnownRequestButRetainsBusAndArena() throws Exception {
    for (Throwable failure :
        List.of(
            new IOException(SYNTHETIC_FAILURE_MESSAGE),
            new IllegalStateException(SYNTHETIC_FAILURE_MESSAGE),
            new LinkageError(SYNTHETIC_FAILURE_MESSAGE))) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var literal = new Calls(data);
        var closes = new ArrayList<String>();
        LinuxSystemdSession.Calls calls =
            (symbol, arguments) -> {
              String closed = "";
              if (symbol.equals(LIBC_FREE) || symbol.endsWith("_unref")) {
                closed = released(literal, symbol, arguments);
                closes.add(closed);
              }
              Object value = literal.call(symbol, arguments);
              if (closed.equals(REPLY_RELEASE_EVENT)) failWith(failure);
              return value;
            };
        var session = new LinuxSystemdSession(calls, owned);
        session.start(() -> 5000000);
        Class<? extends Throwable> expected =
            failure instanceof IOException ? IOException.class : failure.getClass();
        Throwable actual = assertThrows(expected, () -> session.owner(4999999));
        if (!(failure instanceof IOException)) assertSame(failure, actual);
        assertEquals(List.of(REPLY_RELEASE_EVENT, REQUEST_RELEASE_EVENT), closes);
        assertTrue(owned.scope().isAlive());
        assertThrows(IOException.class, session::close);
        assertEquals(List.of(REPLY_RELEASE_EVENT, REQUEST_RELEASE_EVENT), closes);
        assertFalse(session.closed());
      }
    }
  }

  /** PT-OPS-FFMOWN005: pre-C budget failure has no reply; bad array decode frees known message. */
  @Test
  void ffmown005BeforeCallFailureAndArrayDecodeFailureKeepExactOwnership() throws Exception {
    try (var data = Arena.ofConfined()) {
      var literal = new Calls(data);
      var owned = Arena.ofConfined();
      var failure = new LinkageError("synthetic argument budget");
      var session = new LinuxSystemdSession(literal, owned);
      session.start(
          () -> {
            if (!literal.events.isEmpty()
                && literal.events.getLast().equals("sd_bus_message_append_basic")) throw failure;
            return 5000000;
          });
      assertSame(failure, assertThrows(LinkageError.class, () -> session.owner(4999999)));
      assertFalse(literal.events.contains(BUS_CALL));
      assertEquals(1, literal.events.stream().filter(MESSAGE_UNREF::equals).count());
      session.close();
      assertTrue(session.closed());
      assertFalse(owned.scope().isAlive());
    }
    try (var data = Arena.ofConfined()) {
      var literal = new Calls(data);
      var owned = Arena.ofConfined();
      var session = new LinuxSystemdSession(literal, owned);
      session.start(() -> 5000000);
      session.owner(4999999);
      literal.arrayLength = 17;
      assertThrows(
          IOException.class,
          () ->
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.INVOCATION,
                  4999998));
      assertEquals(7, literal.events.stream().filter(MESSAGE_UNREF::equals).count());
      session.close();
      assertTrue(session.closed());
      assertFalse(owned.scope().isAlive());
    }
  }

  /**
   * PT-OPS-FFMOWN006: an invalidated output buffer never turns pointer decode failure into success.
   */
  @Test
  void ffmown006OutputDecodeFailureRefusesCleanupClaimsAndAnyFurtherNativeCall() throws Exception {
    for (String target : OUTPUT_CALLS) {
      try (var data = Arena.ofConfined()) {
        var owned = Arena.ofConfined();
        var literal = new Calls(data);
        LinuxSystemdSession.Calls calls =
            (symbol, arguments) -> {
              Object status = literal.call(symbol, arguments);
              if (symbol.equals(target))
                owned.close(); // Independent hostile-lifetime fixture, not real OOM.
              return status;
            };
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(IllegalStateException.class, () -> outputRoute(session, target));
        assertFalse(owned.scope().isAlive());
        assertFalse(session.closed());
        int before = literal.events.size();
        assertThrows(IOException.class, session::close);
        assertThrows(IOException.class, () -> session.owner(5000000));
        assertEquals(before, literal.events.size());
        assertFalse(literal.events.contains(BUS_CLOSE_UNREF));
      }
    }
  }

  /** PT-OPS-FFMOWN007/BUG1444: consumed bus + failed arena close is sticky UNKNOWN. */
  @Test
  void ffmown007ArenaCloseUnknownAfterBusConsumptionNeverAllowsANextQueryOrRetry()
      throws Exception {
    for (Throwable failure :
        List.of(
            new IllegalStateException("synthetic arena close"),
            new LinkageError("synthetic arena close"))) {
      try (var data = Arena.ofConfined();
          var backing = Arena.ofConfined()) {
        int[] closes = {0};
        Arena failing =
            new Arena() {
              public MemorySegment allocate(long size, long alignment) {
                return backing.allocate(size, alignment);
              }

              public MemorySegment.Scope scope() {
                return backing.scope();
              }

              public void close() {
                closes[0]++;
                if (failure instanceof RuntimeException runtime) throw runtime;
                throw (Error) failure;
              }
            };
        var literal = new Calls(data);
        var session = new LinuxSystemdSession(literal, failing);
        session.start(() -> 5000000);
        assertSame(failure, assertThrows(failure.getClass(), session::close));
        assertEquals(1, closes[0]);
        assertEquals(1, literal.events.stream().filter(BUS_CLOSE_UNREF::equals).count());
        assertTrue(backing.scope().isAlive());
        assertFalse(session.closed());
        int before = literal.events.size();
        assertThrows(IOException.class, () -> session.owner(5000000));
        assertThrows(IOException.class, session::close);
        assertEquals(before, literal.events.size());
        assertEquals(1, closes[0]);
      }
    }
  }

  /**
   * PT-OPS-FFMOWN008: positive process progress skips wait but never renews the original budget.
   */
  @Test
  void ffmown008PositiveAuthenticationProgressUsesNoWaitAndNeverRenewsBudget() throws Exception {
    for (boolean expires : new boolean[] {false, true}) {
      try (var data = Arena.ofConfined()) {
        var literal = new Calls(data);
        literal.readyAfter = expires ? Integer.MAX_VALUE : 2;
        LinuxSystemdSession.Calls calls =
            (symbol, arguments) -> {
              Object value = literal.call(symbol, arguments);
              if (symbol.equals(BUS_PROCESS)) {
                if (expires) literal.elapsedMicros += 2000000;
                return 1;
              }
              return value;
            };
        var owned = Arena.ofConfined();
        var session = new LinuxSystemdSession(calls, owned);
        SystemManagerObservation.Budget budget =
            () -> {
              long remaining = 5000000 - literal.elapsedMicros;
              if (remaining < 1) throw new IOException("synthetic original budget");
              return remaining;
            };
        if (expires) assertThrows(IOException.class, () -> session.start(budget));
        else session.start(budget);
        assertEquals(expires ? 3 : 2, literal.events.stream().filter(BUS_PROCESS::equals).count());
        assertEquals(0, literal.events.stream().filter("sd_bus_wait"::equals).count());
        assertEquals(expires ? 6000000 : 0, literal.elapsedMicros);
        assertTrue(literal.rpcBudgets.isEmpty());
        session.close();
        assertEquals(1, literal.events.stream().filter(BUS_CLOSE_UNREF::equals).count());
        assertTrue(session.closed());
        assertFalse(owned.scope().isAlive());
      }
    }
  }

  static final class Calls implements LinuxSystemdSession.Calls {
    final Arena data;
    final MemorySegment bus;
    final MemorySegment creds;
    final MemorySegment message;
    final List<String> events = new ArrayList<>();
    String failure = "";
    String negative = "";
    String wrongType = "";
    String nullPointer = "";
    String unique = UNIQUE_BUS_NAME;
    String string = LOADED_STATE;
    String member = "";
    int arrayLength = 16;
    int readyAfter;
    int readyReads;
    long elapsedMicros;
    long rpcDelayMicros;
    long waitDelayMicros;
    final List<Long> rpcBudgets = new ArrayList<>();
    boolean badRelease;
    boolean expireAtSetter;

    Calls(Arena data) {
      this.data = data;
      bus = data.allocate(8);
      creds = data.allocate(8);
      message = data.allocate(8);
    }

    static MemorySegment segment(Object o) {
      return (MemorySegment) o;
    }

    public Object call(String name, Object... a) throws IOException {
      events.add(name);
      if (name.equals(failure)) throw new IOException("literal native fault");
      if (name.equals(negative)) return -5;
      switch (name) {
        case BUS_NEW ->
            segment(a[0])
                .set(ValueLayout.ADDRESS, 0, name.equals(nullPointer) ? MemorySegment.NULL : bus);
        case "sd_bus_set_address" ->
            assertEquals("unix:path=/run/dbus/system_bus_socket", segment(a[1]).getString(0));
        case "sd_bus_set_bus_client" -> assertEquals(1, a[1]);
        case "sd_bus_set_allow_interactive_authorization" -> assertEquals(0, a[1]);
        case MESSAGE_NEW_METHOD_CALL -> {
          assertEquals("org.freedesktop.DBus", segment(a[2]).getString(0));
          assertEquals("/org/freedesktop/DBus", segment(a[3]).getString(0));
          assertEquals("org.freedesktop.DBus", segment(a[4]).getString(0));
          member = segment(a[5]).getString(0);
          assertTrue(
              List.of("GetNameOwner", "GetConnectionUnixProcessID", "GetConnectionUnixUser")
                  .contains(member));
          segment(a[1])
              .set(ValueLayout.ADDRESS, 0, name.equals(nullPointer) ? MemorySegment.NULL : creds);
        }
        case "sd_bus_message_set_auto_start" -> assertEquals(0, a[1]);
        case "sd_bus_message_append_basic" -> {
          assertEquals((byte) 's', a[1]);
          assertEquals(
              member.equals("GetNameOwner") ? "org.freedesktop.systemd1" : unique,
              segment(a[2]).getString(0));
        }
        case BUS_CALL -> {
          assertTrue((long) a[2] > 0 && (long) a[2] <= 5000000);
          long left = (long) a[2];
          rpcBudgets.add(left);
          elapsedMicros += Math.min(left, rpcDelayMicros);
          if (rpcDelayMicros >= left) return -110;
          segment(a[4])
              .set(ValueLayout.ADDRESS, 0, name.equals(nullPointer) ? MemorySegment.NULL : message);
        }
        case MESSAGE_READ_BASIC -> {
          if (member.equals("GetNameOwner")) {
            assertEquals((byte) 's', a[1]);
            segment(a[2])
                .set(
                    ValueLayout.ADDRESS,
                    0,
                    name.equals(nullPointer) ? MemorySegment.NULL : data.allocateFrom(unique));
          } else {
            assertEquals((byte) 'u', a[1]);
            segment(a[2])
                .set(ValueLayout.JAVA_INT, 0, member.equals("GetConnectionUnixProcessID") ? 1 : 0);
          }
          return name.equals(wrongType) ? 0 : 1;
        }
        case "sd_bus_is_ready" -> {
          return readyReads++ >= readyAfter ? 1 : 0;
        }
        case BUS_PROCESS -> {
          return 0;
        }
        case "sd_bus_wait" -> {
          assertTrue((long) a[1] > 0 && (long) a[1] <= 5000000);
          elapsedMicros += Math.min((long) a[1], waitDelayMicros);
        }
        case GET_PROPERTY_STRING, GET_PROPERTY_TRIVIAL, GET_PROPERTY -> {
          assertEquals(UNIQUE_BUS_NAME, segment(a[1]).getString(0));
          assertEquals(
              "/org/freedesktop/systemd1/unit/schubert_2dnk_2dapi_2eservice",
              segment(a[2]).getString(0));
          String member = segment(a[4]).getString(0);
          if (name.equals(GET_PROPERTY_STRING)) {
            assertEquals(
                member.equals("ControlGroup")
                    ? "org.freedesktop.systemd1.Service"
                    : "org.freedesktop.systemd1.Unit",
                segment(a[3]).getString(0));
            segment(a[6])
                .set(
                    ValueLayout.ADDRESS,
                    0,
                    name.equals(nullPointer) ? MemorySegment.NULL : data.allocateFrom(string));
          } else if (name.equals(GET_PROPERTY_TRIVIAL)) {
            assertEquals("org.freedesktop.systemd1.Service", segment(a[3]).getString(0));
            if (member.equals("MainPID")) {
              assertEquals((byte) 'u', a[6]);
              segment(a[7]).set(ValueLayout.JAVA_INT, 0, -1);
            } else {
              assertEquals("ExecMainStartTimestampMonotonic", member);
              assertEquals((byte) 't', a[6]);
              segment(a[7]).set(ValueLayout.JAVA_LONG, 0, -1L);
            }
          } else {
            assertEquals("InvocationID", member);
            assertEquals("ay", segment(a[7]).getString(0));
            segment(a[6])
                .set(
                    ValueLayout.ADDRESS,
                    0,
                    name.equals(nullPointer) ? MemorySegment.NULL : message);
          }
        }
        case "sd_bus_message_read_array" -> {
          assertEquals((byte) 'y', a[1]);
          segment(a[2])
              .set(
                  ValueLayout.ADDRESS,
                  0,
                  name.equals(nullPointer)
                      ? MemorySegment.NULL
                      : data.allocateFrom(
                          ValueLayout.JAVA_BYTE,
                          HexFormat.of().parseHex("00112233445566778899aabbccddeeff")));
          segment(a[3]).set(ValueLayout.JAVA_LONG, 0, arrayLength);
        }
        case MESSAGE_UNREF, BUS_CLOSE_UNREF -> {
          if (name.equals(wrongType)) return "invalid native release type";
          return badRelease ? bus : MemorySegment.NULL;
        }
        case "sd_bus_set_method_call_timeout" -> {
          if (expireAtSetter) elapsedMicros = 5000000;
        }
        case LIBC_FREE, "sd_bus_start" -> {}
        default -> throw new AssertionError("unexpected ABI call " + name);
      }
      return name.equals(wrongType) ? MemorySegment.NULL : 0;
    }
  }

  @Test
  void literalAbiAllKindsAndUniqueDestinationClose() throws Exception {
    try (var data = Arena.ofConfined()) {
      var calls = new Calls(data);
      var session = new LinuxSystemdSession(calls, Arena.ofConfined());
      session.start(() -> 5000000);
      assertEquals(
          new SystemManagerObservation.Owner(1, 0, UNIQUE_BUS_NAME), session.owner(4999999));
      assertEquals(
          LOADED_STATE,
          session.read(
              SystemManagerObservation.Service.API,
              SystemManagerObservation.Property.LOAD,
              4999998));
      assertEquals(
          LOADED_STATE,
          session.read(
              SystemManagerObservation.Service.API,
              SystemManagerObservation.Property.GROUP,
              4999998));
      assertEquals(
          "4294967295",
          session.read(
              SystemManagerObservation.Service.API,
              SystemManagerObservation.Property.PID,
              4999997));
      assertEquals(
          "18446744073709551615",
          session.read(
              SystemManagerObservation.Service.API,
              SystemManagerObservation.Property.START,
              4999996));
      assertEquals(
          "00112233445566778899aabbccddeeff",
          session.read(
              SystemManagerObservation.Service.API,
              SystemManagerObservation.Property.INVOCATION,
              4999995));
      session.close();
      assertTrue(session.closed());
      assertTrue(calls.events.containsAll(List.of(LIBC_FREE, MESSAGE_UNREF, BUS_CLOSE_UNREF)));
      assertThrows(IOException.class, session::close);
    }
  }

  @Test
  void everyNativeCallExceptionIsNotNormalClose() throws Exception {
    for (String failure :
        List.of(
            BUS_NEW,
            "sd_bus_set_method_call_timeout",
            "sd_bus_set_address",
            "sd_bus_set_bus_client",
            "sd_bus_set_allow_interactive_authorization",
            "sd_bus_start",
            "sd_bus_is_ready",
            MESSAGE_NEW_METHOD_CALL,
            "sd_bus_message_set_auto_start",
            "sd_bus_message_append_basic",
            BUS_CALL,
            MESSAGE_READ_BASIC,
            GET_PROPERTY_STRING,
            LIBC_FREE,
            GET_PROPERTY_TRIVIAL,
            GET_PROPERTY,
            "sd_bus_message_read_array",
            MESSAGE_UNREF,
            BUS_CLOSE_UNREF)) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.failure = failure;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(
            IOException.class,
            () -> {
              session.start(() -> 5000000);
              session.owner(4999999);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.ID,
                  4999998);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.PID,
                  4999997);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.INVOCATION,
                  4999996);
              session.close();
            });
        assertFalse(session.closed());
        assertThrows(IOException.class, session::close);
      }
    }
  }

  @Test
  void nullPointersWrongStatusesAndArrayBoundaryNeverReadBadMemory() throws Exception {
    for (String bad :
        List.of(
            BUS_NEW,
            MESSAGE_NEW_METHOD_CALL,
            BUS_CALL,
            MESSAGE_READ_BASIC,
            GET_PROPERTY_STRING,
            GET_PROPERTY,
            "sd_bus_message_read_array")) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.nullPointer = bad;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(
            IOException.class,
            () -> {
              session.start(() -> 5000000);
              session.owner(4999999);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.ID,
                  4999998);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.INVOCATION,
                  4999997);
            });
      }
    }
    for (int length : new int[] {-1, 1, 15, 17, Integer.MAX_VALUE})
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.arrayLength = length;
        var session = new LinuxSystemdSession(calls, owned);
        session.start(() -> 5000000);
        session.owner(4999999);
        assertThrows(
            IOException.class,
            () ->
                session.read(
                    SystemManagerObservation.Service.API,
                    SystemManagerObservation.Property.INVOCATION,
                    4999998));
      }
    try (var data = Arena.ofConfined();
        var owned = Arena.ofConfined()) {
      var calls = new Calls(data);
      calls.arrayLength = 0;
      var session = new LinuxSystemdSession(calls, owned);
      session.start(() -> 5000000);
      session.owner(4999999);
      assertEquals(
          "",
          session.read(
              SystemManagerObservation.Service.API,
              SystemManagerObservation.Property.INVOCATION,
              4999998));
    }
    for (String bad :
        List.of(
            BUS_NEW,
            MESSAGE_NEW_METHOD_CALL,
            BUS_CALL,
            MESSAGE_READ_BASIC,
            GET_PROPERTY_STRING,
            GET_PROPERTY,
            GET_PROPERTY_TRIVIAL))
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.wrongType = bad;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(
            IOException.class,
            () -> {
              session.start(() -> 5000000);
              session.owner(4999999);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.ID,
                  4999998);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.PID,
                  4999997);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.INVOCATION,
                  4999996);
            });
      }
  }

  @Test
  void nulDecoderReadsOnlyActualAllocationAndBoundaries() throws Exception {
    for (String value : List.of("", "a", "short", "x".repeat(4096))) {
      byte[] bytes = (value + "\0").getBytes(java.nio.charset.StandardCharsets.US_ASCII);
      int[] reads = {0};
      assertEquals(
          value,
          LinuxSystemdSession.decode(
              index -> {
                assertEquals(reads[0]++, index);
                return bytes[index];
              }));
      assertEquals(value.length() + 1, reads[0]);
    }
    int[] reads = {0};
    assertThrows(
        IOException.class,
        () ->
            LinuxSystemdSession.decode(
                index -> {
                  reads[0]++;
                  return (byte) 'x';
                }));
    assertEquals(4097, reads[0]);
    assertThrows(NullPointerException.class, () -> LinuxSystemdSession.decode(null));
  }

  @Test
  void unstartedDuplicateWrongPeerThreadBudgetAndUnrefFailure() throws Exception {
    try (var data = Arena.ofConfined();
        var owned = Arena.ofConfined()) {
      var calls = new Calls(data);
      var s = new LinuxSystemdSession(calls, owned);
      assertThrows(IOException.class, () -> s.owner(5000000));
      s.start(() -> 5000000);
      assertThrows(IOException.class, () -> s.start(() -> 5000000));
      assertThrows(
          IOException.class,
          () ->
              s.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.ID,
                  5000000));
      for (long micros : new long[] {0, -1, 5000001})
        assertThrows(IOException.class, () -> s.owner(micros));
      var error = new AtomicReference<Throwable>();
      var thread =
          new Thread(
              () -> {
                try {
                  s.owner(5000000);
                } catch (Throwable failure) {
                  error.set(failure);
                }
              });
      thread.start();
      thread.join();
      assertInstanceOf(IOException.class, error.get());
      calls.unique = "foreign";
      assertThrows(IOException.class, () -> s.owner(5000000));
      calls.unique = UNIQUE_BUS_NAME;
      calls.badRelease = true;
      assertThrows(IOException.class, () -> s.owner(5000000));
      assertThrows(IOException.class, s::close);
      assertFalse(s.closed());
    }
    assertThrows(
        NullPointerException.class, () -> new LinuxSystemdSession(null, Arena.ofConfined()));
    try (var data = Arena.ofConfined()) {
      assertThrows(
          NullPointerException.class, () -> new LinuxSystemdSession(new Calls(data), null));
    }
  }

  @Test
  void authenticationAndSuccessiveRpcUseOneOriginalBudget() throws Exception {
    for (boolean authentication : new boolean[] {true, false}) {
      try (var data = Arena.ofConfined()) {
        var owned = Arena.ofConfined();
        var calls = new Calls(data);
        calls.readyAfter = authentication ? Integer.MAX_VALUE : 2;
        calls.waitDelayMicros = authentication ? 2000000 : 500000;
        calls.rpcDelayMicros = authentication ? 0 : 2000000;
        var session = new LinuxSystemdSession(calls, owned);
        SystemManagerObservation.Budget budget =
            () -> {
              long left = 5000000 - calls.elapsedMicros;
              if (left < 1) throw new IOException("literal whole deadline");
              return left;
            };
        if (authentication) assertThrows(IOException.class, () -> session.start(budget));
        else {
          session.start(budget);
          assertEquals(1000000, calls.elapsedMicros);
          assertThrows(IOException.class, () -> session.owner(5000000));
          assertEquals(List.of(4000000L, 2000000L), calls.rpcBudgets);
        }
        assertEquals(5000000, calls.elapsedMicros);
        session.close();
        assertTrue(session.closed());
      }
    }
    for (String boundary : List.of(BUS_PROCESS, "sd_bus_wait")) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.readyAfter = Integer.MAX_VALUE;
        calls.failure = boundary;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(IOException.class, () -> session.start(() -> 5000000));
        assertThrows(IOException.class, session::close);
        assertFalse(session.closed());
      }
    }
  }

  @Test
  void actualImmutableBindingAndEmptySessionClosureNoServiceAction() throws Exception {
    var factory = new LinuxSystemdSession.Factory();
    var first = factory.create();
    first.close();
    assertTrue(first.closed());
    var second = factory.create();
    second.close();
    assertTrue(second.closed());
    assertNotSame(first, second);
    assertThrows(
        IOException.class,
        () -> LinuxSystemdSession.Native.bind(name -> Optional.empty(), name -> Optional.empty()));
    var actual = LinuxSystemdSession.Native.calls();
    assertThrows(IOException.class, () -> actual.call("unregistered"));
  }

  @Test
  void failedBusAllocationRemainsUnstartedAndWrongReleaseTypeIsUnconfirmed() throws Exception {
    try (var data = Arena.ofConfined()) {
      var calls = new Calls(data);
      calls.nullPointer = BUS_NEW;
      var session = new LinuxSystemdSession(calls, Arena.ofConfined());
      assertThrows(IOException.class, () -> session.start(() -> 5000000));
      assertThrows(IOException.class, () -> session.owner(5000000));
      assertFalse(session.closed());
      session.close();
      assertTrue(session.closed());
    }
    try (var data = Arena.ofConfined();
        var owned = Arena.ofConfined()) {
      var calls = new Calls(data);
      var session = new LinuxSystemdSession(calls, owned);
      session.start(() -> 5000000);
      calls.wrongType = BUS_CLOSE_UNREF;
      assertThrows(IOException.class, session::close);
      assertFalse(session.closed());
      assertThrows(IOException.class, () -> session.owner(5000000));
      assertThrows(IOException.class, session::close);
    }
  }

  @Test
  void everyPropertyRejectsExpiredSetterBeforeRpc() throws Exception {
    for (var property : SystemManagerObservation.Property.values()) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        var session = new LinuxSystemdSession(calls, owned);
        session.start(() -> 5000000 - calls.elapsedMicros);
        session.owner(5000000);
        long before = calls.events.stream().filter(n -> n.startsWith(GET_PROPERTY)).count();
        calls.expireAtSetter = true;
        assertThrows(
            IOException.class,
            () -> session.read(SystemManagerObservation.Service.API, property, 5000000));
        assertEquals(5000000, calls.elapsedMicros);
        assertEquals(before, calls.events.stream().filter(n -> n.startsWith(GET_PROPERTY)).count());
        assertFalse(session.closed());
      }
    }
  }

  @Test
  void explicitPlatformAndLibraryTrustContractsRejectMissingOrWritableMetadata() throws Exception {
    for (String arch : List.of(AMD64_ARCH, "x86_64"))
      assertEquals(
          java.nio.file.Path.of("/usr/lib/x86_64-linux-gnu/libsystemd.so.0"),
          LinuxSystemdSession.Native.library(LINUX_OS, arch, 8));
    assertEquals(
        java.nio.file.Path.of("/usr/lib/aarch64-linux-gnu/libsystemd.so.0"),
        LinuxSystemdSession.Native.library(LINUX_OS, "aarch64", 8));
    assertThrows(IOException.class, () -> LinuxSystemdSession.Native.library(null, AMD64_ARCH, 8));
    assertThrows(
        IOException.class, () -> LinuxSystemdSession.Native.library("Windows", AMD64_ARCH, 8));
    assertThrows(IOException.class, () -> LinuxSystemdSession.Native.library(LINUX_OS, null, 8));
    assertThrows(
        IOException.class, () -> LinuxSystemdSession.Native.library(LINUX_OS, "unknown", 8));
    assertThrows(
        IOException.class, () -> LinuxSystemdSession.Native.library(LINUX_OS, AMD64_ARCH, 4));
    LinuxSystemdSession.Native.trusted(Map.of(UID_KEY, 0, MODE_KEY, 0100755));
    for (var metadata :
        List.<Map<String, ?>>of(
            Map.of(),
            Map.of(UID_KEY, 1, MODE_KEY, 0100755),
            Map.of(UID_KEY, "0", MODE_KEY, 0100755),
            Map.of(UID_KEY, 0),
            Map.of(UID_KEY, 0, MODE_KEY, "755"),
            Map.of(UID_KEY, 0, MODE_KEY, 0100775),
            Map.of(UID_KEY, 0, MODE_KEY, 0100757)))
      assertThrows(IOException.class, () -> LinuxSystemdSession.Native.trusted(metadata));
    assertThrows(NullPointerException.class, () -> LinuxSystemdSession.Native.trusted(null));
  }

  @Test
  void nativeInvocationPreservesUnknownRuntimeFatalAndSanitizesCheckedFailures() throws Exception {
    assertEquals(
        "literal",
        LinuxSystemdSession.Native.invoke(
            java.lang.invoke.MethodHandles.constant(String.class, "literal"), new Object[0]));
    assertEquals(
        MemorySegment.NULL,
        LinuxSystemdSession.Native.invoke(
            java.lang.invoke.MethodHandles.empty(
                java.lang.invoke.MethodType.methodType(void.class)),
            new Object[0]));
    for (Throwable failure :
        List.of(
            new IOException("private checked"),
            new IllegalStateException("private runtime"),
            new AssertionError("private fatal"))) {
      var handle =
          java.lang.invoke.MethodHandles.throwException(Object.class, failure.getClass())
              .bindTo(failure);
      if (failure instanceof IOException) {
        var actual =
            assertThrows(
                IOException.class, () -> LinuxSystemdSession.Native.invoke(handle, new Object[0]));
        assertEquals("system manager read unavailable", actual.getMessage());
        assertNull(actual.getCause());
      } else {
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> LinuxSystemdSession.Native.invoke(handle, new Object[0])));
      }
    }
    assertThrows(IOException.class, () -> LinuxSystemdSession.Native.invoke(null, new Object[0]));
  }

  @Test
  void negativeNativeStatusesAndInvalidBudgetStayFailedButOwnedReleaseIsChecked() throws Exception {
    for (String point :
        List.of(
            BUS_NEW,
            "sd_bus_set_address",
            MESSAGE_NEW_METHOD_CALL,
            BUS_CALL,
            MESSAGE_READ_BASIC,
            GET_PROPERTY_STRING,
            GET_PROPERTY)) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.negative = point;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(
            IOException.class,
            () -> {
              session.start(() -> 5000000);
              session.owner(5000000);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.ID,
                  5000000);
              session.read(
                  SystemManagerObservation.Service.API,
                  SystemManagerObservation.Property.INVOCATION,
                  5000000);
            });
        assertFalse(session.closed());
      }
    }
    for (long bad : new long[] {0, -1, 5000001}) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var session = new LinuxSystemdSession(new Calls(data), owned);
        assertThrows(IOException.class, () -> session.start(() -> bad));
      }
    }
    try (var data = Arena.ofConfined();
        var owned = Arena.ofConfined()) {
      var calls = new Calls(data);
      calls.unique = ":1." + "1".repeat(65);
      var session = new LinuxSystemdSession(calls, owned);
      session.start(() -> 5000000);
      assertThrows(IOException.class, () -> session.owner(5000000));
      calls.unique = UNIQUE_BUS_NAME;
      session.owner(5000000);
      calls.readyAfter = Integer.MAX_VALUE;
      assertThrows(IOException.class, () -> session.owner(5000000));
    }
  }
}
