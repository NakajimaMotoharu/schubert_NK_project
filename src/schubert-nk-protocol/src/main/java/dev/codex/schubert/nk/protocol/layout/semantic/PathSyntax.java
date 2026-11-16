package dev.codex.schubert.nk.protocol.layout.semantic;

import java.util.regex.Pattern;

/**
 * Shared lexical checks for path value objects; this class never resolves a file-system path.
 * Trace: NK-PRO-001, UI 243, SS 323/333, PT-PRO-001-T03, BUG-004/YKT-004.
 */
interface PathSyntax {

  static boolean isAbsoluteOrDriveQualified(String value) {
    Pattern windowsDrivePrefix = Pattern.compile("^[A-Za-z]:");
    return value.startsWith("/")
        || value.startsWith("\\")
        || windowsDrivePrefix.matcher(value).find();
  }

  static boolean containsParentSegment(String value) {
    Pattern parentSegment = Pattern.compile("(?:^|[/\\\\])\\.\\.(?:$|[/\\\\])");
    return parentSegment.matcher(value).find();
  }

  static boolean containsControl(String value) {
    return value.codePoints().anyMatch(Character::isISOControl);
  }
}
