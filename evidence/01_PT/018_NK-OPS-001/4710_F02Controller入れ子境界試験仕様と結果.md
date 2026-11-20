# F02 Controller入れ子の直接依存境界

WBS-F02-b、SS311 §5.2、BUG-3361／YKT-2716。ArchUnit 1.4.2とJava 25の通常classfileのみを使う。六つの合成JARに明示的な型所有を付け、解析対象は初期化しない。製品API/Web、実DB、JMS、filesystem操作は範囲外。

| Test ID | 対象 | 独立した期待 |
| --- | --- | --- |
| PT-F02-NEST-001 | 名前で識別するControllerの名前付き子 | 子からJDBC Connectionを指摘 |
| PT-F02-NEST-002 | Controller実装内の二段の型 | FileChannel呼び出しを指摘 |
| PT-F02-NEST-003 | Spring Controller注釈付き親の子 | Jakarta JMS Messageを指摘 |
| PT-F02-NEST-004 | RestController注釈付き親の匿名型 | Files呼び出しを指摘 |
| PT-F02-NEST-005 | Controllerの子からFacadeと一般streamを使う | 指摘なし |
| PT-F02-NEST-006 | Controller以外のFacadeの子でJMSを使う | 指摘なし |

PG40402の旧工具では禁止4ケースが未検出、許容2と原直接12は期待一致。修正後PG40404では新6、原12の計18が一致し、PG40406が固定classfile、元検出、差分4、他規則、ログhashを照合。どちらもintentionalな禁止例を入れたためArchUnit自体の終了1を記録した。PG40404の式比較は18/18。新規製品試験、製品六JAR検査、全451及び正式加算は各0。変更は解析工具のController判定だけ。
