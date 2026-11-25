# 1647 API Outbox rows metric 単体テスト仕様書

NK-OPS-001/P01809/C07共有費0、RD171/UI252/SS331§7.2/351/PG-D545。OutboxRowsMetricRecorder.constructor/status/record/missing/snapshot/detail、Counts constructor/accessors/value・Status enum。OUTBOXMET001～008。`nk_outbox_rows{store=API,status}`の三statusは既V003/SS331のPENDING/SENT/ERRORのみ。供給immutable三longだけ、row内容/owner/ID/body/token/SQLparameter/例外文字列は受け取らず、実DB/dispatcher/送信/再送/削除を行わない。

| Test ID | fixture/操作 | 独立期待値 |
|---|---|---|
| OUTBOXMET001 | DEBUG/実owned SDK/三enum | 一metric/GAUGE/二key/API固定/三literal状態、3series初期NaN |
| OUTBOXMET002 | 固定Counts3/5/2→record | 全accessor/value/gaugeが3/5/2・同immutable snapshot、series追加0 |
| OUTBOXMET003 | 初期→真0→missing→回復 | 初期/欠測NaNと全0を区別、旧snapshot不変/回復原値 |
| OUTBOXMET004 | STANDARD/invalid payload | 登録/保持0でもnull境界拒否 |
| OUTBOXMET005 | 負三count/null/未知alias/mode/最大long | 先行固定拒否・echo0、原long最大保持/SDK doubleは独立IEEE2^63、不要sum/wrap0 |
| OUTBOXMET006 | 64並行/二complete vector | snapshotは供給二組のどちらか、mixed0/旧原値不変・跨gauge scrape原子性は認定しない |
| OUTBOXMET007 | 二番目Gauge登録でRuntime/Error | 同一伝播/attempt2/retry0・partial registryはcaller所有 |
| OUTBOXMET008 | 別owner/1000反復 | 三series上限/値非共有/外部registry close0 |

oracleは独立SS/DDL三literal/固定long/IEEE値/key集合、productionからexpected生成0。countsは各非負だけ、総和を計算せずlong精度を保持。DEBUG詳細だけ/STD最小healthは止めない。新8＋必要既API56=64PT8suite/全17Java/実15＋metadata1・全1738physical/79sourceは予定未実測。元PG7390/7392以降ordinary verify/真XML終了/FES0/単一sessionCRC/四counter100/NullAway/SB/PMD-CS/全Jar/traceへ環境・command/time/branch/source/exit/BUG-SSC/evidence path/hashを結合する。

この群はAPI件数familyだけ。`nk_outbox_oldest_seconds`、WEB store、実readonly SQL集計/driver/dispatch/backoff/alert/外側有限collector/Root/exporter/native/CHR/全体451は別未受入HOLD。正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0不変更。SDK四＋当既aux二/harness不変更・導入取得0、群1-3-6pp上限10/共有開始20/専有N-Tnull/通常区切り停止0。

BUG-3880／YKT-2997。OUTBOXMET006の合成SDK registry、固定二cohort、8 worker／64件／10秒を維持。有限workerの終了失敗は元例外の抑制として保持し、registryは後に閉じる。局所二件と独立補助一件、F/E/skip各0。 [PG45488](evidence/PG45488-current-outbox-metric-shared-workers/manifest.json)
