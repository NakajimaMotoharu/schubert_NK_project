package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts ANMRSP01. */
public record AnimationMenuResponseData(
    int mainSubtrackCount, int ovaCount, boolean openingPresent, int totalFileCount)
    implements PayloadData {
  public AnimationMenuResponseData {
    TypedFieldValues.requireUnsignedRange("mainSubtrackCount", mainSubtrackCount, 3);
    TypedFieldValues.requireUnsignedRange("ovaCount", ovaCount, 3);
    TypedFieldValues.requireUnsignedRange("totalFileCount", totalFileCount, 3);
  }

  public static AnimationMenuResponseData from(FieldValueSet fields) {
    return new AnimationMenuResponseData(
        TypedFieldValues.requiredInt(fields, "Main/SUBTRACK件数"),
        TypedFieldValues.requiredInt(fields, "OVA件数"),
        TypedFieldValues.requiredBoolean(fields, "Opening有無"),
        TypedFieldValues.requiredInt(fields, "総file件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Main/SUBTRACK件数", TypedFieldValues.numeric(mainSubtrackCount)),
            Map.entry("OVA件数", TypedFieldValues.numeric(ovaCount)),
            Map.entry("Opening有無", TypedFieldValues.flag(openingPresent)),
            Map.entry("総file件数", TypedFieldValues.numeric(totalFileCount))));
  }

  @Override
  public String toString() {
    return "AnimationMenuResponseData[REDACTED]";
  }
}
