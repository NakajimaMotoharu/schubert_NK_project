package dev.codex.schubert.nk.protocol.file;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;

/** MEDIA1024 structure and SSC-004 MIME allowlist. Trace: NK-PRO-003, SS 323/333. */
public final class MediaDescriptorValidator {
  private static final Pattern HASH = Pattern.compile("[0-9a-f]{64}");
  private static final Map<String, String> MUSIC_MIME =
      Map.of(
          ".m4a", "audio/mp4",
          ".mp3", "audio/mpeg",
          ".ogg", "audio/ogg",
          ".wav", "audio/wav",
          ".flac", "audio/flac");

  private MediaDescriptorValidator() {}

  public static void validate(MediaDescriptor descriptor) {
    Objects.requireNonNull(descriptor, "descriptor");
    validateCanonicalText("logical ID", descriptor.logicalId(), 64, false);
    validateStoragePath(descriptor.mediaType(), descriptor.storageRelativePath());
    validateFileName(descriptor.fileName());
    if (descriptor.byteLength() < 1 || descriptor.byteLength() > 999_999_999_999L) {
      throw new IllegalArgumentException("media byte length is outside its N12 range");
    }
    if (!HASH.matcher(descriptor.sha256()).matches()) {
      throw new IllegalArgumentException("media SHA-256 must be lowercase hexadecimal");
    }
    validateMime(descriptor);
  }

  private static void validateStoragePath(MediaType mediaType, String path) {
    validateCanonicalText("storage relative path", path, 512, true);
    if (path.startsWith("/")
        || path.endsWith("/")
        || path.contains("\\")
        || path.contains("//")
        || hasDotSegment(path)) {
      throw new IllegalArgumentException("storage path is not a canonical relative path");
    }
    String requiredPrefix =
        switch (mediaType) {
          case AUDIO -> "scenario/";
          case VIDEO -> "video/";
          case MUSIC -> "music/";
        };
    if (!path.startsWith(requiredPrefix)) {
      throw new IllegalArgumentException("storage path does not match its media type");
    }
  }

  private static void validateFileName(String fileName) {
    validateCanonicalText("media file name", fileName, 256, true);
    if (fileName.indexOf('/') >= 0
        || fileName.indexOf('\\') >= 0
        || fileName.indexOf('"') >= 0
        || fileName.indexOf('\'') >= 0) {
      throw new IllegalArgumentException(
          "media file name contains a forbidden header/path character");
    }
  }

  private static void validateMime(MediaDescriptor descriptor) {
    String extension = extension(descriptor.fileName());
    // BUG-040/YKT-036: display metadata must not hide a different storage format.
    if (!extension.equals(extension(descriptor.storageRelativePath()))) {
      throw new IllegalArgumentException("media storage and display extensions differ");
    }
    String expectedMime =
        switch (descriptor.mediaType()) {
          case AUDIO -> extension.equals(".ogg") ? "audio/ogg" : null;
          case VIDEO -> extension.equals(".mp4") ? "video/mp4" : null;
          case MUSIC -> MUSIC_MIME.get(extension);
        };
    if (expectedMime == null || !expectedMime.equals(descriptor.mimeType())) {
      throw new IllegalArgumentException("media extension and MIME type are not allowlisted");
    }
    if (descriptor.mediaType() == MediaType.VIDEO
        && descriptor.disposition() != ContentDisposition.INLINE) {
      throw new IllegalArgumentException("video descriptor must use inline disposition");
    }
  }

  private static String extension(String fileName) {
    int lastDot = fileName.lastIndexOf('.');
    return lastDot < 0 ? "" : fileName.substring(lastDot);
  }

  private static boolean hasDotSegment(String path) {
    for (String segment : path.split("/", -1)) {
      if (segment.equals(".") || segment.equals("..")) {
        return true;
      }
    }
    return false;
  }

  private static void validateCanonicalText(
      String fieldName, String value, int maximumBytes, boolean forbidAllControls) {
    if (value.isEmpty()
        || !StandardCharsets.UTF_8.newEncoder().canEncode(value)
        || !Normalizer.isNormalized(value, Normalizer.Form.NFC)
        || value.getBytes(StandardCharsets.UTF_8).length > maximumBytes
        || value.endsWith(" ")) {
      throw new IllegalArgumentException(
          fieldName + " is empty, non-canonical, or over its byte limit");
    }
    for (int index = 0; index < value.length(); index++) {
      char character = value.charAt(index);
      if (character == '\0'
          || character == '\r'
          || character == '\n'
          || character == '\t'
          || (forbidAllControls && Character.isISOControl(character))) {
        throw new IllegalArgumentException(fieldName + " contains a forbidden control character");
      }
    }
  }
}
