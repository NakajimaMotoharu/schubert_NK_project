#!/usr/bin/env python3
"""Generate the 69 SS 323 named records from the checked UI field fixture.

Run from the repository root:
  python3 src/schubert-nk-protocol/build-tools/001_generate_payload_records.py

The generator never edits RD/UI/SS or the fixture. Generated records explicitly map every
non-fixed component in wire order and do not use reflection at runtime.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FIELDS = ROOT / "src/schubert-nk-protocol/src/test/resources/protocol/fields-ui234-236.tsv"
SS323 = ROOT / "documents/300_SS/320_メッセージング/323_全電文layout・Java・DB対応表.md"
JAVA_ROOT = (
    ROOT
    / "src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout"
)


NON_ASCII_NAMES = {
    "Active session数": "activeSessionCount",
    "Audio有無": "audioPresent",
    "Entry件数": "entryCount",
    "Error日時": "errorAt",
    "File byte長": "fileByteLength",
    "File record件数": "fileRecordCount",
    "File record長": "fileRecordLength",
    "File件数": "fileCount",
    "From日時": "fromAt",
    "Line番号": "lineNumber",
    "Main/SUBTRACK件数": "mainSubtrackCount",
    "OVA件数": "ovaCount",
    "Opening有無": "openingPresent",
    "Retry after秒": "retryAfterSeconds",
    "Route名": "routeName",
    "Session失効日時": "sessionRevokedAt",
    "Speaker名": "speakerName",
    "To日時": "toAt",
    "Track件数": "trackCount",
    "Voice条件": "voiceCondition",
    "内部状態": "internalState",
    "処理完了日時": "processingCompletedAt",
    "処理開始日時": "processingStartedAt",
    "出現件数": "occurrenceCount",
    "利用者message": "userMessage",
    "利用者向けerror": "userFacingError",
    "削除日時": "deletedAt",
    "取消日時": "cancelledAt",
    "受付ID": "receiptId",
    "受付日時": "submittedAt",
    "受付日時From": "submittedFrom",
    "受付日時To": "submittedTo",
    "回答日時": "answeredAt",
    "回答本文": "answerText",
    "回答状態": "answerState",
    "更新後version": "updatedVersion",
    "更新後状態": "updatedState",
    "最終更新日時": "lastUpdatedAt",
    "期限日時": "expiresAt",
    "本文": "bodyText",
    "本文keyword": "bodyKeyword",
    "業務Message ID": "businessMessageId",
    "残り試行回数": "remainingAttempts",
    "発生日時": "occurredAt",
    "発行日時": "issuedAt",
    "章title": "chapterTitle",
    "総file件数": "totalFileCount",
    "認証context ID": "authenticationContextId",
    "質問削除済み": "questionDeleted",
    "質問本文": "questionText",
    "質問概要": "questionSummary",
    "通知区分": "notificationType",
}


def component_name(label: str) -> str:
    if label in NON_ASCII_NAMES:
        return NON_ASCII_NAMES[label]
    if any(ord(character) > 127 for character in label):
        raise ValueError(f"missing component mapping: {label}")
    normalized = (
        label.replace("SHA-256", "Sha256")
        .replace("HTTP", "Http")
        .replace("MIME", "Mime")
        .replace("SUBTRACK", "Subtrack")
        .replace("OVA", "Ova")
        .replace("ID", "Id")
        .replace("/", " And ")
    )
    words = re.findall(r"[A-Za-z0-9]+", normalized)
    if not words:
        raise ValueError(f"empty component name: {label}")
    return words[0][0].lower() + words[0][1:] + "".join(word[:1].upper() + word[1:] for word in words[1:])


def package_for(layout: str, class_name: str) -> str:
    if class_name == "PagedResponseData":
        return "common"
    if layout.startswith(("LGN", "LOG")):
        return "auth"
    if layout.startswith(("GAM", "SPK", "SRC", "RTE", "SCF", "SCN")):
        return "scenario"
    if layout.startswith(("AUD", "ANM", "ANL", "VID", "MCT", "MCS", "MTR", "MED")):
        return "media"
    if layout.startswith(("LGS", "WLG")):
        return "log"
    if layout.startswith(("USR", "UCR", "UDT", "UST", "URL", "UPW", "ULK")):
        return "admin"
    if layout.startswith(("QSB", "NTS", "NTD", "NTC", "QSS", "QSD", "QDL", "QWK")):
        return "question"
    raise ValueError(f"unknown layout package: {layout}")


fields_by_area: dict[tuple[str, str], list[tuple[str, str, str, int, str]]] = defaultdict(list)
for line in FIELDS.read_text(encoding="utf-8").splitlines():
    if not line or line.startswith("#"):
        continue
    layout, area, label, _start, length, wire, presence, rule = line.split("\t")
    if presence != "F":
        fields_by_area[(layout, area)].append((label, wire, presence, int(length), rule))

layout_types: dict[str, tuple[str, str | None]] = {}
for line in SS323.read_text(encoding="utf-8").splitlines():
    match = re.match(r"^\| `([A-Z0-9]{8})`[^|]*\| ([^|]+) \|", line)
    if not match:
        continue
    names = re.findall(r"`([A-Za-z][A-Za-z0-9]+)`", match.group(2))
    if not names:
        continue
    layout_types[match.group(1)] = (names[0], names[1] if len(names) > 1 else None)

if len(layout_types) != 64:
    raise SystemExit(f"expected 64 layout type rows, got {len(layout_types)}")

class_specs: dict[
    str, tuple[str, str, list[tuple[str, str, str, int, str]], list[str]]
] = {}
for layout, (data_class, record_class) in layout_types.items():
    for class_name, area, kind in [
        (data_class, "DATA", "PayloadData"),
        (record_class, "RECORD", "PayloadRecord"),
    ]:
        if class_name is None:
            continue
        fields = fields_by_area[(layout, area)]
        package = package_for(layout, class_name)
        if class_name in class_specs:
            old_package, old_kind, old_fields, layouts = class_specs[class_name]
            if (old_package, old_kind, old_fields) != (package, kind, fields):
                raise SystemExit(f"shared type schema mismatch: {class_name}")
            layouts.append(layout)
        else:
            class_specs[class_name] = (package, kind, fields, [layout])


def semantic_kind(label: str, wire: str, length: int) -> str:
    if wire == "N":
        return "instant" if length == 17 else "long"
    if wire == "B":
        return "boolean"
    if label == "認証context ID":
        return "authenticationContext"
    if "SHA-256" in label:
        return "sha256"
    if "relative path" in label.lower():
        return "relativePath"
    if label in {"Display path", "Script display path", "Audio display path"}:
        return "displayPath"
    if length == 36:
        return "uuid"
    if length == 17:
        return "instant"
    return "string"


JAVA_TYPES = {
    "string": "String",
    "long": "long",
    "boolean": "boolean",
    "instant": "Instant",
    "uuid": "UUID",
    "authenticationContext": "AuthenticationContext",
    "sha256": "Sha256Hex",
    "relativePath": "RelativePath",
    "displayPath": "DisplayPath",
}


def java_type(kind: str, presence: str) -> str:
    base = JAVA_TYPES[kind]
    return f"Optional<{base}>" if presence in {"C", "O"} else base


def from_expression(label: str, kind: str, presence: str) -> str:
    escaped = label.replace("\\", "\\\\").replace('"', '\\"')
    if presence in {"C", "O"}:
        method = {
            "string": "optionalString",
            "instant": "optionalInstant",
            "uuid": "optionalUuid",
            "authenticationContext": "optionalAuthenticationContext",
            "sha256": "optionalSha256",
            "relativePath": "optionalRelativePath",
            "displayPath": "optionalDisplayPath",
        }[kind]
        return f'TypedFieldValues.{method}(fields, "{escaped}")'
    method = {
        "string": "requiredString",
        "long": "requiredLong",
        "boolean": "requiredBoolean",
        "instant": "requiredInstant",
        "uuid": "requiredUuid",
        "sha256": "requiredSha256",
        "relativePath": "requiredRelativePath",
        "displayPath": "requiredDisplayPath",
    }[kind]
    return f'TypedFieldValues.{method}(fields, "{escaped}")'


def field_expression(name: str, kind: str, presence: str) -> str:
    if presence in {"C", "O"}:
        method = {
            "string": "optionalStringValue",
            "instant": "optionalInstantValue",
            "uuid": "optionalUuidValue",
            "authenticationContext": "optionalAuthenticationContextValue",
            "sha256": "optionalSha256Value",
            "relativePath": "optionalRelativePathValue",
            "displayPath": "optionalDisplayPathValue",
        }[kind]
    else:
        method = {
            "string": "text",
            "long": "numeric",
            "boolean": "flag",
            "instant": "instant",
            "uuid": "uuid",
            "sha256": "sha256",
            "relativePath": "relativePath",
            "displayPath": "displayPath",
        }[kind]
    return f"TypedFieldValues.{method}({name})"


for class_name, (package, kind, fields, layouts) in sorted(class_specs.items()):
    components = [
        (component_name(label), label, semantic_kind(label, wire, length), presence)
        for label, wire, presence, length, _rule in fields
    ]
    names = [component[0] for component in components]
    if len(names) != len(set(names)):
        raise SystemExit(f"duplicate Java component in {class_name}: {names}")
    optional_used = any(presence in {"C", "O"} for _, _, _, presence in components)
    component_kinds = {component_kind for _, _, component_kind, _ in components}
    reference_used = any(component_kind not in {"long", "boolean"} for component_kind in component_kinds)
    imports = [
        "import dev.codex.schubert.nk.protocol.layout.FieldValueSet;",
        f"import dev.codex.schubert.nk.protocol.layout.{kind};",
        "import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;",
    ]
    if components:
        imports.append("import java.util.Map;")
    if reference_used:
        imports.append("import java.util.Objects;")
    if optional_used:
        imports.append("import java.util.Optional;")
    if "instant" in component_kinds:
        imports.append("import java.time.Instant;")
    if "uuid" in component_kinds:
        imports.append("import java.util.UUID;")
    if "authenticationContext" in component_kinds:
        imports.append("import dev.codex.schubert.nk.protocol.header.AuthenticationContext;")
    if "sha256" in component_kinds:
        imports.append("import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;")
    if "relativePath" in component_kinds:
        imports.append("import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;")
    if "displayPath" in component_kinds:
        imports.append("import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;")
    component_text = ",\n    ".join(
        f"{java_type(component_kind, presence)} {name}"
        for name, _label, component_kind, presence in components
    )
    declaration = f"public record {class_name}({component_text}) implements {kind}" if components else f"public record {class_name}() implements {kind}"
    lines = [
        f"package dev.codex.schubert.nk.protocol.layout.{package};",
        "",
        *sorted(imports),
        "",
        f"/** Generated named wire record. Trace: SS 323; layouts {', '.join(layouts)}. */",
        declaration + " {",
    ]
    if components:
        lines.extend([f"  public {class_name} {{"])
        for name, _label, component_kind, _presence in components:
            if component_kind not in {"long", "boolean"}:
                lines.append(f'    Objects.requireNonNull({name}, "{name}");')
        lines.append("  }")
    lines.extend(["", f"  public static {class_name} from(FieldValueSet fields) {{"])
    if components:
        lines.append(f"    return new {class_name}(")
        lines.append(
            ",\n".join(
                "        " + from_expression(label, component_kind, presence)
                for _name, label, component_kind, presence in components
            )
            + ");"
        )
    else:
        lines.extend(["    TypedFieldValues.requireEmpty(fields);", f"    return new {class_name}();"])
    lines.extend(["  }", "", "  @Override", "  public FieldValueSet fields() {"])
    if components:
        lines.append("    return new FieldValueSet(")
        lines.append("        Map.ofEntries(")
        entries = []
        for name, label, component_kind, presence in components:
            escaped = label.replace("\\", "\\\\").replace('"', '\\"')
            entries.append(
                f'            Map.entry("{escaped}", {field_expression(name, component_kind, presence)})'
            )
        lines.append(",\n".join(entries) + "));")
    else:
        lines.append("    return FieldValueSet.empty();")
    lines.extend(
        [
            "  }",
            "",
            "  @Override",
            "  public String toString() {",
            f'    return "{class_name}[REDACTED]";',
            "  }",
            "}",
            "",
        ]
    )
    directory = JAVA_ROOT / package
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{class_name}.java").write_text("\n".join(lines), encoding="utf-8")

print(f"generated {len(class_specs)} named record classes")


catalog_imports = []
for class_name, (package, _kind, _fields, _layouts) in sorted(class_specs.items()):
    catalog_imports.append(
        f"import dev.codex.schubert.nk.protocol.layout.{package}.{class_name};"
    )

catalog_lines = [
    "package dev.codex.schubert.nk.protocol.layout;",
    "",
    *catalog_imports,
    "import java.util.ArrayList;",
    "import java.util.List;",
    "import java.util.Map;",
    "import java.util.Objects;",
    "import java.util.Optional;",
    "import java.util.function.Function;",
    "",
    "/** Explicit SS 323 layout-to-named-type registry; runtime field-order reflection is forbidden. */",
    "public final class PayloadTypeCatalog {",
    "  private static final Map<String, Mapping> STANDARD =",
    "      Map.ofEntries(",
]
mapping_entries = []
for layout, (data_class, record_class) in layout_types.items():
    if record_class is None:
        expression = f'mapping("{layout}", {data_class}.class, {data_class}::from)'
    else:
        expression = (
            f'mapping("{layout}", {data_class}.class, {data_class}::from, '
            f'{record_class}.class, {record_class}::from)'
        )
    mapping_entries.append(f"          Map.entry(\"{layout}\", {expression})")
catalog_lines.append(",\n".join(mapping_entries) + ");")
catalog_lines.extend(
    [
        "",
        "  private PayloadTypeCatalog() {}",
        "",
        "  public static TypedPayloadValues decode(PayloadValues values) {",
        "    Objects.requireNonNull(values, \"values\");",
        "    Mapping mapping = require(values.layoutId());",
        "    PayloadData data = mapping.dataDecoder().apply(values.data());",
        "    List<PayloadRecord> records = decodeRecords(values, mapping.recordMapping());",
        "    return new TypedPayloadValues(values.layoutId(), data, records);",
        "  }",
        "",
        "  public static PayloadValues encode(TypedPayloadValues values) {",
        "    Objects.requireNonNull(values, \"values\");",
        "    Mapping mapping = require(values.layoutId());",
        "    if (!mapping.dataType().isInstance(values.data())) {",
        "      throw new LayoutValidationException(\"named data type does not match layout\");",
        "    }",
        "    validateRecordTypes(values.records(), mapping.recordMapping());",
        "    List<FieldValueSet> records =",
        "        values.records().stream().map(PayloadRecord::fields).toList();",
        "    return new PayloadValues(values.layoutId(), values.data().fields(), records);",
        "  }",
        "",
        "  public static Class<? extends PayloadData> dataType(LayoutId layoutId) {",
        "    return require(layoutId).dataType();",
        "  }",
        "",
        "  public static Optional<Class<? extends PayloadRecord>> recordType(LayoutId layoutId) {",
        "    return require(layoutId).recordMapping().map(RecordMapping::recordType);",
        "  }",
        "",
        "  private static List<PayloadRecord> decodeRecords(",
        "      PayloadValues values, Optional<RecordMapping> optionalMapping) {",
        "    if (optionalMapping.isEmpty()) {",
        "      if (!values.records().isEmpty()) {",
        "        throw new LayoutValidationException(\"layout does not define repeating records\");",
        "      }",
        "      return List.of();",
        "    }",
        "    RecordMapping mapping = optionalMapping.orElseThrow();",
        "    List<PayloadRecord> records = new ArrayList<>(values.records().size());",
        "    for (FieldValueSet fields : values.records()) {",
        "      records.add(mapping.recordDecoder().apply(fields));",
        "    }",
        "    return List.copyOf(records);",
        "  }",
        "",
        "  private static void validateRecordTypes(",
        "      List<PayloadRecord> records, Optional<RecordMapping> optionalMapping) {",
        "    if (optionalMapping.isEmpty()) {",
        "      if (!records.isEmpty()) {",
        "        throw new LayoutValidationException(\"layout does not define repeating records\");",
        "      }",
        "      return;",
        "    }",
        "    Class<? extends PayloadRecord> expected = optionalMapping.orElseThrow().recordType();",
        "    for (PayloadRecord record : records) {",
        "      if (!expected.isInstance(record)) {",
        "        throw new LayoutValidationException(\"named record type does not match layout\");",
        "      }",
        "    }",
        "  }",
        "",
        "  private static Mapping require(LayoutId layoutId) {",
        "    Objects.requireNonNull(layoutId, \"layoutId\");",
        "    Mapping mapping = STANDARD.get(layoutId.value());",
        "    if (mapping == null) {",
        "      throw new UnsupportedLayoutException(\"unsupported named payload layout\");",
        "    }",
        "    return mapping;",
        "  }",
        "",
        "  private static Mapping mapping(",
        "      String layoutId,",
        "      Class<? extends PayloadData> dataType,",
        "      Function<FieldValueSet, ? extends PayloadData> dataDecoder) {",
        "    return new Mapping(layoutId, dataType, dataDecoder, Optional.empty());",
        "  }",
        "",
        "  private static Mapping mapping(",
        "      String layoutId,",
        "      Class<? extends PayloadData> dataType,",
        "      Function<FieldValueSet, ? extends PayloadData> dataDecoder,",
        "      Class<? extends PayloadRecord> recordType,",
        "      Function<FieldValueSet, ? extends PayloadRecord> recordDecoder) {",
        "    return new Mapping(",
        "        layoutId,",
        "        dataType,",
        "        dataDecoder,",
        "        Optional.of(new RecordMapping(recordType, recordDecoder)));",
        "  }",
        "",
        "  private record Mapping(",
        "      String layoutId,",
        "      Class<? extends PayloadData> dataType,",
        "      Function<FieldValueSet, ? extends PayloadData> dataDecoder,",
        "      Optional<RecordMapping> recordMapping) {}",
        "",
        "  private record RecordMapping(",
        "      Class<? extends PayloadRecord> recordType,",
        "      Function<FieldValueSet, ? extends PayloadRecord> recordDecoder) {}",
        "}",
        "",
    ]
)
(JAVA_ROOT / "PayloadTypeCatalog.java").write_text(
    "\n".join(catalog_lines), encoding="utf-8"
)
print(f"generated {len(layout_types)} explicit layout type mappings")
