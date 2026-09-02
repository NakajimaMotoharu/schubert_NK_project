package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts GAMRSP01. */
public record GameRecord(String gameCode,
    String title,
    long displayOrder) implements PayloadRecord {
  public GameRecord {
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(title, "title");
  }

  public static GameRecord from(FieldValueSet fields) {
    return new GameRecord(
        TypedFieldValues.requiredString(fields, "Game code"),
        TypedFieldValues.requiredString(fields, "Title"),
        TypedFieldValues.requiredLong(fields, "Display order"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", TypedFieldValues.text(gameCode)),
            Map.entry("Title", TypedFieldValues.text(title)),
            Map.entry("Display order", TypedFieldValues.numeric(displayOrder))));
  }

  @Override
  public String toString() {
    return "GameRecord[REDACTED]";
  }
}
