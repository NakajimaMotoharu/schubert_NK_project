package dev.codex.schubert.nk.bootstrap;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Objects;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;

/**
 * Immutable canonical public claims, not signature verification or an authorization capability.
 * Only the fixed root-owned original, authenticated by the root assembly, supplies the trust
 * anchor. NK-OPS-001/SYS002/004/OPS009/DAT009/UI212/251/253/SS34311.1/SSC096/PG313;
 * PT-OPS-APPROVAL001..008. Never accepts a key, algorithm, path or approved boolean.
 */
@NullMarked
public final class ReleaseApproval {
  public static final int MAX_BYTES = 192;
  private static final String VERSION = "[A-Za-z0-9][A-Za-z0-9._-]{0,63}";
  private static final String SHA = "[0-9a-f]{64}";
  private static final Pattern FRAME =
      Pattern.compile(
          "NKRELEASEAPPROVAL1\\nversion=(" + VERSION + ")\\nmanifest_sha256=(" + SHA + ")\\n");
  private final String version;
  private final String manifestSha256;

  public ReleaseApproval(String version, String manifestSha256) {
    this.version = Objects.requireNonNull(version, "release version");
    this.manifestSha256 = Objects.requireNonNull(manifestSha256, "manifest digest");
    require(version.matches(VERSION) && manifestSha256.matches(SHA));
  }

  public static ReleaseApproval parse(byte[] input) {
    Objects.requireNonNull(input, "approval bytes");
    require(input.length > 0 && input.length <= MAX_BYTES);
    byte[] copy = input.clone();
    try {
      var match = FRAME.matcher(new String(copy, StandardCharsets.US_ASCII));
      require(match.matches());
      return new ReleaseApproval(
          Objects.requireNonNull(match.group(1)), Objects.requireNonNull(match.group(2)));
    } finally {
      Arrays.fill(copy, (byte) 0);
    }
  }

  public byte[] encode() {
    return ("NKRELEASEAPPROVAL1\nversion=" + version + "\nmanifest_sha256=" + manifestSha256 + "\n")
        .getBytes(StandardCharsets.US_ASCII);
  }

  public String version() {
    return version;
  }

  public String manifestSha256() {
    return manifestSha256;
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("invalid release approval");
  }
}
