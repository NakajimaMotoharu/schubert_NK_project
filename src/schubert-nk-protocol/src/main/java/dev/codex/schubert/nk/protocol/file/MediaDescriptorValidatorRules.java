package dev.codex.schubert.nk.protocol.file;

import java.util.Map;
import java.util.regex.Pattern;

/** Immutable non-public grammar cache. Trace: SSC451, SS322/323/333. */
interface MediaDescriptorValidatorRules {

  Pattern HASH = Pattern.compile("[0-9a-f]{64}");
  Map<String, String> MUSIC_MIME =
      Map.of(
          ".m4a", "audio/mp4",
          ".mp3", "audio/mpeg",
          ".ogg", "audio/ogg",
          ".wav", "audio/wav",
          ".flac", "audio/flac");
}
