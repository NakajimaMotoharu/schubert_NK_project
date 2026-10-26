package dev.codex.schubert.nk.api.application.scenario;

import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.message;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.put;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.search;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.spaces;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.persistence.ScenarioRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.util.Arrays;
import java.util.List;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** PT-SCN-009-Q01..Q03: UI234 independent DATA and SS323 independent LP/HMAC oracles. */
final class ScenarioRequestTest {
  private static final String SPEAKER_QUERY_LAYOUT = "SPKREQ01";
  private static final String GAME_CODE_FIELD = "gameCode";
  private static final String GAME_ONE_CODE = "NUKITASHI1";
  private static final String GAME_TWO_CODE = "NUKITASHI2";
  private static final String SCENARIO_QUERY_LAYOUT = "SRCREQ01";
  private static final AuthenticatedActor ACTOR =
      new AuthenticatedActor(101, "request-reader", Role.USER);

  private record Field(String name, String type, String value) {}

  @Test
  void sixLayoutsHaveIndependentCanonicalVectors() throws Exception {
    check("GAMREQ01", new byte[0], List.of());
    check(SPEAKER_QUERY_LAYOUT, spaces(12), List.of(new Field(GAME_CODE_FIELD, "X1", null)));
    byte[] game = spaces(12);
    put(game, 0, GAME_ONE_CODE);
    check(SPEAKER_QUERY_LAYOUT, game, List.of(new Field(GAME_CODE_FIELD, "X1", GAME_ONE_CODE)));
    check("RTEREQ01", game, List.of(new Field(GAME_CODE_FIELD, "X1", GAME_ONE_CODE)));
    byte[] files = spaces(14);
    put(files, 0, GAME_TWO_CODE);
    put(files, 12, "01");
    check(
        "SCFREQ01",
        files,
        List.of(new Field(GAME_CODE_FIELD, "X1", GAME_TWO_CODE), new Field("prefix", "N1", "1")));
    check(
        "SCNREQ01",
        "000000000030".getBytes(StandardCharsets.US_ASCII),
        List.of(new Field("scriptFileId", "N1", "30")));
    byte[] search = search();
    put(search, 0, " Alpha%_é");
    put(search, 256, GAME_ONE_CODE);
    put(search, 268, "話者");
    put(search, 396, "Chapter");
    put(search, 652, "dialogue");
    put(search, 662, "1");
    check(
        SCENARIO_QUERY_LAYOUT,
        search,
        List.of(
            new Field("bodyKeyword", "X1", " Alpha%_é"),
            new Field(GAME_CODE_FIELD, "X1", GAME_ONE_CODE),
            new Field("speakerName", "X1", "話者"),
            new Field("chapterTitle", "X1", "Chapter"),
            new Field("entryType", "X1", "dialogue"),
            new Field("voiceCondition", "X1", "1"),
            new Field("page", "N1", "1"),
            new Field("pageSize", "N1", "100")));
  }

  @Test
  void optionalAndNumericBoundariesPreserveFieldPresenceAndRequestValues() throws Exception {
    check(
        SCENARIO_QUERY_LAYOUT,
        search(),
        List.of(
            new Field("bodyKeyword", "X1", null),
            new Field(GAME_CODE_FIELD, "X1", null),
            new Field("speakerName", "X1", null),
            new Field("chapterTitle", "X1", null),
            new Field("entryType", "X1", null),
            new Field("voiceCondition", "X1", null),
            new Field("page", "N1", "1"),
            new Field("pageSize", "N1", "100")));
    byte[] maximal = search();
    put(maximal, 0, "a".repeat(256));
    put(maximal, 256, GAME_TWO_CODE);
    put(maximal, 268, "s".repeat(128));
    put(maximal, 396, "c".repeat(256));
    put(maximal, 652, "narration");
    put(maximal, 662, "0");
    put(maximal, 663, "999999");
    check(
        SCENARIO_QUERY_LAYOUT,
        maximal,
        List.of(
            new Field("bodyKeyword", "X1", "a".repeat(256)),
            new Field(GAME_CODE_FIELD, "X1", GAME_TWO_CODE),
            new Field("speakerName", "X1", "s".repeat(128)),
            new Field("chapterTitle", "X1", "c".repeat(256)),
            new Field("entryType", "X1", "narration"),
            new Field("voiceCondition", "X1", "0"),
            new Field("page", "N1", "999999"),
            new Field("pageSize", "N1", "100")));
    for (String prefix : List.of("00", "99")) {
      byte[] data = spaces(14);
      put(data, 0, GAME_ONE_CODE);
      put(data, 12, prefix);
      check(
          "SCFREQ01",
          data,
          List.of(
              new Field(GAME_CODE_FIELD, "X1", GAME_ONE_CODE),
              new Field("prefix", "N1", prefix.equals("00") ? "0" : "99")));
    }
    for (String id : List.of("000000000001", "999999999999")) {
      check(
          "SCNREQ01",
          id.getBytes(StandardCharsets.US_ASCII),
          List.of(new Field("scriptFileId", "N1", id.equals("000000000001") ? "1" : id)));
    }
  }

  @Test
  void malformedNullAndOutcomeBoundariesNeverBecomeQueries() {
    assertThrows(NullPointerException.class, () -> ScenarioRequest.decode(null));
    for (String layout : List.of("LOGREQ01", "ZZZREQ01")) invalid(layout, new byte[0]);
    invalid("GAMREQ01", spaces(1));
    invalid(SPEAKER_QUERY_LAYOUT, spaces(11));
    invalid(SPEAKER_QUERY_LAYOUT, spaces(13));
    for (String value : List.of("UNKNOWN", "e\u0301")) {
      byte[] data = spaces(12);
      put(data, 0, value);
      invalid(SPEAKER_QUERY_LAYOUT, data);
    }
    byte[] invalidUtf8 = spaces(12);
    invalidUtf8[0] = (byte) 0xc3;
    invalid(SPEAKER_QUERY_LAYOUT, invalidUtf8);
    invalid("RTEREQ01", spaces(12));
    byte[] nonNfcSearch = search();
    put(nonNfcSearch, 0, "e\u0301");
    invalid(SCENARIO_QUERY_LAYOUT, nonNfcSearch);
    invalid("SCNREQ01", "000000000000".getBytes(StandardCharsets.US_ASCII));
    for (String tail : List.of("000000100", "000001099", "000001101")) {
      byte[] data = search();
      put(data, 663, tail);
      invalid(SCENARIO_QUERY_LAYOUT, data);
    }
    var request = ScenarioRequest.decode(message("GAMREQ01", new byte[0]));
    assertEquals("ScenarioRequest[REDACTED]", request.toString());
    assertThrows(NullPointerException.class, () -> request.canonical(null));
    Connection unused =
        (Connection)
            Proxy.newProxyInstance(
                Connection.class.getClassLoader(),
                new Class<?>[] {Connection.class},
                (p, m, a) -> {
                  throw new AssertionError("null query boundary touched JDBC");
                });
    assertThrows(NullPointerException.class, () -> request.query(null, unused, ACTOR));
    assertThrows(
        NullPointerException.class, () -> request.query(new ScenarioRepository(), null, ACTOR));
    assertThrows(
        NullPointerException.class, () -> request.query(new ScenarioRepository(), unused, null));
    assertThrows(NullPointerException.class, () -> new ScenarioQuerySnapshot.Inline(null));
    assertThrows(NullPointerException.class, () -> new ScenarioQuerySnapshot.Detail(null));
  }

  private static void invalid(String layout, byte[] data) {
    var wire = message(layout, data);
    var failure =
        assertThrows(PermanentProtocolException.class, () -> ScenarioRequest.decode(wire));
    assertEquals("scenario request is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void check(String layout, byte[] data, List<Field> fields) throws Exception {
    byte[] original = data.clone();
    var decoded = ScenarioRequest.decode(message(layout, data));
    Arrays.fill(data, (byte) 0);
    byte[] key = new byte[32];
    Arrays.fill(key, (byte) 11);
    try (var keys = new FingerprintKeyRing("fixture", key, null, null)) {
      CanonicalRequest canonical = decoded.canonical(ACTOR);
      try (canonical;
          var other = ScenarioRequest.decode(message(layout, original)).canonical(ACTOR)) {
        assertEquals("101", canonical.ownerScope());
        assertEquals(layout, canonical.layoutId());
        assertEquals("001", canonical.layoutVersion());
        assertEquals("REQUEST:" + layout, canonical.target());
        assertEquals(fields.size(), canonical.fields().size());
        for (int i = 0; i < fields.size(); i++) {
          var expected = fields.get(i);
          var actual = canonical.fields().get(i);
          assertEquals(expected.name(), actual.name());
          assertEquals(expected.type(), actual.typeVersion());
          assertArrayEquals(
              expected.value() == null ? null : expected.value().getBytes(StandardCharsets.UTF_8),
              actual.value());
        }
        byte[] expected = independentHmac(layout, fields, key);
        assertArrayEquals(expected, keys.calculate(canonical).digest());
        assertArrayEquals(expected, keys.calculate(other).digest());
      }
      for (var field : canonical.fields()) {
        byte[] value = field.value();
        if (value != null) assertArrayEquals(new byte[value.length], value);
      }
    } finally {
      System.arraycopy(original, 0, data, 0, data.length);
      Arrays.fill(key, (byte) 0);
    }
  }

  private static byte[] independentHmac(String layout, List<Field> fields, byte[] key)
      throws Exception {
    var bytes = new ByteArrayOutputStream();
    try (var out = new DataOutputStream(bytes)) {
      out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
      for (String value : List.of("101", layout, "001", "REQUEST:" + layout)) lp(out, value);
      out.writeInt(fields.size());
      for (var field : fields) {
        lp(out, field.name());
        lp(out, field.type());
        lp(out, field.value());
      }
    }
    var mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(key, "HmacSHA256"));
    return mac.doFinal(bytes.toByteArray());
  }

  private static void lp(DataOutputStream out, String value) throws Exception {
    if (value == null) {
      out.writeInt(-1);
      return;
    }
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    out.writeInt(bytes.length);
    out.write(bytes);
  }
}
