package dev.codex.schubert.nk.api.maintenance;

import dev.codex.schubert.nk.api.idempotency.*;
import dev.codex.schubert.nk.protocol.codec.*;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only inspection of 22 saved query/User results, not authentication or deletion permission.
 * Caller owns transaction, reference locks and key lifetime. No file IO, replay or business writes.
 * NK-DAT-001/NK-MSG-002/NK-SCN-001/NK-MED-001/NK-ADM-001; OPS-009/MQ-008/DAT-009;
 * UI212/234..237/241/251; SS324 section12.4/331/333/352; QA-046/SSC-049/BUG-014; PG-D-123;
 * PT-DB-INBOX-041..048.
 */
@NullMarked
public final class NonAuthenticationInboxInspector {
  private static final Set<String> QUERY = Set.of("0000", "9001");
  private static final Set<String> DESCRIPTOR = Set.of("0000", "0104", "9001");
  private static final Set<String> UPDATE = Set.of("0000", "0104", "0105", "9001");
  private static final Set<String> MUTATIONS =
      Set.of("UCRRSP01", "USTRSP01", "URLRSP01", "UPWRSP01", "ULKRSP01");
  private static final Map<String, Set<String>> STORED_CODES =
      Map.ofEntries(
          Map.entry("GAMRSP01", QUERY),
          Map.entry("SPKRSP01", QUERY),
          Map.entry("RTERSP01", QUERY),
          Map.entry("SCFRSP01", QUERY),
          Map.entry("SRCRSP01", QUERY),
          Map.entry("SCNRSP01", DESCRIPTOR),
          Map.entry("AUDRSP01", DESCRIPTOR),
          Map.entry("ANMRSP01", QUERY),
          Map.entry("ANLRSP01", QUERY),
          Map.entry("VIDRSP01", DESCRIPTOR),
          Map.entry("MCTRSP01", QUERY),
          Map.entry("MCSRSP01", QUERY),
          Map.entry("MTRRSP01", QUERY),
          Map.entry("MEDRSP01", DESCRIPTOR),
          Map.entry("USRRSP01", QUERY),
          Map.entry("UDTRSP01", Set.of("0000", "0104")),
          Map.entry("LGSRSP01", QUERY),
          Map.entry("UCRRSP01", Set.of("0000", "0100", "0105", "9001")),
          Map.entry("USTRSP01", UPDATE),
          Map.entry("URLRSP01", UPDATE),
          Map.entry("UPWRSP01", Set.of("0000", "0100", "0104", "0105", "9001")),
          Map.entry("ULKRSP01", Set.of("0000", "0200", "0104", "0105", "9001")));
  private final ResponseSnapshotCodec snapshots;
  private final InboxResponseInspector structure;

  public NonAuthenticationInboxInspector(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
    structure = new InboxResponseInspector(snapshots);
  }

  /** False preserves an unsupported/unverified row; null caller arguments violate the contract. */
  public boolean isConsistent(
      Connection connection, ResponseSnapshotIdentity identity, InboxCompletion completion) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(completion, "completion");
    var codes = STORED_CODES.get(identity.responseLayoutId());
    if (codes == null || identity.ownerUserId().isEmpty()) return false;
    if (!structure.isStructurallyValid(identity, completion)) return false;
    try {
      if (connection.getAutoCommit()) return false;
      byte[] wire = snapshots.decrypt(identity, completion.responseSnapshot().orElseThrow());
      try {
        var header = HeaderCodec.standard().peek(wire);
        var code = header.resultCode().orElseThrow();
        if (!codes.contains(code.wireValue())) return false;
        var reference = completion.resultReference();
        if (!code.usesSuccessProfile()) return reference.equals(InboxResultReference.none());
        String layout = identity.responseLayoutId();
        if (MUTATIONS.contains(layout)) {
          var data = (UserMutationResponseData) decode(header, wire);
          long version = data.updatedVersion();
          if (layout.equals("UCRRSP01")) {
            if (version != 0) return false;
          } else if (code.wireValue().equals("0000") && version == 0) return false;
          return reference.equals(
                  InboxResultReference.numeric(
                      InboxResultReferenceType.USER, data.userId().value()))
              && referenceValueWithin(
                  connection,
                  "select version as reference_value from schubert.app_users where id = ?",
                  data.userId().value(),
                  version,
                  999_999_999L);
        }
        if (layout.equals("SCNRSP01")) {
          var data = (ScenarioDetailResponseData) decode(header, wire);
          if (data.deliveryMode() == DeliveryMode.INLINE)
            return reference.equals(InboxResultReference.none());
          // Generated record-file hash is not the raw master hash. Physical .ready expiry is valid.
          new LargeResultDescriptor(
              data.fileId().orElseThrow(),
              data.fileRelativePath().orElseThrow().wireValue(),
              data.fileByteLength(),
              data.fileSha256().orElseThrow().wireValue(),
              Math.toIntExact(data.fileRecordCount()));
          long game = data.gameCode() == GameCode.NUKITASHI_1 ? 1 : 2;
          return reference.equals(
                  InboxResultReference.numeric(
                      InboxResultReferenceType.SCENARIO_FILE, data.scriptFileId().value()))
              && referenceValueWithin(
                  connection,
                  "select cast(game_id as bigint) as reference_value from schubert.script_files where id = ?",
                  data.scriptFileId().value(),
                  game,
                  game);
        }
        return reference.equals(InboxResultReference.none());
      } finally {
        Arrays.fill(wire, (byte) 0);
      }
    } catch (SQLException
        | ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      return false;
    }
  }

  private static PayloadData decode(CommonHeader header, byte[] wire) {
    var layout = LayoutRegistry.standard().require(header.layoutId(), header.layoutVersion());
    int offset = 256 + layout.dataLength();
    byte[] data = Arrays.copyOfRange(wire, 256, offset);
    var records = new ArrayList<byte[]>(header.recordCount());
    try {
      for (int i = 0; i < header.recordCount(); i++) {
        records.add(Arrays.copyOfRange(wire, offset, offset + layout.recordLength()));
        offset += layout.recordLength();
      }
      var values =
          PayloadCodec.standard()
              .decode(header.layoutId(), data, records, header.resultCode().orElseThrow());
      return PayloadTypeCatalog.decode(values).data();
    } finally {
      Arrays.fill(data, (byte) 0);
      for (byte[] record : records) Arrays.fill(record, (byte) 0);
    }
  }

  private static boolean referenceValueWithin(
      Connection connection, String sql, long id, long minimum, long maximum) throws SQLException {
    boolean valid = false;
    try (var statement = connection.prepareStatement(sql)) {
      statement.setLong(1, id);
      try (var rows = statement.executeQuery()) {
        if (rows.next()) {
          Long value = rows.getObject("reference_value", Long.class);
          valid = value != null && value >= minimum && value <= maximum && !rows.next();
        }
      }
    }
    return valid;
  }
}
