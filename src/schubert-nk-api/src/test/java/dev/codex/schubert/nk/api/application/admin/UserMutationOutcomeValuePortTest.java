package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-ADM-001/FUN009; UI232/236; SS312/323/332/351; ADM-VALUE-001..004; no command/DB. */
@Timeout(10)
final class UserMutationOutcomeValuePortTest {
  private static final String ID_FIELD = "User ID";
  private static final String VERSION_FIELD = "更新後version";
  private static final long MAXIMUM_VERSION = 999_999_999L;
  private static final UserId ID = new UserId(7);

  @Test
  void value001ClosedProfileTableRejectsEveryOtherPayloadCombination() {
    var payload = new UserMutationResponseData(ID, 0);
    var present = Optional.of(payload);
    Set<String> success = Set.of("0000", "0200");
    Set<String> denial = Set.of("0100", "0104", "0105", "9001");
    assertEquals(12, ResultCode.values().length);
    for (ResultCode code : ResultCode.values()) {
      if (success.contains(code.wireValue())) {
        var result = new UserMutationResult(code, present);
        assertSame(code, result.resultCode());
        assertSame(payload, result.data().orElseThrow());
        assertEquals("UserMutationResult[REDACTED]", result.toString());
        assertThrows(
            IllegalArgumentException.class, () -> new UserMutationResult(code, Optional.empty()));
      } else {
        assertThrows(IllegalArgumentException.class, () -> new UserMutationResult(code, present));
        if (denial.contains(code.wireValue())) {
          var result = new UserMutationResult(code, Optional.empty());
          assertSame(code, result.resultCode());
          assertTrue(result.data().isEmpty());
        } else {
          assertThrows(
              IllegalArgumentException.class, () -> new UserMutationResult(code, Optional.empty()));
        }
      }
    }
    assertThrows(NullPointerException.class, () -> new UserMutationResult(null, Optional.empty()));
    assertThrows(
        NullPointerException.class, () -> new UserMutationResult(ResultCode.SUCCESS, null));
  }

  @Test
  void value002FactoriesKeepIdentityAndN9BoundsWithoutFabricatingFailureData() {
    for (long version : List.of(0L, MAXIMUM_VERSION)) {
      for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS)) {
        var result = UserMutationResult.accepted(ID, version, code);
        assertSame(code, result.resultCode());
        var data = result.data().orElseThrow();
        assertSame(ID, data.userId());
        assertEquals(version, data.updatedVersion());
      }
    }
    for (ResultCode code :
        List.of(
            ResultCode.VALIDATION_ERROR,
            ResultCode.NOT_FOUND,
            ResultCode.CONFLICT,
            ResultCode.RESOURCE_LIMIT)) {
      var result = UserMutationResult.rejected(code);
      assertSame(code, result.resultCode());
      assertTrue(result.data().isEmpty());
      assertThrows(IllegalArgumentException.class, () -> UserMutationResult.accepted(ID, 0, code));
    }
    for (long invalid : List.of(-1L, 1_000_000_000L, Long.MIN_VALUE, Long.MAX_VALUE)) {
      assertThrows(
          LayoutValidationException.class,
          () -> UserMutationResult.accepted(ID, invalid, ResultCode.SUCCESS));
    }
    assertThrows(
        NullPointerException.class, () -> UserMutationResult.accepted(null, 0, ResultCode.SUCCESS));
    assertThrows(NullPointerException.class, () -> UserMutationResult.accepted(ID, 0, null));
    assertThrows(NullPointerException.class, () -> UserMutationResult.rejected(null));
    assertThrows(
        IllegalArgumentException.class, () -> UserMutationResult.rejected(ResultCode.SUCCESS));
    assertThrows(
        IllegalArgumentException.class,
        () -> UserMutationResult.rejected(ResultCode.IDEMPOTENT_SUCCESS));
  }

  @Test
  void value003MicrosecondFloorPreservesTraceValuesAtNegativeEpochAndInstantLimits() {
    UUID message = UUID.fromString("00000000-0000-0000-0000-000000000011");
    UUID correlation = UUID.fromString("00000000-0000-0000-0000-000000000022");
    // Independent ISO literals, including pre-epoch flooring; no Production truncation as oracle.
    Map<String, String> times =
        Map.of(
            "2026-09-08T00:00:00.000000999Z", "2026-09-08T00:00:00Z",
            "2026-09-08T00:00:00.123456789Z", "2026-09-08T00:00:00.123456Z",
            "1969-12-31T23:59:59.999999999Z", "1969-12-31T23:59:59.999999Z",
            "1970-01-01T00:00:00.000001Z", "1970-01-01T00:00:00.000001Z",
            "-1000000000-01-01T00:00:00Z", "-1000000000-01-01T00:00:00Z",
            "+1000000000-12-31T23:59:59.999999999Z", "+1000000000-12-31T23:59:59.999999Z");
    for (var entry : times.entrySet()) {
      var metadata = new UserCommandMetadata(message, correlation, Instant.parse(entry.getKey()));
      assertSame(message, metadata.messageId());
      assertSame(correlation, metadata.correlationId());
      assertEquals(Instant.parse(entry.getValue()), metadata.at());
      assertEquals("UserCommandMetadata[REDACTED]", metadata.toString());
    }
    assertThrows(
        NullPointerException.class,
        () -> new UserCommandMetadata(null, correlation, Instant.EPOCH));
    assertThrows(
        NullPointerException.class, () -> new UserCommandMetadata(message, null, Instant.EPOCH));
    assertThrows(
        NullPointerException.class, () -> new UserCommandMetadata(message, correlation, null));
  }

  @Test
  void value004ResponseProjectionAndParsingUseIndependentNamedLiteralFields() {
    var response = new UserMutationResponseData(ID, MAXIMUM_VERSION);
    var fields = response.fields();
    assertEquals(Set.of(ID_FIELD, VERSION_FIELD), fields.names());
    assertEquals(2, fields.size());
    assertEquals(7L, ((FieldValue.Numeric) fields.getOrUnset(ID_FIELD)).value());
    assertEquals(MAXIMUM_VERSION, ((FieldValue.Numeric) fields.getOrUnset(VERSION_FIELD)).value());
    assertThrows(UnsupportedOperationException.class, () -> fields.names().clear());
    // This fixture is not response.fields(): parsing is checked against independent numeric inputs.
    var parsed =
        UserMutationResponseData.from(
            new FieldValueSet(
                Map.of(
                    ID_FIELD, new FieldValue.Numeric(999_999_999_999L),
                    VERSION_FIELD, new FieldValue.Numeric(0))));
    assertEquals(999_999_999_999L, parsed.userId().value());
    assertEquals(0L, parsed.updatedVersion());
    assertEquals("UserMutationResponseData[REDACTED]", parsed.toString());
    assertThrows(NullPointerException.class, () -> UserMutationResponseData.from(null));
    assertThrows(NullPointerException.class, () -> new UserMutationResponseData(null, 0));
    assertThrows(
        LayoutValidationException.class,
        () -> UserMutationResponseData.from(FieldValueSet.empty()));
    for (FieldValue invalid : List.of(new FieldValue.Text("7"), FieldValue.Unset.INSTANCE)) {
      assertThrows(
          LayoutValidationException.class,
          () ->
              UserMutationResponseData.from(
                  new FieldValueSet(
                      Map.of(ID_FIELD, invalid, VERSION_FIELD, new FieldValue.Numeric(0)))));
      assertThrows(
          LayoutValidationException.class,
          () ->
              UserMutationResponseData.from(
                  new FieldValueSet(
                      Map.of(ID_FIELD, new FieldValue.Numeric(7), VERSION_FIELD, invalid))));
    }
    for (long invalid : List.of(-1L, 1_000_000_000L)) {
      assertThrows(
          LayoutValidationException.class,
          () ->
              UserMutationResponseData.from(
                  new FieldValueSet(
                      Map.of(
                          ID_FIELD,
                          new FieldValue.Numeric(7),
                          VERSION_FIELD,
                          new FieldValue.Numeric(invalid)))));
    }
    for (long invalid : List.of(0L, 1_000_000_000_000L)) {
      assertThrows(
          LayoutValidationException.class,
          () ->
              UserMutationResponseData.from(
                  new FieldValueSet(
                      Map.of(
                          ID_FIELD,
                          new FieldValue.Numeric(invalid),
                          VERSION_FIELD,
                          new FieldValue.Numeric(0)))));
    }
  }
}
