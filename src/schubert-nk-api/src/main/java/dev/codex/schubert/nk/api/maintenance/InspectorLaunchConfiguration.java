package dev.codex.schubert.nk.api.maintenance;

import java.nio.file.Path;
import java.time.DateTimeException;
import java.time.Instant;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Strict non-secret environment snapshot, not a deployment-file validator. NK-DAT-001;
 * DAT-009/OPS-009/FIL-006; UI212/241/251; SS343 6.8/341/352; QA-046/SSC-049/PG-D-144;
 * PT-DB-INBOX-221..224.
 */
@NullMarked
public record InspectorLaunchConfiguration(InspectorSettings settings, InspectionRun run) {
  private static final String ROOT = "CREDENTIALS_DIRECTORY";
  private static final String URL = "NK_INSPECTOR_DB_URL";
  private static final String RUN = "NK_INSPECTOR_RUN_ID";
  private static final String CUTOFF = "NK_INSPECTOR_CUTOFF";
  private static final String VERSIONS = "NK_INSPECTOR_FINGERPRINT_VERSIONS";
  private static final Set<String> KEYS = Set.of(ROOT, URL, RUN, CUTOFF, VERSIONS);

  public InspectorLaunchConfiguration {
    Objects.requireNonNull(settings, "inspector settings");
    Objects.requireNonNull(run, "inspection run");
  }

  /**
   * Values are bounded before parsing/allocation; unrelated environment values are not retained.
   */
  public static InspectorLaunchConfiguration read(
      String[] arguments, Map<String, String> environment) throws Invalid {
    Objects.requireNonNull(arguments, "arguments");
    Objects.requireNonNull(environment, "environment");
    if (arguments.length != 0) throw new Invalid();
    for (String key : environment.keySet()) {
      if (key == null) throw new Invalid();
      if ((key.regionMatches(true, 0, "NK_INSPECTOR", 0, 12) || key.equalsIgnoreCase(ROOT))
          && !KEYS.contains(key)) throw new Invalid();
    }
    String root = value(environment, ROOT, 4096);
    String url = value(environment, URL, 256);
    String id = value(environment, RUN, 36);
    String cutoff = value(environment, CUTOFF, 32);
    String names = value(environment, VERSIONS, 65536);
    try {
      UUID runId = UUID.fromString(id);
      Instant instant = Instant.parse(cutoff);
      if (!runId.toString().equals(id) || !instant.toString().equals(cutoff)) throw new Invalid();
      var versions = new HashSet<String>();
      for (String version : names.split(",", -1)) if (!versions.add(version)) throw new Invalid();
      return new InspectorLaunchConfiguration(
          new InspectorSettings(Path.of(root), url, versions), new InspectionRun(runId, instant));
    } catch (IllegalArgumentException | DateTimeException failure) {
      throw new Invalid();
    }
  }

  private static String value(Map<String, String> environment, String key, int maximum)
      throws Invalid {
    String value = environment.get(key);
    if (value == null
        || value.isEmpty()
        || value.length() > maximum
        || value.indexOf('\0') >= 0
        || value.indexOf('\r') >= 0
        || value.indexOf('\n') >= 0) throw new Invalid();
    return value;
  }

  /** No source value, cause or suppressed diagnostic is published. */
  public static final class Invalid extends Exception {
    private static final long serialVersionUID = 1L;

    public Invalid() {
      super("inspector configuration is invalid");
    }
  }

  @Override
  public String toString() {
    return "InspectorLaunchConfiguration[REDACTED]";
  }
}
