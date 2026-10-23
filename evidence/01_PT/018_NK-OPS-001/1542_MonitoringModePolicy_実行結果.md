# 1542 MonitoringModePolicy 実行結果

2026-10-23、Program NK-OPS-001/P018-09、1541/PG-D517、工程1797。製造stage完了、C07/P018-09全受入0、正式1964/53・工数null不変更。

| 原job/source | 真正結果 | 証拠 |
|---|---|---|
| PG7000 /06da06745 | format1、PT0/未実行 | manifest49d786d08ed7c7af7e3d2b167bbb34c78dca0087f7f405284d77ef626a2609e5 |
| PG7004 /0b97ab904 | 六format0、依存Storage no-testsで1、選択PT0 | c35df63aaf1be0605bef2fc30ea1218129a26a94ac5e7d8089be697f7c3220a5 |
| PG7006 /bcca200ac7ae985d4ef978c46ba5eb8eb7161b6a | 六format0、pure通常verify0、7件/1suite、F/E/S0、rerun/flaky0 | 22a05a2e42dffbebdeffd2742f00637ffac1b272a1c66733d77e5f9e5b2a35ce |
| PG7008 同source独立post | 実class CRC不一致0/単一session、元XML完全一致、L28/M8/C2/B9全miss0 | c06fb7e6827d879743988d5d55b976b1a6b34f736b26d95b8df7e5ca4f700d74 |

公開manifestは各 `evidence/provisional/PG7000-monitoring-mode-host-v1`、`PG7004-monitoring-mode-host-v2`、`PG7006-monitoring-pure-host-v1`、`PG7008-monitoring-mode-post-v1` 配下。原source.tar/開始/実process/実終了code/log/target/XML/execは `work/pgpt-runs/PG379/pg7006-monitoring-pure-host-v1` に保持。新7PTのTest IDと独立32状態oracleは1541/元XML methodsに一意対応。Main sourceはpolicy+package-infoの2file、Test1file、物理は実行2class＋annotation metadata1class。metadataを実行class3や除外によるcoverage増加とはしない。

Java25.0.4/Maven3.9.12、既親Enforcer/lint/Werror/NullAway、SpotBugs Max/Low0・Checkstyle0、JaCoCo0.8.15。実command・OS・版固定path・tool/source/XML/hashは原manifestを正とする。scopeはpure追加packageだけであり、Production六全体の四100やnativeを再認定しない。原4222/common44の再実行/新source合算0。

## PMD raw3件の個別適用性（raw終了4を保持）

| 元finding行/field | 判定 | 独立根拠と確認 |
|---|---|---|
|25 detailedMetricsEnabled|CONTEXT_NOT_APPLICABLE|private final primitive enum状態の明示read-only accessor。bean setter/可変propertyの誤用ではない。001/002/007が二mode literalと並行不変を検証 |
|26 retentionDays|CONTEXT_NOT_APPLICABLE|同final intのread-only accessor。15/0というSS351保持値を表す。001/007で独立literal一致 |
|27 retentionBytes|CONTEXT_NOT_APPLICABLE|同final longのread-only accessor。5000000000/0を返す。001/007で独立literal一致 |

全3件は同rule AvoidFieldNameMatchingMethodName。field/method同名を禁ずる意味ではなく可変bean混同への一般heuristicで、411の下位camelCase/value accessor契約に適合する。source全体をreviewし、既不変型と同じ限定適用性判断。各source/line/rule/message/原report hashは7008に保存。抑止/除外/閾値変更0、未分類0、raw3/exit4を0へ書換えない。F03 Root11の判定とは別。

BUG1644は所有joinの管理正負test/原6998六join0、1645は新二fileだけ正規format→7006六check0、1646はtrue no-tests gate/元7XML/全四100/CRC/sessionで当工具範囲を是正。修正commitは順に06da06745/0b97ab904/bcca200ac。YKT1397～1399は全当対象の修正又は非該当と再発防止を確認した。失敗・未知・未選択を成功へ加算しない。

共有枠は着手6→post照会6/reset1793306748（整数表示差0は実消費0を意味しない、PMO他chat込み、専有N/Tnull）。元/v4/v5と群開始0.5/1.5/3ppは不変更。次はSS351§6のcatalogue metadataと閉label-name契約の独立実装/PTを一工程として選ぶ。実collector/exporter/mode switch/配布・F03/Root/VM/native等は引き続きHOLD。
