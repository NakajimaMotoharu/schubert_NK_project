package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC193: closed isolated-PT instrumentation data, never startup/readiness authority. The native
 * caller separately admits the real manager invocation, pinned agent, held output and owner/budget.
 * Default argv remains unchanged; no environment, arbitrary JVM option, path or socket forwarding.
 * Trace NK-OPS-001 / SYS002004,OPS009,TST004 / UI212251 / SS342343451; PT-OPS-NC193001..005.
 * Source/run qualification remains the native collector's responsibility.
 */
@NullMarked
public final class FixedNativeCoverageProfile {
  public enum Phase {
    ROOT,
    ORDINARY
  }

  public static final String AGENT_PATH = "/opt/pgpt-tools-pg390/jacoco-agent.jar";
  public static final String AGENT_SHA256 =
      "fb5b0036a0899ea97edfa0fc2c7985b55f3f7c5695028163e5e60d4f3cf6075d";
  private static final String RESERVED_PREFIX = "-javaagent:/opt/pgpt-tools-pg390/";
  private final ServiceConfigFiles.Service service;
  private final Phase phase;
  private final String invocation;

  private FixedNativeCoverageProfile(
      ServiceConfigFiles.Service service, Phase phase, String invocation) {
    this.service = service;
    this.phase = phase;
    this.invocation = invocation;
  }

  /** Only a complete matching reserved agent option activates PT; unrelated host agents do not. */
  public static Optional<FixedNativeCoverageProfile> parse(
      ServiceConfigFiles.@Nullable Service service,
      @Nullable Phase phase,
      @Nullable String invocation,
      @Nullable List<? extends @Nullable String> options) {
    if (service == null || phase == null || options == null)
      throw new IllegalArgumentException("fixed PT role, phase and options required");
    String selected = null;
    for (String option : options) {
      if (option == null) throw new IllegalArgumentException("null JVM option");
      if (option.startsWith(RESERVED_PREFIX)) {
        if (selected != null) throw new IllegalArgumentException("duplicate reserved PT agent");
        selected = option;
      }
    }
    if (selected == null) return Optional.empty();
    if (invocation == null || !invocation.matches("(?!0{32}$)[0-9a-f]{32}"))
      throw new IllegalArgumentException("admitted manager invocation required");
    var profile = new FixedNativeCoverageProfile(service, phase, invocation);
    if (!profile.argument().equals(selected))
      throw new IllegalArgumentException("fixed PT agent option mismatch");
    return Optional.of(profile);
  }

  public ServiceConfigFiles.Service service() {
    return service;
  }

  public Phase phase() {
    return phase;
  }

  public String invocation() {
    return invocation;
  }

  public String sessionId() {
    return service.name() + "-" + invocation + "-" + phase.name().toLowerCase(Locale.ROOT);
  }

  /** output=none: no vendor pathname reopen/truncation; held new-only export is separate. */
  public String argument() {
    return "-javaagent:"
        + AGENT_PATH
        + "=output=none,append=false,dumponexit=false,sessionid="
        + sessionId();
  }

  public FixedNativeCoverageProfile forOrdinary() {
    return new FixedNativeCoverageProfile(service, Phase.ORDINARY, invocation);
  }
}
