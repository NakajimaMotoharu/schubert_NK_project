package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;
import org.snakeyaml.engine.v2.api.Load;
import org.snakeyaml.engine.v2.api.LoadSettings;

/**
 * SS343 §4–5 non-secret Web layers only. File identity, env location, credential distribution and
 * real root admission remain caller responsibilities. NK-OPS-001; RD SYS-002/004, AUT-002, MED-001;
 * UI212/223/226/237/253; PG273/PT-OPS-WEB-CFG-001..006.
 */
@NullMarked
public final class WebNonSecretConfig {
  private static final String RETAINED_INVALID = "Web non-secret configuration unavailable";
  private static final Pattern RETAINED_DECIMAL = Pattern.compile("0|[1-9][0-9]{0,4}");
  private static final Pattern MILLIS = Pattern.compile("([1-9][0-9]{0,3})ms");
  private static final Pattern SECONDS = Pattern.compile("([1-9][0-9]?)s");
  private static final Pattern DB_URL =
      Pattern.compile(
          "jdbc:postgresql://127\\.0\\.0\\.1:([1-9][0-9]{0,4})/([a-z_][a-z0-9_]{0,62})");
  private static final Pattern MQ_URL = Pattern.compile("tcp://127\\.0\\.0\\.1:([1-9][0-9]{0,4})");
  private static final Map<String, String> DEFAULTS =
      Map.ofEntries(
          Map.entry("nk.protocol.version", "001"),
          Map.entry("nk.time.display-zone", "Asia/Tokyo"),
          Map.entry("nk.monitoring.mode", "STANDARD"),
          Map.entry("nk.db.url", "jdbc:postgresql://127.0.0.1:5432/schubert_nk"),
          Map.entry("nk.mq.url", "tcp://127.0.0.1:61616"),
          Map.entry("nk.db.pool.web.max", "2"),
          Map.entry("nk.db.pool.web.min", "1"),
          Map.entry("nk.db.connect-timeout", "3s"),
          Map.entry("nk.web.http.address", "127.0.0.1"),
          Map.entry("nk.web.http.port", "8080"),
          Map.entry("nk.web.management.port", "8081"),
          Map.entry("nk.web.mq.reply-timeout", "2s"),
          Map.entry("nk.web.mq.wait.initial", "12"),
          Map.entry("nk.web.mq.wait.max", "20"),
          Map.entry("nk.web.session.idle-timeout", "8h"),
          Map.entry("nk.web.session.max-per-user", "2"),
          Map.entry("nk.web.storage.asset-root", "/srv/schubert-nk/data/assets"),
          Map.entry("nk.web.storage.transfer-root", "/srv/schubert-nk/data/transfer"),
          Map.entry("nk.web.media.max-streams", "20"),
          Map.entry("nk.web.media.max-range-bytes", "1048576"));
  private static final Set<String> COMMON_KEYS =
      Set.of("nk.protocol.version", "nk.time.display-zone", "nk.monitoring.mode");
  private static final Set<String> WEB_KEYS =
      DEFAULTS.keySet().stream()
          .filter(key -> !COMMON_KEYS.contains(key))
          .collect(java.util.stream.Collectors.toUnmodifiableSet());
  private static final LoadSettings YAML_SETTINGS =
      LoadSettings.builder()
          .setAllowDuplicateKeys(false)
          .setAllowRecursiveKeys(false)
          .setAllowNonScalarKeys(false)
          .setMaxAliasesForCollections(0)
          .setCodePointLimit(16_384)
          .build();

  private final Map<String, String> values;
  private final String retainedCanonicalSha256;

  private WebNonSecretConfig(Map<String, String> values, String canonicalSha256) {
    this.values = Map.copyOf(values);
    this.retainedCanonicalSha256 = canonicalSha256;
  }

  public static WebNonSecretConfig parse(String commonYaml, String webYaml)
      throws NoSuchAlgorithmException {
    Objects.requireNonNull(commonYaml, "common YAML");
    Objects.requireNonNull(webYaml, "Web YAML");
    var values = new TreeMap<>(DEFAULTS);
    values.putAll(parseSource(commonYaml, COMMON_KEYS));
    values.putAll(parseSource(webYaml, WEB_KEYS));
    validate(values);
    var canonical = new StringBuilder();
    values.forEach((key, value) -> canonical.append(key).append('=').append(value).append('\n'));
    String hash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(canonical.toString().getBytes(StandardCharsets.UTF_8)));
    return new WebNonSecretConfig(values, hash);
  }

  private static Map<String, String> parseSource(String yaml, Set<String> allowed) {
    if (yaml.getBytes(StandardCharsets.UTF_8).length > 16_384
        || yaml.indexOf('\r') >= 0
        || yaml.indexOf('\uFEFF') >= 0
        || yaml.indexOf('&') >= 0
        || yaml.indexOf('*') >= 0
        || yaml.contains("${")) throw invalid();
    try {
      Object parsed = new Load(YAML_SETTINGS).loadFromString(yaml);
      if (parsed == null && yaml.isBlank()) return Map.of();
      if (!(parsed instanceof Map<?, ?> mapping)) throw invalid();
      var values = new TreeMap<String, String>();
      for (var entry : mapping.entrySet()) {
        if (!(entry.getKey() instanceof String key)
            || !allowed.contains(key)
            || !(entry.getValue() instanceof String || entry.getValue() instanceof Integer))
          throw invalid();
        String value = entry.getValue().toString();
        if (value.isBlank() || value.contains("${") || value.indexOf('\n') >= 0) throw invalid();
        values.put(key, value);
      }
      return values;
    } catch (RuntimeException failure) {
      StorageIoException.preserveFatal(failure);
      throw invalid();
    }
  }

  private static void validate(Map<String, String> values) {
    for (String key :
        Set.of(
            "nk.protocol.version",
            "nk.time.display-zone",
            "nk.web.http.address",
            "nk.web.session.idle-timeout",
            "nk.web.session.max-per-user",
            "nk.db.pool.web.max",
            "nk.db.pool.web.min",
            "nk.db.connect-timeout",
            "nk.web.media.max-range-bytes"))
      if (!Objects.requireNonNull(DEFAULTS.get(key)).equals(values.get(key))) throw invalid();
    if (!Set.of("STANDARD", "DEBUG").contains(values.get("nk.monitoring.mode"))) throw invalid();
    if (!validPort(DB_URL, Objects.requireNonNull(values.get("nk.db.url")))
        || !validPort(MQ_URL, Objects.requireNonNull(values.get("nk.mq.url")))) throw invalid();
    int http = decimal(Objects.requireNonNull(values.get("nk.web.http.port")), 1, 65_535);
    int management =
        decimal(Objects.requireNonNull(values.get("nk.web.management.port")), 1, 65_535);
    if (http == management) throw invalid();
    String timeout = Objects.requireNonNull(values.get("nk.web.mq.reply-timeout"));
    int milliseconds;
    var ms = MILLIS.matcher(timeout);
    if (ms.matches()) {
      milliseconds = Integer.parseInt(Objects.requireNonNull(ms.group(1)));
    } else {
      var seconds = SECONDS.matcher(timeout);
      if (!seconds.matches()) throw invalid();
      milliseconds = 1000 * Integer.parseInt(Objects.requireNonNull(seconds.group(1)));
    }
    if (milliseconds < 100 || milliseconds > 2000) throw invalid();
    int initial = decimal(Objects.requireNonNull(values.get("nk.web.mq.wait.initial")), 1, 20);
    int max = decimal(Objects.requireNonNull(values.get("nk.web.mq.wait.max")), 1, 20);
    if (initial > max) throw invalid();
    decimal(Objects.requireNonNull(values.get("nk.web.media.max-streams")), 1, 20);
    try {
      Path asset = Path.of(Objects.requireNonNull(values.get("nk.web.storage.asset-root")));
      Path transfer = Path.of(Objects.requireNonNull(values.get("nk.web.storage.transfer-root")));
      if (!asset.isAbsolute()
          || !transfer.isAbsolute()
          || asset.equals(transfer)
          || asset.startsWith(transfer)
          || transfer.startsWith(asset)) throw invalid();
    } catch (RuntimeException failure) {
      StorageIoException.preserveFatal(failure);
      throw invalid();
    }
  }

  private static int decimal(String value, int min, int max) {
    if (!RETAINED_DECIMAL.matcher(value).matches()) throw invalid();
    int number = Integer.parseInt(value);
    if (number < min || number > max) throw invalid();
    return number;
  }

  private static boolean validPort(Pattern pattern, String url) {
    var match = pattern.matcher(url);
    return match.matches() && Integer.parseInt(Objects.requireNonNull(match.group(1))) <= 65_535;
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException(RETAINED_INVALID);
  }

  public String value(String key) {
    String value = values.get(Objects.requireNonNull(key, "config key"));
    if (value == null) throw invalid();
    return value;
  }

  public String canonicalSha256() {
    return retainedCanonicalSha256;
  }

  @Override
  public String toString() {
    return "WebNonSecretConfig[REDACTED]";
  }
}
