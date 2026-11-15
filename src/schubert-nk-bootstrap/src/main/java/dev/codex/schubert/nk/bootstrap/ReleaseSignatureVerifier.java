package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.security.KeyFactory;
import java.security.Signature;
import java.security.spec.X509EncodedKeySpec;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed Ed25519 primitive for the separately trusted deployment tool, not an approval publisher.
 * The pinned public DER is supplied only by that tool's fixed root key; never by a candidate BOM.
 * NK-OPS-001/SYS002/004/OPS009/DAT009/UI212/251/253/SS34311.1/SSC096/PG313; PT-OPS-SIGN001..008.
 * RFC8032 original-byte verification, no signer/private key/hash fallback.
 */
@NullMarked
public final class ReleaseSignatureVerifier {
  private static final byte[] PREFIX = HexFormat.of().parseHex("302a300506032b6570032100");
  private final byte[] pinned;
  private final Crypto crypto;

  @FunctionalInterface
  interface Crypto {
    boolean verify(byte[] key, byte[] message, byte[] signature) throws GeneralSecurityException;
  }

  public ReleaseSignatureVerifier(byte[] pinnedPublicDer) {
    this(pinnedPublicDer, new NativeCrypto());
  }

  ReleaseSignatureVerifier(byte[] pinnedPublicDer, Crypto crypto) {
    Objects.requireNonNull(pinnedPublicDer, "pinned public key");
    this.crypto = Objects.requireNonNull(crypto, "signature engine");
    require(pinnedPublicDer.length == 44);
    this.pinned = pinnedPublicDer.clone();
    require(Arrays.equals(PREFIX, 0, PREFIX.length, pinned, 0, PREFIX.length));
  }

  public void verify(byte[] originalManifest, byte[] detachedSignature) throws IOException {
    Objects.requireNonNull(originalManifest, "original manifest");
    Objects.requireNonNull(detachedSignature, "detached signature");
    require(originalManifest.length <= 1_048_576 && detachedSignature.length == 64);
    byte[] key = pinned.clone();
    // SSC419/BUG3015: protect each owned clone before another allocation can fail.
    try {
      byte[] message = originalManifest.clone();
      try {
        byte[] signature = detachedSignature.clone();
        try {
          if (!crypto.verify(key, message, signature)) throw unavailable();
        } catch (GeneralSecurityException invalid) {
          StorageIoException.preserveFatal(invalid);
          throw unavailable();
        } finally {
          Arrays.fill(signature, (byte) 0);
        }
      } finally {
        Arrays.fill(message, (byte) 0);
      }
    } finally {
      Arrays.fill(key, (byte) 0);
    }
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("invalid release signature material");
  }

  private static IOException unavailable() {
    return new IOException("release signature unavailable");
  }

  static final class NativeCrypto implements Crypto {
    public boolean verify(byte[] key, byte[] message, byte[] signature)
        throws GeneralSecurityException {
      var publicKey = KeyFactory.getInstance("Ed25519").generatePublic(new X509EncodedKeySpec(key));
      var verifier = Signature.getInstance("Ed25519");
      verifier.initVerify(publicKey);
      verifier.update(message);
      return verifier.verify(signature);
    }
  }
}
