package dev.codex.schubert.nk.protocol.layout;

/** Named fixed-width data record with an explicit UI field mapping. */
public interface PayloadData {
  FieldValueSet fields();
}
