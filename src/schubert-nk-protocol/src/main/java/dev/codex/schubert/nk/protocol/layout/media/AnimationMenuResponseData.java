package dev.codex.schubert.nk.protocol.layout.media;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts ANMRSP01. */
public record AnimationMenuResponseData(FieldValue.Numeric mainSubtrackCount,
    FieldValue.Numeric ovaCount,
    FieldValue.Flag openingPresent,
    FieldValue.Numeric totalFileCount) implements PayloadData {
  public AnimationMenuResponseData {
    Objects.requireNonNull(mainSubtrackCount, "mainSubtrackCount");
    Objects.requireNonNull(ovaCount, "ovaCount");
    Objects.requireNonNull(openingPresent, "openingPresent");
    Objects.requireNonNull(totalFileCount, "totalFileCount");
  }

  public static AnimationMenuResponseData from(FieldValueSet fields) {
    return new AnimationMenuResponseData(
        TypedFieldValues.requiredNumeric(fields, "Main/SUBTRACK件数"),
        TypedFieldValues.requiredNumeric(fields, "OVA件数"),
        TypedFieldValues.requiredFlag(fields, "Opening有無"),
        TypedFieldValues.requiredNumeric(fields, "総file件数"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Main/SUBTRACK件数", mainSubtrackCount),
            Map.entry("OVA件数", ovaCount),
            Map.entry("Opening有無", openingPresent),
            Map.entry("総file件数", totalFileCount)));
  }
}
