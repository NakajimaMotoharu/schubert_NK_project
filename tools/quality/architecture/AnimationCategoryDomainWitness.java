import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.view.AnimationListViewModel;
import java.time.Instant;
import java.util.List;
import java.util.Optional;

/** BUG2103: five UI235 literal domain checks using only synthetic in-memory DTOs. */
public final class AnimationCategoryDomainWitness {
  private AnimationCategoryDomainWitness() {}

  private static AnimationRecord item(
      String id, AnimationCategory category, Optional<String> parent, int order) {
    return new AnimationRecord(
        id, "synthetic", category, DisplayPath.of("video/synthetic.mp4"), 1, parent, order);
  }

  private static boolean accepted(
      AnimationListCategory category, List<AnimationRecord> records) {
    var actor = new SessionPrincipal(
        "synthetic", UserRole.USER, AuthenticationContext.of("0".repeat(64)), Instant.EPOCH);
    try {
      return AnimationListViewModel.from(
          actor, category, new AnimationListResponseData(records.size()), records)
          .getTotalCount() == records.size();
    } catch (IllegalArgumentException rejected) {
      return false;
    }
  }

  public static void main(String[] args) {
    if (args.length != 0) throw new IllegalArgumentException("no arguments");
    for (String property : List.of("runtime.version", "os.name", "os.arch", "os.version")) {
      System.out.println(property + "="
          + System.getProperty(property.equals("runtime.version") ? "java.runtime.version" : property));
    }
    var main = item("main", AnimationCategory.MAIN, Optional.empty(), 1);
    var sub = item("sub", AnimationCategory.SUBTRACK, Optional.of("main"), 2);
    var ova = item("ova", AnimationCategory.OVA, Optional.empty(), 1);
    var opening = item("opening", AnimationCategory.OPENING, Optional.empty(), 1);
    boolean a = accepted(AnimationListCategory.MAIN, List.of(main));
    boolean b = accepted(AnimationListCategory.OVA, List.of(ova));
    boolean c = accepted(AnimationListCategory.MAIN, List.of(main, sub));
    boolean d = !accepted(AnimationListCategory.MAIN, List.of(opening));
    boolean e = !accepted(AnimationListCategory.OVA, List.of(opening));
    System.out.println("MAIN_BASELINE_ACCEPTED=" + a);
    System.out.println("OVA_BASELINE_ACCEPTED=" + b);
    System.out.println("PAIR_BASELINE_ACCEPTED=" + c);
    System.out.println("MAIN_OPENING_REJECTED=" + d);
    System.out.println("OVA_OPENING_REJECTED=" + e);
    System.exit(a && b && c && d && e ? 0 : 1);
  }
}
