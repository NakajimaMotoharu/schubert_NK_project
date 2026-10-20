package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.api.application.admin.UserApplicationAssembly;
import dev.codex.schubert.nk.api.application.log.LogQueryApplicationAssembly;
import dev.codex.schubert.nk.api.application.media.MediaApplicationAssembly;
import dev.codex.schubert.nk.api.application.question.QuestionCommandService;
import dev.codex.schubert.nk.api.application.question.QuestionMutationApplicationService;
import dev.codex.schubert.nk.api.application.question.QuestionQueryApplicationService;
import dev.codex.schubert.nk.api.application.question.QuestionQueryReplayService;
import dev.codex.schubert.nk.api.application.question.QuestionSubmissionService;
import dev.codex.schubert.nk.api.application.scenario.ScenarioApplicationAssembly;
import dev.codex.schubert.nk.api.bootstrap.ApiNativeCodecs;
import dev.codex.schubert.nk.api.dispatch.JdbcSyncRequestProcessor;
import dev.codex.schubert.nk.api.file.AssetManifestLoader;
import dev.codex.schubert.nk.api.file.HeldMediaFileInspector;
import dev.codex.schubert.nk.api.file.ServiceCredentialSet;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResultBoundResponseSnapshotCodec;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.messaging.outbound.JdbcOutboxRepository;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcher;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxJmsSender;
import dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcher;
import dev.codex.schubert.nk.api.messaging.outbound.TransactedJmsContextProvider;
import dev.codex.schubert.nk.api.persistence.QuestionQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.api.security.LoginApplicationAssembly;
import dev.codex.schubert.nk.api.security.LogoutApplicationAssembly;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.function.Supplier;
import javax.sql.DataSource;

/**
 * Real credential→probe→full usage→existing business graph, inside admitted A interval only. Root
 * all-root/producer-stop/proof verification precedes this operation. Borrowed processors must not
 * escape or outlive their codec/root owners; caller stops consumers before returning. No consumer/A
 * release is performed here. NK-OPS-001/NK-SCN-001/NK-AUT-001; FIL001..009/AUT001..004/MQ006;
 * UI226237243; SS311312333342343/SSC149161; PG-D336; PT-OPS-API-PREP-001..004. Full
 * registration/lifecycle remains mandatory.
 */
public final class ApiApplicationPreparation {
  private ApiApplicationPreparation() {}

  @FunctionalInterface
  public interface Operation {
    void run(Map<String, SyncRequestProcessor> processors, OwnedOutboxDispatcher outbox)
        throws IOException;
  }

  public static void execute(
      DataSource pool,
      ServiceCredentialSet credentials,
      Path transfer,
      Path assets,
      int manifestEntries,
      Clock clock,
      TransactedJmsContextProvider dispatchContexts,
      Operation operation)
      throws IOException {
    execute(
        pool,
        credentials,
        transfer,
        assets,
        manifestEntries,
        clock,
        dispatchContexts,
        operation,
        false);
  }

  /** SSC316: keep the closest codec/root/Outbox owner when its release cannot be confirmed. */
  public static void executeRetainingUnknown(
      DataSource pool,
      ServiceCredentialSet credentials,
      Path transfer,
      Path assets,
      int manifestEntries,
      Clock clock,
      TransactedJmsContextProvider dispatchContexts,
      Operation operation)
      throws IOException {
    execute(
        pool,
        credentials,
        transfer,
        assets,
        manifestEntries,
        clock,
        dispatchContexts,
        operation,
        true);
  }

  private static void execute(
      DataSource pool,
      ServiceCredentialSet credentials,
      Path transfer,
      Path assets,
      int manifestEntries,
      Clock clock,
      TransactedJmsContextProvider dispatchContexts,
      Operation operation,
      boolean retainUnknown)
      throws IOException {
    Objects.requireNonNull(pool, "database");
    Objects.requireNonNull(credentials, "credentials");
    Objects.requireNonNull(transfer, "transfer root");
    Objects.requireNonNull(assets, "asset root");
    Objects.requireNonNull(clock, "clock");
    Objects.requireNonNull(dispatchContexts, "Outbox context source");
    Objects.requireNonNull(operation, "application operation");
    System.err.println("API startup entered CODECS_AND_ROOTS");
    if (retainUnknown) {
      ResourceScope.acquire(
          () -> ApiNativeCodecs.create(credentials),
          ServiceProcessResources.ownedRelease(ApiNativeCodecs::close, true),
          codecs ->
              ResourceScope.acquire(
                  () -> OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), transfer),
                  ServiceProcessResources.ownedRelease(OwnedTransferDirectory::close, true),
                  root ->
                      ResourceScope.acquire(
                          () -> OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), assets),
                          ServiceProcessResources.ownedRelease(OwnedTransferDirectory::close, true),
                          asset -> {
                            executeBorrowed(
                                pool,
                                codecs,
                                root,
                                new StorageIdentity("schubert-api", "schubert-web"),
                                asset,
                                new StorageIdentity("schubert-data", "schubert-read"),
                                manifestEntries,
                                clock,
                                dispatchContexts,
                                operation,
                                true);
                            return Boolean.TRUE;
                          })));
      return;
    }
    try (var codecs = ApiNativeCodecs.create(credentials);
        var root = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), transfer);
        var asset = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), assets)) {
      executeBorrowed(
          pool,
          codecs,
          root,
          new StorageIdentity("schubert-api", "schubert-web"),
          asset,
          new StorageIdentity("schubert-data", "schubert-read"),
          manifestEntries,
          clock,
          dispatchContexts,
          operation);
    }
  }

  // Package-local component boundary, not Root admission. Native caller above fixes NSS identities
  // and retains all owners. Host PT uses real filesystem identities, never a native admission
  // claim.
  static void executeBorrowed(
      DataSource pool,
      ApiNativeCodecs codecs,
      OwnedTransferDirectory root,
      StorageIdentity transferIdentity,
      OwnedTransferDirectory asset,
      StorageIdentity assetIdentity,
      int manifestEntries,
      Clock clock,
      TransactedJmsContextProvider dispatchContexts,
      Operation operation)
      throws IOException {
    executeBorrowed(
        pool,
        codecs,
        root,
        transferIdentity,
        asset,
        assetIdentity,
        manifestEntries,
        clock,
        dispatchContexts,
        operation,
        false);
  }

  private static void executeBorrowed(
      DataSource pool,
      ApiNativeCodecs codecs,
      OwnedTransferDirectory root,
      StorageIdentity transferIdentity,
      OwnedTransferDirectory asset,
      StorageIdentity assetIdentity,
      int manifestEntries,
      Clock clock,
      TransactedJmsContextProvider dispatchContexts,
      Operation operation,
      boolean retainUnknown)
      throws IOException {
    Objects.requireNonNull(pool, "database");
    Objects.requireNonNull(codecs, "codecs");
    Objects.requireNonNull(root, "transfer");
    Objects.requireNonNull(transferIdentity, "transfer identity");
    Objects.requireNonNull(asset, "assets");
    Objects.requireNonNull(assetIdentity, "asset identity");
    Objects.requireNonNull(clock, "clock");
    Objects.requireNonNull(dispatchContexts, "Outbox context source");
    Objects.requireNonNull(operation, "operation");
    System.err.println("API startup entered MANIFEST");
    var manifest = new AssetManifestLoader(asset, assetIdentity).load(manifestEntries);
    var mediaInspector = new HeldMediaFileInspector(asset, assetIdentity, manifest);
    System.err.println("API startup entered TRANSFER");
    var prepared = TransferStoragePreparation.prepare(root, transferIdentity, clock.instant());
    withOutbox(
        () ->
            OwnedOutboxDispatcher.create(
                new OutboxDispatcher(
                    pool::getConnection,
                    dispatchContexts,
                    new JdbcOutboxRepository(),
                    new OutboxJmsSender(),
                    clock),
                "api-outbox"),
        outbox -> {
          assemble(pool, codecs, prepared, mediaInspector, clock, operation, outbox);
          return Boolean.TRUE;
        },
        retainUnknown);
  }

  // Construct every release/action port before factory.get; ordinary TWR precedence is unchanged.
  static void withOutbox(
      Supplier<OwnedOutboxDispatcher> factory,
      ResourceScope.OwnedAction<OwnedOutboxDispatcher, Boolean> operation,
      boolean retainUnknown)
      throws IOException {
    Objects.requireNonNull(factory, "Outbox factory");
    Objects.requireNonNull(operation, "Outbox operation");
    if (retainUnknown) {
      ResourceScope.<OwnedOutboxDispatcher, Boolean, IOException>acquire(
          factory::get,
          ServiceProcessResources.ownedRelease(OwnedOutboxDispatcher::close, true),
          operation);
    } else {
      try (var outbox = Objects.requireNonNull(factory.get(), "Outbox dispatcher")) {
        operation.run(outbox);
      }
    }
  }

  private static void assemble(
      DataSource pool,
      ApiNativeCodecs codecs,
      TransferStoragePreparation.Prepared prepared,
      HeldMediaFileInspector mediaInspector,
      Clock clock,
      Operation operation,
      OwnedOutboxDispatcher outbox)
      throws IOException {
    try {
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
      var media =
          MediaApplicationAssembly.create(
              pool, codecs.fingerprints(), codecs.snapshots(), mediaInspector, clock);
      for (String id :
          java.util.List.of(
              "AUDREQ01",
              "ANMREQ01",
              "ANLREQ01",
              "VIDREQ01",
              "MCTREQ01",
              "MCSREQ01",
              "MTRREQ01",
              "MEDREQ01")) processors.put(id, media);
      var userQueries =
          UserApplicationAssembly.queries(pool, codecs.fingerprints(), codecs.snapshots(), clock);
      for (String id : java.util.List.of("USRREQ01", "UDTREQ01")) processors.put(id, userQueries);
      var userMutations =
          UserApplicationAssembly.mutations(pool, codecs.fingerprints(), codecs.snapshots(), clock);
      for (String id :
          java.util.List.of("UCRREQ01", "USTREQ01", "URLREQ01", "UPWREQ01", "ULKREQ01"))
        processors.put(id, userMutations);
      var authentication = new AuthenticationContextVerifier(new ContextHash());
      var inbox = new JdbcInboxCoordinator(codecs.fingerprints());
      var questionQueries =
          new QuestionQueryApplicationService(
              pool,
              authentication,
              new QuestionQueryRepository(),
              inbox,
              new QuestionQueryReplayService(codecs.snapshots()),
              clock);
      for (String id : java.util.List.of("QSSREQ01", "QSDREQ01", "NTSREQ01", "NTDREQ01"))
        processors.put(id, questionQueries);
      var questionMutations =
          new QuestionMutationApplicationService(
              pool, authentication, inbox, new QuestionCommandService(), codecs.snapshots(), clock);
      for (String id : java.util.List.of("NTCREQ01", "QDLREQ01"))
        processors.put(id, questionMutations);
      processors.put(
          "QSBREQ01",
          new QuestionSubmissionService(
              pool,
              authentication,
              inbox,
              new ResultBoundResponseSnapshotCodec(codecs.snapshots()),
              outbox::wake,
              clock));
      operation.run(Map.copyOf(processors), outbox);
    } catch (NoSuchAlgorithmException failure) {
      throw new IOException("API cryptography unavailable");
    }
  }
}
