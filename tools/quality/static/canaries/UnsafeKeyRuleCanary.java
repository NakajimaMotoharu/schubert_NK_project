import javax.crypto.spec.SecretKeySpec;

/** Deliberately unsafe public synthetic counterexample, never Production or a real credential. */
final class UnsafeKeyRuleCanary {
  private UnsafeKeyRuleCanary() {}

  static SecretKeySpec specification() {
    return new SecretKeySpec(new byte[] {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, "AES");
  }
}
