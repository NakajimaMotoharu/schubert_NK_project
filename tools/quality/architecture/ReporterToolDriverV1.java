import java.util.Map;

/** Closed, tool-only profiles; this is not an application entry or dynamic class-name interface. */
public final class ReporterToolDriverV1 {
  private static final String PREFIX = "dev.codex.schubert.nk.tooling.ReporterToolFixturesV1$";

  private ReporterToolDriverV1() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2) throw new IllegalArgumentException("tool profile and new output required");
    Map<String, Integer> counts =
        switch (args[0]) {
          case "passing" -> Map.of(PREFIX + "Passing", 2);
          case "two-passing" -> Map.of(PREFIX + "Passing", 2, PREFIX + "OtherPassing", 1);
          case "wrong-total" -> Map.of(PREFIX + "Passing", 3);
          case "wrong-distribution" -> Map.of(PREFIX + "Passing", 1, PREFIX + "OtherPassing", 2);
          case "failing" -> Map.of(PREFIX + "Failing", 1);
          case "skipped" -> Map.of(PREFIX + "Skipped", 1);
          case "aborted" -> Map.of(PREFIX + "Aborted", 1);
          case "failed-container" -> Map.of(PREFIX + "FailedContainer", 1);
          case "empty-tests" -> Map.of(PREFIX + "Empty", 1);
          case "empty-map" -> Map.of();
          case "zero-count" -> Map.of(PREFIX + "Passing", 0);
          case "invalid-name" -> Map.of("../outside", 2);
          default -> throw new IllegalArgumentException("unknown tool profile");
        };
    SharedSelectedJunitReporterV1.run(new String[] {args[1]}, counts);
  }
}
