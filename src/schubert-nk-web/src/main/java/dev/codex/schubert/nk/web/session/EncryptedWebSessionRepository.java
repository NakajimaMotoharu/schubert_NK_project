package dev.codex.schubert.nk.web.session;

import dev.codex.schubert.nk.web.bootstrap.WebStartupException;
import dev.codex.schubert.nk.web.revocation.EncryptedRevocationPayload;
import dev.codex.schubert.nk.web.revocation.PendingRevocationRepository;
import dev.codex.schubert.nk.web.revocation.RevocationFailureCode;
import dev.codex.schubert.nk.web.revocation.RevocationPayloadIdentity;
import dev.codex.schubert.nk.web.security.WebCsrfToken;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.function.UnaryOperator;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;

/**
 * Short-transaction encrypted session lifecycle delegated to by the future Spring adapter.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI226 §6; SS312/314 §7.2.4/331/352;
 * SSC-041/PG-D-098/PT-WEB-036..043. No HTTP/JMS/password verification or business DB access.
 * Codec/DataSource ownership stays with the caller. Mutation callbacks must be pure and bounded.
 */
public final class EncryptedWebSessionRepository {
  private static final int MAXIMUM_SESSION_VERSION = 999_999_999;

  private final DataSource dataSource;
  private final SessionPayloadCodec codec;
  private final Clock clock;
  private final SecureRandom random;
  private final Supplier<UUID> ids;
  private final JdbcWebSessionStore store = new JdbcWebSessionStore();

  public EncryptedWebSessionRepository(
      DataSource dataSource, SessionPayloadCodec codec, Clock clock) {
    this(dataSource, codec, clock, new SecureRandom(), UUID::randomUUID);
  }

  EncryptedWebSessionRepository(
      DataSource dataSource,
      SessionPayloadCodec codec,
      Clock clock,
      SecureRandom random,
      Supplier<UUID> ids) {
    this.dataSource = Objects.requireNonNull(dataSource, "dataSource");
    this.codec = Objects.requireNonNull(codec, "codec");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.random = Objects.requireNonNull(random, "random");
    this.ids = Objects.requireNonNull(ids, "ids");
  }

  /** Persists a new anonymous session with fresh CSRF and the approved eight-hour idle window. */
  public WebSessionSnapshot create() {
    return transaction(
        connection -> {
          Instant now = now();
          var id = WebSessionId.generate(random);
          var attributes =
              new SessionAttributes(
                  Optional.empty(), Optional.of(csrf()), Optional.empty(), List.of());
          var identity = new SessionPayloadIdentity(required(ids.get()), id.lookupHash(), now);
          var row =
              new WebSessionRow(
                  identity,
                  codec.encrypt(identity, attributes),
                  now,
                  now.plusSeconds(28800),
                  28800,
                  0);
          store.insert(connection, row);
          return new WebSessionSnapshot(id, row, attributes);
        });
  }

  /**
   * Valid sessions extend idle/current-key storage. Invalid/expired rows are deleted before
   * absence.
   */
  public Optional<WebSessionSnapshot> find(WebSessionId id) {
    String hash = hash(id);
    return transaction(
        connection -> {
          var loaded = load(connection, hash);
          if (loaded.isEmpty()) return Optional.empty();
          var current = loaded.orElseThrow();
          var row = write(connection, current.row(), current.attributes(), current.now());
          return Optional.of(new WebSessionSnapshot(id, row, current.attributes()));
        });
  }

  /**
   * Applies a pure change to current attributes; only authenticate may change principal or CSRF.
   */
  public Optional<WebSessionSnapshot> mutate(
      WebSessionId id, UnaryOperator<SessionAttributes> mutation) {
    String hash = hash(id);
    Objects.requireNonNull(mutation, "mutation");
    return transaction(
        connection -> {
          var loaded = load(connection, hash);
          if (loaded.isEmpty()) return Optional.empty();
          var current = loaded.orElseThrow();
          var changed = required(mutation.apply(current.attributes()));
          require(
              changed.principal().equals(current.attributes().principal())
                  && changed.csrfToken().equals(current.attributes().csrfToken()));
          var row = write(connection, current.row(), changed, current.now());
          return Optional.of(new WebSessionSnapshot(id, row, changed));
        });
  }

  /**
   * Caller supplies the API-authenticated principal; this is fixation, not password authentication.
   */
  public Optional<WebSessionSnapshot> authenticate(WebSessionId id, SessionPrincipal principal) {
    Objects.requireNonNull(principal, "principal");
    return reidentify(id, attributes -> Optional.of(principal));
  }

  /** SSC-042/PT-WEB-044: changes ID and CSRF without granting a new principal. */
  public Optional<WebSessionSnapshot> rotate(WebSessionId id) {
    return reidentify(id, SessionAttributes::principal);
  }

  /** SSC-042/PT-WEB-044: server/framework time only, never an HTTP-bound field. */
  public Optional<WebSessionSnapshot> touch(WebSessionId id, Instant accessedAt) {
    String hash = hash(id);
    Instant requested =
        Objects.requireNonNull(accessedAt, "accessedAt").truncatedTo(ChronoUnit.MICROS);
    return transaction(
        connection -> {
          var loaded = load(connection, hash);
          if (loaded.isEmpty()) return Optional.empty();
          var current = loaded.orElseThrow();
          Instant access = requested.isAfter(current.now()) ? requested : current.now();
          var row = write(connection, current.row(), current.attributes(), access);
          return Optional.of(new WebSessionSnapshot(id, row, current.attributes()));
        });
  }

  private Optional<WebSessionSnapshot> reidentify(
      WebSessionId id,
      java.util.function.Function<SessionAttributes, Optional<SessionPrincipal>> principal) {
    String hash = hash(id);
    return transaction(
        connection -> {
          var loaded = load(connection, hash);
          if (loaded.isEmpty()) return Optional.empty();
          var current = loaded.orElseThrow();
          var newId = WebSessionId.generate(random);
          String newHash = newId.lookupHash();
          String newCsrf = csrf();
          UUID uuid = required(ids.get());
          require(!newHash.equals(hash) && !uuid.equals(current.row().identity().id()));
          require(
              !current
                  .attributes()
                  .csrfToken()
                  .map(value -> WebCsrfToken.parse(value).matches(newCsrf))
                  .orElse(false));
          var attributes =
              new SessionAttributes(
                  principal.apply(current.attributes()),
                  Optional.of(newCsrf),
                  current.attributes().savedRequest(),
                  current.attributes().operationTokens());
          var identity = new SessionPayloadIdentity(uuid, newHash, current.now());
          var row =
              new WebSessionRow(
                  identity,
                  codec.encrypt(identity, attributes),
                  current.now(),
                  current.now().plusSeconds(28800),
                  28800,
                  0);
          require(store.delete(connection, current.row().identity(), current.row().version()));
          store.insert(connection, row);
          return Optional.of(new WebSessionSnapshot(newId, row, attributes));
        });
  }

  /**
   * Immediate local invalidation only; API revoke/queue and browser cookie clearing are external.
   */
  public void invalidate(WebSessionId id) {
    String hash = hash(id);
    transaction(
        connection -> {
          store.deleteByHash(connection, hash);
          return Boolean.TRUE;
        });
  }

  /**
   * QA050/RERUN006: encrypted retry and old local row deletion in one existing short TX. Context
   * was captured by the authenticated Logout caller; no guessed API expiry or remote I/O. An
   * already absent old row stays absent; neither this operation nor stale save creates it.
   */
  public void invalidateAndRetain(
      WebSessionId id,
      RevocationPayloadIdentity identity,
      EncryptedRevocationPayload payload,
      RevocationFailureCode reason) {
    String hash = hash(id);
    Objects.requireNonNull(identity, "revocation identity");
    Objects.requireNonNull(payload, "revocation payload");
    Objects.requireNonNull(reason, "revocation failure code");
    transaction(
        connection -> {
          new PendingRevocationRepository().enqueue(connection, identity, payload, null, reason);
          store.deleteByHash(connection, hash);
          return Boolean.TRUE;
        });
  }

  private Optional<Loaded> load(Connection connection, String hash) {
    Optional<WebSessionRow> found;
    try {
      found = store.findLocked(connection, hash);
    } catch (InvalidSessionRowException failure) {
      require(store.deleteByHash(connection, hash));
      return Optional.empty();
    }
    if (found.isEmpty()) return Optional.empty();
    var row = found.orElseThrow();
    Instant now = now();
    if (!row.expiresAt().isAfter(now)) {
      require(store.delete(connection, row.identity(), row.version()));
      return Optional.empty();
    }
    try {
      return Optional.of(new Loaded(row, codec.decrypt(row.identity(), row.payload()), now));
    } catch (SessionPayloadException failure) {
      require(store.delete(connection, row.identity(), row.version()));
      return Optional.empty();
    }
  }

  private WebSessionRow write(
      Connection connection, WebSessionRow current, SessionAttributes attributes, Instant now) {
    Instant access = now.isBefore(current.lastAccessedAt()) ? current.lastAccessedAt() : now;
    Instant expiry = access.plusSeconds(current.maxInactiveSeconds());
    if (current.version() == MAXIMUM_SESSION_VERSION) {
      UUID uuid = required(ids.get());
      require(!uuid.equals(current.identity().id()));
      var identity =
          new SessionPayloadIdentity(
              uuid, current.identity().sessionIdHash(), current.identity().createdAt());
      var replacement =
          new WebSessionRow(
              identity,
              codec.encrypt(identity, attributes),
              access,
              expiry,
              current.maxInactiveSeconds(),
              0);
      require(store.delete(connection, current.identity(), current.version()));
      store.insert(connection, replacement);
      return replacement;
    }
    var replacement =
        new WebSessionRow(
            current.identity(),
            codec.encrypt(current.identity(), attributes),
            access,
            expiry,
            current.maxInactiveSeconds(),
            current.version() + 1);
    require(store.replace(connection, current, replacement));
    return replacement;
  }

  private Instant now() {
    return required(clock.instant()).truncatedTo(ChronoUnit.MICROS);
  }

  private String csrf() {
    return WebCsrfToken.generate(random).formValue();
  }

  private static String hash(WebSessionId id) {
    Objects.requireNonNull(id, "id");
    try {
      return id.lookupHash();
    } catch (GeneralSecurityException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }

  private <T> T transaction(Work<T> work) {
    try (var connection = dataSource.getConnection()) {
      required(connection);
      try {
        connection.setAutoCommit(false);
        connection.setReadOnly(false);
        T result = work.execute(connection);
        connection.commit();
        return result;
      } catch (SQLException | GeneralSecurityException | RuntimeException | Error failure) {
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException | Error rollback) {
          // SS312/332/354, SSC329330: the outer TWR still owns close on early fatal propagation.
          WebStartupException.attachSecondary(failure, rollback);
        }
        SessionStoreException.preserveFatal(failure);
        throw new SessionStoreException();
      }
    } catch (SQLException | RuntimeException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }

  private static <T> T required(@Nullable T value) {
    if (value == null) throw new SessionStoreException();
    return value;
  }

  private static void require(boolean valid) {
    if (!valid) throw new SessionStoreException();
  }

  private record Loaded(WebSessionRow row, SessionAttributes attributes, Instant now) {}

  @FunctionalInterface
  private interface Work<T> {
    T execute(Connection connection) throws GeneralSecurityException, SQLException;
  }
}
