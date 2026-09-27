# PG312 schema履歴照合PT（暫定）

Program NK-OPS-001、SchemaHistoryAdmission.Row/constructor/verify・JdbcAdmissionFailures・ServiceDatabaseAdmission.verify。RD DAT009/SYS002/OPS009、UI212/253、SS3313.3/3439.1、SSC095、BUG283/YKT216。正式認定へ限定成功を加算しない。

| Test ID | 入力・操作/fixture | 独立期待値・根拠 |
|---|---|---|
| PT-OPS-SCHEMA001 | literal SCHEMA0/SQL1・CRC -170000001、public JDBC proxy | 固定六列query、timeout5、各owner close1、borrowed connection close0。SCHEMA0 version/checksumNULL |
| SCHEMA002 | 全列NULL/不一致、失敗/欠落/余剰/順序変更 | SS六列全行比較で08001固定診断、例外provider text/causeを出さない |
| SCHEMA003 | rank/version/type/script/checksum/success/null全境界 | SCHEMA0限定、SQL1..999/三桁非000/固定script/nonnull CRC/successのみ、正規境界999/200字可 |
| SCHEMA004 | null/list要素/empty/1001/order/duplicate、防御copy | constructor invariant、mutable入力変更非影響、最大1000行可、借用接続null拒否 |
| SCHEMA005 | null statement/rows、prepare/timeout/query/read/全close SQL失敗 | 固定08001、取得済ownerを一度close、接続不所有 |
| SCHEMA006 | body/rowclose/statementclose各success/SQL/runtime/Errorの64組＋同一例外 | 独立順位matrix。未知primary identity保持、known＋unknown closeはunknown、secondary固定診断、自抑制なし |
| SCHEMA007 | 呼出前/最後のnextで割込 | 非成功・割込保持、取得owner全close |
| SCHEMA008 | barrierで同時8呼出 | expected immutable共有、各接続/owner独立、全結果とclose数一致 |
| PT-OPS-DBADMIT003 | BUG283 null owner2＋同一未知body/close＋known body/unknown statementclose | NPE正常化なし、原未知identity保持・全close・borrowed非close |

fixture期待値はtestのliteral map/定数から構成し、Production query/helper/運用DBから生成しない。SQL履歴expectedは最終Assemblyで承認release BOMへ結び付ける必要があり、このproxy fixtureはrelease信頼の証明ではない。null annotation/NullAway・SpotBugs、line/method/class/branch各100%、例外/境界/並行要求。実行command/環境/対象hash/結果は148とprovisional PG312 manifestへ保存する。DB権限の実PG試験はNK-DAT-001/068へ対応。
