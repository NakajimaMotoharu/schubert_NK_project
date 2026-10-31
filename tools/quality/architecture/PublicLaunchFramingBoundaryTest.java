package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;

/** PT-LAUNCH-FRAMING-001: SS343 public ASCII/strict-EOF, independent of Production encoding. */
final class PublicLaunchFramingBoundaryTest {
  private static final String FRAME =
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

  @Test
  void rejectsDelAndNonemptyTenthLine() {
    byte[] del = FRAME.getBytes(StandardCharsets.US_ASCII);
    del[0] = 0x7f;
    assertThrows(IOException.class, () -> StartupLaunchRecord.consume(del));
    byte[] trailing = (FRAME + "x").getBytes(StandardCharsets.US_ASCII);
    assertThrows(IOException.class, () -> StartupLaunchRecord.consume(trailing));
  }
}
