package dev.codex.schubert.nk.protocol.file;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/** Non-public digest factory. Trace: NK-PRO-003, SS333, SSC452, BUG3182. */
interface LargeResultDigest {
  static MessageDigest digestFor(String algorithm) {
    try {
      return MessageDigest.getInstance(algorithm);
    } catch (NoSuchAlgorithmException exception) {
      throw new IllegalStateException("requested message digest is unavailable", exception);
    }
  }
}
