package dev.codex.schubert.nk.web.session;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.Strictness;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.security.SavedRequestTarget;
import java.io.IOException;
import java.io.StringReader;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.DateTimeException;
import java.time.Instant;
import java.util.*;

/**
 * Stateless strict JSON schema, not encryption, persistence or authorization.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.1/352;
 * SSC-038/PG-D-094/PT-WEB-009..015. Caller erases encoded plaintext after encryption.
 */
public final class SessionAttributeCodec {
  public static final int MAXIMUM_PLAINTEXT_BYTES = 16384;
  private static final Set<String> AUTH_FIELDS =
      Set.of("username", "role", "authenticationContext", "loginAt");

  /** Explicit fields only; immutable input invariants bound output below the decode byte limit. */
  public byte[] encode(SessionAttributes attributes) {
    Objects.requireNonNull(attributes, "attributes");
    var json = new JsonObject();
    json.addProperty("formatVersion", 1);
    attributes
        .principal()
        .ifPresent(
            principal -> {
              json.addProperty("username", principal.username());
              json.addProperty("role", principal.role().wireValue());
              json.addProperty(
                  "authenticationContext", principal.authenticationContext().wireValue());
              json.addProperty("loginAt", principal.loginAt().toString());
            });
    attributes.csrfToken().ifPresent(value -> json.addProperty("csrfToken", value));
    attributes
        .savedRequest()
        .ifPresent(value -> json.addProperty("savedRequest", value.location()));
    var tokens = new JsonArray();
    for (var token : attributes.operationTokens()) {
      var item = new JsonObject();
      item.addProperty("purpose", token.purpose());
      item.addProperty("token", token.token().toString());
      item.addProperty("issuedAt", token.issuedAt().toString());
      tokens.add(item);
    }
    json.add("operationTokens", tokens);
    return json.toString().getBytes(StandardCharsets.UTF_8);
  }

  /** Rejects unknown/duplicate/null/type/version/UTF8/trailing data without parser diagnostics. */
  public SessionAttributes decode(byte[] plaintext) {
    Objects.requireNonNull(plaintext, "plaintext");
    require(plaintext.length > 0 && plaintext.length <= MAXIMUM_PLAINTEXT_BYTES);
    byte[] candidate = plaintext.clone();
    try {
      String text =
          StandardCharsets.UTF_8.newDecoder().decode(ByteBuffer.wrap(candidate)).toString();
      require(!text.startsWith("\ufeff"));
      try (var reader = new JsonReader(new StringReader(text))) {
        reader.setStrictness(Strictness.STRICT);
        reader.setNestingLimit(3);
        reader.beginObject();
        var keys = new HashSet<String>();
        var fields = new HashMap<String, String>();
        Optional<List<SessionOperationToken>> tokens = Optional.empty();
        boolean version = false;
        while (reader.hasNext()) {
          String key = reader.nextName();
          require(keys.add(key));
          switch (key) {
            case "formatVersion" -> {
              require(reader.peek() == JsonToken.NUMBER);
              require(reader.nextString().equals("1"));
              version = true;
            }
            case "username",
                "role",
                "authenticationContext",
                "loginAt",
                "csrfToken",
                "savedRequest" ->
                fields.put(key, string(reader));
            case "operationTokens" -> tokens = Optional.of(tokens(reader));
            default -> throw new SessionAttributeException();
          }
        }
        reader.endObject();
        reader.peek(); // Strict parser permits only END_DOCUMENT after root.
        require(version);
        Optional<SessionPrincipal> principal = Optional.empty();
        if (fields.keySet().stream().anyMatch(AUTH_FIELDS::contains)) {
          require(fields.keySet().containsAll(AUTH_FIELDS));
          principal =
              Optional.of(
                  new SessionPrincipal(
                      required(fields, "username"),
                      UserRole.valueOf(required(fields, "role")),
                      AuthenticationContext.of(required(fields, "authenticationContext")),
                      instant(required(fields, "loginAt"))));
        }
        return new SessionAttributes(
            principal,
            Optional.ofNullable(fields.get("csrfToken")),
            Optional.ofNullable(fields.get("savedRequest"))
                .map(value -> SavedRequestTarget.fromGet("GET", value)),
            tokens.orElseThrow(SessionAttributeException::new));
      }
    } catch (IOException
        | IllegalArgumentException
        | IllegalStateException
        | DateTimeException failure) {
      throw new SessionAttributeException();
    } finally {
      Arrays.fill(candidate, (byte) 0);
    }
  }

  private static List<SessionOperationToken> tokens(JsonReader reader) throws IOException {
    reader.beginArray();
    var tokens = new ArrayList<SessionOperationToken>();
    while (reader.hasNext()) {
      require(tokens.size() < 10);
      reader.beginObject();
      var fields = new HashMap<String, String>();
      while (reader.hasNext()) {
        String key = reader.nextName();
        require(!fields.containsKey(key));
        require(Set.of("purpose", "token", "issuedAt").contains(key));
        fields.put(key, string(reader));
      }
      reader.endObject();
      require(fields.size() == 3);
      String raw = required(fields, "token");
      UUID token = UUID.fromString(raw);
      require(token.toString().equals(raw));
      tokens.add(
          new SessionOperationToken(
              required(fields, "purpose"), token, instant(required(fields, "issuedAt"))));
    }
    reader.endArray();
    return tokens;
  }

  private static String required(Map<String, String> fields, String name) {
    return Objects.requireNonNull(fields.get(name), "validated field");
  }

  private static String string(JsonReader reader) throws IOException {
    require(reader.peek() == JsonToken.STRING);
    return reader.nextString();
  }

  private static Instant instant(String text) {
    var instant = Instant.parse(text);
    require(instant.toString().equals(text));
    return instant;
  }

  private static void require(boolean valid) {
    if (!valid) throw new SessionAttributeException();
  }
}
