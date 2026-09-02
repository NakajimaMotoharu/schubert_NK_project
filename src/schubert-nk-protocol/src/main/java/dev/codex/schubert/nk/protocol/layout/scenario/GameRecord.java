package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts GAMRSP01. */
public record GameRecord(GameCode gameCode,
    String title,
    int displayOrder) implements PayloadRecord {
  public GameRecord {
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(title, "title");
    TypedFieldValues.requireUnsignedRange("displayOrder", displayOrder, 3);
  }

  public static GameRecord from(FieldValueSet fields) {
    return new GameRecord(
        TypedFieldValues.requiredEnum(fields, "Game code", GameCode.class),
        TypedFieldValues.requiredString(fields, "Title"),
        TypedFieldValues.requiredInt(fields, "Display order"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", TypedFieldValues.enumValue(gameCode)),
            Map.entry("Title", TypedFieldValues.text(title)),
            Map.entry("Display order", TypedFieldValues.numeric(displayOrder))));
  }

  @Override
  public String toString() {
    return "GameRecord[REDACTED]";
  }
}
