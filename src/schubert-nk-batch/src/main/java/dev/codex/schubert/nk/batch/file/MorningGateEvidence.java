package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClient;
import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation;
import dev.codex.schubert.nk.batch.platform.BrokerJournalEvidence;
import dev.codex.schubert.nk.batch.platform.MaintenanceUnit;
import dev.codex.schubert.nk.batch.platform.MorningPreviousBroker;
import dev.codex.schubert.nk.batch.platform.MorningUnitTerminals;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.nio.CharBuffer;
import java.nio.charset.*;
import java.time.format.DateTimeFormatterBuilder;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * SSC129 actual POSTGRES/RELEASE_BOM byte frames, data only and never an issuer capability.
 * NK-OPS-001/NK-BAT-001; SYS004/OPS009/DAT009/UI251/253/SS3436.17; ISSPG001/ISSREL001. Native
 * caller separately owns M/A/original/current/deadline and rechecks every live observation.
 */
@NullMarked
public final class MorningGateEvidence {
  private static final List<String> ADDRESSES =
      List.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");
  private static final List<String> BROKER_FIELDS =
      List.of(
          "name",
          "persistenceEnabled",
          "journalType",
          "journalFileSize",
          "journalMinFiles",
          "journalPoolFiles",
          "globalMaxSize",
          "IDCacheSize",
          "persistIDCache",
          "maxDiskUsage",
          "diskStoreUsage");
  private static final Set<String> TOPOLOGY_FIELDS =
      Set.of(
          "address_exists",
          "anycast",
          "multicast",
          "auto_create_queues",
          "auto_create_addresses",
          "queue_names",
          "queue_exists",
          "temporary",
          "durable",
          "auto_created",
          "queue_auto_create",
          "routing_type",
          "queue_address",
          "queue_name");
  private static final Set<String> SETTINGS_FIELDS =
      Set.of(
          "deadLetterAddress",
          "expiryAddress",
          "autoCreateDeadLetterResources",
          "autoCreateExpiryResources",
          "autoCreateAddresses",
          "autoCreateQueues",
          "autoDeleteAddresses",
          "autoDeleteQueues",
          "autoDeleteCreatedQueues",
          "addressFullMessagePolicy",
          "pageFullMessagePolicy",
          "diskFullMessagePolicy",
          "pageSizeBytes",
          "maxReadPageBytes",
          "maxReadPageMessages",
          "redeliveryCollisionAvoidanceFactor",
          "redeliveryDelay",
          "redeliveryMultiplier",
          "maxRedeliveryDelay",
          "maxDeliveryAttempts",
          "enableMetrics",
          "enableIngressTimestamp",
          "maxSizeBytes",
          "maxSizeMessages",
          "pageLimitBytes",
          "pageLimitMessages");
  private static final List<String> PERMISSIONS =
      List.of(
          "browse",
          "consume",
          "createAddress",
          "createDurableQueue",
          "createNonDurableQueue",
          "deleteAddress",
          "deleteDurableQueue",
          "deleteNonDurableQueue",
          "edit",
          "manage",
          "send",
          "view");
  private static final Set<String> ROLE_MATCHES =
      Set.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry",
          "activemq.management.#",
          "mops.#",
          "mops.queue.nk.expiry.q.countMessages",
          "mops.queue.nk.expiry.q.getMessageCount",
          "mops.queue.nk.expiry.q.getPersistentSize",
          "mops.queue.nk.expiry.q.removeMessages");

  static byte[] broker(
      StartupPermitRecords.Epoch epoch,
      String morningInvocation,
      String brokerInvocation,
      ArtemisStartupObservation.Evidence actual,
      BrokerJournalEvidence.Summary journal)
      throws IOException {
    Objects.requireNonNull(actual);
    Objects.requireNonNull(journal);
    var text = header("NKBROKER1", epoch, morningInvocation, brokerInvocation);
    fields(text, "BROKER", BROKER_FIELDS, actual.broker());
    addressFields(text, "TOPOLOGY", TOPOLOGY_FIELDS, actual.topology());
    addressFields(text, "SETTINGS", SETTINGS_FIELDS, actual.settings());
    fields(
        text,
        "ACCEPTOR",
        List.of("factoryClassName", "host", "name", "port", "protocols", "scheme", "started"),
        actual.acceptor());
    require(actual.roles().keySet().equals(ROLE_MATCHES));
    for (var match : new TreeMap<>(actual.roles()).entrySet()) {
      require(!match.getValue().isEmpty());
      for (var role : new TreeMap<>(match.getValue()).entrySet()) {
        require(Set.of("nk_ops", "nk_web", "nk_api", "nk_mq_maintenance").contains(role.getKey()));
        require(role.getValue().keySet().equals(Set.copyOf(PERMISSIONS)));
        text.append("ROLE|")
            .append(hex(match.getKey()))
            .append('|')
            .append(hex(role.getKey()))
            .append('|');
        for (String key : PERMISSIONS)
          text.append(bit(Objects.requireNonNull(role.getValue().get(key))));
        text.append('\n');
      }
    }
    require(actual.pressure().keySet().equals(Set.copyOf(ADDRESSES)));
    for (String address : ADDRESSES) {
      var value = Objects.requireNonNull(actual.pressure().get(address));
      require(value.state() != ArtemisQueuePressureClient.Pressure.CRITICAL);
      for (var field :
          new TreeMap<>(
                  Map.of(
                      "count",
                      Long.toString(value.count()),
                      "bytes",
                      Long.toString(value.bytes()),
                      "state",
                      value.state().name()))
              .entrySet())
        text.append("PRESSURE|")
            .append(hex(address))
            .append('|')
            .append(field.getKey())
            .append('|')
            .append(hex(field.getValue()))
            .append('\n');
    }
    require(journal.entries() > 0);
    text.append("JOURNAL|entries|")
        .append(journal.entries())
        .append('\n')
        .append("JOURNAL|sha256|")
        .append(hash(journal.sha256()))
        .append('\n');
    return bytes(text);
  }

  private static void addressFields(
      StringBuilder text, String label, Set<String> fields, Map<String, Map<String, String>> actual)
      throws IOException {
    require(actual.keySet().equals(Set.copyOf(ADDRESSES)));
    for (String address : ADDRESSES) {
      var values = Objects.requireNonNull(actual.get(address));
      require(values.keySet().equals(fields));
      for (var field : new TreeMap<>(values).entrySet())
        text.append(label)
            .append('|')
            .append(hex(address))
            .append('|')
            .append(field.getKey())
            .append('|')
            .append(hex(field.getValue()))
            .append('\n');
    }
  }

  private static final List<String> VERSIONS =
      List.of("app", "protocol", "storage", "bootstrap", "schema", "config");
  private static final List<String> BUILD = List.of("jdkVendor", "jdkVersion", "mavenVersion");
  private static final List<String> PLATFORM =
      List.of("osId", "osVersion", "architecture", "javaFeature");
  private static final List<String> RUNTIME =
      List.of("osId", "osVersion", "architecture", "javaFeature", "jdkVendor", "jdkVersion");

  private MorningGateEvidence() {}

  /** SSC131 pure formatter over actual snapshots; this method confers no issuer authority. */
  public static byte[] stop(
      StartupPermitRecords.Epoch epoch,
      String morning,
      String broker,
      MorningUnitTerminals.Snapshot initial,
      MorningPreviousBroker.Evidence previous)
      throws IOException {
    Objects.requireNonNull(epoch);
    Objects.requireNonNull(initial);
    Objects.requireNonNull(previous);
    // Snapshot and Closed have private constructors and validated immutable shapes. Do not
    // duplicate impossible shape checks here; factory negative tests own those invariants.
    require(
        initial.parent().boot().equals(epoch.boot().toString())
            && previous.boot().equals(epoch.boot())
            && initial.parent().invocation().equals(morning));
    var text = header("NKSTOP1", epoch, morning, broker);
    var properties =
        List.of(
            "Id",
            "LoadState",
            "ActiveState",
            "SubState",
            "Job",
            "MainPID",
            "ControlPID",
            "Slice",
            "Delegate",
            "ControlGroup",
            "InvocationID",
            "StateChangeTimestampMonotonic");
    var units = MaintenanceUnit.values();
    for (int index = 0; index < units.length; index++) {
      var row = initial.units().get(index);
      var values = row.manager().observedValues();
      for (int field = 0; field < properties.size(); field++) {
        var value = values.get(field);
        text.append("UNIT|")
            .append(units[index].serviceName())
            .append('|')
            .append(properties.get(field))
            .append('|')
            .append(value.isEmpty() ? "" : hex(value))
            .append('\n');
      }
      text.append("LEAF|")
          .append(units[index].serviceName())
          .append('|')
          .append(bit(row.leafPresent()))
          .append('\n');
      for (int segment = 0; segment < row.directories().size(); segment++) {
        var actual = row.directories().get(segment);
        text.append("KERNEL|")
            .append(units[index].serviceName())
            .append('|')
            .append(segment)
            .append('|')
            .append(actual.mode())
            .append('|')
            .append(actual.uid())
            .append('|')
            .append(actual.gid())
            .append('|')
            .append(actual.device())
            .append('|')
            .append(actual.inode())
            .append('\n');
      }
    }
    switch (previous) {
      case MorningPreviousBroker.NoPrior ignored ->
          text.append("NO_PRIOR|BOOT_JOURNAL_EMPTY|2|0|0\n");
      case MorningPreviousBroker.Closed old -> {
        require(!old.invocation().equals(broker));
        text.append("CLEAN|")
            .append(old.source())
            .append('|')
            .append(old.invocation())
            .append('|')
            .append(old.nativeStart().map(Object::toString).orElse("-"))
            .append('|')
            .append(old.nativeEnd().map(Object::toString).orElse("-"))
            .append('|')
            .append(old.upper())
            .append('|')
            .append(old.journal().entries())
            .append('|')
            .append(hash(old.journal().sha256()))
            .append('|')
            .append(hash(old.contentSha256()))
            .append('\n');
      }
    }
    return bytes(text);
  }

  static byte[] postgres(
      StartupPermitRecords.Epoch epoch,
      String morningInvocation,
      String brokerInvocation,
      MorningDatabaseSession.DatabaseObservation actual)
      throws IOException {
    Objects.requireNonNull(actual);
    require(
        actual.loginRole().equals("schubert_batch")
            && actual.effectiveRole().equals("schubert_batch")
            && actual.database().equals("schubert_nk")
            && actual.autoCommit()
            && !actual.jdbcReadOnly()
            && actual.isolation() == java.sql.Connection.TRANSACTION_READ_COMMITTED
            && !actual.recovery()
            && actual.advisoryHeld());
    var text = header("NKPG1", epoch, morningInvocation, brokerInvocation);
    text.append("login_role=")
        .append(hex(actual.loginRole()))
        .append('\n')
        .append("effective_role=")
        .append(hex(actual.effectiveRole()))
        .append('\n')
        .append("database=")
        .append(hex(actual.database()))
        .append('\n')
        .append("auto_commit=")
        .append(bit(actual.autoCommit()))
        .append('\n')
        .append("read_only=")
        .append(bit(actual.jdbcReadOnly()))
        .append('\n')
        .append("isolation=")
        .append(actual.isolation())
        .append('\n')
        .append("recovery=")
        .append(bit(actual.recovery()))
        .append('\n')
        .append("advisory_lock=")
        .append(bit(actual.advisoryHeld()))
        .append('\n');
    var rows = actual.release().schemaRows();
    require(
        !rows.isEmpty()
            && rows.size() <= 1000
            && rows.equals(actual.release().contents().migrations()));
    text.append("schema_rows=").append(rows.size()).append('\n');
    for (int index = 0; index < rows.size(); index++) {
      var row = rows.get(index);
      require(row.installedRank() == index);
      text.append("SCHEMA|")
          .append(row.installedRank())
          .append('|')
          .append(row.version() == null ? "-" : row.version())
          .append('|')
          .append(hex(row.type()))
          .append('|')
          .append(hex(row.script()))
          .append('|')
          .append(row.checksum() == null ? "-" : row.checksum().toString())
          .append('|')
          .append(bit(row.success()))
          .append('\n');
    }
    return bytes(text);
  }

  static byte[] release(
      StartupPermitRecords.Epoch epoch,
      String morningInvocation,
      String brokerInvocation,
      RootReleaseAdmission.DatabaseInspection actual,
      String apiConfiguration,
      String webConfiguration)
      throws IOException {
    Objects.requireNonNull(actual);
    var contents = actual.contents();
    var text = header("NKREL1", epoch, morningInvocation, brokerInvocation);
    text.append("release_version=")
        .append(hex(contents.version()))
        .append('\n')
        .append("manifest_sha256=")
        .append(hash(contents.sha256()))
        .append('\n')
        .append("api_config_sha256=")
        .append(hash(apiConfiguration))
        .append('\n')
        .append("web_config_sha256=")
        .append(hash(webConfiguration))
        .append('\n');
    fields(text, "VERSION", VERSIONS, contents.versions());
    fields(text, "BUILD", BUILD, contents.build());
    fields(text, "PLATFORM", PLATFORM, contents.platform());
    fields(text, "RUNTIME", RUNTIME, actual.runtime());
    require(
        contents
            .artifactHashes()
            .keySet()
            .containsAll(Set.of("VERSION", "api/api.jar", "web/web.jar", "operations/batch.jar")));
    for (var entry : new TreeMap<>(contents.artifactHashes()).entrySet()) {
      String path = entry.getKey();
      require(!path.isEmpty() && path.chars().allMatch(c -> c >= 33 && c <= 126));
      require(
          !path.startsWith("/")
              && !path.contains("\\")
              && Arrays.stream(path.split("/", -1))
                  .noneMatch(p -> p.isEmpty() || p.equals(".") || p.equals("..")));
      text.append("ARTIFACT|")
          .append(hex(path))
          .append('|')
          .append(hash(entry.getValue()))
          .append('\n');
    }
    return bytes(text);
  }

  /** SSC133/ISSRET: pure rendering of actual bounded observations, never retention authority. */
  static byte[] retention(
      StartupPermitRecords.Epoch epoch,
      String morning,
      String broker,
      MorningBackupRetention.Result actual)
      throws IOException {
    Objects.requireNonNull(actual);
    var text = header("NKBRET1", epoch, morning, broker);
    if (actual.current.isPresent())
      require(actual.current.orElseThrow().run().equals(epoch.activation().run()));
    var root = actual.root;
    text.append("MODE|")
        .append(actual.mode)
        .append('\n')
        .append("CURRENT|")
        .append(
            actual.current.isPresent()
                ? retentionName(actual.current.orElseThrow().directoryName())
                : "-")
        .append('|')
        .append(actual.currentSha256.isPresent() ? hash(actual.currentSha256.orElseThrow()) : "-")
        .append('\n')
        .append("ROOT|")
        .append(root.mode())
        .append('|')
        .append(root.uid())
        .append('|')
        .append(root.gid())
        .append('|')
        .append(root.device())
        .append('|')
        .append(root.inode())
        .append('\n')
        .append("COUNTS|")
        .append(actual.before.size())
        .append('|')
        .append(actual.after.size())
        .append('|')
        .append(
            actual.mode == MorningBackupRetention.Mode.NEW_SUCCESS
                ? Integer.toString(actual.kept.size())
                : "-")
        .append('|')
        .append(actual.deleted.size())
        .append('|')
        .append(actual.protectedNames.size())
        .append('\n');
    for (String name : actual.before)
      text.append("BEFORE|").append(retentionName(name)).append('\n');
    for (String name : actual.after) text.append("AFTER|").append(retentionName(name)).append('\n');
    for (String name : actual.deleted)
      text.append("DELETE|")
          .append(retentionName(name))
          .append('|')
          .append(hash(Objects.requireNonNull(actual.deletedSha256.get(name))))
          .append('\n');
    for (var entry : actual.kept.entrySet()) {
      var manifest = entry.getValue();
      text.append("RETAIN|")
          .append(retentionName(entry.getKey()))
          .append('|')
          .append(
              hash(Objects.requireNonNull(actual.files.get(entry.getKey())).manifest().sha256()));
      for (var file : List.of(manifest.dump(), manifest.configuration(), manifest.credentials()))
        text.append('|').append(file.size()).append('|').append(hash(file.sha256()));
      text.append('\n');
    }
    for (var entry : actual.protectedNames.entrySet()) {
      // Private Result factory emits only the eight SS133 reasons; no external reason input.
      text.append("PROTECT|")
          .append(retentionName(entry.getKey()))
          .append('|')
          .append(entry.getValue())
          .append('\n');
    }
    // Private Result factory: <=4096 names, <=7 retained bundles, <=255 UTF8 bytes/name.
    // The complete fixed layout is <16MiB; do not add an impossible duplicate shape branch.
    return text.toString().getBytes(StandardCharsets.US_ASCII);
  }

  private static String retentionName(String name) throws IOException {
    String encoded = hex(name);
    require(encoded.length() <= 510);
    return encoded;
  }

  static StringBuilder header(
      String prefix, StartupPermitRecords.Epoch epoch, String morning, String broker)
      throws IOException {
    Objects.requireNonNull(epoch);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(broker);
    require(
        epoch.state() == StartupPermitRecords.State.INVALID
            && morning.matches("[0-9a-f]{32}")
            && !morning.equals("0".repeat(32))
            && broker.matches("[0-9a-f]{32}")
            && !broker.equals("0".repeat(32))
            && !morning.equals(broker));
    var activation = epoch.activation();
    var nil = new UUID(0, 0);
    require(!activation.id().equals(nil) && !activation.run().id().equals(nil));
    var time = new DateTimeFormatterBuilder().appendInstant(6).toFormatter();
    return new StringBuilder(prefix)
        .append('\n')
        .append("boot_id=")
        .append(epoch.boot())
        .append('\n')
        .append("epoch_id=")
        .append(epoch.epoch())
        .append('\n')
        .append("run_id=")
        .append(activation.run().id())
        .append('\n')
        .append("cutoff_utc=")
        .append(time.format(activation.run().cutoff()))
        .append('\n')
        .append("activation_id=")
        .append(activation.id())
        .append('\n')
        .append("morning_invocation_id=")
        .append(morning)
        .append('\n')
        .append("broker_invocation_id=")
        .append(broker)
        .append('\n');
  }

  private static void fields(
      StringBuilder text, String label, List<String> keys, Map<String, String> actual)
      throws IOException {
    require(actual.keySet().equals(Set.copyOf(keys)));
    for (String key : keys)
      text.append(label)
          .append('|')
          .append(key)
          .append('|')
          .append(hex(Objects.requireNonNull(actual.get(key))))
          .append('\n');
  }

  private static String hex(String actual) throws IOException {
    Objects.requireNonNull(actual);
    require(!actual.isEmpty());
    try {
      var data =
          StandardCharsets.UTF_8
              .newEncoder()
              .onMalformedInput(CodingErrorAction.REPORT)
              .onUnmappableCharacter(CodingErrorAction.REPORT)
              .encode(CharBuffer.wrap(actual));
      byte[] bytes = new byte[data.remaining()];
      data.get(bytes);
      return HexFormat.of().formatHex(bytes);
    } catch (CharacterCodingException malformed) {
      throw unavailable();
    }
  }

  private static String hash(String actual) throws IOException {
    Objects.requireNonNull(actual);
    require(actual.matches("[0-9a-f]{64}"));
    return actual;
  }

  private static char bit(boolean actual) {
    return actual ? '1' : '0';
  }

  private static byte[] bytes(StringBuilder text) throws IOException {
    require(text.length() <= 65536);
    return text.toString().getBytes(StandardCharsets.US_ASCII);
  }

  private static void require(boolean accepted) throws IOException {
    if (!accepted) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("actual gate evidence unavailable");
  }
}
