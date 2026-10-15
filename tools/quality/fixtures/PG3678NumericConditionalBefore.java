import java.util.Set;

/** Independent Java numeric-conditional reproduction; no Production method or private data. */
final class PG3678NumericConditionalBefore {
  public static void main(String[] args) {
    int mismatches = 0;
    for (String key : new String[] {"uid", "gid", "mode", "nlink", "dev", "ino", "size"}) {
      Object actual =
          Set.of("uid", "gid", "mode", "nlink").contains(key)
              ? Integer.valueOf(1)
              : Long.valueOf(0);
      if (key.equals("nlink")) actual = Integer.valueOf(2);
      Class<?> expected =
          Set.of("uid", "gid", "mode", "nlink").contains(key) ? Integer.class : Long.class;
      if (expected != actual.getClass()) mismatches++;
      System.out.println(key + ":" + expected.getSimpleName() + ":" + actual.getClass().getSimpleName());
    }
    if (mismatches != 3) throw new AssertionError("Original fixture expected exactly three type defects");
    System.out.println("originalTypedFixtureMismatches=" + mismatches);
  }
}
