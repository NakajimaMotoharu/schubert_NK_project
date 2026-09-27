package dev.codex.schubert.nk.batch.platform;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed effective systemd policy check before a parent stop command. Read-only and not stop
 * authority or a whole-Unit termination proof. NK-OPS-001/UI251/253/SS341/342/SSC101;
 * PT-OPS-MPOL001..008.
 */
@NullMarked
public final class MaintenanceUnitStopPolicy {
  interface Source {
    byte[] read(MaintenanceUnit unit);
  }

  static final String PROPERTIES = "Id,LoadState,KillMode,SendSIGKILL";
  private static final Set<String> KEYS = Set.copyOf(List.of(PROPERTIES.split(",")));
  private final Source source;

  public static MaintenanceUnitStopPolicy create() {
    return new MaintenanceUnitStopPolicy(new NativeSource(new InspectorUnitProbe.NativeReader()));
  }

  MaintenanceUnitStopPolicy(Source source) {
    this.source = Objects.requireNonNull(source, "fixed policy source");
  }

  public void requireSafe(MaintenanceUnit unit) {
    Objects.requireNonNull(unit, "fixed Unit");
    interrupted();
    byte[] bytes = Objects.requireNonNull(source.read(unit), "fixed policy projection");
    try {
      interrupted();
      parse(unit, bytes);
      interrupted();
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static void parse(MaintenanceUnit unit, byte[] bytes) {
    require(bytes.length > 0 && bytes.length <= 512);
    for (byte value : bytes) require(value == 10 || (value >= 32 && value <= 126));
    String[] lines = new String(bytes, StandardCharsets.US_ASCII).split("\n", -1);
    require(lines.length == 5 && lines[4].isEmpty());
    Map<String, String> fields = new HashMap<>();
    for (int i = 0; i < 4; i++) {
      int separator = lines[i].indexOf('=');
      require(separator > 0 && separator == lines[i].lastIndexOf('='));
      String key = lines[i].substring(0, separator);
      require(KEYS.contains(key));
      require(fields.putIfAbsent(key, lines[i].substring(separator + 1)) == null);
    }
    require(unit.serviceName().equals(fields.get("Id")));
    require("loaded".equals(fields.get("LoadState")));
    require("control-group".equals(fields.get("KillMode")));
    require("no".equals(fields.get("SendSIGKILL")));
  }

  private static void interrupted() {
    if (Thread.currentThread().isInterrupted())
      throw new StopGateException(StopGateFailure.INTERRUPTED);
  }

  private static void require(boolean valid) {
    if (!valid) throw new StopGateException(StopGateFailure.MALFORMED_STATE);
  }

  static final class NativeSource implements Source {
    private final InspectorUnitProbe.NativeReader reader;

    NativeSource(InspectorUnitProbe.NativeReader reader) {
      this.reader = Objects.requireNonNull(reader, "fixed systemctl reader");
    }

    public byte[] read(MaintenanceUnit unit) {
      Objects.requireNonNull(unit, "fixed Unit");
      return reader.execute(
          List.of(
              "/usr/bin/systemctl",
              "--system",
              "--no-pager",
              "--no-ask-password",
              "show",
              "--property=" + PROPERTIES,
              unit.serviceName()),
          512);
    }
  }
}
