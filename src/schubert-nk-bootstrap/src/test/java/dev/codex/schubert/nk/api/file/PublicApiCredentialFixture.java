package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.ServiceCredentialId;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;

/**
 * Test-jar only: actual reader/retained FD, existing synthetic metadata; public keys 65/66/67. Does
 * not certify native admission. SSC149/PT-OPS-API-KEY-006.
 */
public final class PublicApiCredentialFixture implements AutoCloseable {
  private final InspectorCredentialLoaderTest.Fixture fixture;
  private final ServiceCredentialSet credentials;

  public PublicApiCredentialFixture(Path parent) throws Exception {
    fixture = new InspectorCredentialLoaderTest.Fixture(parent);
    try {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
      var ids =
          List.of(
              ServiceCredentialId.API_CONTEXT_AES_CURRENT,
              ServiceCredentialId.API_INBOX_RESPONSE_AES_CURRENT,
              ServiceCredentialId.OPERATION_HMAC_CURRENT);
      for (int i = 0; i < ids.size(); i++) {
        byte[] key = new byte[32];
        Arrays.fill(key, (byte) (65 + i));
        var value =
            "NKKEY1\n"
                + List.of("ctx1", "snp1", "fp1").get(i)
                + "\n"
                + Base64.getEncoder().encodeToString(key)
                + "\n";
        Files.writeString(
            fixture.root.resolve(ids.get(i).fileName()), value, StandardCharsets.US_ASCII);
        Arrays.fill(key, (byte) 0);
      }
      var io = new InspectorCredentialLoaderTest.TestIo();
      credentials =
          ServiceCredentialSet.load(
              new ServiceCredentialReader(
                  fixture.held,
                  new InspectorCredentialLoaderTest.TestSecurity(io),
                  ServiceConfigFiles.Service.API,
                  io),
              ServiceConfigFiles.Service.API);
      ServiceCredentialSetTest.assertCleared(io);
    } catch (Exception | Error failure) {
      try {
        fixture.close();
      } catch (Exception close) {
        failure.addSuppressed(close);
      }
      throw failure;
    }
  }

  public ServiceCredentialSet credentials() {
    return credentials;
  }

  @Override
  public void close() throws java.io.IOException {
    credentials.close();
    fixture.close();
  }
}
