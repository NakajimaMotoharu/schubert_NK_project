package dev.codex.schubert.nk.protocol.codec;

/** Immutable non-public grammar cache. Trace: SSC451, SS322/323/333. */
interface FieldCodecRules {

  int BOOLEAN_FIELD_LENGTH = 1;
  int MINIMUM_FIELD_LENGTH = 1;

  java.lang.String LITERAL_FIELD = "field";

  byte ASCII_SPACE = 0x20;
  byte ASCII_ZERO = 0x30;
}
