package dev.codex.schubert.nk.protocol.file;

import java.time.DateTimeException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.util.Objects;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Validated SCNRSP01 file-mode descriptor. Trace: NK-PRO-003, UI 237 §5, SS 333 §6. */
public final class LargeResultDescriptor {
  public static final int RECORD_LENGTH = 4_800;
  public static final int MAXIMUM_RECORD_COUNT = 10_000;
  public static final long MAXIMUM_BYTE_LENGTH = 48_000_000L;

  private static final Pattern HASH = Pattern.compile("[0-9a-f]{64}");
  private static final Pattern PATH =
      Pattern.compile("([0-9]{8})/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\\.ready");
  private static final DateTimeFormatter DATE =
      DateTimeFormatter.ofPattern("uuuuMMdd").withResolverStyle(ResolverStyle.STRICT);

  private final UUID fileId;
  private final String relativePath;
  private final long byteLength;
  private final String sha256;
  private final int recordCount;

  public LargeResultDescriptor(
      UUID fileId, String relativePath, long byteLength, String sha256, int recordCount) {
    this.fileId = Objects.requireNonNull(fileId, "fileId");
    this.relativePath = Objects.requireNonNull(relativePath, "relativePath");
    this.sha256 = Objects.requireNonNull(sha256, "sha256");
    if (recordCount < 1 || recordCount > MAXIMUM_RECORD_COUNT) {
      throw new IllegalArgumentException("large-result record count is outside 1..10000");
    }
    long expectedByteLength = Math.multiplyExact(RECORD_LENGTH, (long) recordCount);
    if (byteLength != expectedByteLength) {
      throw new IllegalArgumentException("large-result byte length differs from record length times count");
    }
    if (!HASH.matcher(sha256).matches()) {
      throw new IllegalArgumentException("large-result SHA-256 must be lowercase hexadecimal");
    }
    validatePath(fileId, relativePath);
    this.byteLength = byteLength;
    this.recordCount = recordCount;
  }

  public UUID fileId() {
    return fileId;
  }

  /** Validated wire value; do not log it. */
  public String relativePath() {
    return relativePath;
  }

  public long byteLength() {
    return byteLength;
  }

  public String sha256() {
    return sha256;
  }

  public int recordLength() {
    return RECORD_LENGTH;
  }

  public int recordCount() {
    return recordCount;
  }

  @Override
  public String toString() {
    return "LargeResultDescriptor[fileId="
        + fileId
        + ", relativePath=REDACTED, byteLength="
        + byteLength
        + ", sha256=REDACTED, recordLength="
        + RECORD_LENGTH
        + ", recordCount="
        + recordCount
        + ']';
  }

  private static void validatePath(UUID fileId, String relativePath) {
    if (!relativePath.isEmpty()
        && relativePath.length() <= 256
        && relativePath.chars().allMatch(character -> character >= 0x20 && character <= 0x7e)) {
      Matcher matcher = PATH.matcher(relativePath);
      if (matcher.matches()) {
        try {
          // The matched canonical pattern has a mandatory date capture (BUG-016/YKT-013).
          LocalDate.parse(Objects.requireNonNull(matcher.group(1), "canonical date"), DATE);
        } catch (DateTimeException exception) {
          throw new IllegalArgumentException("large-result path contains an invalid JST date", exception);
        }
        if (fileId.toString().equals(matcher.group(2))) {
          return;
        }
      }
    }
    throw new IllegalArgumentException("large-result relative path is not canonical");
  }
}
