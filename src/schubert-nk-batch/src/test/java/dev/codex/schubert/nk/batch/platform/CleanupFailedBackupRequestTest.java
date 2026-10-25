package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS343 SSC124 independent literal, never an expected frame generated with Production encode. */
final class CleanupFailedBackupRequestTest {
  private static final String GOLDEN =
      """
      NKCLEANFAIL1
      run=11111111-2222-4333-8444-555555555555
      activation=21111111-2222-4333-8444-555555555555
      cutoff=2026-09-27T15:00:00Z
      boot=31111111-2222-4333-8444-555555555555
      epoch=41111111-2222-4333-8444-555555555555
      backup_invocation=51111111-2222-4333-8444-555555555555
      backup_started_monotonic=1000000000
      backup_ended_monotonic=2000000000
      backup_exit=30
      database=7,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:05.654321Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed
      configuration=8,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:05.654321Z,FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed
      """;

  private static byte[] bytes(String input) {
    return input.getBytes(StandardCharsets.US_ASCII);
  }

  @Test
  void cfreq001LiteralBytesAndIndependentFieldsMatchBothClosedProfiles() {
    byte[] input = bytes(GOLDEN);
    var value = CleanupFailedBackupRequest.consume(input);
    assertArrayEquals(new byte[input.length], input);
    assertArrayEquals(bytes(GOLDEN), value.encode());
    assertEquals(UUID.fromString("11111111-2222-4333-8444-555555555555"), value.run());
    assertEquals(7, value.failure().database().id());
    assertEquals(8, value.failure().configuration().id());
    assertEquals(java.time.LocalDate.of(2026, 9, 28), value.failure().database().businessDate());
    assertEquals("CleanupFailedBackupRequest[data=<redacted>]", value.toString());
    assertEquals("BackupFailureSnapshot[data=<redacted>]", value.failure().toString());
    assertInstanceOf(CleanupFailedBackupRequest.class, CleanupProfile.consume(bytes(GOLDEN)));
    String success =
        """
        NKCLEAN1
        run=11111111-2222-4333-8444-555555555555
        activation=21111111-2222-4333-8444-555555555555
        cutoff=2026-09-27T15:00:00Z
        manifest=0000000000000000000000000000000000000000000000000000000000000000
        """;
    assertInstanceOf(CleanupWorkerRequest.class, CleanupProfile.consume(bytes(success)));
  }

  @Test
  void cfreq002MalformedOwnedInputsAlwaysClearAndNeverBecomeSuccess() {
    assertThrows(NullPointerException.class, () -> CleanupFailedBackupRequest.consume(null));
    assertThrows(NullPointerException.class, () -> CleanupProfile.consume(null));
    for (String bad :
        List.of(
            "",
            "x",
            "a".repeat(1025),
            GOLDEN + "\n",
            GOLDEN.replace("NKCLEANFAIL1", "NKCLEAN1"),
            GOLDEN.replace("\nrun=", "\nother="),
            GOLDEN.replace("\nboot=", "\nrun="),
            GOLDEN.replace("\n", "\r\n"),
            GOLDEN + "extra=x\n",
            GOLDEN.substring(0, GOLDEN.length() - 1),
            GOLDEN.replace("backup_exit=30", "backup_exit=\u0000"))) {
      byte[] owned = bytes(bad);
      assertThrows(IllegalArgumentException.class, () -> CleanupFailedBackupRequest.consume(owned));
      assertArrayEquals(new byte[owned.length], owned);
      byte[] closed = bytes(bad);
      assertThrows(IllegalArgumentException.class, () -> CleanupProfile.consume(closed));
      assertArrayEquals(new byte[closed.length], closed);
    }
    var nonAscii = bytes(GOLDEN);
    nonAscii[100] = (byte) 0xff;
    assertThrows(
        IllegalArgumentException.class, () -> CleanupFailedBackupRequest.consume(nonAscii));
    assertArrayEquals(new byte[nonAscii.length], nonAscii);
  }

  @Test
  void cfreq004ActualReceiptMustMatchFixedTargetInvocationTimesAndNormalFailure() {
    var request = CleanupFailedBackupRequest.consume(bytes(GOLDEN));
    String literal =
        """
        Id=schubert-nk-backup.service
        LoadState=loaded
        ActiveState=failed
        SubState=failed
        Job=
        MainPID=0
        ControlPID=0
        InvocationID=51111111222243338444555555555555
        ExecMainCode=1
        ExecMainStatus=30
        ExecMainStartTimestampMonotonic=1000000000
        ExecMainExitTimestampMonotonic=2000000000
        Result=exit-code
        Type=oneshot
        Restart=no
        RemainAfterExit=yes
        KillMode=control-group
        SendSIGKILL=no
        """;
    assertTrue(
        request.receiptMatches(
            InspectorUnitSnapshot.parse(bytes(literal), InspectorUnitSnapshot.Target.BACKUP)));
    for (String changed :
        List.of(
            literal.replace("51111111222243338444555555555555", "61111111222243338444555555555555"),
            literal.replace("ExecMainStatus=30", "ExecMainStatus=1"),
            literal.replace("ExecMainCode=1", "ExecMainCode=2"),
            literal.replace("Result=exit-code", "Result=timeout"),
            literal.replace("1000000000", "1000000001"),
            literal.replace("2000000000", "2000000001"),
            literal.replace("MainPID=0", "MainPID=99")))
      assertFalse(
          request.receiptMatches(
              InspectorUnitSnapshot.parse(bytes(changed), InspectorUnitSnapshot.Target.BACKUP)));
    assertFalse(
        request.receiptMatches(
            InspectorUnitSnapshot.parse(
                bytes(literal.replace("schubert-nk-backup.service", "schubert-nk-cleanup.service")),
                InspectorUnitSnapshot.Target.CLEANUP)));
    assertThrows(NullPointerException.class, () -> request.receiptMatches(null));
  }

  @Test
  void cfreq003CanonicalBoundariesAndEachFixedTerminalFieldAreIndependent() {
    var changes = new ArrayList<String>();
    for (String id : List.of("boot", "epoch", "backup_invocation"))
      changes.add(
          GOLDEN.replace(
              id
                  + "="
                  + switch (id) {
                    case "boot" -> "31111111";
                    case "epoch" -> "41111111";
                    default -> "51111111";
                  }
                  + "-2222-4333-8444-555555555555",
              id + "=00000000-0000-0000-0000-000000000000"));
    for (String number : List.of("0", "-1", "+1", "01", "18446744073709551616", "not-number"))
      changes.add(
          GOLDEN.replace(
              "backup_started_monotonic=1000000000", "backup_started_monotonic=" + number));
    for (String number : List.of("0", "999999999", "18446744073709551616"))
      changes.add(
          GOLDEN.replace("backup_ended_monotonic=2000000000", "backup_ended_monotonic=" + number));
    for (String code : List.of("0", "-1", "256", "030", "not-number"))
      changes.add(GOLDEN.replace("backup_exit=30", "backup_exit=" + code));
    for (String row : List.of("0,4", "1000000000000,4", "7,0", "7,100", "07,4", "7,04"))
      changes.add(GOLDEN.replace("database=7,4", "database=" + row));
    changes.add(GOLDEN.replace("configuration=8,4", "configuration=7,4"));
    changes.add(GOLDEN.replace("2026-09-28,", "2026-09-27,"));
    changes.add(GOLDEN.replace("2026-09-30T01:02:03.123456Z", "2026-09-30T01:02:03.1234567Z"));
    changes.add(GOLDEN.replace("2026-09-30T01:02:05.654321Z", "2026-09-30T01:02:02Z"));
    changes.add(
        GOLDEN.replace(
            "configuration=8,4,2026-09-28,2026-09-30T01:02:03.123456Z",
            "configuration=8,4,2026-09-28,2026-09-30T01:02:04Z"));
    changes.add(
        GOLDEN.replace(
            "configuration=8,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:05.654321Z",
            "configuration=8,4,2026-09-28,2026-09-30T01:02:03.123456Z,2026-09-30T01:02:06Z"));
    for (String terminal :
        List.of(
            "SUCCESS,1,0,1,0,COMMAND_FAILURE,batch command failed",
            "FAILED,0,0,1,0,COMMAND_FAILURE,batch command failed",
            "FAILED,1,1,1,0,COMMAND_FAILURE,batch command failed",
            "FAILED,1,0,0,0,COMMAND_FAILURE,batch command failed",
            "FAILED,1,0,1,1,COMMAND_FAILURE,batch command failed",
            "FAILED,1,0,1,0,ABANDONED,batch command failed",
            "FAILED,1,0,1,0,COMMAND_FAILURE,unknown",
            "FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed,extra"))
      changes.add(GOLDEN.replace("FAILED,1,0,1,0,COMMAND_FAILURE,batch command failed", terminal));
    for (String bad : changes) {
      var owned = bytes(bad);
      assertThrows(IllegalArgumentException.class, () -> CleanupFailedBackupRequest.consume(owned));
      assertArrayEquals(new byte[owned.length], owned);
    }
    for (String code : List.of("1", "255")) {
      var valid =
          CleanupFailedBackupRequest.consume(
              bytes(GOLDEN.replace("backup_exit=30", "backup_exit=" + code)));
      assertEquals(Integer.parseInt(code), valid.backupExit());
    }
    var upper =
        CleanupFailedBackupRequest.consume(
            bytes(
                GOLDEN
                    .replace(
                        "backup_started_monotonic=1000000000",
                        "backup_started_monotonic=18446744073709551615")
                    .replace(
                        "backup_ended_monotonic=2000000000",
                        "backup_ended_monotonic=18446744073709551615")));
    assertEquals(new BigInteger("18446744073709551615"), upper.backupEnded());
  }
}
