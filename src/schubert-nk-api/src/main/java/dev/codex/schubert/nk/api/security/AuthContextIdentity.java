package dev.codex.schubert.nk.api.security;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.UUID;

/** Non-secret row binding. NK-AUT-001; AUT-001/DAT-009; SS314 §6/352 §11.2; PT-AUT-005-C01/03. */
public record AuthContextIdentity(UUID sessionId, long userId) {
  public AuthContextIdentity {
    Objects.requireNonNull(sessionId, "sessionId");
    if (userId < 1 || userId > 999_999_999_999L) {
      throw new IllegalArgumentException("auth context owner is outside N12");
    }
  }

  byte[] aad(String keyVersion) {
    Objects.requireNonNull(keyVersion, "keyVersion");
    if (!keyVersion.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
      throw new IllegalArgumentException("auth context key version is invalid");
    }
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    for (String field :
        new String[] {
          "SCHUBERT-NK-AUTHCTX-v1",
          "schubert.auth_sessions",
          sessionId.toString(),
          Long.toString(userId),
          "1",
          keyVersion
        }) {
      byte[] bytes = field.getBytes(StandardCharsets.US_ASCII);
      output.writeBytes(ByteBuffer.allocate(4).putInt(bytes.length).array());
      output.writeBytes(bytes);
    }
    return output.toByteArray();
  }
}
