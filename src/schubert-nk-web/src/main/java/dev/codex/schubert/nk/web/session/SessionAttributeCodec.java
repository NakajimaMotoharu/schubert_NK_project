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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Stateless strict JSON schema, not encryption, persistence or authorization.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.1/352;
 * SSC-038/QA049/PG-D356/PT-WEB-009..015/TOKV202..206. Writes v2, strictly reads legacy v1. Caller
 * erases encoded plaintext after encryption; completion metadata grants no business success.
 */
public final class SessionAttributeCodec {
  private static final java.lang.String LITERAL_USERNAME = "username";

  private static final java.lang.String LITERAL_ROLE = "role";

  private static final java.lang.String LITERAL_AUTHENTICATIONCONTEXT = "authenticationContext";

  private static final java.lang.String LITERAL_LOGINAT = "loginAt";

  private static final java.lang.String LITERAL_PURPOSE = "purpose";

  private static final java.lang.String LITERAL_TOKEN = "token";

  private static final java.lang.String LITERAL_ISSUEDAT = "issuedAt";

  public static final int MAXIMUM_PLAINTEXT_BYTES = 16384;
  private static final Set<String> AUTH_FIELDS =
      Set.of(LITERAL_USERNAME, LITERAL_ROLE, LITERAL_AUTHENTICATIONCONTEXT, LITERAL_LOGINAT);

  /** Explicit fields only; immutable input invariants bound output below the decode byte limit. */
  public byte[] encode(SessionAttributes attributes) {
    Objects.requireNonNull(attributes, "attributes");
    var json = new JsonObject();
    json.addProperty("formatVersion", 2);
    attributes
        .principal()
        .ifPresent(
            principal -> {
              json.addProperty(LITERAL_USERNAME, principal.username());
              json.addProperty(LITERAL_ROLE, principal.role().wireValue());
              json.addProperty(
                  LITERAL_AUTHENTICATIONCONTEXT, principal.authenticationContext().wireValue());
              json.addProperty(LITERAL_LOGINAT, principal.loginAt().toString());
            });
    attributes.csrfToken().ifPresent(value -> json.addProperty("csrfToken", value));
    attributes
        .savedRequest()
        .ifPresent(value -> json.addProperty("savedRequest", value.location()));
    var tokens = new JsonArray();
    for (var token : attributes.operationTokens()) {
      var item = new JsonObject();
      item.addProperty(LITERAL_PURPOSE, token.purpose());
      item.addProperty(LITERAL_TOKEN, token.token().toString());
      item.addProperty(LITERAL_ISSUEDAT, token.issuedAt().toString());
      token.completedAt().ifPresent(value -> item.addProperty("completedAt", value.toString()));
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
        int version = 0;
        while (reader.hasNext()) {
          String key = reader.nextName();
          require(keys.add(key));
          switch (key) {
            case "formatVersion" -> {
              require(reader.peek() == JsonToken.NUMBER);
              String rawVersion = reader.nextString();
              require(rawVersion.equals("1") || rawVersion.equals("2"));
              version = rawVersion.equals("1") ? 1 : 2;
            }
            case LITERAL_USERNAME,
                LITERAL_ROLE,
                LITERAL_AUTHENTICATIONCONTEXT,
                LITERAL_LOGINAT,
                "csrfToken",
                "savedRequest" ->
                fields.put(key, string(reader));
            case "operationTokens" -> tokens = Optional.of(tokens(reader));
            default -> throw new SessionAttributeException();
          }
        }
        reader.endObject();
        reader.peek(); // Strict parser permits only END_DOCUMENT after root.
        require(version != 0);
        var operationTokens = tokens.orElseThrow(SessionAttributeException::new);
        // Version may occur after tokens; completedAt remains forbidden under legacy v1.
        require(
            version != 1
                || operationTokens.stream().allMatch(value -> value.completedAt().isEmpty()));
        Optional<SessionPrincipal> principal = Optional.empty();
        if (fields.keySet().stream().anyMatch(AUTH_FIELDS::contains)) {
          require(fields.keySet().containsAll(AUTH_FIELDS));
          principal =
              Optional.of(
                  new SessionPrincipal(
                      required(fields, LITERAL_USERNAME),
                      UserRole.valueOf(required(fields, LITERAL_ROLE)),
                      AuthenticationContext.of(required(fields, LITERAL_AUTHENTICATIONCONTEXT)),
                      instant(required(fields, LITERAL_LOGINAT))));
        }
        return new SessionAttributes(
            principal,
            Optional.ofNullable(fields.get("csrfToken")),
            Optional.ofNullable(fields.get("savedRequest"))
                .map(value -> SavedRequestTarget.fromGet("GET", value)),
            operationTokens);
      }
    } catch (IOException
        | IllegalArgumentException
        | IllegalStateException
        | DateTimeException failure) {
      SessionStoreException.preserveFatal(failure);
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
        require(
            Set.of(LITERAL_PURPOSE, LITERAL_TOKEN, LITERAL_ISSUEDAT, "completedAt").contains(key));
        fields.put(key, string(reader));
      }
      reader.endObject();
      require(
          fields.keySet().containsAll(Set.of(LITERAL_PURPOSE, LITERAL_TOKEN, LITERAL_ISSUEDAT)));
      String raw = required(fields, LITERAL_TOKEN);
      UUID token = UUID.fromString(raw);
      require(token.toString().equals(raw));
      tokens.add(
          new SessionOperationToken(
              required(fields, LITERAL_PURPOSE),
              token,
              instant(required(fields, LITERAL_ISSUEDAT)),
              Optional.ofNullable(fields.get("completedAt")).map(SessionAttributeCodec::instant)));
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
