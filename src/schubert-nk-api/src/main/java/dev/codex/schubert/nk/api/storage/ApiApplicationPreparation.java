package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.api.application.log.LogQueryApplicationAssembly;
import dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationAssembly;
import dev.codex.schubert.nk.api.bootstrap.ApiNativeCodecs;
import dev.codex.schubert.nk.api.dispatch.JdbcSyncRequestProcessor;
import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.security.LoginApplicationAssembly;
import dev.codex.schubert.nk.api.security.LogoutApplicationAssembly;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Real credential→probe→full usage→existing business graph, inside admitted A interval only. Root
 * all-root/producer-stop/proof verification precedes this operation. Borrowed processors must not
 * escape or outlive their codec/root owners; caller stops consumers before returning. No consumer/A
 * release is performed here. NK-OPS-001/NK-SCN-001/NK-AUT-001; FIL001..009/AUT001..004/MQ006;
 * UI226237243; SS311312333342343/SSC149; PT-OPS-API-PREP-001..004. Full registration/lifecycle
 * remains mandatory.
 */
public final class ApiApplicationPreparation {
  private ApiApplicationPreparation() {}

  @FunctionalInterface
  public interface Operation {
    void run(Map<String, SyncRequestProcessor> processors) throws IOException;
  }

  public static void execute(
      DataSource pool,
      ServiceCredentialSet credentials,
      Path transfer,
      Clock clock,
      Operation operation)
      throws IOException {
    Objects.requireNonNull(pool, "database");
    Objects.requireNonNull(credentials, "credentials");
    Objects.requireNonNull(transfer, "transfer root");
    Objects.requireNonNull(clock, "clock");
    Objects.requireNonNull(operation, "application operation");
    try (var codecs = ApiNativeCodecs.create(credentials);
        var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), transfer)) {
      var prepared =
          TransferStoragePreparation.prepare(
              root, new StorageIdentity("schubert-api", "schubert-web"), clock.instant());
      var login =
          LoginApplicationAssembly.create(
              codecs.fingerprints(), codecs.contexts(), codecs.snapshots(), clock);
      var logout =
          LogoutApplicationAssembly.create(codecs.fingerprints(), codecs.snapshots(), clock);
      var scenario =
          ScenarioApplicationAssembly.create(
              pool,
              codecs.fingerprints(),
              codecs.snapshots(),
              prepared.publisher(),
              prepared.inspector(),
              clock);
      var log =
          LogQueryApplicationAssembly.create(
              pool, codecs.fingerprints(), codecs.snapshots(), clock);
      var processors = new HashMap<String, SyncRequestProcessor>();
      processors.put("LGNREQ01", new JdbcSyncRequestProcessor(pool, login::execute, clock));
      processors.put("LOGREQ01", new JdbcSyncRequestProcessor(pool, logout::execute, clock));
      for (String id :
          java.util.List.of("GAMREQ01", "SPKREQ01", "SRCREQ01", "RTEREQ01", "SCFREQ01", "SCNREQ01"))
        processors.put(id, scenario);
      processors.put("LGSREQ01", log);
      operation.run(Map.copyOf(processors));
    } catch (NoSuchAlgorithmException failure) {
      throw new IOException("API cryptography unavailable");
    }
  }
}
