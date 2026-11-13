package dev.codex.schubert.nk.api.bootstrap;

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
 * Strict, non-secret API config merge before process-resource admission. Only flat dotted-key YAML
 * is accepted; caller still owns file identity/permission checks, env location, credential tree, DB
 * role and storage-root admission. NK-OPS-001; RD SYS-002/004, MQ-001, DAT-001; UI212/231/253;
 * SS311/321/342/343 §4–5; PG272/PT-OPS-API-CFG-001.. .
 */
@NullMarked
public final class ApiNonSecretConfig {
  private static final String RETAINED_INVALID = "API non-secret configuration unavailable";
  private static final Pattern DB_URL =
      Pattern.compile(
          "jdbc:postgresql://127\\.0\\.0\\.1:([1-9][0-9]{0,4})/([a-z_][a-z0-9_]{0,62})");
  private static final Pattern MQ_URL = Pattern.compile("tcp://127\\.0\\.0\\.1:([1-9][0-9]{0,4})");
  private static final Map<String, String> DEFAULTS =
      Map.ofEntries(
          Map.entry("nk.protocol.version", "001"),
          Map.entry("nk.time.display-zone", "Asia/Tokyo"),
          Map.entry("nk.monitoring.mode", "STANDARD"),
          Map.entry("nk.mq.url", "tcp://127.0.0.1:61616"),
          Map.entry("nk.mq.sync-request", "nk.sync.request"),
          Map.entry("nk.mq.sync-reply", "nk.sync.reply.web"),
          Map.entry("nk.mq.async-work", "nk.async.work"),
          Map.entry("nk.mq.web-log", "nk.web.log"),
          Map.entry("nk.mq.dlq", "nk.dead.letter"),
          Map.entry("nk.mq.expiry", "nk.expiry"),
          Map.entry("nk.db.url", "jdbc:postgresql://127.0.0.1:5432/schubert_nk"),
          Map.entry("nk.db.connect-timeout", "3s"),
          Map.entry("nk.db.pool.api.max", "8"),
          Map.entry("nk.db.pool.api.min", "2"),
          Map.entry("nk.api.sync-consumers.initial", "4"),
          Map.entry("nk.api.sync-consumers.max", "8"),
          Map.entry("nk.api.async-consumers", "1"),
          Map.entry("nk.api.storage.asset-root", "/srv/schubert-nk/data/assets"),
          Map.entry("nk.api.storage.asset-manifest-entries", "59627"),
          Map.entry("nk.api.storage.transfer-root", "/srv/schubert-nk/data/transfer"),
          Map.entry("nk.inbox.reference-retention", "24h"),
          Map.entry("nk.inbox.update-retention", "7d"),
          Map.entry("nk.outbox.sent-retention", "7d"));
  private static final Set<String> COMMON_KEYS =
      Set.of("nk.protocol.version", "nk.time.display-zone", "nk.monitoring.mode");
  private static final Set<String> API_KEYS =
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

  private ApiNonSecretConfig(Map<String, String> values, String canonicalSha256) {
    this.values = Map.copyOf(values);
    this.retainedCanonicalSha256 = canonicalSha256;
  }

  /**
   * Merges jar defaults, common YAML and API YAML in SS343 precedence; secrets are never inputs.
   */
  public static ApiNonSecretConfig parse(String commonYaml, String apiYaml)
      throws NoSuchAlgorithmException {
    Objects.requireNonNull(commonYaml, "common YAML");
    Objects.requireNonNull(apiYaml, "API YAML");
    var values = new TreeMap<>(DEFAULTS);
    values.putAll(parseSource(commonYaml, COMMON_KEYS));
    values.putAll(parseSource(apiYaml, API_KEYS));
    validate(values);
    var bytes = new StringBuilder();
    values.forEach((key, value) -> bytes.append(key).append('=').append(value).append('\n'));
    String hash =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(bytes.toString().getBytes(StandardCharsets.UTF_8)));
    return new ApiNonSecretConfig(values, hash);
  }

  private static Map<String, String> parseSource(String yaml, Set<String> allowed) {
    if (yaml.getBytes(StandardCharsets.UTF_8).length > 16_384
        || yaml.indexOf('\r') >= 0
        || yaml.indexOf('\uFEFF') >= 0
        || yaml.indexOf('&') >= 0
        || yaml.indexOf('*') >= 0
        || yaml.contains("${")) {
      throw invalid();
    }
    try {
      Object parsed = new Load(YAML_SETTINGS).loadFromString(yaml);
      if (parsed == null && yaml.isBlank()) return Map.of();
      if (!(parsed instanceof Map<?, ?> mapping)) throw invalid();
      var values = new TreeMap<String, String>();
      for (var entry : mapping.entrySet()) {
        if (!(entry.getKey() instanceof String key)
            || !allowed.contains(key)
            || !(entry.getValue() instanceof String || entry.getValue() instanceof Integer)) {
          throw invalid();
        }
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
            "nk.db.connect-timeout",
            "nk.db.pool.api.max",
            "nk.db.pool.api.min",
            "nk.api.sync-consumers.initial",
            "nk.api.sync-consumers.max",
            "nk.api.async-consumers",
            "nk.inbox.reference-retention",
            "nk.inbox.update-retention",
            "nk.outbox.sent-retention")) {
      if (!Objects.requireNonNull(DEFAULTS.get(key)).equals(values.get(key))) throw invalid();
    }
    // SS321/343 fixed scalar policy; no business/protocol dependency in shared bootstrap.
    for (String key :
        Set.of(
            "nk.mq.sync-request",
            "nk.mq.sync-reply",
            "nk.mq.async-work",
            "nk.mq.web-log",
            "nk.mq.dlq",
            "nk.mq.expiry")) {
      if (!Objects.requireNonNull(DEFAULTS.get(key)).equals(values.get(key))) throw invalid();
    }
    if (!Set.of("STANDARD", "DEBUG").contains(values.get("nk.monitoring.mode"))) throw invalid();
    // SSC150: independently configured migrated inventory, not the observed manifest's own count.
    String entries = Objects.requireNonNull(values.get("nk.api.storage.asset-manifest-entries"));
    if (!entries.matches("[1-9][0-9]{0,4}") || Integer.parseInt(entries) > 59_627) throw invalid();
    if (!validPort(DB_URL, Objects.requireNonNull(values.get("nk.db.url")))
        || !validPort(MQ_URL, Objects.requireNonNull(values.get("nk.mq.url")))) throw invalid();
    try {
      Path asset = Path.of(Objects.requireNonNull(values.get("nk.api.storage.asset-root")));
      Path transfer = Path.of(Objects.requireNonNull(values.get("nk.api.storage.transfer-root")));
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

  private static boolean validPort(Pattern pattern, String url) {
    var match = pattern.matcher(url);
    return match.matches() && Integer.parseInt(Objects.requireNonNull(match.group(1))) <= 65_535;
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException(RETAINED_INVALID);
  }

  /** Approved non-secret scalar only. Unknown keys are not available to callers. */
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
    return "ApiNonSecretConfig[REDACTED]";
  }
}
