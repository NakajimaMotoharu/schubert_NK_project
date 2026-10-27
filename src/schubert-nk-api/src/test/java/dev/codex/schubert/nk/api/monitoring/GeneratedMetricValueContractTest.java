package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** GENMET001..008: compiler-generated value contracts, independent literals/JDK25 hash vectors. */
class GeneratedMetricValueContractTest {
  private static final String ERROR_STATE = "ERROR";
  private static final String PENDING_STATE = "PENDING";

  @Test
  void genMetric001PoolRecordEqualityUsesEveryComponentAndRejectsNullAndOtherTypes() {
    var actual = new DbPoolMetricRecorder.Counts(3, 5, 2, 8);
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = "not a pool count";
    assertTrue(actual.equals(sameInstance));
    assertTrue(actual.equals(new DbPoolMetricRecorder.Counts(3, 5, 2, 8)));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    for (var different :
        List.of(
            new DbPoolMetricRecorder.Counts(4, 5, 2, 8),
            new DbPoolMetricRecorder.Counts(3, 6, 2, 8),
            new DbPoolMetricRecorder.Counts(3, 5, 3, 8),
            new DbPoolMetricRecorder.Counts(3, 5, 2, 9))) assertFalse(actual.equals(different));
    assertEquals(3, actual.active());
    assertEquals(5, actual.idle());
    assertEquals(2, actual.pending());
    assertEquals(8, actual.maximum());
  }

  @Test
  void genMetric002PoolRecordGeneratedHashAndTextHaveIndependentFixedVectors() {
    var actual = new DbPoolMetricRecorder.Counts(3, 5, 2, 8);
    // JDK25 ObjectMethods.hashCombiner: 31*h + Long.hashCode(component), initial h=0.
    assertEquals(94248, actual.hashCode());
    assertEquals("Counts[active=3, idle=5, pending=2, maximum=8]", actual.toString());
    var maximum =
        new DbPoolMetricRecorder.Counts(
            Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE);
    assertEquals(0, maximum.hashCode());
    assertEquals(
        "Counts[active=9223372036854775807, idle=9223372036854775807, pending=9223372036854775807, maximum=9223372036854775807]",
        maximum.toString());
  }

  @Test
  void genMetric003OutboxRecordEqualityUsesEveryComponentAndRejectsNullAndOtherTypes() {
    var actual = new OutboxRowsMetricRecorder.Counts(3, 5, 2);
    Object sameInstance = actual;
    Object absent = null;
    Object otherType = new DbPoolMetricRecorder.Counts(3, 5, 2, 8);
    assertTrue(actual.equals(sameInstance));
    assertTrue(actual.equals(new OutboxRowsMetricRecorder.Counts(3, 5, 2)));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(otherType));
    for (var different :
        List.of(
            new OutboxRowsMetricRecorder.Counts(4, 5, 2),
            new OutboxRowsMetricRecorder.Counts(3, 6, 2),
            new OutboxRowsMetricRecorder.Counts(3, 5, 3))) assertFalse(actual.equals(different));
    assertEquals(3, actual.pending());
    assertEquals(5, actual.sent());
    assertEquals(2, actual.error());
  }

  @Test
  void genMetric004OutboxRecordGeneratedHashAndTextHaveIndependentFixedVectors() {
    var actual = new OutboxRowsMetricRecorder.Counts(3, 5, 2);
    assertEquals(3040, actual.hashCode());
    assertEquals("Counts[pending=3, sent=5, error=2]", actual.toString());
    var maximum =
        new OutboxRowsMetricRecorder.Counts(Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE);
    assertEquals(Integer.MIN_VALUE, maximum.hashCode());
    assertEquals(
        "Counts[pending=9223372036854775807, sent=9223372036854775807, error=9223372036854775807]",
        maximum.toString());
    assertEquals(0, new OutboxRowsMetricRecorder.Counts(0, 0, 0).hashCode());
  }

  @Test
  void genMetric005AsyncEnumGeneratedFactoriesAndDefensiveArrayAreClosed() {
    assertEquals(
        List.of("RECEIVED", "PROCESSING", "COMPLETED", ERROR_STATE, "CANCELLED"),
        Arrays.stream(AsyncJobMetricRecorder.State.values()).map(Enum::name).toList());
    assertEquals(
        AsyncJobMetricRecorder.State.RECEIVED, AsyncJobMetricRecorder.State.valueOf("RECEIVED"));
    assertEquals(
        AsyncJobMetricRecorder.State.PROCESSING,
        AsyncJobMetricRecorder.State.valueOf("PROCESSING"));
    assertEquals(
        AsyncJobMetricRecorder.State.COMPLETED, AsyncJobMetricRecorder.State.valueOf("COMPLETED"));
    assertEquals(
        AsyncJobMetricRecorder.State.ERROR, AsyncJobMetricRecorder.State.valueOf(ERROR_STATE));
    assertEquals(
        AsyncJobMetricRecorder.State.CANCELLED, AsyncJobMetricRecorder.State.valueOf("CANCELLED"));
    assertThrows(
        IllegalArgumentException.class, () -> AsyncJobMetricRecorder.State.valueOf("UNKNOWN"));
    assertThrows(NullPointerException.class, () -> AsyncJobMetricRecorder.State.valueOf(null));
    var copy = AsyncJobMetricRecorder.State.values();
    copy[0] = AsyncJobMetricRecorder.State.CANCELLED;
    assertEquals(AsyncJobMetricRecorder.State.RECEIVED, AsyncJobMetricRecorder.State.values()[0]);
  }

  @Test
  void genMetric006PoolEnumGeneratedFactoriesAndDefensiveArrayAreClosed() {
    assertEquals(
        List.of("ACTIVE", "IDLE", PENDING_STATE, "MAX"),
        Arrays.stream(DbPoolMetricRecorder.State.values()).map(Enum::name).toList());
    assertEquals(DbPoolMetricRecorder.State.ACTIVE, DbPoolMetricRecorder.State.valueOf("ACTIVE"));
    assertEquals(DbPoolMetricRecorder.State.IDLE, DbPoolMetricRecorder.State.valueOf("IDLE"));
    assertEquals(
        DbPoolMetricRecorder.State.PENDING, DbPoolMetricRecorder.State.valueOf(PENDING_STATE));
    assertEquals(DbPoolMetricRecorder.State.MAX, DbPoolMetricRecorder.State.valueOf("MAX"));
    assertThrows(
        IllegalArgumentException.class, () -> DbPoolMetricRecorder.State.valueOf("active"));
    assertThrows(NullPointerException.class, () -> DbPoolMetricRecorder.State.valueOf(null));
    var copy = DbPoolMetricRecorder.State.values();
    copy[0] = DbPoolMetricRecorder.State.MAX;
    assertEquals(DbPoolMetricRecorder.State.ACTIVE, DbPoolMetricRecorder.State.values()[0]);
  }

  @Test
  void genMetric007OperationEnumGeneratedFactoriesAndDefensiveArrayAreClosed() {
    assertEquals(
        List.of(
            "UCRREQ01",
            "USTREQ01",
            "URLREQ01",
            "UPWREQ01",
            "ULKREQ01",
            "QSBREQ01",
            "NTCREQ01",
            "QDLREQ01"),
        Arrays.stream(OperationMismatchMetricRecorder.Operation.values()).map(Enum::name).toList());
    assertEquals(
        OperationMismatchMetricRecorder.Operation.UCRREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("UCRREQ01"));
    assertEquals(
        OperationMismatchMetricRecorder.Operation.USTREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("USTREQ01"));
    assertEquals(
        OperationMismatchMetricRecorder.Operation.URLREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("URLREQ01"));
    assertEquals(
        OperationMismatchMetricRecorder.Operation.UPWREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("UPWREQ01"));
    assertEquals(
        OperationMismatchMetricRecorder.Operation.ULKREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("ULKREQ01"));
    assertEquals(
        OperationMismatchMetricRecorder.Operation.QSBREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("QSBREQ01"));
    assertEquals(
        OperationMismatchMetricRecorder.Operation.NTCREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("NTCREQ01"));
    assertEquals(
        OperationMismatchMetricRecorder.Operation.QDLREQ01,
        OperationMismatchMetricRecorder.Operation.valueOf("QDLREQ01"));
    assertThrows(
        IllegalArgumentException.class,
        () -> OperationMismatchMetricRecorder.Operation.valueOf("UNKNOWN"));
    assertThrows(
        NullPointerException.class, () -> OperationMismatchMetricRecorder.Operation.valueOf(null));
    var copy = OperationMismatchMetricRecorder.Operation.values();
    copy[0] = OperationMismatchMetricRecorder.Operation.QDLREQ01;
    assertEquals(
        OperationMismatchMetricRecorder.Operation.UCRREQ01,
        OperationMismatchMetricRecorder.Operation.values()[0]);
  }

  @Test
  void genMetric008OutboxEnumGeneratedFactoriesAndDefensiveArrayAreClosed() {
    assertEquals(
        List.of(PENDING_STATE, "SENT", ERROR_STATE),
        Arrays.stream(OutboxRowsMetricRecorder.Status.values()).map(Enum::name).toList());
    assertEquals(
        OutboxRowsMetricRecorder.Status.PENDING,
        OutboxRowsMetricRecorder.Status.valueOf(PENDING_STATE));
    assertEquals(
        OutboxRowsMetricRecorder.Status.SENT, OutboxRowsMetricRecorder.Status.valueOf("SENT"));
    assertEquals(
        OutboxRowsMetricRecorder.Status.ERROR,
        OutboxRowsMetricRecorder.Status.valueOf(ERROR_STATE));
    assertThrows(
        IllegalArgumentException.class, () -> OutboxRowsMetricRecorder.Status.valueOf("UNKNOWN"));
    assertThrows(NullPointerException.class, () -> OutboxRowsMetricRecorder.Status.valueOf(null));
    var copy = OutboxRowsMetricRecorder.Status.values();
    copy[0] = OutboxRowsMetricRecorder.Status.ERROR;
    assertEquals(
        OutboxRowsMetricRecorder.Status.PENDING, OutboxRowsMetricRecorder.Status.values()[0]);
  }
}
