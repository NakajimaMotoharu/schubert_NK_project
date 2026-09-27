package dev.codex.schubert.nk.bootstrap;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Canonical public root-to-child snapshot only, never an authorization by itself. NK-OPS-001;
 * SYS-002/004,OPS-009; UI212/251; SS341/342/343; SSC086/087; PG295; PT-OPS-PROOF-001..008. Native
 * root ownership/seals/A and fresh process/Unit identity must be admitted before consuming these
 * fields. Root-only facts are attested by that admitted emitter; child reobserves only its own
 * identity/readable config/release/app capabilities. Proof's own reserved FD is deliberately
 * absent: it is allocated after sealing, and never guessed.
 */
@NullMarked
public final class StartupProofFrame {
  private static final BigInteger U64 = new BigInteger("18446744073709551615");
  private static final BigInteger ID_MAX = new BigInteger("4294967294");
  private static final String UUID_PATTERN =
      "(?!00000000-0000-0000-0000-000000000000$)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}";
  private static final String INVOCATION_PATTERN = "(?!0{32}$)[0-9a-f]{32}";
  private static final String SHA_PATTERN = "[0-9a-f]{64}";
  private static final List<Field> SCHEMA =
      List.of(
          text("service", "(API|WEB)"),
          text("boot_id", UUID_PATTERN),
          text("invocation_id", INVOCATION_PATTERN),
          number("pid", 2, BigInteger.valueOf(Integer.MAX_VALUE)),
          number("start_ticks", 1, BigInteger.valueOf(Long.MAX_VALUE)),
          number("admission_fd", 128, BigInteger.valueOf(65535)),
          number("admission_device", 1, U64),
          number("admission_inode", 1, U64),
          number("service_uid", 1, ID_MAX),
          number("service_gid", 1, ID_MAX),
          text("service_groups", "[1-9][0-9]{0,9}(,[1-9][0-9]{0,9}){0,15}"),
          text("permit_epoch", UUID_PATTERN),
          text("permit_sha256", SHA_PATTERN),
          text("release_sha256", SHA_PATTERN),
          text("config_sha256", SHA_PATTERN),
          text("roots_sha256", SHA_PATTERN),
          text("broker_invocation_id", INVOCATION_PATTERN));
  private static final Set<String> NAMES = Set.copyOf(SCHEMA.stream().map(Field::name).toList());
  private final Map<String, String> values;

  private StartupProofFrame(Map<String, String> values) {
    this.values = values;
  }

  public static StartupProofFrame fromFields(Map<String, String> input) {
    var values = Map.copyOf(Objects.requireNonNull(input, "proof fields"));
    require(values.keySet().equals(NAMES));
    for (Field field : SCHEMA) {
      String value = Objects.requireNonNull(values.get(field.name()), "proof invariant");
      require(value.matches(field.pattern()));
      if (field.bounds().isPresent()) {
        var range = field.bounds().orElseThrow();
        var number = new BigInteger(value);
        require(number.compareTo(range.minimum()) >= 0 && number.compareTo(range.maximum()) <= 0);
      }
    }
    BigInteger previous = BigInteger.ZERO;
    for (String value : Objects.requireNonNull(values.get("service_groups")).split(",")) {
      var group = new BigInteger(value);
      require(group.compareTo(previous) > 0 && group.compareTo(ID_MAX) <= 0);
      previous = group;
    }
    return new StartupProofFrame(values);
  }

  public static StartupProofFrame parse(byte[] input) {
    Objects.requireNonNull(input, "proof bytes");
    require(input.length > 0 && input.length <= 8192);
    byte[] copy = input.clone();
    try {
      for (byte value : copy) require(value == 10 || (value >= 32 && value <= 126));
      String[] lines = new String(copy, StandardCharsets.US_ASCII).split("\n", -1);
      require(lines.length == SCHEMA.size() + 2);
      require(lines[0].equals("NKSTART1") && lines[lines.length - 1].isEmpty());
      var values = new HashMap<String, String>();
      for (int i = 0; i < SCHEMA.size(); i++) {
        String prefix = SCHEMA.get(i).name() + "=";
        require(lines[i + 1].startsWith(prefix));
        values.put(SCHEMA.get(i).name(), lines[i + 1].substring(prefix.length()));
      }
      return fromFields(values);
    } finally {
      Arrays.fill(copy, (byte) 0);
    }
  }

  public byte[] encode() {
    var output = new StringBuilder("NKSTART1\n");
    for (Field field : SCHEMA)
      output.append(field.name()).append('=').append(value(field.name())).append('\n');
    return output.toString().getBytes(StandardCharsets.US_ASCII);
  }

  public String value(String name) {
    Objects.requireNonNull(name, "proof field name");
    require(NAMES.contains(name));
    return Objects.requireNonNull(values.get(name), "proof invariant");
  }

  public Map<String, String> fields() {
    return Collections.unmodifiableMap(new HashMap<>(values));
  }

  @Override
  public String toString() {
    return "StartupProofFrame[REDACTED]";
  }

  private static Field text(String name, String pattern) {
    return new Field(name, pattern, Optional.empty());
  }

  private static Field number(String name, long minimum, BigInteger maximum) {
    return new Field(
        name, "[1-9][0-9]{0,19}", Optional.of(new Bounds(BigInteger.valueOf(minimum), maximum)));
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("invalid startup proof frame");
  }

  private record Bounds(BigInteger minimum, BigInteger maximum) {}

  private record Field(String name, String pattern, Optional<Bounds> bounds) {}
}
