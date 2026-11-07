package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;

/** NK-OPS-001; SS321§10/13,342§4; SSC075/076/130; OPS-ROLE-MAP-001..004. */
final class RoleSettingsProjectionPortTest {
  private static final String JSON_NAME_PREFIX = "\"name\":\"";
  private static final String JSON_SEND_PREFIX = "\"send\":";
  private static final String REQUEST = "nk.sync.request";
  private static final String SEND = "send";
  private static final String NAME = "name";
  private static final int FAILURE_READ = 5;
  private static final List<String> PERMISSIONS =
      List.of(
          SEND,
          "consume",
          "createDurableQueue",
          "deleteDurableQueue",
          "createNonDurableQueue",
          "deleteNonDurableQueue",
          "manage",
          "browse",
          "createAddress",
          "deleteAddress",
          "view",
          "edit");
  // Literal SS321 role table, including SSC075/076's closed management exceptions.
  private static final Map<String, String> GRANTS =
      Map.ofEntries(
          Map.entry(REQUEST, "nk_web:send;nk_api:consume;nk_ops:browse"),
          Map.entry("nk.sync.reply.web", "nk_web:consume;nk_api:send;nk_ops:browse"),
          Map.entry("nk.async.work", "nk_api:send,consume;nk_ops:send,browse"),
          Map.entry("nk.web.log", "nk_web:send;nk_api:consume;nk_ops:browse"),
          Map.entry("nk.dead.letter", "nk_web:send;nk_api:send;nk_ops:consume,browse,manage"),
          Map.entry("nk.expiry", "nk_mq_maintenance:consume,browse;nk_ops:consume,browse,manage"),
          Map.entry(
              "activemq.management.#",
              "nk_ops:send,consume,manage,createAddress,deleteAddress,createNonDurableQueue,deleteNonDurableQueue;"
                  + "nk_mq_maintenance:send,consume,manage,createAddress,deleteAddress,createNonDurableQueue,deleteNonDurableQueue"),
          Map.entry("mops.#", "nk_ops:manage,view,edit"),
          Map.entry(
              "mops.queue.nk.expiry.q.countMessages",
              "nk_ops:manage,view;nk_mq_maintenance:manage,view"),
          Map.entry(
              "mops.queue.nk.expiry.q.getMessageCount",
              "nk_ops:manage,view;nk_mq_maintenance:manage,view"),
          Map.entry(
              "mops.queue.nk.expiry.q.getPersistentSize",
              "nk_ops:manage,view;nk_mq_maintenance:manage,view"),
          Map.entry(
              "mops.queue.nk.expiry.q.removeMessages",
              "nk_ops:manage,edit;nk_mq_maintenance:manage,edit"));

  @Test
  void rmap001ReturnsAll324ApprovedBooleanValuesWithoutAnySessionOperation() {
    var reads = new ArrayList<String>();
    var client =
        new ArtemisRoleReadinessClient(
            (session, match) -> {
              reads.add(match);
              return json(expected(match));
            });
    var result = client.inspect(unusedSession());
    assertEquals(12, result.size());
    assertEquals(GRANTS.keySet(), result.keySet());
    assertEquals(12, reads.size());
    assertEquals(GRANTS.keySet(), Set.copyOf(reads));
    int roleCount = 0;
    int permissionCount = 0;
    for (var match : result.entrySet()) {
      assertEquals(expected(match.getKey()), match.getValue());
      roleCount += match.getValue().size();
      for (var role : match.getValue().values()) {
        assertEquals(Set.copyOf(PERMISSIONS), role.keySet());
        permissionCount += role.size();
      }
    }
    assertEquals(27, roleCount);
    assertEquals(324, permissionCount);
  }

  @Test
  void rmap002AllThreeSnapshotLayersAreImmutableAndIndependent() {
    var client = new ArtemisRoleReadinessClient((session, match) -> json(expected(match)));
    var first = client.inspect(unusedSession());
    assertThrows(UnsupportedOperationException.class, () -> first.clear());
    assertThrows(UnsupportedOperationException.class, () -> first.get(REQUEST).clear());
    assertThrows(
        UnsupportedOperationException.class, () -> first.get(REQUEST).get("nk_web").clear());
    var second = client.inspect(unusedSession());
    assertEquals(first, second);
    assertNotSame(first, second);
    assertNotSame(first.get(REQUEST), second.get(REQUEST));
    assertNotSame(first.get(REQUEST).get("nk_web"), second.get(REQUEST).get("nk_web"));
  }

  @Test
  void rmap003FifthReadFailureNeverPublishesPartialSnapshotOrContinuesReading() {
    var retained =
        new ArtemisRoleReadinessClient((session, match) -> json(expected(match)))
            .inspect(unusedSession());
    for (int variant = 0; variant < 10; variant++) {
      final int selected = variant;
      var reads = new AtomicInteger();
      var client =
          new ArtemisRoleReadinessClient(
              (session, match) ->
                  reads.incrementAndGet() == FAILURE_READ
                      ? invalid(match, selected)
                      : json(expected(match)));
      var failure =
          assertThrows(
              ArtemisManagementReadinessException.class, () -> client.inspect(unusedSession()));
      assertEquals("Artemis effective broker configuration is unavailable", failure.getMessage());
      assertEquals(FAILURE_READ, reads.get());
      assertEquals(expected(REQUEST), retained.get(REQUEST));
    }
    var duplicate =
        new ArtemisRoleReadinessClient(
            (session, match) -> REQUEST.equals(match) ? invalid(match, 3) : json(expected(match)));
    assertThrows(
        ArtemisManagementReadinessException.class, () -> duplicate.inspect(unusedSession()));
    for (Throwable failure :
        List.of(
            new IllegalStateException("synthetic role reader"),
            new AssertionError("synthetic role reader"))) {
      var reads = new AtomicInteger();
      var client =
          new ArtemisRoleReadinessClient(
              (session, match) -> {
                if (reads.incrementAndGet() == FAILURE_READ) {
                  if (failure instanceof Error fatal) throw fatal;
                  throw (RuntimeException) failure;
                }
                return json(expected(match));
              });
      assertSame(failure, assertThrows(failure.getClass(), () -> client.inspect(unusedSession())));
      assertEquals(FAILURE_READ, reads.get());
    }
  }

  @Test
  void rmap004NullMalformedAndVerifyContractKeepBorrowedSessionUntouched() {
    assertThrows(NullPointerException.class, () -> new ArtemisRoleReadinessClient(null));
    var unconnected = new ArtemisRoleReadinessClient();
    assertThrows(NullPointerException.class, () -> unconnected.verify(null));
    var invalid = new ArrayList<Object>(List.of(7, "", "not-json", "{}"));
    invalid.add(null);
    for (Object value : invalid) {
      var reads = new AtomicInteger();
      var client =
          new ArtemisRoleReadinessClient(
              (session, match) -> {
                reads.incrementAndGet();
                return value;
              });
      assertThrows(
          ArtemisManagementReadinessException.class, () -> client.inspect(unusedSession()));
      assertEquals(1, reads.get());
    }
    var reads = new AtomicInteger();
    new ArtemisRoleReadinessClient(
            (session, match) -> {
              reads.incrementAndGet();
              return json(expected(match));
            })
        .verify(unusedSession());
    assertEquals(12, reads.get());
  }

  private static Map<String, Map<String, Boolean>> expected(String match) {
    var result = new LinkedHashMap<String, Map<String, Boolean>>();
    for (String role : GRANTS.get(match).split(";")) {
      String[] fields = role.split(":");
      var allowed = Set.of(fields[1].split(","));
      var flags = new LinkedHashMap<String, Boolean>();
      PERMISSIONS.forEach(permission -> flags.put(permission, allowed.contains(permission)));
      result.put(fields[0], flags);
    }
    return result;
  }

  private static String json(Map<String, Map<String, Boolean>> roles) {
    return roles.entrySet().stream()
        .map(entry -> roleJson(entry.getKey(), entry.getValue()))
        .collect(Collectors.joining(",", "[", "]"));
  }

  private static String roleJson(String name, Map<String, Boolean> flags) {
    return "{\"name\":\""
        + name
        + "\","
        + flags.entrySet().stream()
            .map(entry -> "\"" + entry.getKey() + "\":" + entry.getValue())
            .collect(Collectors.joining(","))
        + "}";
  }

  private static String invalid(String match, int variant) {
    var roles = expected(match);
    var first = roles.entrySet().iterator().next();
    String valid = json(roles);
    return switch (variant) {
      case 0 -> "[]";
      case 1 -> "[" + String.join(",", java.util.Collections.nCopies(roles.size(), "null")) + "]";
      case 2 -> valid.replace(JSON_NAME_PREFIX + first.getKey() + "\"", "\"name\":\"unknown\"");
      case 3 ->
          roles.size() > 1
              ? "["
                  + String.join(
                      ",",
                      java.util.Collections.nCopies(
                          roles.size(), roleJson(first.getKey(), first.getValue())))
                  + "]"
              : valid.replace(JSON_NAME_PREFIX + first.getKey() + "\"", "\"name\":\"unknown\"");
      case 4 -> valid.replace(JSON_SEND_PREFIX + first.getValue().get(SEND) + ",", "");
      case 5 -> valid.replace("\"name\":", "\"unapproved\":true,\"name\":");
      case 6 -> valid.replace(JSON_NAME_PREFIX + first.getKey() + "\"", "\"name\":7");
      case 7 -> valid.replace(JSON_SEND_PREFIX + first.getValue().get(SEND), "\"send\":\"false\"");
      case 8 ->
          valid.replace(
              JSON_SEND_PREFIX + first.getValue().get(SEND),
              JSON_SEND_PREFIX + !first.getValue().get(SEND));
      case 9 -> valid.replace(JSON_NAME_PREFIX + first.getKey() + "\"", "\"name\":null");
      default -> throw new AssertionError("unknown fixed variant");
    };
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, arguments) -> {
              throw new AssertionError("borrowed session must remain untouched");
            });
  }
}
