package dev.codex.schubert.nk.api.file;

/**
 * Private inspector's four allowed AES credential IDs; never accepts a caller path. NK-DAT-001;
 * DAT-009/OPS-009; UI212/251; SS343 6.4; QA-046/SSC-049/PG-D-134; PT-DB-INBOX-129/130/138.
 */
public enum AesCredentialFile {
  CONTEXT_CURRENT("api-context-aes-current", false),
  CONTEXT_PREVIOUS("api-context-aes-previous", true),
  RESPONSE_CURRENT("api-inbox-response-aes-current", false),
  RESPONSE_PREVIOUS("api-inbox-response-aes-previous", true);

  private final String credentialFileName;
  private final boolean optionalCredential;

  AesCredentialFile(String fileName, boolean optional) {
    this.credentialFileName = fileName;
    this.optionalCredential = optional;
  }

  public String fileName() {
    return credentialFileName;
  }

  public boolean optional() {
    return optionalCredential;
  }
}
