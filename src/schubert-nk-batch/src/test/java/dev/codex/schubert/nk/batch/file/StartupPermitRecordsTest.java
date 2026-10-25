package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Permit;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.State;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;

/**
 * SS343 SSC089; PT-OPS-PERMITREC001..008; literal order/bytes independent of production encoder.
 */
final class StartupPermitRecordsTest {
  private static final UUID BOOT = UUID.fromString("11111111-1111-1111-1111-111111111111");
  private static final UUID EPOCH = UUID.fromString("33333333-3333-3333-3333-333333333333");
  private static final UUID RUN = UUID.fromString("44444444-4444-4444-4444-444444444444");
  private static final UUID ACT = UUID.fromString("55555555-5555-5555-5555-555555555555");
  private static final UUID ZERO = new UUID(0, 0);
  private static final MaintenanceActivation ACTIVE =
      new MaintenanceActivation(
          new BatchRun(RUN, Instant.parse("2026-09-27T00:00:00.000000Z")), ACT);
  private static final String BIND =
      "boot_id=11111111-1111-1111-1111-111111111111\n"
          + "epoch_id=33333333-3333-3333-3333-333333333333\n"
          + "run_id=44444444-4444-4444-4444-444444444444\n"
          + "cutoff_utc=2026-09-27T00:00:00.000000Z\n"
          + "activation_id=55555555-5555-5555-5555-555555555555\n";
  private static final String GOLD =
      "NKPERMIT1\n"
          + BIND
          + "broker_invocation_id="
          + "2".repeat(32)
          + "\nrelease_sha256="
          + "b".repeat(64)
          + "\napi_config_sha256="
          + "c".repeat(64)
          + "\nweb_config_sha256="
          + "d".repeat(64)
          + "\nroots_sha256="
          + "e".repeat(64)
          + "\nprestart_steps_sha256="
          + "f".repeat(64)
          + "\n";
  private static final String INVALID = "NKEPOCH1\nstate=INVALID\n" + BIND + "permit_sha256=-\n";
  private static final String ISSUED =
      "NKEPOCH1\nstate=ISSUED\n" + BIND + "permit_sha256=" + "a".repeat(64) + "\n";

  private static Permit value() {
    return new Permit(
        BOOT,
        EPOCH,
        ACTIVE,
        "2".repeat(32),
        "b".repeat(64),
        "c".repeat(64),
        "d".repeat(64),
        "e".repeat(64),
        "f".repeat(64));
  }

  private static Epoch invalid() {
    return new Epoch(State.INVALID, BOOT, EPOCH, ACTIVE, Optional.empty());
  }

  private static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void rejected(String text, boolean epoch) {
    IOException e =
        assertThrows(
            IOException.class,
            () -> {
              if (epoch) StartupPermitRecords.readEpoch(bytes(text));
              else StartupPermitRecords.readPermit(bytes(text));
            });
    assertEquals("startup record is invalid", e.getMessage());
    assertNull(e.getCause());
  }

  @Test
  void literalRecords() throws Exception {
    assertArrayEquals(bytes(INVALID), StartupPermitRecords.epoch(invalid()));
    Epoch issued = invalid().issued("a".repeat(64));
    assertArrayEquals(bytes(ISSUED), StartupPermitRecords.epoch(issued));
    assertArrayEquals(bytes(GOLD), StartupPermitRecords.permit(value()));
    assertEquals(invalid(), StartupPermitRecords.readEpoch(bytes(INVALID)));
    assertEquals(issued, StartupPermitRecords.readEpoch(bytes(ISSUED)));
    assertEquals(value(), StartupPermitRecords.readPermit(bytes(GOLD)));
    assertEquals(State.INVALID, State.valueOf("INVALID"));
    assertEquals(2, State.values().length);
  }

  @Test
  void syntaxFailures() throws Exception {
    for (boolean epoch : List.of(false, true)) {
      String text = epoch ? INVALID : GOLD;
      for (String malformed :
          List.of(
              "",
              "x".repeat(8193),
              text.replace("\n", "\r\n"),
              text.substring(0, text.length() - 1),
              "UNKNOWN" + text,
              text + "\n",
              text + "unknown=x\n")) rejected(malformed, epoch);
      String[] lines = text.split("\n");
      for (int i = 1; i < lines.length; i++) {
        rejected(text.replace(lines[i] + "\n", ""), epoch);
        rejected(text.replace(lines[i], "unknown=x"), epoch);
        rejected(text.replace(lines[i] + "\n", lines[i] + "\n" + lines[i] + "\n"), epoch);
        if (i > 1)
          rejected(
              text.replace(lines[i - 1] + "\n" + lines[i], lines[i] + "\n" + lines[i - 1]), epoch);
      }
      byte[] nonascii = bytes(text);
      nonascii[3] = (byte) 128;
      assertThrows(
          IOException.class,
          () -> {
            if (epoch) StartupPermitRecords.readEpoch(nonascii);
            else StartupPermitRecords.readPermit(nonascii);
          });
    }
    rejected(INVALID.replace("INVALID", "unknown"), true);
  }

  @Test
  void identityAndHashFailures() {
    for (String uuid :
        List.of(ZERO.toString(), "bad", "1-1-1-1-1", "ABCDEFAB-1111-1111-1111-111111111111")) {
      rejected(GOLD.replace(BOOT.toString(), uuid), false);
      rejected(INVALID.replace(EPOCH.toString(), uuid), true);
    }
    for (String bad :
        List.of("0".repeat(32), "2".repeat(31), "2".repeat(33), "A".repeat(32), "z".repeat(32)))
      rejected(GOLD.replace("2".repeat(32), bad), false);
    for (char member : List.of('b', 'c', 'd', 'e', 'f'))
      for (String bad : List.of("a".repeat(63), "a".repeat(65), "A".repeat(64), "g".repeat(64), ""))
        rejected(GOLD.replace(String.valueOf(member).repeat(64), bad), false);
    for (String bad : List.of("a".repeat(63), "A".repeat(64), "g".repeat(64)))
      rejected(ISSUED.replace("a".repeat(64), bad), true);
  }

  @Test
  void stateTransitions() {
    assertThrows(
        IllegalArgumentException.class,
        () -> new Epoch(State.INVALID, BOOT, EPOCH, ACTIVE, Optional.of("a".repeat(64))));
    assertThrows(
        IllegalArgumentException.class,
        () -> new Epoch(State.ISSUED, BOOT, EPOCH, ACTIVE, Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () -> invalid().issued("a".repeat(64)).issued("b".repeat(64)));
    rejected(ISSUED.replace("a".repeat(64), "-"), true);
    rejected(INVALID.replace("permit_sha256=-", "permit_sha256=" + "a".repeat(64)), true);
  }

  @Test
  void issuedBinding() throws Exception {
    // Independent JCA calculation over the hand-written golden, never the production encoder.
    String expected =
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes(GOLD)));
    Epoch current = invalid().issued(expected);
    assertEquals(value(), StartupPermitRecords.verifyIssued(current, bytes(GOLD)));
    for (Epoch wrong :
        List.of(
            invalid(),
            invalid().issued("a".repeat(64)),
            new Epoch(State.ISSUED, ACT, EPOCH, ACTIVE, Optional.of(expected)),
            new Epoch(State.ISSUED, BOOT, ACT, ACTIVE, Optional.of(expected)),
            new Epoch(
                State.ISSUED,
                BOOT,
                EPOCH,
                new MaintenanceActivation(new BatchRun(ACT, ACTIVE.run().cutoff()), ACT),
                Optional.of(expected)),
            new Epoch(
                State.ISSUED,
                BOOT,
                EPOCH,
                new MaintenanceActivation(
                    new BatchRun(RUN, Instant.parse("2026-09-28T00:00:00Z")), ACT),
                Optional.of(expected)),
            new Epoch(
                State.ISSUED,
                BOOT,
                EPOCH,
                new MaintenanceActivation(ACTIVE.run(), EPOCH),
                Optional.of(expected))))
      assertThrows(IOException.class, () -> StartupPermitRecords.verifyIssued(wrong, bytes(GOLD)));
    IOException failure =
        assertThrows(
            IOException.class,
            () ->
                StartupPermitRecords.verifyIssued(
                    current,
                    bytes(GOLD),
                    () -> {
                      throw new NoSuchAlgorithmException("secret sentinel");
                    }));
    assertNull(failure.getCause());
    assertEquals("startup record is invalid", failure.getMessage());
  }

  @Test
  void cutoffContract() throws Exception {
    for (String cutoff : List.of("0001-01-01T00:00:00.000000Z", "9999-12-31T23:59:59.999999Z")) {
      String text = GOLD.replace("2026-09-27T00:00:00.000000Z", cutoff);
      assertEquals(
          Instant.parse(cutoff),
          StartupPermitRecords.readPermit(bytes(text)).activation().run().cutoff());
    }
    for (String bad :
        List.of(
            "0000-12-31T23:59:59.999999Z",
            "+10000-01-01T00:00:00.000000Z",
            "2026-09-27T00:00:00Z",
            "2026-09-27T00:00:00.000000001Z",
            "bad")) rejected(GOLD.replace("2026-09-27T00:00:00.000000Z", bad), false);
    assertEquals(
        ZERO,
        StartupPermitRecords.readPermit(bytes(GOLD.replace(RUN.toString(), ZERO.toString())))
            .activation()
            .run()
            .id());
  }

  @Test
  void nullAndOwnership() throws Exception {
    assertThrows(NullPointerException.class, () -> StartupPermitRecords.epoch(null));
    assertThrows(NullPointerException.class, () -> StartupPermitRecords.permit(null));
    assertThrows(NullPointerException.class, () -> StartupPermitRecords.readEpoch(null));
    assertThrows(NullPointerException.class, () -> StartupPermitRecords.readPermit(null));
    assertThrows(
        NullPointerException.class, () -> StartupPermitRecords.verifyIssued(null, bytes(GOLD)));
    assertThrows(
        NullPointerException.class, () -> StartupPermitRecords.verifyIssued(invalid(), null));
    assertThrows(
        NullPointerException.class,
        () -> StartupPermitRecords.verifyIssued(invalid(), bytes(GOLD), null));
    for (int i = 0; i < 5; i++) {
      int n = i;
      assertThrows(
          NullPointerException.class,
          () ->
              new Epoch(
                  n == 0 ? null : State.INVALID,
                  n == 1 ? null : BOOT,
                  n == 2 ? null : EPOCH,
                  n == 3 ? null : ACTIVE,
                  n == 4 ? null : Optional.empty()));
    }
    for (int i = 0; i < 9; i++) {
      int n = i;
      assertThrows(
          NullPointerException.class,
          () ->
              new Permit(
                  n == 0 ? null : BOOT,
                  n == 1 ? null : EPOCH,
                  n == 2 ? null : ACTIVE,
                  n == 3 ? null : "2".repeat(32),
                  n == 4 ? null : "b".repeat(64),
                  n == 5 ? null : "c".repeat(64),
                  n == 6 ? null : "d".repeat(64),
                  n == 7 ? null : "e".repeat(64),
                  n == 8 ? null : "f".repeat(64)));
    }
    assertThrows(NullPointerException.class, () -> invalid().issued(null));
    byte[] input = bytes(GOLD);
    StartupPermitRecords.readPermit(input);
    assertArrayEquals(bytes(GOLD), input);
    byte[] encoded = StartupPermitRecords.permit(value());
    Arrays.fill(encoded, (byte) 0);
    assertEquals(value(), StartupPermitRecords.readPermit(bytes(GOLD)));
    assertEquals("Epoch[public binding=<redacted>]", invalid().toString());
    assertEquals("Permit[public binding=<redacted>]", value().toString());
  }

  @Test
  void concurrentSnapshots() throws Exception {
    String digest =
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes(GOLD)));
    try (var workers = Executors.newFixedThreadPool(4)) {
      var calls = new ArrayList<Callable<Permit>>();
      for (int i = 0; i < 32; i++)
        calls.add(() -> StartupPermitRecords.verifyIssued(invalid().issued(digest), bytes(GOLD)));
      for (Future<Permit> f : workers.invokeAll(calls)) assertEquals(value(), f.get());
    }
  }
}
