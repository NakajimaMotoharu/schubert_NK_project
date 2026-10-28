package dev.codex.schubert.nk.api.application.scenario;

import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.message;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.put;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.search;
import static dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture.spaces;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.gson.JsonParser;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * Independent JDBC bindings/fault oracle; BUG742/PT-SCN-AUD469003..006. No DB expected generator.
 */
final class ScenarioAuditWriterTest {
  private static final String FIXTURE_NONE_30A0924A = "none";
  private static final String FIXTURE_PREPARE_1F4EE68F = "prepare";
  private static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  private static final AuthenticatedActor ACTOR =
      new AuthenticatedActor(101, "e\u0301\n\t\r\u2028\u2029", Role.USER);

  @Test
  void searchCountAndSensitiveConditionsNeverLeak() throws Exception {
    for (long count : new long[] {0, 2, 99_999_900}) {
      var data = search();
      put(data, 0, "synthetic-private-keyword");
      var request = ScenarioRequest.decode(message("SRCREQ01", data));
      var response =
          new TypedPayloadValues(
              new LayoutId("SRCRSP01"),
              new PagedResponseData(
                  1,
                  100,
                  count,
                  count == 0 ? 0 : (int) ((count + 99) / 100),
                  count == 0 ? 0 : 1,
                  Math.min(count, 100)),
              List.of());
      var jdbc = new Jdbc(FIXTURE_NONE_30A0924A, 1);
      new ScenarioAuditWriter().write(jdbc.connection(), ACTOR, request, response, NOW);
      assertBinding(jdbc, request, "SCENARIO_SEARCHED", count);
    }
  }

  @Test
  void inlineAndFileUseTheirIndependentRecordCounts() throws Exception {
    for (boolean file : new boolean[] {false, true}) {
      var request =
          ScenarioRequest.decode(
              message("SCNREQ01", "000000000030".getBytes(StandardCharsets.US_ASCII)));
      var metadata =
          new ScenarioDetailResponseData(
              new ScriptFileId(30),
              GameCode.NUKITASHI_1,
              "synthetic-private-title",
              DisplayPath.of("synthetic-private-display"),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              file ? DeliveryMode.FILE : DeliveryMode.INLINE,
              file ? Optional.of(new UUID(0, 999)) : Optional.empty(),
              file
                  ? Optional.of(
                      RelativePath.of("20260908/00000000-0000-0000-0000-000000000999.ready"))
                  : Optional.empty(),
              file ? 964800 : 0,
              file ? Optional.of(Sha256Hex.of("a".repeat(64))) : Optional.empty(),
              file ? 4800 : 0,
              file ? 201 : 0);
      var record =
          new ScenarioEntryRecord(
              new EntryId(1),
              1,
              1,
              EntryType.NARRATION,
              Optional.empty(),
              "synthetic-private-body",
              0,
              Optional.empty(),
              Optional.empty());
      var response =
          new TypedPayloadValues(
              new LayoutId("SCNRSP01"), metadata, file ? List.of() : List.of(record));
      var jdbc = new Jdbc(FIXTURE_NONE_30A0924A, 1);
      new ScenarioAuditWriter().write(jdbc.connection(), ACTOR, request, response, NOW);
      assertBinding(jdbc, request, "SCENARIO_VIEWED", file ? 201 : 1);
    }
  }

  @Test
  void nonCatalogListQueriesDoNotTouchDatabase() throws Exception {
    for (String prefix : List.of("GAM", "SPK", "RTE", "SCF")) {
      byte[] data = spaces(prefix.equals("GAM") ? 0 : prefix.equals("SCF") ? 14 : 12);
      if (!prefix.equals("GAM")) put(data, 0, "NUKITASHI1");
      if (prefix.equals("SCF")) put(data, 12, "01");
      var request = ScenarioRequest.decode(message(prefix + "REQ01", data));
      var jdbc = new Jdbc(FIXTURE_PREPARE_1F4EE68F, 1);
      new ScenarioAuditWriter().write(jdbc.connection(), ACTOR, request, searchResponse(), NOW);
      assertEquals(0, jdbc.prepare);
      assertEquals(0, jdbc.close);
    }
  }

  @Test
  void sqlFailuresArePropagatedWithStatementOwnership() {
    var request = ScenarioRequest.decode(message("SRCREQ01", search()));
    for (String fault : List.of(FIXTURE_PREPARE_1F4EE68F, "bind", "execute", "close")) {
      var jdbc = new Jdbc(fault, 1);
      var failure =
          assertThrows(
              SQLException.class,
              () ->
                  new ScenarioAuditWriter()
                      .write(jdbc.connection(), ACTOR, request, searchResponse(), NOW));
      assertSame(jdbc.failure, failure);
      assertEquals(1, jdbc.faultReached);
      assertEquals(fault.equals(FIXTURE_PREPARE_1F4EE68F) ? 0 : 1, jdbc.close);
    }
    for (int changed : new int[] {0, 2}) {
      var jdbc = new Jdbc(FIXTURE_NONE_30A0924A, changed);
      assertThrows(
          SQLException.class,
          () ->
              new ScenarioAuditWriter()
                  .write(jdbc.connection(), ACTOR, request, searchResponse(), NOW));
      assertEquals(1, jdbc.execute);
      assertEquals(1, jdbc.close);
    }
  }

  @Test
  void nullBoundaryFailsBeforeDatabaseEffects() {
    var request = ScenarioRequest.decode(message("SRCREQ01", search()));
    var jdbc = new Jdbc(FIXTURE_NONE_30A0924A, 1);
    var writer = new ScenarioAuditWriter();
    assertThrows(
        NullPointerException.class,
        () -> writer.write(null, ACTOR, request, searchResponse(), NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(jdbc.connection(), null, request, searchResponse(), NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(jdbc.connection(), ACTOR, null, searchResponse(), NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(jdbc.connection(), ACTOR, request, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(jdbc.connection(), ACTOR, request, searchResponse(), null));
    assertEquals(0, jdbc.prepare);
  }

  private static TypedPayloadValues searchResponse() {
    return new TypedPayloadValues(
        new LayoutId("SRCRSP01"), new PagedResponseData(1, 100, 0, 0, 0, 0), List.of());
  }

  private static void assertBinding(Jdbc jdbc, ScenarioRequest request, String action, long count) {
    assertEquals(1, jdbc.prepare);
    assertEquals(1, jdbc.execute);
    assertEquals(1, jdbc.close);
    assertEquals(Set.of(1, 2, 3, 4, 5, 6, 7, 8), jdbc.bindings.keySet());
    assertEquals(NOW.atOffset(ZoneOffset.UTC), jdbc.bindings.get(1));
    assertEquals(action, jdbc.bindings.get(2));
    assertEquals(action, jdbc.bindings.get(3));
    assertEquals(request.header().messageId(), jdbc.bindings.get(4));
    assertEquals(request.header().correlationId(), jdbc.bindings.get(5));
    assertEquals(101L, jdbc.bindings.get(6));
    assertEquals("é     ", jdbc.bindings.get(7));
    var details = JsonParser.parseString((String) jdbc.bindings.get(8)).getAsJsonObject();
    assertEquals(Set.of("layout", "resultCount"), details.keySet());
    assertEquals(request.header().layoutId().value(), details.get("layout").getAsString());
    assertEquals(count, details.get("resultCount").getAsLong());
    assertFalse(details.toString().contains("synthetic-private"));
  }

  private static final class Jdbc {
    final SQLException failure = new SQLException("synthetic critical audit fault");
    final Map<Integer, Object> bindings = new HashMap<>();
    final String fault;
    final int changed;
    int prepare;
    int execute;
    int close;
    int faultReached;

    Jdbc(String fault, int changed) {
      this.fault = fault;
      this.changed = changed;
    }

    void fail(String step) throws SQLException {
      if (fault.equals(step)) {
        faultReached++;
        throw failure;
      }
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (p, m, a) -> {
                if (!m.getName().equals("prepareStatement"))
                  throw new AssertionError("audit must not own connection lifecycle");
                prepare++;
                fail(FIXTURE_PREPARE_1F4EE68F);
                assertEquals(
                    "insert into schubert.app_logs(logged_at,service,category,level,action,message, message_id,correlation_id,actor_user_id,actor_username,details) values (?,'API','ACTION','INFO',?,?,?,?,?,?,cast(? as jsonb))",
                    ((String) a[0]).replaceAll("\\s+", " ").trim());
                return Proxy.newProxyInstance(
                    PreparedStatement.class.getClassLoader(),
                    new Class<?>[] {PreparedStatement.class},
                    (s, n, b) -> {
                      return switch (n.getName()) {
                        case "setObject", "setString", "setLong" -> {
                          fail("bind");
                          assertNull(bindings.put((Integer) b[0], b[1]));
                          yield null;
                        }
                        case "executeUpdate" -> {
                          execute++;
                          fail("execute");
                          yield changed;
                        }
                        case "close" -> {
                          close++;
                          fail("close");
                          yield null;
                        }
                        default -> throw new AssertionError("unexpected JDBC operation");
                      };
                    });
              });
    }
  }
}
