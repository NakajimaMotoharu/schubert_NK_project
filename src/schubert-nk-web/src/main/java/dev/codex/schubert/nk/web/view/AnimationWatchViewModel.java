package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.VideoCategory;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.springframework.web.util.UriUtils;

/** Display-only closed map: SCR010/FUN006/UI223235/SS313/PG-D365/PT-CONTENT. */
public final class AnimationWatchViewModel {
  private static final Map<VideoCategory, List<String>> NAVIGATION =
      Map.of(
          VideoCategory.MAIN, List.of("メインパート", "/animation/main", "メインパート一覧"),
          VideoCategory.SUBTRACK, List.of("メインパート", "/animation/main", "メインパート一覧"),
          VideoCategory.OVA, List.of("OVA", "/animation/ova", "OVA一覧"),
          VideoCategory.OPENING, List.of("オープニング", "/animation", "アニメ視聴"));

  private final Map<String, Object> values;

  private AnimationWatchViewModel(SessionPrincipal actor, VideoDescriptorResponseData data) {
    var navigation = Objects.requireNonNull(NAVIGATION.get(data.category()), "video navigation");
    String id = data.mediaLogicalId();
    if (id.isEmpty() || id.equals(".") || id.equals(".."))
      throw new IllegalArgumentException("invalid video link ID");
    values =
        Map.of(
            "topBar",
            TopBarViewModel.from(actor),
            "title",
            data.title(),
            "category",
            navigation.get(0),
            "displayPath",
            data.displayPath().wireValue(),
            "backHref",
            navigation.get(1),
            "backLabel",
            navigation.get(2),
            "mediaHref",
            "/animation/media/" + UriUtils.encode(id, StandardCharsets.UTF_8));
  }

  public static AnimationWatchViewModel from(
      SessionPrincipal actor, VideoDescriptorResponseData data) {
    return new AnimationWatchViewModel(
        Objects.requireNonNull(actor, "actor"), Objects.requireNonNull(data, "data"));
  }

  public Map<String, Object> getValues() {
    return values;
  }

  @Override
  public String toString() {
    return "AnimationWatchViewModel[REDACTED]";
  }
}
