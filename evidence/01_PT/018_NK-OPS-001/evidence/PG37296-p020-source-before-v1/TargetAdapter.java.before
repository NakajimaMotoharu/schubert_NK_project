package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.JsonNode;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/** Current/NK共通runnerへ接続先と証跡先だけを与えるtarget境界。SS 355 §4, §12。 */
public final class TargetAdapter {
  private static final String APPLICABILITY_RUN = "RUN";
  private static final int CATALOG_CASE_COUNT = 24;
  private final Target selectedTarget;
  private final URI canonicalOrigin;
  private final Path selectedEvidenceRoot;

  private TargetAdapter(Target target, URI baseUri, Path evidenceRoot) {
    selectedTarget = target;
    canonicalOrigin = baseUri;
    selectedEvidenceRoot = evidenceRoot;
  }

  public static TargetAdapter create(
      String targetName,
      String baseUrl,
      Path reportsRoot,
      Path evidenceRoot,
      Set<String> allowedHosts) {
    Target target = Target.parse(targetName);
    if (baseUrl == null || baseUrl.isBlank()) {
      throw new IllegalArgumentException("baseUrl is required");
    }
    if (reportsRoot == null || evidenceRoot == null) {
      throw new IllegalArgumentException("reportsRoot and evidenceRoot are required");
    }
    if (allowedHosts == null
        || allowedHosts.isEmpty()
        || allowedHosts.stream().anyMatch(host -> host == null || host.isBlank())) {
      throw new IllegalArgumentException("host allowlist must contain non-blank hosts");
    }

    URI uri = URI.create(baseUrl);
    String host = uri.getHost();
    String path = uri.getPath();
    boolean validPath = path != null && (path.isEmpty() || "/".equals(path));
    Set<String> normalizedHosts = new HashSet<>();
    allowedHosts.forEach(value -> normalizedHosts.add(value.toLowerCase(Locale.ROOT)));
    boolean validOrigin =
        "https".equalsIgnoreCase(uri.getScheme())
            & host != null
            & uri.getUserInfo() == null
            & uri.getQuery() == null
            & uri.getFragment() == null
            & validPath;
    if (!validOrigin || !normalizedHosts.contains(host.toLowerCase(Locale.ROOT))) {
      throw new IllegalArgumentException("baseUrl must be an allowlisted HTTPS origin");
    }
    String canonicalAuthority =
        host.toLowerCase(Locale.ROOT) + (uri.getPort() < 0 ? "" : ":" + uri.getPort());
    URI canonicalBaseUri = URI.create("https://" + canonicalAuthority + "/");

    Path normalizedReports = reportsRoot.toAbsolutePath().normalize();
    Path normalizedEvidence = evidenceRoot.toAbsolutePath().normalize();
    if (!normalizedEvidence.startsWith(normalizedReports)
        || normalizedEvidence.equals(normalizedReports)) {
      throw new IllegalArgumentException("evidenceRoot must be below reportsRoot");
    }
    if (Files.exists(normalizedEvidence, java.nio.file.LinkOption.NOFOLLOW_LINKS)) {
      throw new IllegalArgumentException("evidenceRoot already exists");
    }
    return new TargetAdapter(target, canonicalBaseUri, normalizedEvidence);
  }

  public Target target() {
    return selectedTarget;
  }

  public URI baseUri() {
    return canonicalOrigin;
  }

  public Path evidenceRoot() {
    return selectedEvidenceRoot;
  }

  public URI endpoint(String applicationPath) {
    if (applicationPath == null || !applicationPath.startsWith("/")) {
      throw new IllegalArgumentException("application path must be an absolute same-origin path");
    }
    URI reference = URI.create(applicationPath);
    if (reference.getHost() != null) {
      throw new IllegalArgumentException("application path must not change origin");
    }
    return canonicalOrigin.resolve(reference);
  }

  public Path caseArtifact(String caseId) {
    if (caseId == null || !caseId.matches("CHR-[A-Z][0-9]{2}")) {
      throw new IllegalArgumentException("invalid case ID");
    }
    return selectedEvidenceRoot.resolve("artifacts").resolve(caseId + ".json");
  }

  public List<String> executableCaseIds(JsonNode catalog) {
    if (catalog == null || !catalog.path("cases").isArray()) {
      throw new IllegalArgumentException("case catalog is required");
    }
    List<String> executable = new ArrayList<>();
    Set<String> all = new HashSet<>();
    for (JsonNode item : catalog.path("cases")) {
      String id = item.path("id").asText();
      if (!id.matches("CHR-[A-Z][0-9]{2}") || !all.add(id)) {
        throw new IllegalArgumentException("invalid or duplicate case ID: " + id);
      }
      String applicability = item.path(selectedTarget.property()).asText();
      if (APPLICABILITY_RUN.equals(applicability)) {
        executable.add(id);
      } else if (!(selectedTarget == Target.CURRENT
          && "CHR-N01".equals(id)
          && "NK_ONLY".equals(applicability))) {
        throw new IllegalArgumentException(
            "unsupported applicability for " + selectedTarget.externalName() + ": " + id);
      }
    }
    if (all.size() != CATALOG_CASE_COUNT) {
      throw new IllegalArgumentException("case catalog must contain exactly 24 cases");
    }
    return List.copyOf(executable);
  }

  public enum Target {
    CURRENT("current"),
    NK("nk");

    private final String configurationProperty;

    Target(String property) {
      configurationProperty = property;
    }

    static Target parse(String value) {
      if (value == null || value.isBlank()) {
        throw new IllegalArgumentException("target is required");
      }
      return switch (value.toLowerCase(Locale.ROOT)) {
        case "current" -> CURRENT;
        case "nk" -> NK;
        default -> throw new IllegalArgumentException("target must be current or nk");
      };
    }

    String property() {
      return configurationProperty;
    }

    public String externalName() {
      return configurationProperty;
    }
  }
}
