package dev.codex.schubert.nk.protocol.layout.scenario;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts GAMRSP01. */
public record GameRecord(FieldValue.Text gameCode,
    FieldValue.Text title,
    FieldValue.Numeric displayOrder) implements PayloadRecord {
  public GameRecord {
    Objects.requireNonNull(gameCode, "gameCode");
    Objects.requireNonNull(title, "title");
    Objects.requireNonNull(displayOrder, "displayOrder");
  }

  public static GameRecord from(FieldValueSet fields) {
    return new GameRecord(
        TypedFieldValues.requiredText(fields, "Game code"),
        TypedFieldValues.requiredText(fields, "Title"),
        TypedFieldValues.requiredNumeric(fields, "Display order"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Game code", gameCode),
            Map.entry("Title", title),
            Map.entry("Display order", displayOrder)));
  }
}
