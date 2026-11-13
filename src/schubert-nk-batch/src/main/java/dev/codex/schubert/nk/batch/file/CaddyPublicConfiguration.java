package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxHostDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import org.jspecify.annotations.NullMarked;

/** Fixed non-secret Caddy config/public CA only, never key/credential access. SSC178/CADDY455. */
@NullMarked
public final class CaddyPublicConfiguration {
  private CaddyPublicConfiguration() {}

  public static URI site(RootStartupContext root, RootStartupContext.Snapshot morning)
      throws IOException {
    var fixed = new FixedServiceIdentity().resolveCaddy();
    return site(new String(read(root, morning, fixed, false), StandardCharsets.US_ASCII));
  }

  /** Initial SS342 IP/internal-CA profile, no arbitrary URL/DNS/proxy/HTTP downgrade. */
  static URI site(String text) throws IOException {
    Objects.requireNonNull(text);
    String normalized =
        text.lines()
            .map(String::trim)
            .filter(line -> !line.isEmpty() && !line.startsWith("#"))
            .collect(java.util.stream.Collectors.joining("\n"));
    String global = "{\nadmin off\nauto_https disable_redirects\nskip_install_trust\n}\n";
    require(normalized.startsWith(global));
    normalized = normalized.substring(global.length());
    int firstEnd = normalized.indexOf('\n');
    require(firstEnd > 0);
    String first = normalized.substring(0, firstEnd);
    require(first.startsWith("https://") && first.endsWith(":55160 {"));
    String address = first.substring(8, first.length() - 8);
    String bind;
    if (address.startsWith("[") && address.endsWith("]")) {
      bind = address.substring(1, address.length() - 1);
      require(bind.contains(":") && bind.matches("[0-9a-fA-F:]{2,39}"));
      require(java.net.InetAddress.getByName(bind) instanceof java.net.Inet6Address);
    } else {
      require(address.matches("(?:0|[1-9][0-9]{0,2})(?:\\.(?:0|[1-9][0-9]{0,2})){3}"));
      for (String octet : address.split("\\.")) require(Integer.parseInt(octet) <= 255);
      bind = address;
    }
    String expected = "https://" + address + ":55160 {\nbind " + bind + "\n" + BODY;
    require(normalized.equals(expected));
    return URI.create("https://" + address + ":55160/login");
  }

  private static final String BODY =
      """
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
      }\
      """;

  public static SSLContext tls(RootStartupContext root, RootStartupContext.Snapshot morning)
      throws IOException {
    var fixed = new FixedServiceIdentity().resolveCaddy();
    byte[] bytes = read(root, morning, fixed, true);
    try {
      var input = new ByteArrayInputStream(bytes);
      var certificate =
          (X509Certificate) CertificateFactory.getInstance("X.509").generateCertificate(input);
      require(input.available() == 0 && certificate.getBasicConstraints() >= 0);
      certificate.checkValidity();
      var store = KeyStore.getInstance(KeyStore.getDefaultType());
      store.load(null, null);
      store.setCertificateEntry("fixed-caddy-public-ca", certificate);
      var trust = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
      trust.init(store);
      var context = SSLContext.getInstance("TLS");
      context.init(null, trust.getTrustManagers(), null);
      root.recheck(morning);
      return context;
    } catch (GeneralSecurityException failure) {
      StorageIoException.preserveFatal(failure);
      throw new IOException("Caddy TLS admission unavailable");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private static byte[] read(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      FixedServiceIdentity.Value fixed,
      boolean ca)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    require(morning.service() == RootStartupContext.Service.MORNING);
    root.recheck(morning);
    var calls = LinuxHostDirectoryCalls.create();
    Path path = Path.of(ca ? "/var" : "/etc");
    return ResourceScope.acquire(
        () -> OwnedTransferDirectory.open(calls, path),
        OwnedTransferDirectory::close,
        directory ->
            walk(
                root,
                morning,
                fixed,
                ca,
                List.of(directory),
                ca
                    ? List.of(
                        "lib", "caddy", ".local", "share", "caddy", "pki", "authorities", "local")
                    : List.of("caddy"),
                0));
  }

  private static byte[] walk(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      FixedServiceIdentity.Value fixed,
      boolean ca,
      List<OwnedTransferDirectory> held,
      List<String> segments,
      int index)
      throws IOException {
    root.recheck(morning);
    var current = held.getLast();
    var security = LinuxInodeSecurity.create();
    boolean ordinary = ca && index >= 2;
    var before =
        current.atDirectory(
            p -> directory(p, security, ordinary ? fixed.uid() : 0, ordinary ? fixed.gid() : 0));
    byte[] bytes;
    if (index < segments.size()) {
      bytes =
          ResourceScope.acquire(
              () -> current.openExistingChild(segments.get(index)),
              OwnedTransferDirectory::close,
              child -> {
                var next = new ArrayList<>(held);
                next.add(child);
                return walk(root, morning, fixed, ca, List.copyOf(next), segments, index + 1);
              });
    } else {
      bytes =
          current.atExistingEntryHandle(
              ca ? "root.crt" : "Caddyfile",
              p -> {
                var metadata = file(p, security, ca ? fixed.uid() : 0, fixed.gid(), ca);
                byte[] actual =
                    ResourceScope.acquire(
                        () -> Files.newInputStream(p),
                        java.io.InputStream::close,
                        input -> input.readNBytes(65537));
                require(actual.length == metadata.size());
                require(metadata.equals(file(p, security, ca ? fixed.uid() : 0, fixed.gid(), ca)));
                return actual;
              });
    }
    var after =
        current.atDirectory(
            p -> directory(p, security, ordinary ? fixed.uid() : 0, ordinary ? fixed.gid() : 0));
    requireStableDirectory(before, after);
    root.recheck(morning);
    return bytes;
  }

  /** Internal value guard only; native held-directory capture and Root rechecks stay in walk. */
  static void requireStableDirectory(
      EnvironmentInodePolicy.Metadata before, EnvironmentInodePolicy.Metadata after)
      throws IOException {
    Objects.requireNonNull(before);
    Objects.requireNonNull(after);
    require(
        before.mode() == after.mode()
            && before.uid() == after.uid()
            && before.gid() == after.gid()
            && before.links() == after.links()
            && before.device() == after.device()
            && before.inode() == after.inode());
  }

  private static EnvironmentInodePolicy.Metadata directory(
      Path held, InodeSecurityCalls security, long uid, long gid) throws IOException {
    var m = metadata(held, security);
    requireDirectoryMetadata(m, uid, gid);
    return m;
  }

  static void requireDirectoryMetadata(EnvironmentInodePolicy.Metadata m, long uid, long gid)
      throws IOException {
    Objects.requireNonNull(m);
    require(
        m.uid() == uid
            && m.gid() == gid
            && m.links() >= 2
            && Set.of(0x41c0, 0x41e8, 0x41ed).contains(m.mode()));
  }

  private static EnvironmentInodePolicy.Metadata file(
      Path held, InodeSecurityCalls security, long uid, long gid, boolean ca) throws IOException {
    var m = metadata(held, security);
    requireFileMetadata(m, uid, gid, ca);
    return m;
  }

  /** SSC183: owner-only public CA is not a configuration or private-key permission waiver. */
  static void requireFileMetadata(EnvironmentInodePolicy.Metadata m, long uid, long gid, boolean ca)
      throws IOException {
    Objects.requireNonNull(m);
    require(
        m.uid() == uid
            && m.gid() == gid
            && m.links() == 1
            && m.size() > 0
            && m.size() <= 65536
            && (m.mode() == 0x81a0 || (ca && (m.mode() == 0x8180 || m.mode() == 0x81a4))));
  }

  private static EnvironmentInodePolicy.Metadata metadata(Path held, InodeSecurityCalls security)
      throws IOException {
    var m =
        EnvironmentInodePolicy.metadata(
            Files.readAttributes(
                held, "unix:mode,uid,gid,nlink,size,dev,ino,lastModifiedTime,ctime"));
    requireInodeIdentity(m);
    byte[] acl = security.accessAcl(held, 44);
    requireNoAccessAcl(acl);
    return m;
  }

  static void requireInodeIdentity(EnvironmentInodePolicy.Metadata m) throws IOException {
    Objects.requireNonNull(m);
    require(m.device() >= 0 && m.inode() > 0);
  }

  static void requireNoAccessAcl(@org.jspecify.annotations.Nullable byte[] acl) throws IOException {
    require(acl != null && acl.length == 0);
  }
}
