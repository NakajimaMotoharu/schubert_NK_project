package dev.codex.schubert.nk.web.session;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import java.util.function.UnaryOperator;

/**
 * QA049/PG-D356/NK-WEB-002; FUN001/AUT004/MQ021; UI226/236; SS314; TOKV207208. Only fresh short
 * session transactions; no API/JMS or business database ownership. Completion is retention
 * metadata, never authorization or business-result proof.
 */
public final class SessionOperationTokenLifecycle {
  private final EncryptedWebSessionRepository repository;
  private final Clock clock;
  private final Supplier<UUID> ids;

  public SessionOperationTokenLifecycle(EncryptedWebSessionRepository repository, Clock clock) {
    this(repository, clock, UUID::randomUUID);
  }

  SessionOperationTokenLifecycle(
      EncryptedWebSessionRepository repository, Clock clock, Supplier<UUID> ids) {
    this.repository = Objects.requireNonNull(repository, "repository");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.ids = Objects.requireNonNull(ids, "ids");
  }

  /** Called for an explicit new form, not a retry. Full pending capacity generates no UUID. */
  public SessionOperationToken issue(WebSessionId session, String purpose) {
    return issueForForms(session, List.of(purpose)).getFirst();
  }

  /**
   * SSC177/PG-D366: one explicit screen's actual visible forms, one fresh short transaction. No
   * partially saved undisplayed pending tokens; capacity refusal creates no UUID.
   */
  public List<SessionOperationToken> issueForForms(WebSessionId session, List<String> purposes) {
    var required = List.copyOf(purposes);
    if (required.isEmpty() || required.size() > 10)
      throw new IllegalArgumentException("invalid operation form count");
    for (String purpose : required) validate(purpose, new UUID(0, 0));
    var issued = new AtomicReference<List<SessionOperationToken>>(List.of());
    mutate(
        session,
        current -> {
          var tokens = new ArrayList<>(current.operationTokens());
          long pending = tokens.stream().filter(token -> token.completedAt().isEmpty()).count();
          if (pending + required.size() > 10) return current;
          var candidates = new ArrayList<SessionOperationToken>();
          for (String purpose : required) {
            if (tokens.size() == 10) {
              int oldest = -1;
              for (int index = 0; index < tokens.size(); index++) {
                var completion = tokens.get(index).completedAt();
                if (completion.isPresent()
                    && (oldest < 0
                        || completion
                            .orElseThrow()
                            .isBefore(tokens.get(oldest).completedAt().orElseThrow())))
                  oldest = index;
              }
              tokens.remove(oldest);
            }
            var candidate =
                new SessionOperationToken(
                    purpose, Objects.requireNonNull(ids.get(), "operation UUID"), now());
            if (current.operationTokens().stream()
                    .anyMatch(token -> token.token().equals(candidate.token()))
                || candidates.stream().anyMatch(token -> token.token().equals(candidate.token())))
              throw new IllegalArgumentException("operation UUID collision");
            candidates.add(candidate);
            tokens.add(candidate);
          }
          issued.set(List.copyOf(candidates));
          return attributes(current, tokens);
        });
    if (issued.get().isEmpty()) throw new OperationTokenConflictException();
    return issued.get();
  }

  /** Retained pending and consumed forms both require fresh API validation outside this call. */
  public SessionOperationToken require(WebSessionId session, String purpose, UUID token) {
    validate(purpose, token);
    var snapshot = mutate(session, UnaryOperator.identity());
    return find(snapshot.attributes().operationTokens(), purpose, token)
        .orElseThrow(OperationTokenConflictException::new);
  }

  /**
   * Caller must first verify the genuine API reply (owner/layout/token/HMAC/stored result). This
   * method accepts only 0000/0200 and does not establish that proof itself.
   */
  public SessionOperationToken completeVerified(
      WebSessionId session, String purpose, UUID token, ResultCode verifiedResult) {
    validate(purpose, token);
    Objects.requireNonNull(verifiedResult, "verifiedResult");
    if (verifiedResult != ResultCode.SUCCESS && verifiedResult != ResultCode.IDEMPOTENT_SUCCESS)
      throw new IllegalArgumentException("operation completion requires verified success");
    var snapshot =
        mutate(
            session,
            current -> {
              var found = find(current.operationTokens(), purpose, token);
              if (found.isEmpty() || found.orElseThrow().completedAt().isPresent()) return current;
              var pending = found.orElseThrow();
              var completed =
                  new SessionOperationToken(
                      pending.purpose(), pending.token(), pending.issuedAt(), Optional.of(now()));
              var tokens = new ArrayList<>(current.operationTokens());
              tokens.set(tokens.indexOf(pending), completed);
              return attributes(current, tokens);
            });
    return find(snapshot.attributes().operationTokens(), purpose, token)
        .orElseThrow(OperationTokenConflictException::new);
  }

  private WebSessionSnapshot mutate(WebSessionId session, UnaryOperator<SessionAttributes> change) {
    return repository.mutate(session, change).orElseThrow(OperationTokenConflictException::new);
  }

  private Instant now() {
    return Objects.requireNonNull(clock.instant(), "operation clock");
  }

  private static void validate(String purpose, UUID token) {
    new SessionOperationToken(purpose, token, Instant.EPOCH);
  }

  private static Optional<SessionOperationToken> find(
      List<SessionOperationToken> tokens, String purpose, UUID id) {
    return tokens.stream()
        .filter(token -> token.purpose().equals(purpose) && token.token().equals(id))
        .findFirst();
  }

  private static SessionAttributes attributes(
      SessionAttributes current, List<SessionOperationToken> tokens) {
    return new SessionAttributes(
        current.principal(), current.csrfToken(), current.savedRequest(), tokens);
  }
}
