package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * PT-IDEM-REFERENCE001..003; SS324/331/354: inert values only, no repository/session/codec grant.
 */
final class InboxReferenceValueContractTest {
  private static final UUID ID = new UUID(0, 1);
  private static final UUID OTHER_ID = new UUID(0, 2);
  private static final long MAXIMUM_ID = 999_999_999_999L;
  private static final String FIXED = "result reference value does not match its type";

  @Test
  void reference001IndependentLiteralAcceptedSetClassifiesAllEightyFourCells() {
    Set<String> accepted =
        Set.of(
            "NONE:none:false", "AUTH_SESSION:none:true",
            "USER:one:false", "USER:max:false",
            "QUESTION:one:false", "QUESTION:max:false",
            "JOB:one:false", "JOB:max:false",
            "SCENARIO_FILE:one:false", "SCENARIO_FILE:max:false");
    List<OptionalLong> ids =
        List.of(
            OptionalLong.empty(),
            OptionalLong.of(0),
            OptionalLong.of(-1),
            OptionalLong.of(1),
            OptionalLong.of(MAXIMUM_ID),
            OptionalLong.of(1_000_000_000_000L),
            OptionalLong.of(Long.MAX_VALUE));
    String[] labels = {"none", "zero", "negative", "one", "max", "over", "longmax"};
    int permitted = 0;
    int rejected = 0;
    for (InboxResultReferenceType type : InboxResultReferenceType.values()) {
      for (int index = 0; index < ids.size(); index++) {
        OptionalLong numeric = ids.get(index);
        for (boolean present : List.of(false, true)) {
          Optional<UUID> uuid = present ? Optional.of(ID) : Optional.empty();
          String cell = type.name() + ":" + labels[index] + ":" + present;
          if (accepted.contains(cell)) {
            InboxResultReference actual = new InboxResultReference(type, numeric, uuid);
            assertSame(type, actual.type());
            assertEquals(numeric, actual.numericId());
            assertEquals(uuid, actual.uuid());
            assertEquals("InboxResultReference[<redacted>]", actual.toString());
            permitted++;
          } else {
            IllegalArgumentException failure =
                assertThrows(
                    IllegalArgumentException.class,
                    () -> new InboxResultReference(type, numeric, uuid),
                    cell);
            assertEquals(FIXED, failure.getMessage());
            assertNull(failure.getCause());
            assertEquals(0, failure.getSuppressed().length);
            rejected++;
          }
        }
      }
    }
    assertEquals(10, permitted);
    assertEquals(74, rejected);
  }

  @Test
  void reference002PublicFactoriesAndEveryAdmittedValueShapeKeepTheirRecordIdentity() {
    InboxResultReference none = InboxResultReference.none();
    assertSame(InboxResultReferenceType.NONE, none.type());
    assertEquals(OptionalLong.empty(), none.numericId());
    assertEquals(Optional.empty(), none.uuid());
    InboxResultReference session = InboxResultReference.authSession(ID);
    assertSame(InboxResultReferenceType.AUTH_SESSION, session.type());
    assertEquals(OptionalLong.empty(), session.numericId());
    assertEquals(Optional.of(ID), session.uuid());
    for (InboxResultReferenceType type :
        List.of(
            InboxResultReferenceType.USER,
            InboxResultReferenceType.QUESTION,
            InboxResultReferenceType.JOB,
            InboxResultReferenceType.SCENARIO_FILE)) {
      InboxResultReference numeric = InboxResultReference.numeric(type, MAXIMUM_ID);
      assertSame(type, numeric.type());
      assertEquals(OptionalLong.of(MAXIMUM_ID), numeric.numericId());
      assertEquals(Optional.empty(), numeric.uuid());
    }
    for (InboxResultReference value :
        List.of(none, session, InboxResultReference.numeric(InboxResultReferenceType.USER, 1))) {
      InboxResultReference equal =
          new InboxResultReference(value.type(), value.numericId(), value.uuid());
      assertEquals(value, value);
      assertEquals(value, equal);
      assertEquals(equal, value);
      assertEquals(value.hashCode(), equal.hashCode());
      assertEquals("found", Map.of(value, "found").get(equal));
      assertNotEquals(value, null);
      assertNotEquals(value, "different type");
    }
    InboxResultReference user = InboxResultReference.numeric(InboxResultReferenceType.USER, 1);
    for (InboxResultReference other :
        List.of(
            none,
            session,
            InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 1),
            InboxResultReference.numeric(InboxResultReferenceType.USER, MAXIMUM_ID))) {
      assertNotEquals(user, other);
      assertNotEquals(other, user);
    }
    assertNotEquals(session, InboxResultReference.authSession(OTHER_ID));
    assertThrows(
        IllegalArgumentException.class,
        () -> InboxResultReference.numeric(InboxResultReferenceType.NONE, 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> InboxResultReference.numeric(InboxResultReferenceType.AUTH_SESSION, 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> InboxResultReference.numeric(InboxResultReferenceType.USER, 0));
    assertThrows(NullPointerException.class, () -> InboxResultReference.authSession(null));
    assertThrows(NullPointerException.class, () -> InboxResultReference.numeric(null, 1));
    assertThrows(
        NullPointerException.class,
        () -> new InboxResultReference(null, OptionalLong.empty(), Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new InboxResultReference(InboxResultReferenceType.NONE, null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new InboxResultReference(InboxResultReferenceType.NONE, OptionalLong.empty(), null));
  }

  @Test
  void reference003ClosedEnumNamesOrderOrdinalAndFactoriesDoNotExposeTheReturnedArray() {
    String[] names = {"NONE", "AUTH_SESSION", "USER", "QUESTION", "JOB", "SCENARIO_FILE"};
    InboxResultReferenceType[] values = InboxResultReferenceType.values();
    assertArrayEquals(names, Arrays.stream(values).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < names.length; index++) {
      assertEquals(index, values[index].ordinal());
      assertSame(values[index], InboxResultReferenceType.valueOf(names[index]));
    }
    InboxResultReferenceType[] copy = InboxResultReferenceType.values();
    assertNotSame(values, copy);
    copy[0] = null;
    assertSame(InboxResultReferenceType.NONE, InboxResultReferenceType.values()[0]);
    for (String unknown : List.of("", "none", "NONE ", "unknown")) {
      assertThrows(IllegalArgumentException.class, () -> InboxResultReferenceType.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> InboxResultReferenceType.valueOf(null));
  }
}
