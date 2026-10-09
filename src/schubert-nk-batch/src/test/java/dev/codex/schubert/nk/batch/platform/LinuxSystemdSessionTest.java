package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.lang.foreign.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Literal sd-bus ABI arguments and independently allocated C reply vectors; MANAGER817007..012. */
final class LinuxSystemdSessionTest {
  static final class Calls implements LinuxSystemdSession.Calls {
    final Arena data;
    final MemorySegment bus, creds, message;
    final List<String> events = new ArrayList<>();
    String failure = "", wrongType = "", nullPointer = "", unique = ":1.7", string = "loaded";
    int arrayLength = 16;
    boolean badRelease;

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
      switch (name) {
        case "sd_bus_new" ->
            segment(a[0])
                .set(ValueLayout.ADDRESS, 0, name.equals(nullPointer) ? MemorySegment.NULL : bus);
        case "sd_bus_set_address" ->
            assertEquals("unix:path=/run/dbus/system_bus_socket", segment(a[1]).getString(0));
        case "sd_bus_set_bus_client" -> assertEquals(1, a[1]);
        case "sd_bus_set_allow_interactive_authorization" -> assertEquals(0, a[1]);
        case "sd_bus_get_name_creds" -> {
          assertEquals("org.freedesktop.systemd1", segment(a[1]).getString(0));
          assertEquals(2147483657L, a[2]);
          segment(a[3])
              .set(ValueLayout.ADDRESS, 0, name.equals(nullPointer) ? MemorySegment.NULL : creds);
        }
        case "sd_bus_creds_get_pid" -> segment(a[1]).set(ValueLayout.JAVA_INT, 0, 1);
        case "sd_bus_creds_get_uid" -> segment(a[1]).set(ValueLayout.JAVA_INT, 0, 0);
        case "sd_bus_creds_get_unique_name" ->
            segment(a[1])
                .set(
                    ValueLayout.ADDRESS,
                    0,
                    name.equals(nullPointer) ? MemorySegment.NULL : data.allocateFrom(unique));
        case "sd_bus_get_property_string", "sd_bus_get_property_trivial", "sd_bus_get_property" -> {
          assertEquals(":1.7", segment(a[1]).getString(0));
          assertEquals(
              "/org/freedesktop/systemd1/unit/schubert_2dnk_2dapi_2eservice",
              segment(a[2]).getString(0));
          String member = segment(a[4]).getString(0);
          if (name.equals("sd_bus_get_property_string")) {
            assertEquals("org.freedesktop.systemd1.Unit", segment(a[3]).getString(0));
            segment(a[6])
                .set(
                    ValueLayout.ADDRESS,
                    0,
                    name.equals(nullPointer) ? MemorySegment.NULL : data.allocateFrom(string));
          } else if (name.equals("sd_bus_get_property_trivial")) {
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
        case "sd_bus_creds_unref", "sd_bus_message_unref", "sd_bus_close_unref" -> {
          return badRelease ? bus : MemorySegment.NULL;
        }
        case "free", "sd_bus_start", "sd_bus_set_method_call_timeout" -> {}
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
      session.start(5000000);
      assertEquals(new LinuxSystemdQuery.Owner(1, 0, ":1.7"), session.owner(4999999));
      assertEquals(
          "loaded",
          session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.LOAD, 4999998));
      assertEquals(
          "4294967295",
          session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.PID, 4999997));
      assertEquals(
          "18446744073709551615",
          session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.START, 4999996));
      assertEquals(
          "00112233445566778899aabbccddeeff",
          session.read(
              RootStartupContext.Service.API, LinuxSystemdQuery.Property.INVOCATION, 4999995));
      session.close();
      assertTrue(session.closed());
      assertTrue(
          calls.events.containsAll(
              List.of("free", "sd_bus_creds_unref", "sd_bus_message_unref", "sd_bus_close_unref")));
      assertThrows(IOException.class, session::close);
    }
  }

  @Test
  void everyNativeCallExceptionIsNotNormalClose() throws Exception {
    for (String failure :
        List.of(
            "sd_bus_new",
            "sd_bus_set_method_call_timeout",
            "sd_bus_set_address",
            "sd_bus_set_bus_client",
            "sd_bus_set_allow_interactive_authorization",
            "sd_bus_start",
            "sd_bus_get_name_creds",
            "sd_bus_creds_get_pid",
            "sd_bus_creds_get_uid",
            "sd_bus_creds_get_unique_name",
            "sd_bus_creds_unref",
            "sd_bus_get_property_string",
            "free",
            "sd_bus_get_property_trivial",
            "sd_bus_get_property",
            "sd_bus_message_read_array",
            "sd_bus_message_unref",
            "sd_bus_close_unref")) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.failure = failure;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(
            IOException.class,
            () -> {
              session.start(5000000);
              session.owner(4999999);
              session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.ID, 4999998);
              session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.PID, 4999997);
              session.read(
                  RootStartupContext.Service.API, LinuxSystemdQuery.Property.INVOCATION, 4999996);
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
            "sd_bus_new",
            "sd_bus_get_name_creds",
            "sd_bus_creds_get_unique_name",
            "sd_bus_get_property_string",
            "sd_bus_get_property",
            "sd_bus_message_read_array")) {
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.nullPointer = bad;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(
            IOException.class,
            () -> {
              session.start(5000000);
              session.owner(4999999);
              session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.ID, 4999998);
              session.read(
                  RootStartupContext.Service.API, LinuxSystemdQuery.Property.INVOCATION, 4999997);
            });
      }
    }
    for (int length : new int[] {-1, 1, 15, 17, Integer.MAX_VALUE})
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.arrayLength = length;
        var session = new LinuxSystemdSession(calls, owned);
        session.start(5000000);
        session.owner(4999999);
        assertThrows(
            IOException.class,
            () ->
                session.read(
                    RootStartupContext.Service.API,
                    LinuxSystemdQuery.Property.INVOCATION,
                    4999998));
      }
    try (var data = Arena.ofConfined();
        var owned = Arena.ofConfined()) {
      var calls = new Calls(data);
      calls.arrayLength = 0;
      var session = new LinuxSystemdSession(calls, owned);
      session.start(5000000);
      session.owner(4999999);
      assertEquals(
          "",
          session.read(
              RootStartupContext.Service.API, LinuxSystemdQuery.Property.INVOCATION, 4999998));
    }
    for (String bad :
        List.of(
            "sd_bus_new",
            "sd_bus_get_name_creds",
            "sd_bus_get_property_string",
            "sd_bus_get_property",
            "sd_bus_get_property_trivial"))
      try (var data = Arena.ofConfined();
          var owned = Arena.ofConfined()) {
        var calls = new Calls(data);
        calls.wrongType = bad;
        var session = new LinuxSystemdSession(calls, owned);
        assertThrows(
            IOException.class,
            () -> {
              session.start(5000000);
              session.owner(4999999);
              session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.ID, 4999998);
              session.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.PID, 4999997);
              session.read(
                  RootStartupContext.Service.API, LinuxSystemdQuery.Property.INVOCATION, 4999996);
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
      s.start(5000000);
      assertThrows(IOException.class, () -> s.start(5000000));
      assertThrows(
          IOException.class,
          () -> s.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.ID, 5000000));
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
      s.owner(5000000);
      assertThrows(
          IOException.class,
          () -> s.read(RootStartupContext.Service.API, LinuxSystemdQuery.Property.ID, 5000000));
      calls.unique = ":1.7";
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
}
