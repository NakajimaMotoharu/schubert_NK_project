package dev.codex.schubert.nk.protocol.layout;

import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/** Immutable 64-layout registry. Trace: NK-PRO-001, UI 233, SS 322 §12/§13. */
public final class LayoutRegistry {
  private static final LayoutRegistry STANDARD = new LayoutRegistry(standardDefinitions());

  private final List<LayoutDefinition> definitions;
  private final Map<String, LayoutDefinition> byKey;

  private LayoutRegistry(Collection<LayoutDefinition> source) {
    LinkedHashMap<String, LayoutDefinition> index = validatedIndex(source);
    byKey = Collections.unmodifiableMap(index);
    definitions = List.copyOf(index.values());
  }

  static void validateDefinitions(Collection<LayoutDefinition> source) {
    validatedIndex(source);
  }

  private static LinkedHashMap<String, LayoutDefinition> validatedIndex(
      Collection<LayoutDefinition> source) {
    Objects.requireNonNull(source, "source");
    LinkedHashMap<String, LayoutDefinition> index = new LinkedHashMap<>();
    for (LayoutDefinition definition : source) {
      Objects.requireNonNull(definition, "definition");
      validateIdentifierKind(definition);
      String key = key(definition.id(), definition.version());
      if (index.putIfAbsent(key, definition) != null) {
        throw new LayoutValidationException("duplicate layout ID/version");
      }
    }
    if (index.isEmpty()) {
      throw new LayoutValidationException("layout registry must not be empty");
    }
    return index;
  }

  public static LayoutRegistry standard() {
    return STANDARD;
  }

  public List<LayoutDefinition> all() {
    return definitions;
  }

  public LayoutDefinition require(LayoutId id, int version) {
    Objects.requireNonNull(id, "id");
    LayoutDefinition definition = byKey.get(key(id, version));
    if (definition == null) {
      throw new UnsupportedLayoutException("unsupported layout ID/version");
    }
    return definition;
  }

  public LayoutDefinition require(String id, int version) {
    Objects.requireNonNull(id, "id");
    return require(new LayoutId(id), version);
  }

  private static String key(LayoutId id, int version) {
    return id.value() + ':' + version;
  }

  private static void validateIdentifierKind(LayoutDefinition definition) {
    String id = definition.id().value();
    MessageKind expected =
        ifEvent(id)
            ? MessageKind.EVENT
            : id.substring(3, 6).equals("REQ")
                ? MessageKind.REQUEST
                : id.substring(3, 6).equals("RSP")
                    ? MessageKind.RESPONSE
                    : null;
    if (expected == null || definition.messageKind() != expected) {
      throw new LayoutValidationException("layout ID and message kind disagree");
    }
    InteractionKind expectedInteraction =
        ifEvent(id)
            ? InteractionKind.INTERNAL
            : (id.equals("QSBREQ01") || id.equals("QSBRSP01"))
                ? InteractionKind.ASYNC_ACCEPTANCE
                : InteractionKind.SYNCHRONOUS;
    if (definition.interactionKind() != expectedInteraction) {
      throw new LayoutValidationException("layout ID and interaction kind disagree");
    }
  }

  private static boolean ifEvent(String id) {
    return id.equals("QWKREQ01") || id.equals("WLGEVT01");
  }

  private static List<LayoutDefinition> standardDefinitions() {
    return List.of(
        d("LGNREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 384, 0, 0, 640),
        d("LGNRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 432, 0, 0, 688),
        d("LOGREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0, 256),
        d("LOGRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 24, 0, 0, 280),
        d("GAMREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0, 256),
        d("GAMRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 9, 272, 10, 2_985),
        d("SPKREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 12, 0, 0, 268),
        d("SPKRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 9, 152, 500, 76_265),
        d("SRCREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 672, 0, 0, 928),
        d("SRCRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 48, 5_584, 100, 558_704),
        d("RTEREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 12, 0, 0, 268),
        d("RTERSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 9, 72, 50, 3_865),
        d("SCFREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 14, 0, 0, 270),
        d("SCFRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 88, 800, 500, 400_344),
        d("SCNREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 12, 0, 0, 268),
        d("SCNRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 1_728, 4_800, 200, 961_984),
        d("AUDREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 16, 0, 0, 272),
        d("AUDRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 1_024, 0, 0, 1_280),
        d("ANMREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0, 256),
        d("ANMRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 16, 0, 0, 272),
        d("ANLREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 16, 0, 0, 272),
        d("ANLRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 8, 928, 50, 46_664),
        d("VIDREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 64, 0, 0, 320),
        d("VIDRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 1_808, 0, 0, 2_064),
        d("MCTREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0, 256),
        d("MCTRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 8, 72, 20, 1_704),
        d("MCSREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 64, 0, 0, 320),
        d("MCSRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 8, 136, 100, 13_864),
        d("MTRREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 192, 0, 0, 448),
        d("MTRRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 16, 1_312, 200, 262_672),
        d("MEDREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 72, 0, 0, 328),
        d("MEDRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 1_024, 0, 0, 1_280),
        d("LGSREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 656, 0, 0, 912),
        d("LGSRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 48, 2_088, 100, 209_104),
        d("USRREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 96, 0, 0, 352),
        d("USRRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 48, 168, 50, 8_704),
        d("UCRREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 372, 0, 0, 628),
        d("UCRRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 24, 0, 0, 280),
        d("UDTREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 12, 0, 0, 268),
        d("UDTRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 320, 0, 0, 576),
        d("USTREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 60, 0, 0, 316),
        d("USTRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 24, 0, 0, 280),
        d("URLREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 68, 0, 0, 324),
        d("URLRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 24, 0, 0, 280),
        d("UPWREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 324, 0, 0, 580),
        d("UPWRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 24, 0, 0, 280),
        d("ULKREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 60, 0, 0, 316),
        d("ULKRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 24, 0, 0, 280),
        d("QSBREQ01", MessageKind.REQUEST, InteractionKind.ASYNC_ACCEPTANCE, 4_144, 0, 0, 4_400),
        d("QSBRSP01", MessageKind.RESPONSE, InteractionKind.ASYNC_ACCEPTANCE, 64, 0, 0, 320),
        d("NTSREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 64, 0, 0, 320),
        d("NTSRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 48, 624, 50, 31_504),
        d("NTDREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 12, 0, 0, 268),
        d("NTDRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 8_896, 0, 0, 9_152),
        d("NTCREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 48, 0, 0, 304),
        d("NTCRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 32, 0, 0, 288),
        d("QSSREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 384, 0, 0, 640),
        d("QSSRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 48, 672, 50, 33_904),
        d("QSDREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 12, 0, 0, 268),
        d("QSDRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 8_352, 0, 0, 8_608),
        d("QDLREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 48, 0, 0, 304),
        d("QDLRSP01", MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 24, 0, 0, 280),
        d("QWKREQ01", MessageKind.EVENT, InteractionKind.INTERNAL, 64, 0, 0, 320),
        d("WLGEVT01", MessageKind.EVENT, InteractionKind.INTERNAL, 2_080, 0, 0, 2_336));
  }

  private static LayoutDefinition d(
      String id,
      MessageKind kind,
      InteractionKind interaction,
      int dataLength,
      int recordLength,
      int maximumRecordCount,
      int maximumTotalLength) {
    return new LayoutDefinition(
        new LayoutId(id),
        1,
        kind,
        interaction,
        dataLength,
        recordLength,
        maximumRecordCount,
        maximumTotalLength);
  }
}
