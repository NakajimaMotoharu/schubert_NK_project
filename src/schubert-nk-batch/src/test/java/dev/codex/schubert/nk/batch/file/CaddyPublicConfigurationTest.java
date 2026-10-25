package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.net.URI;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SSC178 fixed SS342 literal HTTPS profile, not Production-built expected. */
final class CaddyPublicConfigurationTest {
  static final String GOLDEN =
      """
      {
          admin off
          auto_https disable_redirects
          skip_install_trust
      }
      https://127.0.0.1:55160 {
          bind 127.0.0.1
          tls internal
          request_body {
              max_size 2MB
          }
          header {
              Strict-Transport-Security "max-age=31536000"
              X-Content-Type-Options "nosniff"
              X-Frame-Options "DENY"
              Referrer-Policy "same-origin"
              -Server
          }
          reverse_proxy 127.0.0.1:8080 {
              header_up X-Forwarded-For {remote_host}
              header_up X-Forwarded-Proto {scheme}
              header_up X-Forwarded-Host {host}
              transport http {
                  dial_timeout 2s
                  response_header_timeout 30s
                  read_timeout 60s
                  write_timeout 60s
              }
          }
      }
      """;

  @Test
  void caddy455006Ipv4Ipv6AndFormattingRemainTlsOnly() throws Exception {
    assertEquals(
        URI.create("https://127.0.0.1:55160/login"), CaddyPublicConfiguration.site(GOLDEN));
    assertEquals(
        URI.create("https://255.255.255.255:55160/login"),
        CaddyPublicConfiguration.site(
            GOLDEN
                .replace("127.0.0.1", "255.255.255.255")
                .replace("reverse_proxy 255.255.255.255", "reverse_proxy 127.0.0.1")));
    String ipv6 =
        GOLDEN
            .replace("https://127.0.0.1", "https://[2001:db8::1]")
            .replace("bind 127.0.0.1", "bind 2001:db8::1");
    assertEquals(
        URI.create("https://[2001:db8::1]:55160/login"), CaddyPublicConfiguration.site(ipv6));
    assertEquals(
        URI.create("https://127.0.0.1:55160/login"),
        CaddyPublicConfiguration.site("# fixed trace\n\n" + GOLDEN.replace("\n", "\r\n")));
    assertThrows(NullPointerException.class, () -> CaddyPublicConfiguration.site(null));
  }

  @Test
  void caddy455007AnyUnexpectedDirectiveOrAddressFailsClosed() {
    for (String bad :
        List.of(
            "",
            "x",
            // PT-OPS-CADDY3050-001: global block without a site-body separator is incomplete.
            "{\nadmin off\nauto_https disable_redirects\nskip_install_trust\n}\nhttps://127.0.0.1:55160 {",
            GOLDEN.replace("admin off", "admin localhost:2019"),
            GOLDEN.replace("tls internal", "tls /tmp/cert /tmp/key"),
            GOLDEN + "file_server\n",
            GOLDEN.replace("https://", "http://"),
            GOLDEN.replace(":55160", ":55161"),
            GOLDEN.replace("max_size 2MB", "max_size 10MB"),
            GOLDEN.replace("-Server", "Server secret"),
            GOLDEN.replace("bind 127.0.0.1", "bind 0.0.0.0"),
            GOLDEN.replace("auto_https disable_redirects", "auto_https off")))
      assertThrows(IOException.class, () -> CaddyPublicConfiguration.site(bad));
    for (String ip :
        List.of(
            "256.0.0.1",
            "01.2.3.4",
            "localhost",
            "127.0.0.1@evil",
            "[localhost]",
            "[::1%lo]",
            // Bracket halves, colon-free hex and IPv4-mapped IPv6 are not the fixed IPv6 profile.
            "[::1",
            "::1]",
            "[11]",
            "[::ffff:7f00:1]",
            "[:::]",
            "[2001:db8]")) {
      String text = GOLDEN.replace("https://127.0.0.1", "https://" + ip);
      assertThrows(IOException.class, () -> CaddyPublicConfiguration.site(text), ip);
    }
  }

  @Test
  void caddy455008DeploymentTemplateMatchesIndependentDirectiveSet() throws Exception {
    String template = Files.readString(Path.of("../deployment/caddy/Caddyfile.template"));
    assertEquals(normal(GOLDEN), normal(template.replace("<GLOBAL_IP>", "127.0.0.1")));
  }

  private static String normal(String value) {
    return value
        .lines()
        .map(String::trim)
        .filter(line -> !line.isEmpty() && !line.startsWith("#"))
        .collect(java.util.stream.Collectors.joining("\n"));
  }
}
