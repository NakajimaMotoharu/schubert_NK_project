package dev.codex.schubert.nk.protocol.layout.semantic;

/** Positive N12 protocol identifier. Trace: NK-PRO-001, SS 323 section 2. */
public sealed interface ProtocolId
    permits AsyncJobId,
        AudioId,
        EntryId,
        LogId,
        NotificationId,
        QuestionId,
        ScriptFileId,
        SpeakerId,
        UserId {
  long value();
}
