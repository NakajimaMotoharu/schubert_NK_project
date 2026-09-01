package dev.codex.schubert.nk.protocol.layout;

import java.util.List;
import java.util.Objects;

/** Immutable data/record field catalog for one UI 233 layout. Trace: UI 234-236, SS 322 §12. */
public record LayoutFields(
    LayoutDefinition layout,
    List<FieldDefinition<?>> dataFields,
    List<FieldDefinition<?>> recordFields) {

  public LayoutFields {
    Objects.requireNonNull(layout, "layout");
    dataFields = List.copyOf(dataFields);
    recordFields = List.copyOf(recordFields);
    validateArea(FieldArea.DATA, layout.dataLength(), dataFields);
    validateArea(FieldArea.RECORD, layout.recordLength(), recordFields);
  }

  public LayoutId id() {
    return layout.id();
  }

  private static void validateArea(
      FieldArea expectedArea, int declaredLength, List<FieldDefinition<?>> fields) {
    int nextStart = 1;
    for (FieldDefinition<?> field : fields) {
      if (field.area() != expectedArea) {
        throw new LayoutValidationException("field is assigned to the wrong payload area");
      }
      if (field.start() != nextStart) {
        throw new LayoutValidationException("field catalog contains a gap or overlap");
      }
      nextStart = field.end() + 1;
    }
    if (nextStart - 1 != declaredLength) {
      throw new LayoutValidationException("field catalog does not cover the declared area length");
    }
  }
}
