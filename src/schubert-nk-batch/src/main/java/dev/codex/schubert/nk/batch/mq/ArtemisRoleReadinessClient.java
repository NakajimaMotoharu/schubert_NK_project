package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.apache.activemq.artemis.api.core.JsonUtil;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.json.JsonValue;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Reads effective broker role permissions, not the XML template or JAAS user store. NK-OPS-001; RD
 * MQ-001/002/009/010,SYS-004; UI231/251/253; SS321 §10/13,342 §4; PG241; PT-OPS-MQ-016..018. User
 * credential provisioning and other startup gates remain separate.
 */
@NullMarked
public final class ArtemisRoleReadinessClient {
  private static final java.lang.String LITERAL_SEND = "send";

  private static final java.lang.String LITERAL_CONSUME = "consume";

  private static final java.lang.String LITERAL_MANAGE = "manage";

  private static final java.lang.String LITERAL_BROWSE = "browse";

  private static final java.lang.String LITERAL_VIEW = "view";

  private static final java.lang.String LITERAL_EDIT = "edit";

  private static final java.lang.String LITERAL_NK_WEB = "nk_web";

  private static final java.lang.String LITERAL_NK_API = "nk_api";

  private static final java.lang.String LITERAL_NK_OPS = "nk_ops";

  private static final java.lang.String LITERAL_NK_MQ_MAINTENANCE = "nk_mq_maintenance";

  @FunctionalInterface
  interface Reader {
    @Nullable Object read(ClientSession session, String addressMatch);
  }

  private static final Set<String> PERMISSIONS =
      Set.of(
          LITERAL_SEND,
          LITERAL_CONSUME,
          "createDurableQueue",
          "deleteDurableQueue",
          "createNonDurableQueue",
          "deleteNonDurableQueue",
          LITERAL_MANAGE,
          LITERAL_BROWSE,
          "createAddress",
          "deleteAddress",
          LITERAL_VIEW,
          LITERAL_EDIT);
  private static final Set<String> RETAINED_FIELDS = fields();
  private static final Map<String, Map<String, Set<String>>> RETAINED_APPROVED = approved();

  private static Map<String, Map<String, Set<String>>> approved() {
    var roles =
        new HashMap<String, Map<String, Set<String>>>(
            Map.of(
                "nk.sync.request",
                    Map.of(
                        LITERAL_NK_WEB,
                        Set.of(LITERAL_SEND),
                        LITERAL_NK_API,
                        Set.of(LITERAL_CONSUME),
                        LITERAL_NK_OPS,
                        Set.of(LITERAL_BROWSE)),
                "nk.sync.reply.web",
                    Map.of(
                        LITERAL_NK_WEB,
                        Set.of(LITERAL_CONSUME),
                        LITERAL_NK_API,
                        Set.of(LITERAL_SEND),
                        LITERAL_NK_OPS,
                        Set.of(LITERAL_BROWSE)),
                "nk.async.work",
                    Map.of(
                        LITERAL_NK_API,
                        Set.of(LITERAL_SEND, LITERAL_CONSUME),
                        LITERAL_NK_OPS,
                        Set.of(LITERAL_SEND, LITERAL_BROWSE)),
                "nk.web.log",
                    Map.of(
                        LITERAL_NK_WEB,
                        Set.of(LITERAL_SEND),
                        LITERAL_NK_API,
                        Set.of(LITERAL_CONSUME),
                        LITERAL_NK_OPS,
                        Set.of(LITERAL_BROWSE)),
                "nk.dead.letter",
                    Map.of(
                        LITERAL_NK_WEB,
                        Set.of(LITERAL_SEND),
                        LITERAL_NK_API,
                        Set.of(LITERAL_SEND),
                        LITERAL_NK_OPS,
                        Set.of(LITERAL_CONSUME, LITERAL_BROWSE, LITERAL_MANAGE)),
                "nk.expiry",
                    Map.of(
                        LITERAL_NK_MQ_MAINTENANCE,
                        Set.of(LITERAL_CONSUME, LITERAL_BROWSE),
                        LITERAL_NK_OPS,
                        Set.of(LITERAL_CONSUME, LITERAL_BROWSE, LITERAL_MANAGE)),
                "activemq.management.#",
                    Map.of(
                        LITERAL_NK_OPS,
                        Set.of(
                            LITERAL_SEND,
                            LITERAL_CONSUME,
                            LITERAL_MANAGE,
                            "createAddress",
                            "deleteAddress",
                            "createNonDurableQueue",
                            "deleteNonDurableQueue"),
                        LITERAL_NK_MQ_MAINTENANCE,
                        Set.of(
                            LITERAL_SEND,
                            LITERAL_CONSUME,
                            LITERAL_MANAGE,
                            "createAddress",
                            "deleteAddress",
                            "createNonDurableQueue",
                            "deleteNonDurableQueue"))));
    roles.put("mops.#", Map.of(LITERAL_NK_OPS, Set.of(LITERAL_MANAGE, LITERAL_VIEW, LITERAL_EDIT)));
    var view =
        Map.of(
            LITERAL_NK_OPS,
            Set.of(LITERAL_MANAGE, LITERAL_VIEW),
            LITERAL_NK_MQ_MAINTENANCE,
            Set.of(LITERAL_MANAGE, LITERAL_VIEW));
    roles.put("mops.queue.nk.expiry.q.countMessages", view);
    roles.put("mops.queue.nk.expiry.q.getMessageCount", view);
    roles.put("mops.queue.nk.expiry.q.getPersistentSize", view);
    roles.put(
        "mops.queue.nk.expiry.q.removeMessages",
        Map.of(
            LITERAL_NK_OPS,
            Set.of(LITERAL_MANAGE, LITERAL_EDIT),
            LITERAL_NK_MQ_MAINTENANCE,
            Set.of(LITERAL_MANAGE, LITERAL_EDIT)));
    return Map.copyOf(roles);
  }

  private final Reader reader;

  public ArtemisRoleReadinessClient() {
    this(ArtemisManagementReadinessClient::roles);
  }

  ArtemisRoleReadinessClient(Reader reader) {
    this.reader = Objects.requireNonNull(reader, "role reader");
  }

  /** Borrow one Ops-authenticated session; reject excess as well as missing permissions. */
  public void verify(ClientSession session) {
    inspect(session);
  }

  /** SSC130: every actual role and all twelve permission values, one reply per match. */
  public Map<String, Map<String, Map<String, Boolean>>> inspect(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    var actual = new HashMap<String, Map<String, Map<String, Boolean>>>();
    for (var entry : RETAINED_APPROVED.entrySet()) {
      Object response = reader.read(session, entry.getKey());
      if (!(response instanceof String json)) throw new ArtemisManagementReadinessException();
      actual.put(entry.getKey(), verifyResponse(json, entry.getValue()));
    }
    return Map.copyOf(actual);
  }

  private static Map<String, Map<String, Boolean>> verifyResponse(
      String json, Map<String, Set<String>> expected) {
    try {
      var roles = JsonUtil.readJsonArray(json);
      if (roles.size() != expected.size()) throw new ArtemisManagementReadinessException();
      var seen = new HashSet<String>();
      var observed = new HashMap<String, Map<String, Boolean>>();
      for (int index = 0; index < roles.size(); index++) {
        if (!(roles.get(index) instanceof org.apache.activemq.artemis.json.JsonObject role))
          throw new ArtemisManagementReadinessException();
        if (!RETAINED_FIELDS.equals(role.keySet())) throw new ArtemisManagementReadinessException();
        String name = role.getString("name");
        Set<String> allowed = expected.get(name);
        if (allowed == null || !seen.add(name)) throw new ArtemisManagementReadinessException();
        var actualPermissions = new HashMap<String, Boolean>();
        for (String permission : PERMISSIONS) {
          JsonValue actual = role.get(permission);
          if (actual != JsonValue.TRUE && actual != JsonValue.FALSE)
            throw new ArtemisManagementReadinessException();
          if ((actual == JsonValue.TRUE) != allowed.contains(permission))
            throw new ArtemisManagementReadinessException();
          actualPermissions.put(permission, actual == JsonValue.TRUE);
        }
        observed.put(name, Map.copyOf(actualPermissions));
      }
      return Map.copyOf(observed);
    } catch (org.apache.activemq.artemis.commons.shaded.json.JsonException
        | ClassCastException
        | IllegalStateException malformed) {
      JdbcFailureGraph.preserveFatal(malformed);
      throw new ArtemisManagementReadinessException();
    }
  }

  private static Set<String> fields() {
    var values = new HashSet<>(PERMISSIONS);
    values.add("name");
    return Set.copyOf(values);
  }
}
