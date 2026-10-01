package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** Public correlation only, not startup authority. NK-OPS-001/OPS009/UI251/SS343/SSC137/PT297. */
@NullMarked
record StartupLaunchRecord(
    ServiceConfigFiles.Service service,
    UUID boot,
    UUID epoch,
    String permitSha256,
    String ownerSha256,
    MaintenanceOwnerFrame.Parent child) {
  static final int MAXIMUM_BYTES = 1024;
  private static final String[] KEYS = {
    "service", "boot", "epoch", "permit_sha256", "owner_sha256", "invocation", "pid", "start_ticks"
  };

  StartupLaunchRecord {
    Objects.requireNonNull(service, "fixed service");
    Objects.requireNonNull(boot, "actual boot");
    Objects.requireNonNull(epoch, "actual epoch");
    Objects.requireNonNull(permitSha256, "actual permit raw hash");
    Objects.requireNonNull(ownerSha256, "actual owner raw hash");
    Objects.requireNonNull(child, "actual Root generation");
    if (boot.equals(new UUID(0, 0))
        || epoch.equals(new UUID(0, 0))
        || !permitSha256.matches("[0-9a-f]{64}")
        || !ownerSha256.matches("[0-9a-f]{64}"))
      throw new IllegalArgumentException("startup launch invalid");
  }

  byte[] encode() {
    String[] values = {
      service.name(),
      boot.toString(),
      epoch.toString(),
      permitSha256,
      ownerSha256,
      child.invocation(),
      Long.toString(child.pid()),
      Long.toString(child.startTicks())
    };
    var text = new StringBuilder("NKLAUNCH1\n");
    for (int i = 0; i < KEYS.length; i++)
      text.append(KEYS[i]).append('=').append(values[i]).append('\n');
    return text.toString().getBytes(StandardCharsets.US_ASCII);
  }

  static StartupLaunchRecord consume(byte[] bytes) throws IOException {
    Objects.requireNonNull(bytes, "whole launch bytes");
    if (bytes.length == 0 || bytes.length > MAXIMUM_BYTES) throw unavailable();
    for (byte value : bytes) if (value != 10 && (value < 32 || value > 126)) throw unavailable();
    String[] lines = new String(bytes, StandardCharsets.US_ASCII).split("\n", -1);
    if (lines.length != 10 || !lines[0].equals("NKLAUNCH1") || !lines[9].isEmpty())
      throw unavailable();
    String[] values = new String[KEYS.length];
    for (int i = 0; i < KEYS.length; i++) {
      String prefix = KEYS[i] + "=";
      if (!lines[i + 1].startsWith(prefix)) throw unavailable();
      values[i] = lines[i + 1].substring(prefix.length());
    }
    try {
      var record =
          new StartupLaunchRecord(
              ServiceConfigFiles.Service.valueOf(values[0]),
              UUID.fromString(values[1]),
              UUID.fromString(values[2]),
              values[3],
              values[4],
              new MaintenanceOwnerFrame.Parent(
                  values[5], Long.parseLong(values[6]), Long.parseLong(values[7])));
      if (!Arrays.equals(bytes, record.encode())) throw unavailable();
      return record;
    } catch (IllegalArgumentException invalid) {
      throw unavailable();
    }
  }

  @Override
  public String toString() {
    return "StartupLaunchRecord[identity=<redacted>]";
  }

  @FunctionalInterface
  interface DigestFactory {
    MessageDigest create() throws NoSuchAlgorithmException;
  }

  static String sha256(byte[] actualBytes) throws IOException {
    return sha256(actualBytes, () -> MessageDigest.getInstance("SHA-256"));
  }

  static String sha256(byte[] actualBytes, DigestFactory factory) throws IOException {
    Objects.requireNonNull(actualBytes);
    Objects.requireNonNull(factory);
    try {
      return java.util.HexFormat.of().formatHex(factory.create().digest(actualBytes));
    } catch (NoSuchAlgorithmException invalid) {
      throw unavailable();
    }
  }

  private static IOException unavailable() {
    return new IOException("startup launch unavailable");
  }
}
