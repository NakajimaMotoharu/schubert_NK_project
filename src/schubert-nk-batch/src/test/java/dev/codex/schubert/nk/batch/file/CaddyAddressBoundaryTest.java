package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.net.URI;
import java.util.List;
import org.junit.jupiter.api.Test;

/** NK-OPS-001 / SS342343 / CADDY1746; literal SS342 HTTPS fixture, no native waiver. */
final class CaddyAddressBoundaryTest {
  @Test
  void caddy1746001MissingBodyAndPartialBracketRejectBeforeUri() {
    String global = "{\nadmin off\nauto_https disable_redirects\nskip_install_trust\n}\n";
    assertThrows(
        IOException.class,
        () -> CaddyPublicConfiguration.site(global + "https://127.0.0.1:55160 {"));
    for (String address : List.of("[::1", "::1]", "[: ]", "[:]", "[::g]", "[::ffff:7f00:1]")) {
      String value =
          CaddyPublicConfigurationTest.GOLDEN.replace("https://127.0.0.1", "https://" + address);
      assertThrows(IOException.class, () -> CaddyPublicConfiguration.site(value), address);
    }
  }

  @Test
  void caddy1746002Ipv4ZeroAndIpv6UnspecifiedHaveExactTlsLoginUri() throws Exception {
    String ipv4 =
        CaddyPublicConfigurationTest.GOLDEN
            .replace("https://127.0.0.1", "https://0.0.0.0")
            .replace("bind 127.0.0.1", "bind 0.0.0.0");
    assertEquals(URI.create("https://0.0.0.0:55160/login"), CaddyPublicConfiguration.site(ipv4));
    String ipv6 =
        CaddyPublicConfigurationTest.GOLDEN
            .replace("https://127.0.0.1", "https://[::]")
            .replace("bind 127.0.0.1", "bind ::");
    assertEquals(URI.create("https://[::]:55160/login"), CaddyPublicConfiguration.site(ipv6));
    // Address acceptance only: not a server binding, HTTP readiness or CA proof.
  }
}
