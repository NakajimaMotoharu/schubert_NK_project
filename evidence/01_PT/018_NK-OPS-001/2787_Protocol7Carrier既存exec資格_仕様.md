# 2787 Protocol7 Carrier既存exec資格仕様

## 対象・依存

Production source `6b53efeec87f3ec36a840dd8e7759656cb4aee5c`、normal PG14216、原run PG14360、独立post PG14362。既存31件/7 suiteのXML・exec/session・CRCを使用し、製品試験は再実行しない。31件はCurrent908に計上済みであり、新規試験/JVM/正式受入への加算は0。

Program: protocol/layout の FieldValue、FieldValueSet、LayoutPayload、PayloadData、PayloadRecord、semantic/ProtocolId、semantic/WireEnum。7 Source/11 physicalの完全closureをJar・classfile・SourceFile・Code属性で確認する。関連WBSはP001-02/P001-03/P002-01。RD/UI/SSとの対応は485の各artifactの既存canonical ownerと原PG14360/14362の関連仕様を保持し、新たな業務仕様は変更しない。

## Test ID・独立期待値

- PT-OPS-2787-01: 原manifest/hash、XML31件一意・F/E/S0、same source、normal、fixtures、実環境prefix、one exec/session、CRCと既存registryとの非重複Sourceを照合する。
- PT-OPS-2787-02: 7 Source/11 physicalをJar inventoryから独立に確定。6 interfaceにはCodeがないことを要求する。Numeric/FlagはCodeを持つrecordであり、JaCoCo標準生成filterにより実際にzero counterとなった場合だけGENERATED_RECORD_CODEとする。NO_CODEに読み替えない。
- PT-OPS-2787-03: 受動CounterInventoryと既存CoverageDiagnosticで同一exec/classの四counterを照合。実missedをそのまま保持し、0/0を100%にせずN/Aを分離する。FieldValueSet等の不足は未受入のまま残す。
- PT-OPS-2787-04: 独立postでclosure・class metadata・XML・CRC・counter合計・source分類を照合し、fake metadata/four100/旧source/重複試験等を拒否する。
- PT-OPS-2787-05: BUG2113/YKT1860。literal置換の固定11正常/11異常工具vector、元native置換の再現、修正版のliteral保存、9既存工具の実hash・AST・元成功証跡を確認する。製品PTには加算しない。

期待値は固定classfile構造、原XML、独立class inventoryおよび既存固定fixtureに基づく。Production methodからexpectedを生成しない。null/未知/境界/例外の業務試験期待値は原31試験を維持する。新規並行・再送・実DB/VM/サービス試験は行わない。

## 実行・禁止・証跡

`env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14862_protocol_carrier_seven_existing_post.py`

工具compileはJDK25.0.4、proc:none/Werror、JaCoCo0.8.15/ASMのみ。製品classをload/初期化せず、原classとexecを解析する。原exec/sourceは変更しない。独立postはPG14864として保存する。結果・hash・時刻・実command/exit・OS/JDK・branch・source・欠測は2788と各公開manifestに保存する。

外部/VM/DB/Root/native/HOLD対象へのアクセスなし。四counter100、451/F03/G07、正式1964PT/53scope、QA051 final、工数率nullの条件は緩和しない。
