# 性能・資源・Logout混在 結合テストケース

編集正本は [cases.json](../data/cases.json)。この巻は自動生成。全件NOT_EXECUTED。

全ケースは [512](../510_方針・準備/512_結合構成・環境・データ.md) の経路・環境・fixture・観測・C-ISOLATE と [541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md) を参照する。共通CP-BASEの入力以外の初期状態・証跡・中断・後片付けは cases.json.profiles に一元化し、個別追加条件と併せて必須とする。

他巻：[インターフェース](521_インターフェース.md) / [トランザクション・データ](522_トランザクション・データ.md) / [認証・権限・セキュリティ](523_認証・権限・セキュリティ.md) / [ファイル・メディア・Range](524_ファイル・メディア・Range.md) / [運用・復旧・監視](525_運用・復旧・監視.md) / [MQ・非同期・容量](526_MQ・非同期・容量.md) / [性能・資源・Logout混在](527_性能・資源・Logout混在.md)

<a id="it-perf-001"></a>
## IT-PERF-001 STANDARD10名・同期p95/MQ待ち

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

STANDARD10名・同期p95/MQ待ちによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SYNC |
| 確認契約 | STANDARD10名・同期p95/MQ待ち |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | 故障なし。負荷generatorとserverの時計相関・collector overheadを事前校正。 |
| 反復 | 1 |
| timeout・中断 | case45分。最低sample不足は不足扱い、新窓を事前固定して追加し同窓へ偽合算しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) §8 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [362_PG・PT・IT工程引継ぎ事項.md](<../../300_SS/360_引継ぎ・監査/362_PG・PT・IT工程引継ぎ事項.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（57件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "mode": "STANDARD",
  "users": 10,
  "inflight_per_user": 1,
  "warmup_minutes": 5,
  "measure_minutes": 30,
  "workload": "Login/Scenario検索/明細/Logを各独立窓、USER8+ADMIN2、最悪検索100件、各user think0で1完了後次。route別sample最低1000。"
}
```

**操作順序・入口**

同じ正規release/fixtureを各窓へ復元→5分warmup（窓外と明示）→barrier10userを解放→30分の全試行をraw CSVへ記録。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 各同期routeのp95=sort全試行elapsedのceil(.95*N)番&lt;=2.5秒、Web打鍵→描画完了まで。MQ待ち各要求&lt;=2.0秒、取り違え0、業務後条件一致。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A02 | timeout/error試行を分母から落とさず率を併記し失敗試行は非合格。計画停止/起動直後/故障中/media全体転送時間はRD151の明示範囲だけ除外し別窓保存。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A03 | OS/PG/API/Web/Artemis CPU/RSS/heap/direct/metaspace/thread/GC/FD/DBpool/lock/queue/disk/walを同窓で採取、設定上限内。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |
| A04 | instrumentation/DEBUG計測負荷付き窓を正式STANDARD値へ混在しない、raw値から都合の良い試行だけ採用0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-002"></a>
## IT-PERF-002 20stream混在とScenario/DB上限

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

20stream混在とScenario/DB上限によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-MEDIA |
| 確認契約 | 20stream混在とScenario/DB上限 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 45分、全raw latency/retentionを保全。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) §5/8 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（40件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "users": 10,
  "streams": 20,
  "range_bytes": 1048576,
  "scenario_records": 10000,
  "log_page": 100,
  "user_notification_question_page": 50,
  "measurement_minutes": 30
}
```

**操作順序・入口**

PERF001と同じ窓へ20Range stream/10000record SCNを重ね、各機能単独窓とも比較。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | Range開始応答と通常同期p95&lt;=2.5秒/MQ待ち&lt;=2.0秒、media全長完了をp95対象へ混ぜ0、最大stream20/21はRANGE020判定。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | SCN48000000byte/10000record、worst検索100/log100/新一覧50、最大wire&lt;=1000000byte。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | FD/thread/direct/heap/pool/lock/Query ID/planを実採取、N+1/無制限sortやstream完了時permit leak0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-003"></a>
## IT-PERF-003 16GB/256GB資源予算

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

16GB/256GB資源予算によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-OPS |
| 確認契約 | 16GB/256GB資源予算 |
| 必要環境 | E-OPS |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 個別45分、backup組合せは1800秒の親deadline不変更。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [342_Caddy・systemd・PostgreSQL・Java設定設計.md](<../../300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md>) §5.1/8 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [321_Artemis物理構成・JMS設定設計.md](<../../300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md>) §3/5.3 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（60件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "RAM_GB": 16,
  "SSD_GB": [
    45,
    35,
    30,
    10,
    5,
    10,
    80,
    5,
    36
  ],
  "budget_RAM_GB": {
    "PG": 4,
    "Artemis": 2,
    "API": 2,
    "Web": 1.5,
    "OS_Caddy_cache": 3,
    "safety_DEBUG": 3.5
  }
}
```

**操作順序・入口**

通常/同期10/stream20/SCN10000/backup-cleanupの個別と許された組合せでresource peakを同窓測定。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 全16GB・SSD配分256GB内、Web MemoryMax1536M/API2048M/Batch1536M/Artemis2048M、heap/direct/metaspaceのSS342表値一致。 | O-UNIT, O-FILE, O-DB, O-TIME, O-MQ, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | Artemis journal/paging&lt;=10GiB予算、metadata/consumer buffer overhead別計測。DB WAL/temp、backup7世代80GB、DEBUG停止を確認。 | O-UNIT, O-FILE, O-DB, O-TIME, O-MQ, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A03 | effective_cache_size6GBをallocationと二重計数0、native/thread/codecache headroomを0にせず過負荷時9001/ready制御・既受付保全。 | O-UNIT, O-FILE, O-DB, O-TIME, O-MQ, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-010"></a>
## IT-PERF-010 transfer byte容量 3499999999

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer byte容量 3499999999によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer byte容量 3499999999 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分、専用volumeの保全余裕をreserve。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_bytes": 3499999999,
  "request_records": 201,
  "file_count": "countcriticalに達しない500未満"
}
```

**操作順序・入口**

正規名前/所有/属性のtrial file群でroot scan→201record生成要求→実使用byte・alert・拒否を観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 3.5GB以上warning、4.5GB以上新規file mode9001/ready公開0、5GB設計上限超過受付0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 3.5GB未満は容量以外の条件を満たす場合生成許可、critical前からcritical超過を予約する扱いはSS未規定ならISS-TRANSFERへ止める。既存readyの削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-TRANSFER を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-011"></a>
## IT-PERF-011 transfer byte容量 3500000000

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer byte容量 3500000000によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer byte容量 3500000000 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分、専用volumeの保全余裕をreserve。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_bytes": 3500000000,
  "request_records": 201,
  "file_count": "countcriticalに達しない500未満"
}
```

**操作順序・入口**

正規名前/所有/属性のtrial file群でroot scan→201record生成要求→実使用byte・alert・拒否を観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 3.5GB以上warning、4.5GB以上新規file mode9001/ready公開0、5GB設計上限超過受付0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 3.5GB未満は容量以外の条件を満たす場合生成許可、critical前からcritical超過を予約する扱いはSS未規定ならISS-TRANSFERへ止める。既存readyの削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-TRANSFER を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-012"></a>
## IT-PERF-012 transfer byte容量 4499999999

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer byte容量 4499999999によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer byte容量 4499999999 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分、専用volumeの保全余裕をreserve。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_bytes": 4499999999,
  "request_records": 201,
  "file_count": "countcriticalに達しない500未満"
}
```

**操作順序・入口**

正規名前/所有/属性のtrial file群でroot scan→201record生成要求→実使用byte・alert・拒否を観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 3.5GB以上warning、4.5GB以上新規file mode9001/ready公開0、5GB設計上限超過受付0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 3.5GB未満は容量以外の条件を満たす場合生成許可、critical前からcritical超過を予約する扱いはSS未規定ならISS-TRANSFERへ止める。既存readyの削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-TRANSFER を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-013"></a>
## IT-PERF-013 transfer byte容量 4500000000

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer byte容量 4500000000によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer byte容量 4500000000 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分、専用volumeの保全余裕をreserve。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_bytes": 4500000000,
  "request_records": 201,
  "file_count": "countcriticalに達しない500未満"
}
```

**操作順序・入口**

正規名前/所有/属性のtrial file群でroot scan→201record生成要求→実使用byte・alert・拒否を観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 3.5GB以上warning、4.5GB以上新規file mode9001/ready公開0、5GB設計上限超過受付0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 3.5GB未満は容量以外の条件を満たす場合生成許可、critical前からcritical超過を予約する扱いはSS未規定ならISS-TRANSFERへ止める。既存readyの削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-TRANSFER を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-014"></a>
## IT-PERF-014 transfer byte容量 5000000000

仕様：**PENDING_DECISION** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer byte容量 5000000000によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer byte容量 5000000000 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分、専用volumeの保全余裕をreserve。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_bytes": 5000000000,
  "request_records": 201,
  "file_count": "countcriticalに達しない500未満"
}
```

**操作順序・入口**

正規名前/所有/属性のtrial file群でroot scan→201record生成要求→実使用byte・alert・拒否を観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 3.5GB以上warning、4.5GB以上新規file mode9001/ready公開0、5GB設計上限超過受付0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 3.5GB未満は容量以外の条件を満たす場合生成許可、critical前からcritical超過を予約する扱いはSS未規定ならISS-TRANSFERへ止める。既存readyの削除0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA, ISS-TRANSFER を全解除。判断待ち：ISS-TRANSFER。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-020"></a>
## IT-PERF-020 transfer file件数 4999

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer file件数 4999によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer file件数 4999 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_file_count": 4999,
  "byte_total": "3.5GB未満",
  "request_records": 201
}
```

**操作順序・入口**

正規file群を初期化しscan完了後の新規SCN要求とalertを観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 5000以上warning、9000以上新規file mode9001、10000上限超の受入0、既存成果保全。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 件数/byteを別条件で判定、part/ready/診断entryの計数定義をscanと照合し未知entryを0へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-021"></a>
## IT-PERF-021 transfer file件数 5000

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer file件数 5000によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer file件数 5000 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_file_count": 5000,
  "byte_total": "3.5GB未満",
  "request_records": 201
}
```

**操作順序・入口**

正規file群を初期化しscan完了後の新規SCN要求とalertを観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 5000以上warning、9000以上新規file mode9001、10000上限超の受入0、既存成果保全。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 件数/byteを別条件で判定、part/ready/診断entryの計数定義をscanと照合し未知entryを0へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-022"></a>
## IT-PERF-022 transfer file件数 8999

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer file件数 8999によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer file件数 8999 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_file_count": 8999,
  "byte_total": "3.5GB未満",
  "request_records": 201
}
```

**操作順序・入口**

正規file群を初期化しscan完了後の新規SCN要求とalertを観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 5000以上warning、9000以上新規file mode9001、10000上限超の受入0、既存成果保全。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 件数/byteを別条件で判定、part/ready/診断entryの計数定義をscanと照合し未知entryを0へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-023"></a>
## IT-PERF-023 transfer file件数 9000

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer file件数 9000によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer file件数 9000 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_file_count": 9000,
  "byte_total": "3.5GB未満",
  "request_records": 201
}
```

**操作順序・入口**

正規file群を初期化しscan完了後の新規SCN要求とalertを観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 5000以上warning、9000以上新規file mode9001、10000上限超の受入0、既存成果保全。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 件数/byteを別条件で判定、part/ready/診断entryの計数定義をscanと照合し未知entryを0へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-perf-024"></a>
## IT-PERF-024 transfer file件数 10000

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

transfer file件数 10000によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-FILE |
| 確認契約 | transfer file件数 10000 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。故障・並行を要求しない通常経路。 |
| 反復 | 1 |
| timeout・中断 | 15分。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [333_大容量結果file・media・Range配信設計.md](<../../300_SS/330_データ・ファイル/333_大容量結果file・media・Range配信設計.md>) §13 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) §7 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) §5.5 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（33件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "root_file_count": 10000,
  "byte_total": "3.5GB未満",
  "request_records": 201
}
```

**操作順序・入口**

正規file群を初期化しscan完了後の新規SCN要求とalertを観測。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 5000以上warning、9000以上新規file mode9001、10000上限超の受入0、既存成果保全。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 件数/byteを別条件で判定、part/ready/診断entryの計数定義をscanと照合し未知entryを0へ補完しない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-FILE, O-LOCK, O-FD。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-100-集中-なし"></a>
## IT-RETRY-100-集中-なし QA050通常業務混在 100集中なし

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 100集中なしによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 100集中なし |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 100,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "なし",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-100-集中-api停止復帰"></a>
## IT-RETRY-100-集中-API停止復帰 QA050通常業務混在 100集中API停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 100集中API停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 100集中API停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | API停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 100,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "API停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-100-集中-broker停止復帰"></a>
## IT-RETRY-100-集中-Broker停止復帰 QA050通常業務混在 100集中Broker停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 100集中Broker停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 100集中Broker停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | Broker停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 100,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "Broker停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-100-分散-なし"></a>
## IT-RETRY-100-分散-なし QA050通常業務混在 100分散なし

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 100分散なしによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 100分散なし |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 100,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "なし",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-100-分散-api停止復帰"></a>
## IT-RETRY-100-分散-API停止復帰 QA050通常業務混在 100分散API停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 100分散API停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 100分散API停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | API停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 100,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "API停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-100-分散-broker停止復帰"></a>
## IT-RETRY-100-分散-Broker停止復帰 QA050通常業務混在 100分散Broker停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 100分散Broker停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 100分散Broker停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | Broker停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 100,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "Broker停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-1000-集中-なし"></a>
## IT-RETRY-1000-集中-なし QA050通常業務混在 1000集中なし

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 1000集中なしによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 1000集中なし |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 1000,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "なし",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-1000-集中-api停止復帰"></a>
## IT-RETRY-1000-集中-API停止復帰 QA050通常業務混在 1000集中API停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 1000集中API停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 1000集中API停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | API停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 1000,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "API停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-1000-集中-broker停止復帰"></a>
## IT-RETRY-1000-集中-Broker停止復帰 QA050通常業務混在 1000集中Broker停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 1000集中Broker停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 1000集中Broker停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | Broker停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 1000,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "Broker停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-1000-分散-なし"></a>
## IT-RETRY-1000-分散-なし QA050通常業務混在 1000分散なし

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 1000分散なしによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 1000分散なし |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 1000,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "なし",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-1000-分散-api停止復帰"></a>
## IT-RETRY-1000-分散-API停止復帰 QA050通常業務混在 1000分散API停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 1000分散API停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 1000分散API停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | API停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 1000,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "API停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-1000-分散-broker停止復帰"></a>
## IT-RETRY-1000-分散-Broker停止復帰 QA050通常業務混在 1000分散Broker停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 1000分散Broker停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 1000分散Broker停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | Broker停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 1000,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "Broker停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-10000-集中-なし"></a>
## IT-RETRY-10000-集中-なし QA050通常業務混在 10000集中なし

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 10000集中なしによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 10000集中なし |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 10000,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "なし",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-10000-集中-api停止復帰"></a>
## IT-RETRY-10000-集中-API停止復帰 QA050通常業務混在 10000集中API停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 10000集中API停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 10000集中API停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | API停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 10000,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "API停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-10000-集中-broker停止復帰"></a>
## IT-RETRY-10000-集中-Broker停止復帰 QA050通常業務混在 10000集中Broker停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 10000集中Broker停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 10000集中Broker停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | Broker停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 10000,
  "due": "集中",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "Broker停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-10000-分散-なし"></a>
## IT-RETRY-10000-分散-なし QA050通常業務混在 10000分散なし

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 10000分散なしによりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 10000分散なし |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | なし。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 10000,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "なし",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-10000-分散-api停止復帰"></a>
## IT-RETRY-10000-分散-API停止復帰 QA050通常業務混在 10000分散API停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 10000分散API停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 10000分散API停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | API停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 10000,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "API停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。

<a id="it-retry-10000-分散-broker停止復帰"></a>
## IT-RETRY-10000-分散-Broker停止復帰 QA050通常業務混在 10000分散Broker停止復帰

仕様：**CONFIRMED** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。

QA050通常業務混在 10000分散Broker停止復帰によりSSの部品間契約と非更新条件を確認する。

| 項目 | 個別仕様（CP-BASEへ追加） |
|---|---|
| 結合経路・部品 | R-SESSION |
| 確認契約 | QA050通常業務混在 10000分散Broker停止復帰 |
| 必要環境 | E-REAL |
| artifact/設定/schema/data版 | F-BASE-v1（各case差分はinput）。release/config/schema/protocol/data版=baseline+最終再照合manifest。 |
| 事前条件・依存 | 独立cloneのため依存caseなし。UI操作に必要なLogin/GET formは当case setup内で行い、別caseのPASSを前提にしない。 |
| 同期・待機 | barrier到達receipt/DB commit/HTTP終端をイベントで待つ。未到達はTIMEOUT、sleepで到達推測しない。 |
| 故障注入・並行・再現 | Broker停止復帰。停止/復帰は専用所有envの正規操作だけ。 |
| 反復 | 1 |
| timeout・中断 | warmup5分+本窓45分+後処理10分=60分。保護row無限待機しない。 |
| 副作用禁止 | CP-BASE.non_effectsを適用。各assertionにある0件・不変条件は追加必須。 |
| 観測方法 | 512 O-*と513 T-*、assertionごとのraw artifactと判定recordを1:1対応。 |
| 判定式 | 全assertionが独立実測からtrue、必須evidenceのhash/相関が一致、未判定0の時だけPASS。 |
| 失敗保全 | CP-BASE.abort |
| 後片付け・再実行 | CP-BASE.cleanup。失敗時再実行は542に従い新attempt、初回結果を保持。 |
| 自動化・未作成工具 | CP-BASE.automation。故障/負荷/OS caseはT-FAULT/T-LOAD/T-OSも未実装。 |

**根拠文書・節・承認変更**

- [354_PT・IT試験観点詳細設計.md](<../../300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md>) QA050承認反映節 ／ QA050/UIC009/SSC171 ／ commit `8b91944df582`
- [314_認証・認可・session・CSRF実装設計.md](<../../300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md>) §10 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [351_Log・metric・alert・error code設計.md](<../../300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`
- [352_Security・credential・監査実装設計.md](<../../300_SS/350_運用・品質/352_Security・credential・監査実装設計.md>) QA050節 ／ なし（本文に明記した補足IDは別途参照） ／ commit `8b91944df582`

条件ID：JSONの `ss_condition_ids`（11件の節別/個別割当、内部詳細のIT複写ではない）。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。

**入力・初期状態差分**

```json
{
  "normal_load": "PERF001と同一10user/同route/同30分窓",
  "pending_revocations": 10000,
  "due": "分散",
  "due_distribution": "集中は初回T、分散は15分内へ等間隔（i*900/n秒）",
  "outage": "Broker停止復帰",
  "record_states": "NULL期限/物理session削除0102/復号不可/正常contextを各25%（割切れない端数は正常へ）、attempt99/100を交互",
  "duration": "初期5s/30s/5minと定常15minを2周期以上含む45分、障害variantは最初5分停止後復帰"
}
```

**操作順序・入口**

再試行なし同通常負荷基準を先に別窓で採取→指定残件/分布/停止を重ね45分実時間→復帰後claim/send/DB解放/滞留を採取。
CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。

**期待結果・取得証跡**

| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |
|---|---|---|
| A01 | 通常業務各route p95&lt;=2.5秒/MQ待ち&lt;=2.0秒/取り違え0、error/timeout率とCPU/pool/lock/Inbox/WAL/MQ/journal/diskを基準と同条件比較。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A02 | 初期5秒/30秒/5分、以後15分、attempt100でも継続。0000/0200だけ削除、一般0102/NULL期限/復号不可は保護・警告、context捏造送信0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A03 | JMS待機中DB接続/lock0、同時有効lease1/CAS、同lease重複dispatch0、lease切替後の遅着は元attemptへ追跡して失効/監査の論理更新1、freshMessage・元context不変、残row/borrowerがある旧keyは保持。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A04 | 解消可能残件の減少/最古時間/解消までを実時間記録。保護rowの有限自動解消は期待しない。15分定常平均だけで初期burstを隠さない。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |
| A05 | 基準未達なら因果を切分け、DB/lease不具合を間隔延長だけで隠さない。間隔変更はQA050変更記録とSS/UI整合後に同条件再測定、無断閾値緩和0。 | O-HTTP, O-WIRE, O-DB, O-MQ, O-LOG, O-LOCK, O-TIME。実測/path/SHA/判定式はattemptへ記録 |

**実行可能条件・不足**

DEP-PGPT, DEP-REBASE, DEP-ENV, PREP-TOOLS, PREP-DATA を全解除。判断待ち：なし（開始依存・工具準備は別途必要）。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。
