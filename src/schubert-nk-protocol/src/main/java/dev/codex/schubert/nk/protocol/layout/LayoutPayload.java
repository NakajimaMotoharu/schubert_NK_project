package dev.codex.schubert.nk.protocol.layout;

import java.util.List;

/**
 * Sealed protocol payload carrier. Business typed records are layered over this exact byte model.
 */
public sealed interface LayoutPayload permits FixedPayload {
  int dataLength();

  int recordLength();

  int recordCount();

  byte[] copyData();

  List<byte[]> copyRecords();
}
