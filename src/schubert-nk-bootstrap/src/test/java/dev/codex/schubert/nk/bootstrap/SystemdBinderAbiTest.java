package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemoryLayout;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** SS354/SSC239; independent C-header vectors in NK-OPS-001/1476; no manager/library IO. */
final class SystemdBinderAbiTest {
  // Hand-fixed public sd-bus.h C signatures; never derived from Production descriptors.
  private static final List<Shape> GOLDEN =
      List.of(
          new Shape("sd_bus_new", "I:P"),
          new Shape("sd_bus_set_address", "I:PP"),
          new Shape("sd_bus_set_bus_client", "I:PI"),
          new Shape("sd_bus_set_allow_interactive_authorization", "I:PI"),
          new Shape("sd_bus_set_method_call_timeout", "I:PL"),
          new Shape("sd_bus_start", "I:P"),
          new Shape("sd_bus_is_ready", "I:P"),
          new Shape("sd_bus_process", "I:PP"),
          new Shape("sd_bus_wait", "I:PL"),
          new Shape("sd_bus_message_new_method_call", "I:PPPPPP"),
          new Shape("sd_bus_message_set_auto_start", "I:PI"),
          new Shape("sd_bus_message_append_basic", "I:PBP"),
          new Shape("sd_bus_call", "I:PPLPP"),
          new Shape("sd_bus_message_read_basic", "I:PBP"),
          new Shape("sd_bus_close_unref", "P:P"),
          new Shape("sd_bus_message_unref", "P:P"),
          new Shape("sd_bus_get_property_string", "I:PPPPPPP"),
          new Shape("sd_bus_get_property_trivial", "I:PPPPPPBP"),
          new Shape("sd_bus_get_property", "I:PPPPPPPP"),
          new Shape("sd_bus_message_read_array", "I:PBPP"),
          new Shape("free", "V:P"));

  /** PT-OPS-MANAGER-ABI-001: all symbols/argument order and two primitive/NULL boundaries. */
  @Test
  void abi001AllOwnedSymbolsDispatchIndependentBoundaryVectors() throws Exception {
    try (var fixture = new Fixture()) {
      var calls =
          LinuxSystemdSession.Native.bind(fixture.lookup(false, ""), fixture.lookup(true, ""));
      assertEquals(21, fixture.lookups.size());
      for (var shape : GOLDEN) {
        assertEquals(
            1,
            fixture.lookups.get(
                (shape.name().equals("free") ? "libc:" : "systemd:") + shape.name()));
        assertEquals(0, fixture.probes.get(shape.name()).calls);
      }
      for (int vector = 0; vector < 2; vector++) {
        for (var shape : GOLDEN) {
          var probe = fixture.probes.get(shape.name());
          Object[] expected = fixture.arguments(shape, vector);
          Object result = calls.call(shape.name(), expected);
          assertTrue(probe.unexpected == null, "owned upcall must not fail");
          assertEquals(vector + 1, probe.calls, shape.name());
          assertEquals(expected.length, probe.arguments.length, shape.name());
          for (int i = 0; i < expected.length; i++) {
            if (expected[i] instanceof MemorySegment pointer) {
              assertTrue(probe.arguments[i] instanceof MemorySegment, "pointer carrier");
              assertTrue(
                  pointer.address() == ((MemorySegment) probe.arguments[i]).address(),
                  "same owned pointer bits");
            } else assertEquals(expected[i], probe.arguments[i], shape.name() + " argument " + i);
          }
          if (shape.signature().charAt(0) == 'P') {
            assertTrue(result instanceof MemorySegment, "pointer result carrier");
            assertTrue(
                ((MemorySegment) result).address() == ((MemorySegment) probe.result).address(),
                "symbol-specific owned pointer result");
          } else if (shape.signature().charAt(0) == 'V') {
            assertEquals(MemorySegment.NULL, result);
          } else assertEquals(probe.result, result, shape.name());
        }
      }
      for (var probe : fixture.probes.values()) assertEquals(2, probe.calls);
    }
  }

  /** PT-OPS-MANAGER-ABI-002: each missing symbol and unknown dispatch fail before any stub call. */
  @Test
  void abi002MissingAndUnknownSymbolsRemainUnavailableWithoutInvocation() throws Exception {
    for (var shape : GOLDEN) {
      try (var fixture = new Fixture()) {
        IOException failure =
            assertThrows(
                IOException.class,
                () ->
                    LinuxSystemdSession.Native.bind(
                        fixture.lookup(false, shape.name()), fixture.lookup(true, shape.name())));
        assertEquals("system manager read unavailable", failure.getMessage());
        assertNull(failure.getCause());
        for (var probe : fixture.probes.values()) assertEquals(0, probe.calls);
      }
    }
    try (var fixture = new Fixture()) {
      var calls =
          LinuxSystemdSession.Native.bind(fixture.lookup(false, ""), fixture.lookup(true, ""));
      IOException failure = assertThrows(IOException.class, () -> calls.call("not_in_closed_abi"));
      assertEquals("system manager read unavailable", failure.getMessage());
      assertNull(failure.getCause());
      for (var probe : fixture.probes.values()) assertEquals(0, probe.calls);
    }
  }

  private record Shape(String name, String signature) {
    FunctionDescriptor descriptor() {
      var arguments = new MemoryLayout[signature.length() - 2];
      for (int i = 0; i < arguments.length; i++) arguments[i] = layout(signature.charAt(i + 2));
      return signature.charAt(0) == 'V'
          ? FunctionDescriptor.ofVoid(arguments)
          : FunctionDescriptor.of(layout(signature.charAt(0)), arguments);
    }
  }

  private static MemoryLayout layout(char type) {
    return switch (type) {
      case 'P' -> ValueLayout.ADDRESS;
      case 'I' -> ValueLayout.JAVA_INT;
      case 'L' -> ValueLayout.JAVA_LONG;
      case 'B' -> ValueLayout.JAVA_BYTE;
      default -> throw new AssertionError("independent golden scalar type");
    };
  }

  private static final class Probe {
    private final Object result;
    private Object[] arguments = new Object[0];
    private int calls;
    private @Nullable Throwable unexpected;

    Probe(Object result) {
      this.result = result;
    }

    Object capture(Object[] values) {
      arguments = values;
      calls++;
      return result;
    }

    Object failed(Throwable failure) {
      unexpected = failure;
      return result;
    }
  }

  private static final class Fixture implements AutoCloseable {
    private final Arena arena = Arena.ofConfined();
    private final Map<String, MemorySegment> stubs = new LinkedHashMap<>();
    private final Map<String, Probe> probes = new LinkedHashMap<>();
    private final Map<String, Integer> lookups = new LinkedHashMap<>();

    @SuppressWarnings("restricted")
    Fixture() throws ReflectiveOperationException {
      boolean complete = false;
      try {
        for (int i = 0; i < GOLDEN.size(); i++) {
          var shape = GOLDEN.get(i);
          Object returned =
              shape.signature().charAt(0) == 'P' ? arena.allocate(1) : Integer.valueOf(700 + i);
          var probe = new Probe(returned);
          var descriptor = shape.descriptor();
          var type = descriptor.toMethodType();
          var capture =
              MethodHandles.lookup()
                  .findVirtual(
                      Probe.class, "capture", MethodType.methodType(Object.class, Object[].class))
                  .bindTo(probe)
                  .asCollector(Object[].class, type.parameterCount())
                  .asType(type);
          var failure =
              MethodHandles.lookup()
                  .findVirtual(
                      Probe.class, "failed", MethodType.methodType(Object.class, Throwable.class))
                  .bindTo(probe)
                  .asType(MethodType.methodType(type.returnType(), Throwable.class));
          // JDK25 forbids exceptions escaping upcalls. Record any failure, assert AFTER return.
          var protectedCapture = MethodHandles.catchException(capture, Throwable.class, failure);
          stubs.put(
              shape.name(), Linker.nativeLinker().upcallStub(protectedCapture, descriptor, arena));
          probes.put(shape.name(), probe);
        }
        complete = true;
      } finally {
        if (!complete) arena.close();
      }
    }

    SymbolLookup lookup(boolean libc, String missing) {
      return name -> {
        lookups.merge((libc ? "libc:" : "systemd:") + name, 1, Integer::sum);
        if (libc != name.equals("free") || name.equals(missing)) return Optional.empty();
        return Optional.ofNullable(stubs.get(name));
      };
    }

    Object[] arguments(Shape shape, int vector) {
      var values = new Object[shape.signature().length() - 2];
      for (int i = 0; i < values.length; i++) {
        values[i] =
            switch (shape.signature().charAt(i + 2)) {
              case 'P' -> vector == 1 && i % 2 == 0 ? MemorySegment.NULL : arena.allocate(1);
              case 'I' -> vector == 0 ? Integer.MIN_VALUE + i : Integer.MAX_VALUE - i;
              case 'L' -> vector == 0 ? Long.MIN_VALUE + i : Long.MAX_VALUE - i;
              case 'B' -> (byte) (vector == 0 ? Byte.MIN_VALUE + i : Byte.MAX_VALUE - i);
              default -> throw new AssertionError("independent golden argument type");
            };
      }
      return values;
    }

    @Override
    public void close() {
      arena.close();
    }
  }
}
