package dev.codex.schubert.nk.protocol.layout.semantic;

import java.util.regex.Pattern;

/**
 * Shared lexical checks for path value objects; this class never resolves a file-system path.
 * Trace: NK-PRO-001, UI 243, SS 323/333, PT-PRO-001-T03, BUG-004/YKT-004.
 */
final class PathSyntax {
  private static final Pattern WINDOWS_DRIVE_PREFIX = Pattern.compile("^[A-Za-z]:");
  private static final Pattern PARENT_SEGMENT = Pattern.compile("(?:^|[/\\\\])\\.\\.(?:$|[/\\\\])");

  private PathSyntax() {}

  static boolean isAbsoluteOrDriveQualified(String value) {
    return value.startsWith("/")
        || value.startsWith("\\")
        || WINDOWS_DRIVE_PREFIX.matcher(value).find();
  }

  static boolean containsParentSegment(String value) {
    return PARENT_SEGMENT.matcher(value).find();
  }

  static boolean containsControl(String value) {
    return value.codePoints().anyMatch(Character::isISOControl);
  }
}
