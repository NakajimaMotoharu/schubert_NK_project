# 1635 API DB pool metric 単体テスト仕様書

NK-OPS-001/P018-09/共有C07追加費0、RD171 MON005～013/UI252/SS342351/PG-D542。DbPoolMetricRecorder.constructor/state/record/missing/snapshot/detail、Counts constructor/value/accessor・State.label。POOLMET001～008。SS351 `nk_db_pool_connections{service,state}`のactive/idle/pending/max、serviceはAPI固定（既WebのWEBと同じ内部所有ラベル方針）。caller供給immutable四longのみ、Hikari poolの生成/接続/管理getter・実DB/VM/Root/ネットワーク操作なし。

| Test ID | 入力・操作/fixture | 独立期待値 |
|---|---|---|
| POOLMET001 | DEBUG・実owned SDK/四enum | 固定名/GAUGE/二key/APIと四小文字state、全4series/初期NaN |
| POOLMET002 | 固定Counts3/5/2/8→record | 各getter/value/gaugeが原値3/5/2/8・同immutable snapshot、追加labelなし |
| POOLMET003 | 初期未知→真0/最大8→missing→回復 | 未知NaNとactive-idle-pending真0の分離、missing後snapshot空/旧snapshot不変 |
| POOLMET004 | STANDARD/invalid payload | 登録/保持0でもnull拒否、missing0、DEBUG/STD以外modeは固定拒否 |
| POOLMET005 | 各負count/max0/最大long/未知state/null | invalid先行拒否・元原long保持/総和計算やcross-getter原子性の捏造なし |
| POOLMET006 | 64並行・二固定completeCounts | snapshotが二vectorのどちらかだけ・mixed0/元snapshot不変、scrape跨series原子性は要求しない |
| POOLMET007 | SDK二番目登録でRuntime/Error故障 | 同一故障伝播/attempt2/retry0、partial registryはcaller所有・外部registry close0 |
| POOLMET008 | 別owner/反復1000record/missing | 全4series上限/owner値非共有/外部label生成0、資源closeはownedfixtureだけ |

Countsは全count非負・maximum>=1だけを確定し、実poolの非原子的getter列にactive+idle<=max等を推測追加しない。供給値から実接続真正性・警報・正常性/起動許可を作らない。expectedはSS四state/key/固定long/IEEE NaN/固定double値から独立、productionからexpected生成0。Null/欠落/未知/境界/並行/provider例外を通常PTで実行予定。

当sourceの新8＋必要既API24=32PT4suite/全9Java/実8＋metadata1・全1731physical/71sourceは予定で未実測。ordinary verify/XML真正終了/FES0/単一sessionCRC/四counter100/NullAway/SB/PMD-CS/全Jar/traceの実結果をPG7348/7350以降へ保存。実行環境・command/time/branch/source/exit/input/期待/実値/coverage/BUG/SSC/evidence path/hashを元manifestへ結合。実Hikari/DB/driver/sampling/outer有限collector/警報source/Root/exporter/native/CHR/全体451は未受入HOLD、正式1964/53・歴史17/別source新7・原190新受入0/工数null/QA051final/PTALT0維持。

BUG-3881／YKT-2997。POOLMET006の元の固定期待、8worker、64件、10秒、registry個別所有を保持。期限付き終了を共用し、二次失敗は一次を覆わない。現版の真正5件は[PG45494](evidence/PG45494-current-five-api-metric-fixture-owners/manifest.json)。実環境と正規全451は別。
