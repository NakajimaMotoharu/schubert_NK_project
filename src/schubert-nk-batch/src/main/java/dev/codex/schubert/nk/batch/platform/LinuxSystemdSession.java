package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.ResourceScope;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.lang.foreign.Arena;
import java.lang.foreign.FunctionDescriptor;
import java.lang.foreign.Linker;
import java.lang.foreign.MemorySegment;
import java.lang.foreign.SymbolLookup;
import java.lang.foreign.ValueLayout;
import java.lang.invoke.MethodHandle;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC239 Linux LP64 libsystemd public sd-bus ABI, fixed local socket and fixed read properties.
 * NK-OPS-001/OPS009/SYS002/UI251/SS343354; PT-OPS-MANAGER817007..012. ABI: systemd v257 sd-bus.h,
 * independently rechecked for the deployed Ubuntu library. No environment bus address,
 * process/shell, fallback, mutable state cache or remote endpoint.
 */
@NullMarked
final class LinuxSystemdSession implements LinuxSystemdQuery.Session {
  private static final String DESTINATION = "org.freedesktop.systemd1";

  @FunctionalInterface
  interface Calls {
    Object call(String symbol, Object... arguments) throws IOException;
  }

  private final Calls calls;
  private final Arena arena;
  private final long thread = Thread.currentThread().threadId();
  private MemorySegment bus = MemorySegment.NULL;
  private boolean closed;
  private boolean uncertain;
  private @Nullable String peer;
  private LinuxSystemdQuery.@Nullable Budget budget;

  LinuxSystemdSession(Calls calls, Arena arena) {
    this.calls = Objects.requireNonNull(calls);
    this.arena = Objects.requireNonNull(arena);
  }

  static final class Factory {
    private @Nullable Calls binding;

    LinuxSystemdSession create() throws IOException {
      // Only immutable native ABI handles are shared. Every bus/owner/property read is fresh.
      if (binding == null) binding = Native.calls();
      return new LinuxSystemdSession(binding, Arena.ofConfined());
    }
  }

  private void check() throws IOException {
    if (closed || uncertain || thread != Thread.currentThread().threadId())
      throw LinuxSystemdQuery.unavailable();
  }

  private MemorySegment text(String value) {
    return arena.allocateFrom(value);
  }

  private int integer(String symbol, Object... args) throws IOException {
    Object value = call(symbol, args);
    if (!(value instanceof Integer code) || code < 0) throw LinuxSystemdQuery.unavailable();
    return code;
  }

  private Object call(String symbol, Object... args) throws IOException {
    try {
      return calls.call(symbol, args);
    } catch (IOException | RuntimeException | Error failure) {
      // Native-call uncertainty is not a normal close. The query retains this session/arena.
      uncertain = true;
      throw failure;
    }
  }

  private MemorySegment pointer() {
    return arena.allocate(ValueLayout.ADDRESS);
  }

  private long remaining(long micros) throws IOException {
    check();
    var current = budget;
    if (current == null || bus.address() == 0 || micros < 1 || micros > 5_000_000)
      throw LinuxSystemdQuery.unavailable();
    long left = current.remainingMicros();
    if (left < 1 || left > 5_000_000) throw LinuxSystemdQuery.unavailable();
    return Math.min(micros, left);
  }

  private void timeout(long micros) throws IOException {
    long left = remaining(micros);
    if (integer("sd_bus_is_ready", bus) != 1) throw LinuxSystemdQuery.unavailable();
    integer("sd_bus_set_method_call_timeout", bus, left);
    remaining(micros); // Setter/ready work must not cross the original deadline before sending.
  }

  @Override
  public void start(LinuxSystemdQuery.Budget source) throws IOException {
    check();
    Objects.requireNonNull(source);
    if (bus.address() != 0) throw LinuxSystemdQuery.unavailable();
    budget = source;
    MemorySegment result = pointer();
    Object status = call("sd_bus_new", result);
    bus = result.get(ValueLayout.ADDRESS, 0); // Capture ownership even if the status is a failure.
    if (!(status instanceof Integer code) || code < 0 || bus.address() == 0)
      throw LinuxSystemdQuery.unavailable();
    integer("sd_bus_set_method_call_timeout", bus, remaining(5_000_000));
    integer("sd_bus_set_address", bus, text("unix:path=/run/dbus/system_bus_socket"));
    integer("sd_bus_set_bus_client", bus, 1);
    integer("sd_bus_set_allow_interactive_authorization", bus, 0);
    integer("sd_bus_start", bus);
    // BUS_RUNNING is established with bounded process/wait before any synchronous RPC.
    // sd_bus_call's implicit bus_ensure_running would otherwise wait without our deadline.
    while (integer("sd_bus_is_ready", bus) != 1) {
      remaining(5_000_000);
      if (integer("sd_bus_process", bus, MemorySegment.NULL) == 0)
        integer("sd_bus_wait", bus, remaining(5_000_000));
    }
    remaining(5_000_000);
  }

  @Override
  public LinuxSystemdQuery.Owner owner(long micros) throws IOException {
    String unique = ownerValue("GetNameOwner", DESTINATION, 's', micros);
    if (unique.length() > 64 || !unique.matches(":[0-9]+\\.[0-9]+"))
      throw LinuxSystemdQuery.unavailable();
    int pid =
        Integer.parseUnsignedInt(ownerValue("GetConnectionUnixProcessID", unique, 'u', micros));
    int euid = Integer.parseUnsignedInt(ownerValue("GetConnectionUnixUser", unique, 'u', micros));
    var owner = new LinuxSystemdQuery.Owner(pid, euid, unique);
    peer = unique;
    return owner;
  }

  private String ownerValue(String member, String argument, char kind, long micros)
      throws IOException {
    timeout(micros);
    MemorySegment result = pointer();
    Object status =
        call(
            "sd_bus_message_new_method_call",
            bus,
            result,
            text("org.freedesktop.DBus"),
            text("/org/freedesktop/DBus"),
            text("org.freedesktop.DBus"),
            text(member));
    MemorySegment request = result.get(ValueLayout.ADDRESS, 0);
    return ResourceScope.use(
        () -> release("sd_bus_message_unref", request),
        () -> {
          if (!(status instanceof Integer code) || code < 0 || request.address() == 0)
            throw LinuxSystemdQuery.unavailable();
          integer("sd_bus_message_set_auto_start", request, 0);
          integer("sd_bus_message_append_basic", request, (byte) 's', text(argument));
          var output = pointer();
          // Each explicit RPC receives the original query's remaining budget, never renewed.
          timeout(micros);
          Object called =
              call("sd_bus_call", bus, request, remaining(micros), MemorySegment.NULL, output);
          MemorySegment reply = output.get(ValueLayout.ADDRESS, 0);
          return ResourceScope.use(
              () -> release("sd_bus_message_unref", reply),
              () -> {
                if (!(called instanceof Integer ok) || ok < 0 || reply.address() == 0)
                  throw LinuxSystemdQuery.unavailable();
                var value = kind == 's' ? pointer() : arena.allocate(ValueLayout.JAVA_INT);
                if (integer("sd_bus_message_read_basic", reply, (byte) kind, value) != 1)
                  throw LinuxSystemdQuery.unavailable();
                remaining(micros);
                return kind == 's'
                    ? string(value.get(ValueLayout.ADDRESS, 0))
                    : Integer.toUnsignedString(value.get(ValueLayout.JAVA_INT, 0));
              });
        });
  }

  @Override
  @SuppressWarnings("restricted")
  public String read(
      RootStartupContext.Service service, LinuxSystemdQuery.Property property, long micros)
      throws IOException {
    Objects.requireNonNull(service);
    Objects.requireNonNull(property);
    remaining(micros);
    MemorySegment path =
        text(
            "/org/freedesktop/systemd1/unit/"
                + service.unit().replace("_", "_5f").replace("-", "_2d").replace(".", "_2e"));
    String unique = peer;
    if (unique == null) throw LinuxSystemdQuery.unavailable();
    // peer is established only by owner(), after its strict unique-name validation.
    // A unique bus name cannot auto-activate a service if its captured owner disappears.
    MemorySegment destination = text(unique);
    MemorySegment type = text("org.freedesktop.systemd1." + property.kind);
    MemorySegment name = text(property.member);
    if (property.type == 's') {
      var result = pointer();
      timeout(micros);
      Object status =
          call(
              "sd_bus_get_property_string",
              bus,
              destination,
              path,
              type,
              name,
              MemorySegment.NULL,
              result);
      MemorySegment value = result.get(ValueLayout.ADDRESS, 0);
      return ResourceScope.use(
          () -> {
            if (value.address() != 0) call("free", value);
          },
          () -> {
            if (!(status instanceof Integer code) || code < 0)
              throw LinuxSystemdQuery.unavailable();
            return string(value);
          });
    }
    if (property.type == 'u' || property.type == 't') {
      var value = arena.allocate(ValueLayout.JAVA_LONG);
      timeout(micros);
      integer(
          "sd_bus_get_property_trivial",
          bus,
          destination,
          path,
          type,
          name,
          MemorySegment.NULL,
          (byte) property.type,
          value);
      return property.type == 'u'
          ? Integer.toUnsignedString(value.get(ValueLayout.JAVA_INT, 0))
          : Long.toUnsignedString(value.get(ValueLayout.JAVA_LONG, 0));
    }
    var result = pointer();
    var signature = text("ay");
    timeout(micros);
    Object status =
        call(
            "sd_bus_get_property",
            bus,
            destination,
            path,
            type,
            name,
            MemorySegment.NULL,
            result,
            signature);
    MemorySegment message = result.get(ValueLayout.ADDRESS, 0);
    return ResourceScope.use(
        () -> release("sd_bus_message_unref", message),
        () -> {
          if (!(status instanceof Integer code) || code < 0 || message.address() == 0)
            throw LinuxSystemdQuery.unavailable();
          var data = pointer();
          var size = arena.allocate(ValueLayout.JAVA_LONG);
          integer("sd_bus_message_read_array", message, (byte) 'y', data, size);
          long length = size.get(ValueLayout.JAVA_LONG, 0);
          if (length == 0) return "";
          MemorySegment value = data.get(ValueLayout.ADDRESS, 0);
          if (length != 16 || value.address() == 0) throw LinuxSystemdQuery.unavailable();
          return HexFormat.of().formatHex(value.reinterpret(16).toArray(ValueLayout.JAVA_BYTE));
        });
  }

  @SuppressWarnings("restricted")
  private static String string(MemorySegment value) throws IOException {
    if (value.address() == 0) throw LinuxSystemdQuery.unavailable();
    MemorySegment memory = value.reinterpret(4097);
    return decode(index -> memory.get(ValueLayout.JAVA_BYTE, index));
  }

  @FunctionalInterface
  interface Octets {
    byte read(int index);
  }

  static String decode(Octets memory) throws IOException {
    Objects.requireNonNull(memory);
    byte[] bytes = new byte[4097];
    // sd-bus supplies a NUL-terminated owned/borrowed C string. Only read up to that NUL.
    int end = 0;
    while (end < bytes.length) {
      byte octet = memory.read(end);
      if (octet == 0) break;
      bytes[end++] = octet;
    }
    if (end > 4096) throw LinuxSystemdQuery.unavailable();
    return new String(bytes, 0, end, java.nio.charset.StandardCharsets.UTF_8);
  }

  private void release(String symbol, MemorySegment value) throws IOException {
    if (value.address() == 0) return;
    Object after = call(symbol, value);
    if (!(after instanceof MemorySegment pointer) || pointer.address() != 0) {
      uncertain = true;
      throw LinuxSystemdQuery.unavailable();
    }
  }

  @Override
  public void close() throws IOException {
    check();
    release("sd_bus_close_unref", bus);
    arena.close();
    closed = true;
  }

  @Override
  public boolean closed() {
    return closed;
  }

  static final class Native {
    private Native() {}

    @SuppressWarnings("restricted")
    static Calls calls() throws IOException {
      Path path =
          library(
              System.getProperty("os.name", ""),
              System.getProperty("os.arch", ""),
              ValueLayout.ADDRESS.byteSize());
      Path real = path.toRealPath();
      for (Path current = real; current != null; current = current.getParent()) {
        var attributes = Files.readAttributes(current, "unix:uid,mode", LinkOption.NOFOLLOW_LINKS);
        trusted(attributes);
      }
      SymbolLookup systemd = SymbolLookup.libraryLookup(real, Arena.global());
      SymbolLookup libc = Linker.nativeLinker().defaultLookup();
      return bind(systemd, libc);
    }

    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC239 fixed protected Linux ABI library, no caller path. BUG957/MANAGER817012.")
    static Path library(@Nullable String os, @Nullable String arch, long addressBytes)
        throws IOException {
      if (!"Linux".equals(os)
          || addressBytes != 8
          || arch == null
          || !Set.of("amd64", "x86_64", "aarch64").contains(arch))
        throw LinuxSystemdQuery.unavailable();
      return Path.of(
          "/usr/lib",
          arch.equals("aarch64") ? "aarch64-linux-gnu" : "x86_64-linux-gnu",
          "libsystemd.so.0");
    }

    static void trusted(Map<String, ?> attributes) throws IOException {
      Objects.requireNonNull(attributes);
      if (!Integer.valueOf(0).equals(attributes.get("uid"))
          || !(attributes.get("mode") instanceof Integer mode)
          || (mode & 0022) != 0) throw LinuxSystemdQuery.unavailable();
    }

    @SuppressWarnings("restricted")
    static Calls bind(SymbolLookup systemd, SymbolLookup libc) throws IOException {
      var handles = new HashMap<String, MethodHandle>();
      var pointer = ValueLayout.ADDRESS;
      var integer = ValueLayout.JAVA_INT;
      var longValue = ValueLayout.JAVA_LONG;
      var octet = ValueLayout.JAVA_BYTE;
      var descriptors =
          Map.ofEntries(
              Map.entry("sd_bus_new", FunctionDescriptor.of(integer, pointer)),
              Map.entry("sd_bus_set_address", FunctionDescriptor.of(integer, pointer, pointer)),
              Map.entry("sd_bus_set_bus_client", FunctionDescriptor.of(integer, pointer, integer)),
              Map.entry(
                  "sd_bus_set_allow_interactive_authorization",
                  FunctionDescriptor.of(integer, pointer, integer)),
              Map.entry(
                  "sd_bus_set_method_call_timeout",
                  FunctionDescriptor.of(integer, pointer, longValue)),
              Map.entry("sd_bus_start", FunctionDescriptor.of(integer, pointer)),
              Map.entry("sd_bus_is_ready", FunctionDescriptor.of(integer, pointer)),
              Map.entry("sd_bus_process", FunctionDescriptor.of(integer, pointer, pointer)),
              Map.entry("sd_bus_wait", FunctionDescriptor.of(integer, pointer, longValue)),
              Map.entry(
                  "sd_bus_message_new_method_call",
                  FunctionDescriptor.of(
                      integer, pointer, pointer, pointer, pointer, pointer, pointer)),
              Map.entry(
                  "sd_bus_message_set_auto_start",
                  FunctionDescriptor.of(integer, pointer, integer)),
              Map.entry(
                  "sd_bus_message_append_basic",
                  FunctionDescriptor.of(integer, pointer, octet, pointer)),
              Map.entry(
                  "sd_bus_call",
                  FunctionDescriptor.of(integer, pointer, pointer, longValue, pointer, pointer)),
              Map.entry(
                  "sd_bus_message_read_basic",
                  FunctionDescriptor.of(integer, pointer, octet, pointer)),
              Map.entry("sd_bus_close_unref", FunctionDescriptor.of(pointer, pointer)),
              Map.entry("sd_bus_message_unref", FunctionDescriptor.of(pointer, pointer)),
              Map.entry(
                  "sd_bus_get_property_string",
                  FunctionDescriptor.of(
                      integer, pointer, pointer, pointer, pointer, pointer, pointer, pointer)),
              Map.entry(
                  "sd_bus_get_property_trivial",
                  FunctionDescriptor.of(
                      integer, pointer, pointer, pointer, pointer, pointer, pointer, octet,
                      pointer)),
              Map.entry(
                  "sd_bus_get_property",
                  FunctionDescriptor.of(
                      integer, pointer, pointer, pointer, pointer, pointer, pointer, pointer,
                      pointer)),
              Map.entry(
                  "sd_bus_message_read_array",
                  FunctionDescriptor.of(integer, pointer, octet, pointer, pointer)),
              Map.entry("free", FunctionDescriptor.ofVoid(pointer)));
      for (var entry : descriptors.entrySet()) {
        SymbolLookup lookup = entry.getKey().equals("free") ? libc : systemd;
        var address = lookup.find(entry.getKey()).orElseThrow(LinuxSystemdQuery::unavailable);
        handles.put(
            entry.getKey(), Linker.nativeLinker().downcallHandle(address, entry.getValue()));
      }
      return (symbol, arguments) -> invoke(handles.get(symbol), arguments);
    }

    static Object invoke(@Nullable MethodHandle handle, Object[] arguments) throws IOException {
      try {
        if (handle == null) throw LinuxSystemdQuery.unavailable();
        Object value = handle.invokeWithArguments(arguments);
        return value == null ? MemorySegment.NULL : value;
      } catch (RuntimeException | Error failure) {
        throw failure;
      } catch (Throwable failure) {
        throw LinuxSystemdQuery.unavailable();
      }
    }
  }
}
