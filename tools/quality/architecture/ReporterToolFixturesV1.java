package dev.codex.schubert.nk.tooling;

import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

/** Intentionally minimal reporter fixtures, never Product tests, assertions or coverage credit. */
public final class ReporterToolFixturesV1 {
  private ReporterToolFixturesV1() {}

  public static final class Passing {
    @Test
    void first() {}

    @Test
    void second() {}
  }

  public static final class OtherPassing {
    @Test
    void other() {}
  }

  public static final class Failing {
    @Test
    void fails() {
      throw new AssertionError("reporter-tool-only-failure");
    }
  }

  public static final class Skipped {
    @Test
    @Disabled("reporter tool skip")
    void skipped() {}
  }

  public static final class Aborted {
    @Test
    void aborted() {
      Assumptions.assumeTrue(false);
    }
  }

  public static final class FailedContainer {
    @BeforeAll
    static void prepare() {
      throw new IllegalStateException("reporter-tool-only-container-failure");
    }

    @Test
    void notStarted() {}
  }

  public static final class Empty {}
}
