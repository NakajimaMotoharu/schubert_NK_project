import java.util.Arrays;
import java.util.Objects;
import javax.crypto.spec.SecretKeySpec;

/** Public synthetic inputs only; the validation label is not encryption-key material. */
public final class DynamicKeyRuleCanary {
  private final byte[] currentKey;

  private DynamicKeyRuleCanary(byte[] supplied) {
    currentKey = validateKey(supplied, "currentKey");
  }

  private static byte[] validateKey(byte[] key, String label) {
    Objects.requireNonNull(key, label);
    if (key.length != 32) throw new IllegalArgumentException(label);
    return key.clone();
  }

  private SecretKeySpec specification() {
    return new SecretKeySpec(currentKey, "AES");
  }

  public static void main(String[] args) {
    for (byte value : new byte[] {0x11, 0x22}) {
      byte[] expected = new byte[32];
      Arrays.fill(expected, value);
      byte[] supplied = expected.clone();
      DynamicKeyRuleCanary holder = new DynamicKeyRuleCanary(supplied);
      Arrays.fill(supplied, (byte) 0x33);
      if (!Arrays.equals(expected, holder.specification().getEncoded())) {
        throw new AssertionError("dynamic caller value not preserved");
      }
    }
    System.out.println("PASS dynamic-two-independent-inputs; label-not-key; caller-mutation-isolated");
  }
}
