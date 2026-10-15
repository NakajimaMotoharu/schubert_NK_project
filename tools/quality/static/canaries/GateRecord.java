package dev.codex.schubert.quality;

record GateRecord(byte[] value) implements AutoCloseable {
  @Override
  public void close() {
    if (value != null) java.util.Arrays.fill(value, (byte) 0);
  }
}
