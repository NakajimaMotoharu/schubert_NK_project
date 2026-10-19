package dev.codex.schubert.nk.protocol.header;

import java.util.Arrays;
import java.util.Objects;

/** Approved four-byte result codes. Trace: NK-PRO-001, UI 232 §7. */
public enum ResultCode {
  SUCCESS("0000", true),
  VALIDATION_ERROR("0100", false),
  AUTHENTICATION_FAILED("0101", false),
  SESSION_INVALID("0102", false),
  FORBIDDEN("0103", false),
  NOT_FOUND("0104", false),
  CONFLICT("0105", false),
  LOCKED("0106", false),
  NOT_CANCELLABLE("0107", false),
  IDEMPOTENT_SUCCESS("0200", true),
  TEMPORARY_FAILURE("9000", false),
  RESOURCE_LIMIT("9001", false);

  private final String encodedValue;
  private final boolean successProfile;

  ResultCode(String wireValue, boolean successProfile) {
    this.encodedValue = wireValue;
    this.successProfile = successProfile;
  }

  public String wireValue() {
    return encodedValue;
  }

  public boolean usesSuccessProfile() {
    return successProfile;
  }

  public static ResultCode fromWire(String value) {
    Objects.requireNonNull(value, "value");
    return Arrays.stream(values())
        .filter(candidate -> candidate.encodedValue.equals(value))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("unknown result code"));
  }
}
