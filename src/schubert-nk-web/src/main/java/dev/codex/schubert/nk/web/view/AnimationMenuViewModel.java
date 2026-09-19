package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/** SCR008/FUN006/UI223,235/SS313,323/PG204/PT-WEB230..237. Closed display only. */
@NullMarked
public final class AnimationMenuViewModel {
  private final TopBarViewModel topBar;
  private final int mainCount, ovaCount, totalCount;
  private final boolean openingPresent;

  private AnimationMenuViewModel(SessionPrincipal actor, AnimationMenuResponseData data) {
    topBar = TopBarViewModel.from(actor);
    mainCount = data.mainSubtrackCount();
    ovaCount = data.ovaCount();
    totalCount = data.totalFileCount();
    openingPresent = data.openingPresent();
  }

  public static AnimationMenuViewModel from(
      SessionPrincipal actor, AnimationMenuResponseData data) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(data, "data");
    if (data.totalFileCount()
        != data.mainSubtrackCount() + data.ovaCount() + (data.openingPresent() ? 1 : 0))
      throw new IllegalArgumentException("inconsistent animation menu counts");
    return new AnimationMenuViewModel(actor, data);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public int getMainCount() {
    return mainCount;
  }

  public int getOvaCount() {
    return ovaCount;
  }

  public int getTotalCount() {
    return totalCount;
  }

  public boolean isOpeningPresent() {
    return openingPresent;
  }

  @Override
  public String toString() {
    return "AnimationMenuViewModel[REDACTED]";
  }
}
