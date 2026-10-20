package dev.codex.schubert.nk.api.logging;

import com.google.gson.JsonObject;
import com.google.gson.Strictness;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.io.IOException;
import java.io.StringReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Objects;
import java.util.Optional;

/** Strict REQUEST details allowlist. Trace: NK-MSG-002, SS351 section 3.3, SSC-008, PT-IDEM-012. */
final class RequestLogDetails {
  private static final int MAXIMUM_REQUEST_DETAILS_UTF8_BYTES = 1024;

  private RequestLogDetails() {}

  static String normalize(Optional<String> input, Optional<UserRole> role) {
    Objects.requireNonNull(input, "input");
    Objects.requireNonNull(role, "role");
    String text = input.orElse("{}");
    if (text.getBytes(StandardCharsets.UTF_8).length > MAXIMUM_REQUEST_DETAILS_UTF8_BYTES) {
      throw invalid();
    }
    JsonObject output = new JsonObject();
    try (JsonReader reader = new JsonReader(new StringReader(text))) {
      reader.setStrictness(Strictness.STRICT);
      reader.setNestingLimit(2);
      reader.beginObject();
      var keys = new HashSet<String>();
      while (reader.hasNext()) {
        String key = reader.nextName();
        if (!keys.add(key)) {
          throw invalid();
        }
        switch (key) {
          case "responseBytes" -> {
            if (reader.peek() != JsonToken.NUMBER) {
              throw invalid();
            }
            String digits = reader.nextString();
            if (!digits.matches("0|[1-9][0-9]{0,11}")) {
              throw invalid();
            }
            output.addProperty(key, Long.parseLong(digits));
          }
          case "userAgentFamily" -> {
            String family = string(reader);
            if (!family.matches("[A-Za-z0-9 ._-]{1,32}")) {
              throw invalid();
            }
            output.addProperty(key, family);
          }
          case "truncated" -> output.addProperty(key, reader.nextBoolean());
          case "projectionStatus" -> {
            String status = string(reader);
            if (!status.equals("PENDING") && !status.equals("FAILED")) {
              throw invalid();
            }
            output.addProperty(key, status);
          }
          default -> throw invalid();
        }
      }
      reader.endObject();
      // STRICT peek after the root consumes whitespace and throws for every trailing value.
      // Its only successful outcome here is END_DOCUMENT; no second parser/oracle is needed.
      reader.peek();
    } catch (IOException | IllegalStateException failure) {
      // Parser diagnostics may contain untrusted JSON. Do not attach them to the safe error.
      throw invalid();
    }
    role.ifPresent(value -> output.addProperty("actorRole", value.name()));
    // Four bounded scalar keys plus one enum stay below both wire and JSONB-display limits.
    return output.toString();
  }

  private static String string(JsonReader reader) throws IOException {
    if (reader.peek() != JsonToken.STRING) {
      throw invalid();
    }
    return reader.nextString();
  }

  private static PermanentProtocolException invalid() {
    return new PermanentProtocolException(
        "REQUEST log details violate the safe projection contract");
  }
}
