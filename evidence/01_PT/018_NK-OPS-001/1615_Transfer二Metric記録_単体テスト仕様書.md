# 1615 Transfer二Metric記録 単体テスト仕様書

再試験追加（2026-10-23、BUG1657/YKT1410）：元936/7266真正161・7268四100/PMD31は保持し、新規三命名違反だけprivate field改名後の別sourceで7272/7274/7276以降へ再資格する。公開API/独立期待値/新8case数は不変更、旧成功は新sourceへ転用しない。全Main PMDの当rule0と旧28全行一致を再発防止checkに追加し、元31行を抑制/分類だけで消さない。

NK-OPS-001/P018-09/共有C07追加費0、RD171 MON005～013/UI252/SS341§8・SS351§6/8/10・PG-D537。TransferMetricRecorder constructor/record/missing/snapshot/detail/value・Counts/Usage/Suffix。group1856、開始共有16/残84/reset1793306748・1/2/5pp上限10。Inputは固定long files/bytesと二suffixだけ、実file/dir/secure walk/cleanup/Root/DBを一切実行しない。

固定oracle：`nk_file_transfer_files`/`nk_file_transfer_bytes` はgauge/label suffix、既承認`.part`/`.ready`だけ。DEBUG4系列、STANDARD0、未知NaN（zeroにしない）。Countsは非負、Usageは二Counts非null/各総和long範囲内、byte/件数のoverflowをwrapしない。metricはbinary64、long値原本はsnapshotで正確保持する。別gauge scrapeの同時snapshot一貫性は保証せず、実collector/sourceの認定とは分離する。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| TRANSFERMET001 | DEBUG生成/全初期meter・Suffix literal | 既二metric・各二suffix・全4gauge、初期NaN/empty、借用先未close |
| TRANSFERMET002 | 固定part=(2,1024)/ready=(3,2048) | 各gauge2/1024/3/2048、snapshot総和5/3072・旧snapshot不変 |
| TRANSFERMET003 | zero→missing→再観測 | 真のzeroは0、missingはNaN/empty、復帰は固定4値 |
| TRANSFERMET004 | STANDARD全操作/null | meter/保存0、missingはempty、nullは境界拒否 |
| TRANSFERMET005 | null ctor/mode/count/usage・負値・総和overflow | 副作用前に例外、元snapshot不変 |
| TRANSFERMET006 | Long.MAX_VALUE、1byte/件境界 | 原snapshot long厳密、metricの独立IEEE丸め期待・総和overflow拒否 |
| TRANSFERMET007 | 64並行、二cohort交互・旧snapshot | 全snapshotは二承認cohortいずれかで混合なし、固定final値・系列4不変 |
| TRANSFERMET008 | SDK二番目Gauge登録故障/二owner | 同一Throwable/再試行0/partial caller所有、owner間非共有 |

新8＋必要既153を当source固定後ordinary Maven verify、全XML/終了/FES0と独立CRC/単一session/実Main四counter100、lint/Werror/NullAway/SB/CS/PMD個別判定。SDKは既四Jar同版pin/取得なし、src/既POM/設定/oracle変更は新追加以外なし。PG7266/7268以降manifestにOS/JDK/tool/branch/source・command/日時/終了/XML/coverage/static/path/hashを保存予定。未実行は合格にせず、新障害は修正前915/916起票。

実walk/owner/finite期限・Root/cleanup/受入停止制御/exporter/native/CHR/全体451は未受入HOLD。正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0を維持する。
