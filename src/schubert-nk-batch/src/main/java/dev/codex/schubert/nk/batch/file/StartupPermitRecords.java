package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.Arrays;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * NK-OPS-001; OPS009/UI251/SS343 SSC089; PG302; PT-OPS-PERMITREC001..008. Canonical public values
 * only: no inode, current-boot authority, or completed-step assertion.
 */
@NullMarked
public final class StartupPermitRecords {
  private static final DateTimeFormatter TIME =
      new DateTimeFormatterBuilder().appendInstant(6).toFormatter(Locale.ROOT);

  private StartupPermitRecords() {}

  public enum State {
    INVALID,
    ISSUED
  }

  public record Epoch(
      State state,
      UUID boot,
      UUID epoch,
      MaintenanceActivation activation,
      Optional<String> permitDigest) {
    public Epoch {
      Objects.requireNonNull(state, "state");
      nonzero(boot);
      nonzero(epoch);
      Objects.requireNonNull(activation, "activation");
      Objects.requireNonNull(permitDigest, "digest");
      requireValue((state == State.ISSUED) == permitDigest.isPresent());
      permitDigest.ifPresent(StartupPermitRecords::hash);
    }

    /** One-way value transition; caller must independently publish and read back the originals. */
    public Epoch issued(String digest) {
      requireValue(state == State.INVALID);
      return new Epoch(State.ISSUED, boot, epoch, activation, Optional.of(digest));
    }

    @Override
    public String toString() {
      return "Epoch[public binding=<redacted>]";
    }
  }

  public record Permit(
      UUID boot,
      UUID epoch,
      MaintenanceActivation activation,
      String brokerInvocation,
      String releaseDigest,
      String apiConfigDigest,
      String webConfigDigest,
      String rootsDigest,
      String prestartStepsDigest) {
    public Permit {
      nonzero(boot);
      nonzero(epoch);
      Objects.requireNonNull(activation, "activation");
      requireValue(
          Objects.requireNonNull(brokerInvocation, "broker invocation").matches("[0-9a-f]{32}")
              && !brokerInvocation.equals("0".repeat(32)));
      hash(releaseDigest);
      hash(apiConfigDigest);
      hash(webConfigDigest);
      hash(rootsDigest);
      hash(prestartStepsDigest);
    }

    @Override
    public String toString() {
      return "Permit[public binding=<redacted>]";
    }
  }

  public static byte[] epoch(Epoch value) {
    Objects.requireNonNull(value, "epoch");
    return ascii(
        "NKEPOCH1\nstate="
            + value.state()
            + "\n"
            + binding(value.boot(), value.epoch(), value.activation())
            + "permit_sha256="
            + value.permitDigest().orElse("-")
            + "\n");
  }

  public static byte[] permit(Permit value) {
    Objects.requireNonNull(value, "permit");
    return ascii(
        "NKPERMIT1\n"
            + binding(value.boot(), value.epoch(), value.activation())
            + "broker_invocation_id="
            + value.brokerInvocation()
            + "\n"
            + "release_sha256="
            + value.releaseDigest()
            + "\n"
            + "api_config_sha256="
            + value.apiConfigDigest()
            + "\n"
            + "web_config_sha256="
            + value.webConfigDigest()
            + "\n"
            + "roots_sha256="
            + value.rootsDigest()
            + "\n"
            + "prestart_steps_sha256="
            + value.prestartStepsDigest()
            + "\n");
  }

  public static Epoch readEpoch(byte[] bytes) throws IOException {
    byte[] snapshot = Objects.requireNonNull(bytes, "epoch bytes").clone();
    try {
      String[] fields = lines(snapshot, "NKEPOCH1", 9);
      State state = State.valueOf(field(fields[1], "state"));
      String digest = field(fields[7], "permit_sha256");
      Epoch result =
          new Epoch(
              state,
              uuid(fields[2], "boot_id"),
              uuid(fields[3], "epoch_id"),
              activation(fields, 4),
              digest.equals("-") ? Optional.empty() : Optional.of(digest));
      require(Arrays.equals(snapshot, epoch(result)));
      return result;
    } catch (DateTimeException | IllegalArgumentException failure) {
      throw invalid();
    } finally {
      Arrays.fill(snapshot, (byte) 0);
    }
  }

  public static Permit readPermit(byte[] bytes) throws IOException {
    byte[] snapshot = Objects.requireNonNull(bytes, "permit bytes").clone();
    try {
      String[] fields = lines(snapshot, "NKPERMIT1", 13);
      Permit result =
          new Permit(
              uuid(fields[1], "boot_id"),
              uuid(fields[2], "epoch_id"),
              activation(fields, 3),
              field(fields[6], "broker_invocation_id"),
              field(fields[7], "release_sha256"),
              field(fields[8], "api_config_sha256"),
              field(fields[9], "web_config_sha256"),
              field(fields[10], "roots_sha256"),
              field(fields[11], "prestart_steps_sha256"));
      require(Arrays.equals(snapshot, permit(result)));
      return result;
    } catch (DateTimeException | IllegalArgumentException failure) {
      throw invalid();
    } finally {
      Arrays.fill(snapshot, (byte) 0);
    }
  }

  /** Verify the supplied original bytes, not a caller-provided digest or re-encoded equivalent. */
  public static Permit verifyIssued(Epoch current, byte[] original) throws IOException {
    return verifyIssued(current, original, () -> MessageDigest.getInstance("SHA-256"));
  }

  @FunctionalInterface
  interface DigestFactory {
    MessageDigest create() throws NoSuchAlgorithmException;
  }

  static Permit verifyIssued(Epoch current, byte[] original, DigestFactory factory)
      throws IOException {
    Objects.requireNonNull(current, "current");
    Objects.requireNonNull(factory, "digest factory");
    byte[] snapshot = Objects.requireNonNull(original, "permit bytes").clone();
    try {
      require(current.state() == State.ISSUED);
      Permit result = readPermit(snapshot);
      require(current.boot().equals(result.boot()));
      require(current.epoch().equals(result.epoch()));
      require(current.activation().equals(result.activation()));
      String digest;
      try {
        digest = java.util.HexFormat.of().formatHex(factory.create().digest(snapshot));
      } catch (NoSuchAlgorithmException failure) {
        throw invalid();
      }
      require(current.permitDigest().orElseThrow().equals(digest));
      return result;
    } finally {
      Arrays.fill(snapshot, (byte) 0);
    }
  }

  private static String binding(UUID boot, UUID epoch, MaintenanceActivation activation) {
    return "boot_id="
        + boot
        + "\nepoch_id="
        + epoch
        + "\nrun_id="
        + activation.run().id()
        + "\ncutoff_utc="
        + TIME.format(activation.run().cutoff())
        + "\nactivation_id="
        + activation.id()
        + "\n";
  }

  private static MaintenanceActivation activation(String[] fields, int start) throws IOException {
    return new MaintenanceActivation(
        new BatchRun(
            uuid(fields[start], "run_id"), Instant.parse(field(fields[start + 1], "cutoff_utc"))),
        uuid(fields[start + 2], "activation_id"));
  }

  private static UUID uuid(String field, String key) throws IOException {
    return UUID.fromString(field(field, key));
  }

  private static String[] lines(byte[] bytes, String magic, int count) throws IOException {
    require(bytes.length > 0 && bytes.length <= 8192);
    for (byte value : bytes) require(value >= 0);
    String[] fields = new String(bytes, StandardCharsets.US_ASCII).split("\n", -1);
    require(fields.length == count);
    require(fields[0].equals(magic));
    require(fields[count - 1].isEmpty());
    return fields;
  }

  private static String field(String line, String key) throws IOException {
    require(line.startsWith(key + "="));
    return line.substring(key.length() + 1);
  }

  private static byte[] ascii(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  private static void nonzero(UUID id) {
    requireValue(!Objects.requireNonNull(id, "UUID").equals(new UUID(0, 0)));
  }

  private static void hash(String value) {
    requireValue(Objects.requireNonNull(value, "hash").matches("[0-9a-f]{64}"));
  }

  private static void requireValue(boolean accepted) {
    if (!accepted) throw new IllegalArgumentException("startup record value is invalid");
  }

  private static void require(boolean accepted) throws IOException {
    if (!accepted) throw invalid();
  }

  private static IOException invalid() {
    return new IOException("startup record is invalid");
  }
}
