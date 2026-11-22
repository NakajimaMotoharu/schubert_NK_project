package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Immutable registration of the synchronous request handlers before consumer exposure.
 *
 * <p>NK-MSG-001, MQ-003/MQ-006, UI232/233, SS311 §6.2 and SS323, SSC-477, PT-JMS-HREG001..006.
 */
public final class LayoutHandlerRegistry {
  private static final Map<LayoutId, Class<? extends PayloadData>> REQUIRED =
      LayoutRegistry.standard().all().stream()
          .filter(definition -> definition.messageKind() == MessageKind.REQUEST)
          .collect(
              Collectors.toUnmodifiableMap(
                  LayoutDefinition::id,
                  definition -> PayloadTypeCatalog.dataType(definition.id())));

  private final Map<LayoutId, LayoutHandler<?, ?>> handlers;

  public LayoutHandlerRegistry(Collection<? extends LayoutHandler<?, ?>> registrations) {
    Objects.requireNonNull(registrations, "handler registrations");
    Map<LayoutId, LayoutHandler<?, ?>> indexed = new HashMap<>();
    for (var registration : registrations) {
      var handler = Objects.requireNonNull(registration, "handler");
      var layout = Objects.requireNonNull(handler.requestLayout(), "handler layout");
      var expectedType = REQUIRED.get(layout);
      if (expectedType == null) {
        throw new IllegalArgumentException("handler layout is outside the synchronous requests");
      }
      var actualType = Objects.requireNonNull(handler.requestType(), "handler request type");
      if (!expectedType.equals(actualType)) {
        throw new IllegalArgumentException("handler request type does not match its layout");
      }
      if (indexed.putIfAbsent(layout, handler) != null) {
        throw new IllegalArgumentException("duplicate request handler layout");
      }
    }
    if (indexed.size() != REQUIRED.size()) {
      throw new IllegalArgumentException("required request handlers are missing");
    }
    handlers = Map.copyOf(indexed);
  }

  public Optional<LayoutHandler<?, ?>> find(LayoutId layout) {
    return Optional.ofNullable(handlers.get(Objects.requireNonNull(layout, "request layout")));
  }
}
