package dev.codex.schubert.nk.storage;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed Web/API LoadCredential IDs; no caller-supplied filename or cross-service fallback.
 * NK-OPS-001; SYS-002/004; UI243/253; SS342/343 §6; SSC-081; PG280/PT-OPS-CREDID-001..004.
 */
@NullMarked
public enum ServiceCredentialId {
  DB_API(ServiceConfigFiles.Service.API, "db-api", Kind.PASSWORD),
  MQ_API(ServiceConfigFiles.Service.API, "mq-api", Kind.PASSWORD),
  API_CONTEXT_AES_CURRENT(ServiceConfigFiles.Service.API, "api-context-aes-current", Kind.KEY),
  API_INBOX_RESPONSE_AES_CURRENT(
      ServiceConfigFiles.Service.API, "api-inbox-response-aes-current", Kind.KEY),
  OPERATION_HMAC_CURRENT(ServiceConfigFiles.Service.API, "operation-hmac-current", Kind.KEY),
  DB_WEB(ServiceConfigFiles.Service.WEB, "db-web", Kind.PASSWORD),
  MQ_WEB(ServiceConfigFiles.Service.WEB, "mq-web", Kind.PASSWORD),
  WEB_SESSION_AES_CURRENT(ServiceConfigFiles.Service.WEB, "web-session-aes-current", Kind.KEY),
  WEB_REVOKE_AES_CURRENT(ServiceConfigFiles.Service.WEB, "web-revoke-aes-current", Kind.KEY),
  WEB_LOG_AES_CURRENT(ServiceConfigFiles.Service.WEB, "web-log-aes-current", Kind.KEY);

  public enum Kind {
    PASSWORD,
    KEY
  }

  private static final List<ServiceCredentialId> API =
      List.of(
          DB_API,
          MQ_API,
          API_CONTEXT_AES_CURRENT,
          API_INBOX_RESPONSE_AES_CURRENT,
          OPERATION_HMAC_CURRENT);
  private static final List<ServiceCredentialId> WEB =
      List.of(DB_WEB, MQ_WEB, WEB_SESSION_AES_CURRENT, WEB_REVOKE_AES_CURRENT, WEB_LOG_AES_CURRENT);
  private static final Map<ServiceConfigFiles.Service, List<ServiceCredentialId>> BY_SERVICE =
      Map.of(ServiceConfigFiles.Service.API, API, ServiceConfigFiles.Service.WEB, WEB);

  private final ServiceConfigFiles.Service owningService;
  private final String credentialFileName;
  private final Kind credentialKind;

  ServiceCredentialId(ServiceConfigFiles.Service service, String fileName, Kind kind) {
    this.owningService = service;
    this.credentialFileName = fileName;
    this.credentialKind = kind;
  }

  public static List<ServiceCredentialId> forService(ServiceConfigFiles.Service service) {
    Objects.requireNonNull(service, "service");
    return Objects.requireNonNull(
        BY_SERVICE.get(service), "service credential IDs are unconfigured");
  }

  public ServiceConfigFiles.Service service() {
    return owningService;
  }

  public String fileName() {
    return credentialFileName;
  }

  public Kind kind() {
    return credentialKind;
  }
}
