package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** LAUNCH001..006: literal independent canonical frame, never Production-derived expected. */
final class StartupLaunchRecordTest {
  private static final String PARENT_PID_ASSIGNMENT = "pid=300";

  static final String GOLD =
      """
      NKLAUNCH1
      service=API
      boot=31100027-3333-4333-8444-555555555555
      epoch=31100027-4444-4333-8444-555555555555
      permit_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      owner_sha256=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
      invocation=22222222222222222222222222222222
      pid=300
      start_ticks=200
      """;

  static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  @Test
  void wholeIndependentFrameBothServicesAndFields() throws Exception {
    for (var service : ServiceConfigFiles.Service.values()) {
      String literal = GOLD.replace("service=API", "service=" + service.name());
      var record = StartupLaunchRecord.consume(bytes(literal));
      assertEquals(service, record.service());
      assertEquals(UUID.fromString("31100027-3333-4333-8444-555555555555"), record.boot());
      assertEquals(UUID.fromString("31100027-4444-4333-8444-555555555555"), record.epoch());
      assertEquals("a".repeat(64), record.permitSha256());
      assertEquals("b".repeat(64), record.ownerSha256());
      assertEquals(new MaintenanceOwnerFrame.Parent("2".repeat(32), 300, 200), record.child());
      assertArrayEquals(bytes(literal), record.encode());
      assertEquals("StartupLaunchRecord[identity=<redacted>]", record.toString());
    }
  }

  @Test
  void malformedAndNonCanonicalAllFields() {
    String[] invalid = {
      "",
      GOLD + "\n",
      GOLD.substring(0, GOLD.length() - 1),
      GOLD.replace("NKLAUNCH1", "NKLAUNCH2"),
      GOLD.replace("service=API", "service=OTHER"),
      GOLD.replace("service=API", "service=api"),
      GOLD.replace("boot=", "epoch="),
      GOLD.replace("start_ticks=", "unknown="),
      GOLD.replace("31100027-3333-4333-8444-555555555555", "00000000-0000-0000-0000-000000000000"),
      GOLD.replace("31100027-4444-4333-8444-555555555555", "00000000-0000-0000-0000-000000000000"),
      GOLD.replace("31100027-3333-4333-8444-555555555555", "1-1-1-1-1"),
      GOLD.replace("a".repeat(64), "a".repeat(63)),
      GOLD.replace("b".repeat(64), "B".repeat(64)),
      GOLD.replace("2".repeat(32), "0".repeat(32)),
      GOLD.replace(PARENT_PID_ASSIGNMENT, "pid=1"),
      GOLD.replace(PARENT_PID_ASSIGNMENT, "pid=2147483648"),
      GOLD.replace(PARENT_PID_ASSIGNMENT, "pid=0300"),
      GOLD.replace(PARENT_PID_ASSIGNMENT, "pid=+300"),
      GOLD.replace("start_ticks=200", "start_ticks=0"),
      GOLD.replace("start_ticks=200", "start_ticks=9223372036854775808"),
      GOLD.replace("start_ticks=200", "start_ticks=x"),
      GOLD.replace("\n", "\r\n")
    };
    for (String text : invalid)
      assertThrows(IOException.class, () -> StartupLaunchRecord.consume(bytes(text)));
    assertThrows(IOException.class, () -> StartupLaunchRecord.consume(new byte[1025]));
    assertThrows(IOException.class, () -> StartupLaunchRecord.consume(new byte[] {(byte) 255}));
  }

  @Test
  void nullAndConstructorInvariants() throws Exception {
    var value = StartupLaunchRecord.consume(bytes(GOLD));
    assertThrows(NullPointerException.class, () -> StartupLaunchRecord.consume(null));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupLaunchRecord(
                null,
                value.boot(),
                value.epoch(),
                value.permitSha256(),
                value.ownerSha256(),
                value.child()));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupLaunchRecord(
                value.service(),
                null,
                value.epoch(),
                value.permitSha256(),
                value.ownerSha256(),
                value.child()));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupLaunchRecord(
                value.service(),
                value.boot(),
                null,
                value.permitSha256(),
                value.ownerSha256(),
                value.child()));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupLaunchRecord(
                value.service(),
                value.boot(),
                value.epoch(),
                null,
                value.ownerSha256(),
                value.child()));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupLaunchRecord(
                value.service(),
                value.boot(),
                value.epoch(),
                value.permitSha256(),
                null,
                value.child()));
    assertThrows(
        NullPointerException.class,
        () ->
            new StartupLaunchRecord(
                value.service(),
                value.boot(),
                value.epoch(),
                value.permitSha256(),
                value.ownerSha256(),
                null));
  }

  @Test
  void independentShaVectorAlgorithmFailureAndUnknownIdentity() throws Exception {
    assertEquals(
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        StartupLaunchRecord.sha256(bytes("abc")));
    assertThrows(
        IOException.class,
        () ->
            StartupLaunchRecord.sha256(
                bytes(GOLD),
                () -> {
                  throw new NoSuchAlgorithmException("private");
                }));
    var unknown = new IllegalStateException("unknown");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                StartupLaunchRecord.sha256(
                    bytes(GOLD),
                    () -> {
                      throw unknown;
                    })));
    assertThrows(NullPointerException.class, () -> StartupLaunchRecord.sha256(null));
    assertThrows(NullPointerException.class, () -> StartupLaunchRecord.sha256(bytes(GOLD), null));
  }
}
