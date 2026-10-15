package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.web.config.AnimationMvcConfiguration;
import dev.codex.schubert.nk.web.config.ContentDetailMvcConfiguration;
import dev.codex.schubert.nk.web.config.LogMvcConfiguration;
import dev.codex.schubert.nk.web.config.LogoutMvcConfiguration;
import dev.codex.schubert.nk.web.config.MediaMvcConfiguration;
import dev.codex.schubert.nk.web.config.MusicMvcConfiguration;
import dev.codex.schubert.nk.web.config.NotificationBusinessMvcConfiguration;
import dev.codex.schubert.nk.web.config.QuestionAcceptanceMvcConfiguration;
import dev.codex.schubert.nk.web.config.ScenarioMvcConfiguration;
import dev.codex.schubert.nk.web.config.UserBusinessMvcConfiguration;
import dev.codex.schubert.nk.web.logging.WebMediaAudit;
import dev.codex.schubert.nk.web.logging.WebRequestLogProducer;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.media.MediaRangeService;
import dev.codex.schubert.nk.web.messaging.AnimationWireClient;
import dev.codex.schubert.nk.web.messaging.ArtemisRequestSender;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogSearchWireClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.receipt.ReceiptReferenceRepository;
import dev.codex.schubert.nk.web.revocation.LocalLogoutCoordinator;
import dev.codex.schubert.nk.web.revocation.RevocationPayloadCodec;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.security.LocalLogoutHandler;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepository;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
import dev.codex.schubert.nk.web.storage.LargeResultReader;
import java.time.Clock;
import java.time.Duration;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;

/**
 * Native full business graph, every port borrowed. One exact core/Spring pair for security,
 * invalidation, retained tokens and Logout. No legacy duplicate update controller or new pool/key.
 * NK-WEB-002; FUN001..007/AUT002004/MQ003008/FIL001009/MON003; UI223224226237243253;
 * SS313314321332333342352; QA048049050/PG-D369/NATIVE-GRAPH001..008.
 */
@NullMarked
final class WebBusinessAssembly {
  private final JmsRequestReplyClient client;
  private final ArtemisRequestSender sender;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final WebSecurityAudit audit;
  private final ReceiptReferenceRepository receipts;
  private final LargeResultReader files;
  private final MediaRangeService media;
  private final WebMediaAudit mediaAudit;
  private final WebRequestLogProducer requestLog;
  private final RevocationPayloadCodec revoke;
  private final WebHttpAdmission admission;
  private final Duration timeout;

  WebBusinessAssembly(
      JmsRequestReplyClient client,
      ArtemisRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      WebSecurityAudit audit,
      DataSource database,
      LargeResultReader files,
      MediaRangeService media,
      WebMediaAudit mediaAudit,
      WebRequestLogProducer requestLog,
      RevocationPayloadCodec revoke,
      WebHttpAdmission admission) {
    this(
        client,
        sender,
        clock,
        identifiers,
        audit,
        database,
        files,
        media,
        mediaAudit,
        requestLog,
        revoke,
        admission,
        Duration.ofSeconds(2));
  }

  WebBusinessAssembly(
      JmsRequestReplyClient client,
      ArtemisRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      WebSecurityAudit audit,
      DataSource database,
      LargeResultReader files,
      MediaRangeService media,
      WebMediaAudit mediaAudit,
      WebRequestLogProducer requestLog,
      RevocationPayloadCodec revoke,
      WebHttpAdmission admission,
      Duration timeout) {
    Objects.requireNonNull(timeout, "reply timeout");
    if (timeout.compareTo(Duration.ofMillis(100)) < 0
        || timeout.compareTo(Duration.ofSeconds(2)) > 0)
      throw new IllegalArgumentException("native reply timeout is outside 100ms..2s");
    this.timeout = timeout;
    this.client = Objects.requireNonNull(client, "reply client");
    this.sender = Objects.requireNonNull(sender, "request sender");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
    this.audit = Objects.requireNonNull(audit, "audit");
    this.receipts = new ReceiptReferenceRepository(database);
    this.files = Objects.requireNonNull(files, "large result reader");
    this.media = Objects.requireNonNull(media, "media service");
    this.mediaAudit = Objects.requireNonNull(mediaAudit, "media audit");
    this.requestLog = Objects.requireNonNull(requestLog, "request logger");
    this.revoke = Objects.requireNonNull(revoke, "revocation codec");
    this.admission = Objects.requireNonNull(admission, "HTTP admission");
  }

  static Class<?>[] configurations() {
    return new Class<?>[] {
      ScenarioMvcConfiguration.class, LogMvcConfiguration.class,
      AnimationMvcConfiguration.class, MusicMvcConfiguration.class,
      ContentDetailMvcConfiguration.class, MediaMvcConfiguration.class,
      UserBusinessMvcConfiguration.class, QuestionAcceptanceMvcConfiguration.class,
      NotificationBusinessMvcConfiguration.class, LogoutMvcConfiguration.class
    };
  }

  Map<Class<?>, ?> dependencies(
      EncryptedWebSessionRepository core, SpringEncryptedSessionRepository sessions) {
    Objects.requireNonNull(core, "core sessions");
    Objects.requireNonNull(sessions, "security sessions");
    var logout = new LogoutWireClient(client, sender, clock, identifiers, timeout);
    return Map.ofEntries(
        Map.entry(
            LogSearchWireClient.class,
            new LogSearchWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(
            ScenarioWireClient.class,
            new ScenarioWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(
            AnimationWireClient.class,
            new AnimationWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(
            MusicWireClient.class,
            new MusicWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(
            UserAdministrationWireClient.class,
            new UserAdministrationWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(
            NotificationWireClient.class,
            new NotificationWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(
            QuestionWireClient.class,
            new QuestionWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(
            MediaDescriptorWireClient.class,
            new MediaDescriptorWireClient(client, sender, clock, identifiers, timeout)),
        Map.entry(ApiSessionInvalidHandler.class, new ApiSessionInvalidHandler(sessions, audit)),
        Map.entry(
            SessionOperationTokenLifecycle.class, new SessionOperationTokenLifecycle(core, clock)),
        Map.entry(ReceiptReferenceRepository.class, receipts),
        Map.entry(LargeResultReader.class, files),
        Map.entry(MediaRangeService.class, media),
        Map.entry(WebMediaAudit.class, mediaAudit),
        Map.entry(
            LocalLogoutHandler.class,
            new LocalLogoutHandler(
                sessions, new LocalLogoutCoordinator(core, revoke, logout, clock), audit)),
        Map.entry(WebRequestLogProducer.class, requestLog),
        Map.entry(WebHttpAdmission.class, admission));
  }
}
