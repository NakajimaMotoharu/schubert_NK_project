package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion.Outcome;
import dev.codex.schubert.nk.batch.repository.MaintenanceRetirement;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.Arrays;
import java.util.Locale;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Canonical nonsecret persisted values, not inode/expected-run admission or parent success.
 * NK-BAT-001; OPS-009/UI251/SS331/341/343 6.13; SSC-055/PG-D-156; PT-BAT-038..045.
 */
@NullMarked
public final class MaintenanceRecords {
  private static final DateTimeFormatter TIME =
      new DateTimeFormatterBuilder().appendInstant(6).toFormatter(Locale.ROOT);

  private MaintenanceRecords() {}

  public static byte[] anchor(BatchRun run) {
    return ascii("NKRUN1\n" + identity(Objects.requireNonNull(run, "run")));
  }

  public static byte[] activation(MaintenanceActivation value) {
    Objects.requireNonNull(value, "activation");
    return ascii("NKACT1\n" + identity(value.run()) + value.id() + "\n");
  }

  public static byte[] completion(MaintenanceCompletion value) {
    Objects.requireNonNull(value, "completion");
    return ascii(
        "NKDONE1\n"
            + identity(value.activation().run())
            + value.activation().id()
            + "\n"
            + TIME.format(value.endedAt())
            + "\n"
            + value.outcome().exitCode()
            + "\n");
  }

  /** SS343 6.16; PG161; PT-BAT-090..097. */
  public static byte[] retirement(MaintenanceRetirement value) {
    Objects.requireNonNull(value, "retirement");
    return ascii(
        "NKRET1\n"
            + identity(value.run())
            + TIME.format(value.latestEnded())
            + "\n"
            + TIME.format(value.preparedAt())
            + "\n"
            + value.count()
            + "\n"
            + value.digest()
            + "\n");
  }

  public static MaintenanceRetirement readRetirement(byte[] bytes) throws IOException {
    try {
      String[] fields = lines(bytes, "NKRET1", 195, 204, 8);
      var result =
          new MaintenanceRetirement(
              run(fields),
              Instant.parse(fields[3]),
              Instant.parse(fields[4]),
              Integer.parseInt(fields[5]),
              fields[6]);
      require(Arrays.equals(bytes, retirement(result)));
      return result;
    } catch (DateTimeException | IllegalArgumentException failure) {
      throw invalid();
    }
  }

  public static BatchRun readAnchor(byte[] bytes) throws IOException {
    try {
      String[] fields = lines(bytes, "NKRUN1", 72, 72, 4);
      var result = run(fields);
      require(Arrays.equals(bytes, anchor(result)));
      return result;
    } catch (DateTimeException | IllegalArgumentException failure) {
      throw invalid();
    }
  }

  public static MaintenanceActivation readActivation(byte[] bytes) throws IOException {
    try {
      String[] fields = lines(bytes, "NKACT1", 109, 109, 5);
      var result = new MaintenanceActivation(run(fields), UUID.fromString(fields[3]));
      require(Arrays.equals(bytes, activation(result)));
      return result;
    } catch (DateTimeException | IllegalArgumentException failure) {
      throw invalid();
    }
  }

  public static MaintenanceCompletion readCompletion(byte[] bytes) throws IOException {
    try {
      String[] fields = lines(bytes, "NKDONE1", 140, 141, 7);
      Outcome outcome =
          switch (fields[5]) {
            case "0" -> Outcome.SUCCESS;
            case "10" -> Outcome.WARNING;
            default -> throw invalid();
          };
      var result =
          new MaintenanceCompletion(
              new MaintenanceActivation(run(fields), UUID.fromString(fields[3])),
              Instant.parse(fields[4]),
              outcome);
      require(Arrays.equals(bytes, completion(result)));
      return result;
    } catch (DateTimeException | IllegalArgumentException failure) {
      throw invalid();
    }
  }

  private static String[] lines(byte[] bytes, String magic, int minimum, int maximum, int count)
      throws IOException {
    Objects.requireNonNull(bytes, "record bytes");
    require(bytes.length >= minimum && bytes.length <= maximum);
    for (byte value : bytes) require(value >= 0);
    String[] fields = new String(bytes, StandardCharsets.US_ASCII).split("\n", -1);
    require(fields.length == count);
    require(fields[0].equals(magic));
    require(fields[count - 1].isEmpty());
    return fields;
  }

  private static BatchRun run(String[] fields) {
    return new BatchRun(UUID.fromString(fields[1]), Instant.parse(fields[2]));
  }

  private static String identity(BatchRun run) {
    return run.id() + "\n" + TIME.format(run.cutoff()) + "\n";
  }

  private static byte[] ascii(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void require(boolean accepted) throws IOException {
    if (!accepted) throw invalid();
  }

  private static IOException invalid() {
    return new IOException("maintenance record is invalid");
  }
}
