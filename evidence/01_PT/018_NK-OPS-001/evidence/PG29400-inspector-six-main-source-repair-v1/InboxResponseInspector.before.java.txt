package dev.codex.schubert.nk.api.maintenance;

import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.QuestionQueryScopeFrame;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Checks stored ciphertext and response structure only; never authorizes deletion or certifies a
 * database reference. No SQL, replay, authentication or logging side effects. The caller owns the
 * codec lifetime. NK-DAT-001/NK-MSG-002; OPS-009/MQ-008; UI212/241/251; SS324 section12.1/352;
 * QA-046/UIC-006/SSC-049/BUG-014/YKT-012; PG-D-119; PT-DB-INBOX-001..008.
 */
@NullMarked
public final class InboxResponseInspector {
  private final ResponseSnapshotCodec snapshots;

  public InboxResponseInspector(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
  }

  /**
   * False means preserve the row. True still requires independent DB reference, expiry, backup and
   * concurrency checks in the deletion transaction. Null caller arguments violate the contract.
   */
  public boolean isStructurallyValid(
      ResponseSnapshotIdentity identity, InboxCompletion completion) {
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(completion, "completion");
    if (!identity.responseLayoutId().equals(completion.responseLayoutId())
        || !identity.responseVersion().equals(completion.responseVersion())
        || completion.responseSnapshot().isEmpty()) return false;
    try {
      byte[] plaintext = snapshots.decrypt(identity, completion.responseSnapshot().orElseThrow());
      try {
        byte[] wire = QuestionQueryScopeFrame.wireForInspection(identity, plaintext);
        try {
          return inspect(identity, completion, wire);
        } finally {
          Arrays.fill(wire, (byte) 0);
        }
      } finally {
        Arrays.fill(plaintext, (byte) 0);
      }
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      return false;
    }
  }

  // Shared only with the bound mutation inspector after identity/completion/envelope checks.
  // Borrowed plaintext; no public verified flag or ownership transfer. SS324 12.9/PT177..192.
  static boolean inspect(
      ResponseSnapshotIdentity identity, InboxCompletion completion, byte[] wire) {
    var registry = LayoutRegistry.standard();
    var header = new HeaderCodec(registry).peek(wire);
    if (header.messageKind() != MessageKind.RESPONSE
        || !header.layoutId().value().equals(identity.responseLayoutId())
        || !identity.responseVersion().equals("001")
        || !header.correlationId().equals(identity.requestMessageId())
        || header.totalLength() != wire.length
        || !header.sentAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)))
      return false;
    var code = header.resultCode().orElseThrow();
    if (code.usesSuccessProfile() != (completion.state() == InboxCompletionState.COMPLETED))
      return false;
    var layout = registry.require(header.layoutId(), header.layoutVersion());
    int offset = 256 + layout.dataLength();
    byte[] data = Arrays.copyOfRange(wire, 256, offset);
    var records = new ArrayList<byte[]>(header.recordCount());
    try {
      for (int i = 0; i < header.recordCount(); i++) {
        records.add(Arrays.copyOfRange(wire, offset, offset + layout.recordLength()));
        offset += layout.recordLength();
      }
      var values = PayloadCodec.standard().decode(header.layoutId(), data, records, code);
      if (code.usesSuccessProfile()) PayloadTypeCatalog.decode(values);
      return true;
    } finally {
      Arrays.fill(data, (byte) 0);
      for (byte[] record : records) Arrays.fill(record, (byte) 0);
    }
  }
}
