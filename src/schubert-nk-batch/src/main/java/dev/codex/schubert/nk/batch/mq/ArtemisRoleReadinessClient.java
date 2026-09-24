package dev.codex.schubert.nk.batch.mq;

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
  @FunctionalInterface
  interface Reader {
    @Nullable Object read(ClientSession session, String addressMatch);
  }

  private static final Set<String> PERMISSIONS =
      Set.of(
          "send",
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
  private static final Set<String> FIELDS = fields();
  private static final Map<String, Map<String, Set<String>>> APPROVED =
      Map.of(
          "nk.sync.request",
              Map.of(
                  "nk_web",
                  Set.of("send"),
                  "nk_api",
                  Set.of("consume"),
                  "nk_ops",
                  Set.of("browse")),
          "nk.sync.reply.web",
              Map.of(
                  "nk_web",
                  Set.of("consume"),
                  "nk_api",
                  Set.of("send"),
                  "nk_ops",
                  Set.of("browse")),
          "nk.async.work",
              Map.of("nk_api", Set.of("send", "consume"), "nk_ops", Set.of("send", "browse")),
          "nk.web.log",
              Map.of(
                  "nk_web",
                  Set.of("send"),
                  "nk_api",
                  Set.of("consume"),
                  "nk_ops",
                  Set.of("browse")),
          "nk.dead.letter",
              Map.of(
                  "nk_web",
                  Set.of("send"),
                  "nk_api",
                  Set.of("send"),
                  "nk_ops",
                  Set.of("consume", "browse", "manage")),
          "nk.expiry",
              Map.of(
                  "nk_mq_maintenance",
                  Set.of("consume", "browse"),
                  "nk_ops",
                  Set.of("consume", "browse", "manage")),
          "activemq.management.#",
              Map.of(
                  "nk_ops",
                  Set.of(
                      "send",
                      "consume",
                      "manage",
                      "createAddress",
                      "deleteAddress",
                      "createNonDurableQueue",
                      "deleteNonDurableQueue")));

  private final Reader reader;

  public ArtemisRoleReadinessClient() {
    this(ArtemisManagementReadinessClient::roles);
  }

  ArtemisRoleReadinessClient(Reader reader) {
    this.reader = Objects.requireNonNull(reader, "role reader");
  }

  /** Borrow one Ops-authenticated session; reject excess as well as missing permissions. */
  public void verify(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    try {
      for (var entry : APPROVED.entrySet()) {
        Object response = reader.read(session, entry.getKey());
        if (!(response instanceof String json)) throw new ArtemisManagementReadinessException();
        var roles = JsonUtil.readJsonArray(json);
        if (roles.size() != entry.getValue().size())
          throw new ArtemisManagementReadinessException();
        var seen = new HashSet<String>();
        for (int index = 0; index < roles.size(); index++) {
          var role = roles.getJsonObject(index);
          if (!FIELDS.equals(role.keySet())) throw new ArtemisManagementReadinessException();
          String name = role.getString("name");
          Set<String> allowed = entry.getValue().get(name);
          if (allowed == null || !seen.add(name)) throw new ArtemisManagementReadinessException();
          for (String permission : PERMISSIONS) {
            JsonValue actual = role.get(permission);
            if (actual != JsonValue.TRUE && actual != JsonValue.FALSE)
              throw new ArtemisManagementReadinessException();
            if ((actual == JsonValue.TRUE) != allowed.contains(permission))
              throw new ArtemisManagementReadinessException();
          }
        }
      }
    } catch (RuntimeException failure) {
      throw new ArtemisManagementReadinessException();
    }
  }

  private static Set<String> fields() {
    var values = new HashSet<>(PERMISSIONS);
    values.add("name");
    return Set.copyOf(values);
  }
}
