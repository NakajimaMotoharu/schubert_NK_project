package dev.codex.schubert.nk.protocol.layout;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/** Defensive exact-width payload bytes; its textual form never exposes field content. */
public final class FixedPayload implements LayoutPayload {
  private final byte[] data;
  private final int recordLength;
  private final List<byte[]> records;

  public FixedPayload(byte[] data, int recordLength, List<byte[]> records) {
    Objects.requireNonNull(data, "data");
    Objects.requireNonNull(records, "records");
    if (recordLength < 0) {
      throw new LayoutValidationException("record length must not be negative");
    }
    this.data = data.clone();
    this.recordLength = recordLength;
    ArrayList<byte[]> copies = new ArrayList<>(records.size());
    for (byte[] record : records) {
      Objects.requireNonNull(record, "record");
      if (record.length != recordLength) {
        throw new LayoutValidationException("record byte length differs from its declaration");
      }
      copies.add(record.clone());
    }
    this.records = Collections.unmodifiableList(copies);
  }

  @Override
  public int dataLength() {
    return data.length;
  }

  @Override
  public int recordLength() {
    return recordLength;
  }

  @Override
  public int recordCount() {
    return records.size();
  }

  @Override
  public byte[] copyData() {
    return data.clone();
  }

  @Override
  public List<byte[]> copyRecords() {
    ArrayList<byte[]> copies = new ArrayList<>(records.size());
    for (byte[] record : records) {
      copies.add(record.clone());
    }
    return Collections.unmodifiableList(copies);
  }

  @Override
  public String toString() {
    return "FixedPayload[dataLength="
        + data.length
        + ", recordLength="
        + recordLength
        + ", recordCount="
        + records.size()
        + ']';
  }
}
